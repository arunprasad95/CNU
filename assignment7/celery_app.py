from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assignment7.settings')
app = Celery('assignment7',
             broker='redis://tcp.ey.devfactory.com:10231/0',
             backend='redis://tcp.ey.devfactory.com:10231/0')
#app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
if __name__ == '__main__':
    app.start()