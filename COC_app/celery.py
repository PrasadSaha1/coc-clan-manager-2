from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'COC_app.settings')

app = Celery('COC_app')

# Configure Celery using settings from Django settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

"""
app.conf.beat_schedule = {
    'fetch-clan-war-status': {
        'task': 'main.tasks.get_clan_war_status',  # Update to the correct task path
        'schedule': timedelta(hours=46),  # Runs every 46 hours
    },
    'end-of-trophy-season-updates': {
        'task': 'main.tasks.end_of_trophy_season_updates',
        'schedule': crontab(minute=0, hour=2, day_of_week='sun', day_of_month='last'),
    },
    'get-monthly-clan-war-info': {
        'task': 'main.tasks.get_monthly_clan_war_info',
        'schedule': crontab(minute=0, hour=2, day_of_month=3),
    },
"""

app.conf.beat_schedule = {
    'fetch-clan-war-status': {
        'task': 'main.tasks.get_clan_war_status',  # Update to the correct task path
        'schedule': crontab(minute=0, hour=22, day_of_month=30),
    },
    'end-of-trophy-season-updates': {
        'task': 'main.tasks.end_of_trophy_season_updates',
        'schedule': crontab(minute=2, hour=22, day_of_month=30),
    },
    'get-monthly-clan-war-info': {
        'task': 'main.tasks.get_monthly_clan_war_info',
        'schedule': crontab(minute=2, hour=22, day_of_month=30),
    },
}
# Optional: to use timezone-aware scheduling
app.conf.timezone = 'America/New_York'  # Set to the timezone you want (EST for Eastern Standard Time)

# Optional Celery configuration for worker pool
app.conf.update(
    worker_pool='solo'  # Disable multiprocessing
)

# Autodiscover tasks from the Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
