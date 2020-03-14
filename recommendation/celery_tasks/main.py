import os

from celery import Celery

os.environ["DJANGO_SETTINGS_MODULE"] = "recommendation.settings.dev"

celery_app = Celery('recommendation')

celery_app.config_from_object('celery_tasks.config')

celery_app.autodiscover_tasks(['celery_tasks.sms'],
                              ['celery_tasks.email'])