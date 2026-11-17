import os
from celery import Celery
from celery.schedules import crontab

# setting up Celery so I don't have to manually run this every time new financial reports drop
app = Celery(
    'b100_orchestration',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['orchestration.tasks']
)

app.conf.update(
    result_expires=3600,
    timezone='UTC',
)

app.conf.beat_schedule = {
    'run-full-etl-pipeline-weekly': {
        'task': 'orchestration.tasks.run_full_etl_pipeline',
        # schedule to run automatically (e.g., weekly on Friday nights)
        'schedule': crontab(hour=23, minute=0, day_of_week='friday'),
    },
}
