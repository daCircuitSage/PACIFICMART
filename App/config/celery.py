import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factors_Ecom.settings')

app = Celery('factors_Ecom')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Dhaka',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure broker and result backend
if hasattr(settings, 'CELERY_BROKER_URL'):
    app.conf.broker_url = settings.CELERY_BROKER_URL
if hasattr(settings, 'CELERY_RESULT_BACKEND'):
    app.conf.result_backend = settings.CELERY_RESULT_BACKEND

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
