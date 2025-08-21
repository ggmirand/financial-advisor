import os
from celery import Celery

broker = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery("advisor_tasks", broker=broker, backend=broker)

@app.task
def nightly_refresh():
    # placeholder for data refresh, scoring, and alerts
    return {"status":"ok"}
