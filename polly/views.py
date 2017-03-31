import json
# from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse

from heartext.settings import BASE_DIR
# from heartext.models import Snippet, User
from tasks import convert_snippet_task


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    body = json.loads(request.body)
    text = body.get('text')
    url = body.get('url')
    voice = body.get('voice')
    speed = float(body.get('speed'))

    convert_snippet_task.delay(text, request.user.id, url, speed, voice)

    return JsonResponse({"OK": True})


def song_download(request):
    fsock = open('%s/tmp.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=tmp.mp3"
    return response
