"use client";
import { useEffect, useState } from "react";
import AllocationChart from "../components/AllocationChart";
import GoalGauge from "../components/GoalGauge";
import OverviewCards from "../components/OverviewCards";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${api}/reports/overview`, { cache: "no-store" })
      .then(r => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading…</div>;
  if (!data) return <div>Failed to load overview.</div>;

  return (
    <div className="grid gap-6">
      <OverviewCards data={data} />
      <div className="grid md:grid-cols-2 gap-6">
        <AllocationChart data={data.allocation} />
        <GoalGauge value={data.goal_probability} />
      </div>
    </div>
  );
}
