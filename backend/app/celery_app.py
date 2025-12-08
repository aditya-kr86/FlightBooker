from celery import Celery
import os
import sys

# Configure Celery broker via environment variable or default to Redis local
CELERY_BROKER = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", CELERY_BROKER)

celery_app = Celery("gagan", broker=CELERY_BROKER, backend=CELERY_BACKEND)

# Configure pool based on OS (Windows has multiprocessing issues, use solo pool)
if sys.platform.startswith('win'):
    celery_app.conf.update(
        worker_pool='solo',  # single-process pool for Windows
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json'
    )
else:
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json'
    )


@celery_app.task(name="gagan.run_demand_simulation")
def run_demand_simulation_task(within_hours: int = 720):
    """Run the demand simulation once using a DB session.

    This task imports DB session and simulator at runtime so Celery worker
    doesn't require importing the entire FastAPI app at module import time.
    """
    try:
        from app.config import SessionLocal
        from app.services.demand_simulator import run_demand_simulation_once

        db = SessionLocal()
        updated = run_demand_simulation_once(db, within_hours=within_hours)
        db.close()
        return {"updated": updated}
    except Exception as e:
        return {"error": str(e)}
