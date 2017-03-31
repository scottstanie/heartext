# Create your tasks here
from __future__ import absolute_import, unicode_literals
# from celery import Task, shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger
from polly.txt_to_mp3 import InputHandler, Converter
from heartext.models import Snippet, User


log = get_task_logger(__name__)


@task(name="add")
def add(a, b):
    """adds, test celery"""
    log.info("Adding ")
    return a + b


@task(name="convert_snippet_task")
def convert_snippet_task(text, user_id, url, speed, voice):
    user = User.objects.get(id=user_id)
    snippet = Snippet(text=text, created_by=user, source_url=url)
    snippet.save()

    ih = InputHandler(text)
    print('CONVERTING')
    print(text[:100].encode('utf-8') + '...')
    converter = Converter(lines=ih.lines, debug=True, speed=speed, voice=voice)
    mp3_filename = converter.run()

    snippet.upload_to_s3(mp3_filename)
