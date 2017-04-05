from __future__ import division
import json
# from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from celery.result import AsyncResult

from heartext.settings import BASE_DIR
from heartext.models import Snippet, User
import polly.tasks


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    body = json.loads(request.body)
    title = body.get('title')
    text = body.get('text')
    url = body.get('url')
    voice = body.get('voice')
    speed = float(body.get('speed'))

    user = User.objects.get(id=request.user.id)
    snippet = Snippet(title=title, text=text, created_by=user, source_url=url)
    snippet.save()

    job = polly.tasks.convert_snippet_task.delay(snippet.uuid, text, speed, voice)
    # job = polly.tasks.do_work.delay()

    return JsonResponse({"OK": True,
                         "snippet_id": snippet.uuid,
                         "job_id": job.id})


def song_download(request):
    fsock = open('%s/tmp.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=tmp.mp3"
    return response


def progress(request):
    """ A view to report the progress to the user """
    if 'jobId' in request.GET:
        job_id = request.GET['jobId']
    else:
        return JsonResponse({'OK': False, 'message': 'No job id given'})

    job = AsyncResult(job_id)
    if job.state == 'PROGRESS':
        pct_done = 100 * job.info['current'] / job.info['total']
    else:
        pct_done = 100

    return JsonResponse({'OK': False,
                         "state": job.state,
                         'pct_done': pct_done,
                         'data': job.result})
