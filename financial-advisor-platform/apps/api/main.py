from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any
import numpy as np
import os
from datetime import datetime

app = FastAPI(title="Advisor API", version="0.2.0")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Portfolio Advice ----
class PortfolioAdviceRequest(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    horizon_years: int = Field(ge=1, le=60)
    current_value: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    inflation: float = Field(default=0.025, ge=0, le=0.15)

class PortfolioAdviceResponse(BaseModel):
    risk_score: int
    recommended_allocation: Dict[str, float]
    expected_return_annual: float
    expected_volatility_annual: float
    rebalance_policy: Dict[str, Any]
    savings_plan: Dict[str, Any]
    goal_projection: Dict[str, Any]

ASSETS = ["US_Equities","Intl_Equities","US_Bonds","Intl_Bonds","Real_Estate","Cash"]
ANCHORS = {
    20: np.array([0.25,0.10,0.45,0.10,0.07,0.03]),
    60: np.array([0.45,0.20,0.23,0.05,0.05,0.02]),
    90: np.array([0.60,0.25,0.08,0.02,0.04,0.01])
}
EXP_RET = np.array([0.07,0.065,0.035,0.03,0.055,0.02])
VOL = np.array([0.16,0.18,0.06,0.07,0.13,0.01])
CORR = np.array([
 [1.00,0.80,-0.20,-0.15,0.60,-0.05],
 [0.80,1.00,-0.25,-0.20,0.55,-0.05],
 [-0.20,-0.25,1.00,0.65,-0.10,0.10],
 [-0.15,-0.20,0.65,1.00,-0.05,0.10],
 [0.60,0.55,-0.10,-0.05,1.00,-0.02],
 [-0.05,-0.05,0.10,0.10,-0.02,1.00]
])

def interp_weights(score: int) -> np.ndarray:
    if score <= 60: lo, hi = 20, 60
    else:          lo, hi = 60, 90
    t = (score - lo) / (hi - lo) if hi != lo else 0
    w = ANCHORS[lo]*(1-t) + ANCHORS[hi]*t
    return (w / w.sum()).astype(float)

@app.post("/advice/portfolio", response_model=PortfolioAdviceResponse)
def advise_portfolio(req: PortfolioAdviceRequest):
    w = interp_weights(req.risk_score)
    cov = np.outer(VOL, VOL) * CORR
    mu = float(EXP_RET @ w)
    sigma = float(np.sqrt(w @ cov @ w))

    years = req.horizon_years
    infl = req.inflation
    monthly = req.monthly_contribution
    pv = req.current_value

    mu_m = (1 + mu)**(1/12) - 1
    sigma_m = sigma / np.sqrt(12)

    sims = 5000
    final_values = np.zeros(sims)
    for s in range(sims):
        v = pv
        for _ in range(years*12):
            r = np.random.normal(mu_m, sigma_m)
            v = v*(1+r) + monthly
        final_values[s] = v

    deflate = (1 + infl)**years
    fv_real = final_values / deflate
    prob_goal = float(np.mean(fv_real >= 1_000_000.0))
    med = float(np.median(fv_real))
    p10 = float(np.percentile(fv_real, 10))
    p90 = float(np.percentile(fv_real, 90))

    return {
        "risk_score": req.risk_score,
        "recommended_allocation": {k: round(float(v),4) for k,v in zip(ASSETS,w)},
        "expected_return_annual": round(mu,4),
        "expected_volatility_annual": round(sigma,4),
        "rebalance_policy": {"method":"threshold","threshold_pct":0.20,"check_frequency":"quarterly"},
        "savings_plan": {"monthly_contribution": monthly, "emergency_fund_months": 3},
        "goal_projection": {
            "probability_goal_achieved_real": round(prob_goal,4),
            "median_terminal_value_real": round(med,2),
            "p10_p90_terminal_real": [round(p10,2), round(p90,2)],
            "horizon_years": years,
            "inflation_assumption": infl
        }
    }

# ---- Options Advice (conservative) ----
from math import log, sqrt, exp
from statistics import NormalDist
norm = NormalDist()

class OptionIdeaRequest(BaseModel):
    underlying: str
    price: float
    risk_free: float
    iv: float
    dte: int
    shares_owned: int = 0
    cash_available: float = 0.0

class OptionIdeaResponse(BaseModel):
    strategy: str
    legs: List[dict]
    est_yield: float
    max_loss: str
    notes: str

def bs_call_price(S,K,r,sigma,T):
    if sigma <= 0 or T <= 0: 
        return max(S-K, 0.0)
    d1 = (log(S/K)+(r+0.5*sigma**2)*T)/(sigma*sqrt(T))
    d2 = d1 - sigma*sqrt(T)
    return S*norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)

@app.post("/advice/options", response_model=OptionIdeaResponse)
def ideas(req: OptionIdeaRequest):
    T = req.dte/365
    # Covered call if >=100 shares
    if req.shares_owned >= 100:
        strike = round(req.price*1.05, 2)
        prem = bs_call_price(req.price, strike, req.risk_free, req.iv, T)
        est_yield = (prem*100)/(req.price*100)
        return {
            "strategy":"Covered Call",
            "legs":[{"type":"SELL_CALL","strike":strike,"expiry_days":req.dte}],
            "est_yield": round(est_yield,4),
            "max_loss": "Downside of underlying minus premium",
            "notes":"Income generation; caps upside; consider rolling if breached."
        }
    # Cash-secured put
    if req.cash_available >= req.price*100:
        strike = round(req.price*0.95, 2)
        prem = bs_call_price(req.price, strike, req.risk_free, req.iv, T) # parity shortcut
        return {
            "strategy":"Cash-Secured Put",
            "legs":[{"type":"SELL_PUT","strike":strike,"expiry_days":req.dte}],
            "est_yield": round((prem*100)/(strike*100),4),
            "max_loss": "Strike*100 - premium; ensure cash reserved",
            "notes":"Potentially acquire shares at discount; assignment risk."
        }
    raise HTTPException(400,"No eligible conservative strategies for provided inputs.")

# ---- Reports ----
@app.get("/reports/overview")
def overview():
    # Demo payload
    return {
        "as_of": datetime.utcnow().isoformat(),
        "net_worth": 123456.78,
        "allocation": {"US_Equities":0.45,"Intl_Equities":0.20,"US_Bonds":0.23,"Intl_Bonds":0.05,"Real_Estate":0.05,"Cash":0.02},
        "goal_probability": 0.42,
        "alerts": ["Rebalance US_Equities (-6% from target)", "Build emergency fund: 2 months saved"]
    }
