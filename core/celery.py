from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from core.logger import logger
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.conf.enable_UTC = False
app.conf.update(timezone=config('TIME_ZONE', default='Asia/Kathmandu', cast=str))
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.task_routes = {
                    
#                         }


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')

