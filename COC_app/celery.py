from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
from datetime import timedelta, datetime

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'COC_app.settings')

app = Celery('COC_app')

# Configure Celery using settings from Django settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

def last_sunday_of_month():
    today = datetime.today()
    first_day_next_month = datetime(today.year, today.month + 1, 1)
    last_sunday = first_day_next_month - timedelta(days=first_day_next_month.weekday() + 1)
    return last_sunday

def get_current_day():
    return datetime.now().day

app.conf.beat_schedule = {
    'fetch-clan-war-status': {
        'task': 'main.tasks.get_clan_war_status',
        'schedule': timedelta(hours=46),  # Runs every 46 hours
    },
    'get-monthly-clan-war-info': {
        'task': 'main.tasks.get_monthly_clan_war_info',
        'schedule': crontab(minute=0, hour=6, day_of_month=3),  # Runs on the 3rd at 6 AM EST
    },
    """
    'end-of-trophy-season-updates': {
        'task': 'main.tasks.end_of_trophy_season_updates',
        'schedule': last_sunday_of_month(),  # Custom schedule
    },
    """
    'get_CWL_war_tags': {
        'task': 'main.tasks.get_CWL_war_tags',
        'schedule': crontab(minute=0, hour=6, day_of_month='4-10'),
        'args': (get_current_day(),),  # Passing the current day as an argument
    },
    'process_CWL_information': {
        'task': 'main.tasks.process_CWL_information',
        'schedule': crontab(minute=0, hour=2, day_of_month=12),  # Runs on the 12th at 2 AM EST
    },
    'delete_all_CWL_group_info': {
        'task': 'main.tasks.delete_all_CWL_group_info',
        'schedule': crontab(minute=0, hour=2, day_of_month=20),  # Runs on the 20th at 2 AM EST
    }, 
    'test_task': {
        'task': 'main.tasks.test_task',
        'schedule': crontab(minute=0, hour=17, day_of_month=6),  # test task
    }, }

# Optional: to use timezone-aware scheduling
app.conf.timezone = 'America/New_York'  # Set to EST

# Optional Celery configuration for worker pool
app.conf.update(
    worker_pool='solo'  # Disable multiprocessing
)

# Autodiscover tasks from the Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
