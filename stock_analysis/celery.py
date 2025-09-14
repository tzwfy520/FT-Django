import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

app = Celery('stock_analysis')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'update-stock-realtime-data': {
        'task': 'apps.stocks.tasks.update_realtime_stock_data',
        'schedule': 30.0,  # Every 30 seconds during market hours
        'options': {'expires': 25}
    },
    'update-market-data': {
        'task': 'apps.market.tasks.update_market_data',
        'schedule': 60.0,  # Every minute
        'options': {'expires': 55}
    },
    'daily-stock-analysis': {
        'task': 'apps.analysis.tasks.daily_stock_analysis',
        'schedule': 'crontab(hour=16, minute=30)',  # 4:30 PM daily
    },
    'update-stock-history': {
        'task': 'apps.stocks.tasks.update_stock_history',
        'schedule': 'crontab(hour=17, minute=0)',  # 5:00 PM daily
    },
}

app.conf.timezone = 'Asia/Shanghai'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')