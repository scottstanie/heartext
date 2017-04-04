# Create your tasks here
from __future__ import absolute_import
# from celery import Task, shared_task
from celery.result import AsyncResult
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


@task(bind=True)
def convert_snippet_task(self, text, user_id, url, speed, voice):
    user = User.objects.get(id=user_id)
    snippet = Snippet(text=text, created_by=user, source_url=url)
    snippet.save()

    ih = InputHandler(text)
    print('CONVERTING')
    print(text[:100].encode('utf-8') + '...')
    converter = Converter(lines=ih.lines, debug=True, speed=speed, voice=voice)
    mp3_filename = converter.run()

    snippet.upload_to_s3(mp3_filename)

def poll_state(request):
    """ A view to report the progress to the user """
    if 'job' in request.GET:
        job_id = request.GET['job']
    else:
        return HttpResponse('No job id given.')

    job = AsyncResult(job_id)
    data = job.result or job.state
    return HttpResponse(json.dumps(data), mimetype='application/json')


