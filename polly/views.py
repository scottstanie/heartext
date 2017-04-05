from __future__ import division
import json
from tempfile import NamedTemporaryFile
import os
import zipfile
from wsgiref.util import FileWrapper
# from django.shortcuts import get_object_or_404, render
import botocore
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from celery.result import AsyncResult

from heartext.settings import BASE_DIR
from heartext.models import Snippet, User, Playlist
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

    return JsonResponse({"OK": True,
                         "snippet_id": snippet.uuid,
                         "job_id": job.id})


def song_download(request):
    fsock = open('%s/tmp.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=tmp.mp3"
    return response


def download_playlist(request, playlist_id):
    body = json.loads(request.body)
    playlist_id = body.get('playlistId')
    playlist = Playlist.objects.get(id=playlist_id)

    zipf = zipfile.ZipFile('%s.zip' % playlist.title, 'w', zipfile.ZIP_DEFLATED)
    for snippet in playlist.snippets.all():
        print 'ob:', snippet.s3_key, snippet.s3_url
        # obj = snippet.bucket.Object(snippet.s3_key)
        with NamedTemporaryFile() as f:
            try:
                snippet.bucket.download_file(snippet.s3_key, f.name)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print e, snippet.s3_url, 'does not exist'
                else:
                    raise
            # Copies over the temprary file using the key as the
            # file name in the zip.
            zipf.write(f.name, snippet.filename)

    zipf.close()

    return JsonResponse({"OK": True})


def download_zip(request, playlist_id):
    print 'DOWNLOADING!!!'
    playlist = Playlist.objects.get(id=playlist_id)
    with open('%s.zip' % playlist.title, 'rb') as zipf:
        chunk_size = 8192
        response = HttpResponse(FileWrapper(zipf), chunk_size)
        response.content_type = 'application/zip'
        response['Content-Length'] = os.path.getsize(zipf.name)
        response['Content-Disposition'] = "attachment; filename=%s" % zipf.name
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
