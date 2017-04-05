# Create your tasks here
from __future__ import absolute_import
# from celery import Task, shared_task
import time
from celery.decorators import task
from celery.utils.log import get_task_logger
from polly.txt_to_mp3 import InputHandler, Converter
from heartext.models import Snippet


log = get_task_logger(__name__)


@task(bind=True)
def convert_snippet_task(self, snippet_id, text, speed, voice):
    snippet = Snippet.objects.get(uuid=snippet_id)

    ih = InputHandler(text)
    print('CONVERTING')
    print(text[:100].encode('utf-8') + '...')
    converter = Converter(lines=ih.lines, debug=True, speed=speed, voice=voice, celery_job=self)
    mp3_filename = converter.run()

    snippet.upload_to_s3(mp3_filename)


@task(bind=True)
def do_work(self):
    """ Get some rest, asynchronously, and update the state all the time """
    for i in range(100):
        time.sleep(0.2)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': 100})
