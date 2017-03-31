from __future__ import absolute_import, unicode_literals
import os
import celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heartext.settings')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

# Load task modules from all registered Django app configs.


app = celery.Celery('heartext')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print 'Request: {0!r}'.format(self.request)
