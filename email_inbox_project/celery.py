import os
from celery import Celery

#  Make sure this matches folder where settings.py exists----------------------------------------------------------

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee.settings')

app = Celery('employee')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

