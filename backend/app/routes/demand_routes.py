from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Any

from app.config import get_db
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.services.demand_simulator import run_demand_simulation_once

router = APIRouter()


@router.post("/simulate")
def trigger_simulation(background_tasks: BackgroundTasks, async_run: bool = True):
    """Trigger a demand simulation run.

    If Celery is available and `async_run` is True, enqueues a Celery task and
    returns the task id. Otherwise runs the simulator in a background thread
    using FastAPI's BackgroundTasks (non-persistent across process restarts).
    """
    # Try to enqueue Celery task if requested
    if async_run:
        try:
            res = celery_app.send_task("gagan.run_demand_simulation", args=[720])
            return {"task_id": res.id}
        except Exception:
            # fallthrough to background execution
            pass

    # fallback: run in background (will use same process DB)
    def _run():
        db = None
        try:
            db = get_db().__next__()
            run_demand_simulation_once(db, within_hours=720)
        finally:
            if db:
                db.close()

    background_tasks.add_task(_run)
    return {"status": "scheduled_background"}
