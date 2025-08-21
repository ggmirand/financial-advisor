# Financial Advisor Platform (Standard Build)

Stack: FastAPI (Python 3.11) + Next.js 14 (TypeScript, Tailwind, Recharts) + Postgres + Redis + Celery + Docker Compose.

## Quickstart (Dev)
1. Copy `.env.example` to `.env` and adjust if needed.
2. Run:
   ```bash
   docker compose -f infra/docker-compose.yml up --build
   ```
3. Open:
   - API docs: http://localhost:8000/docs
   - Web app:  http://localhost:3000

> Educational use only. Not financial, legal, or tax advice.
