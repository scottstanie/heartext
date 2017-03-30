import json
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse

from heartext.settings import BASE_DIR
from txt_to_mp3 import InputHandler, Converter
from heartext.models import Snippet, User


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    body = json.loads(request.body)
    text = body.get('text')
    url = body.get('url')
    voice = body.get('voice')
    speed = float(body.get('speed'))

    user = get_object_or_404(User, id=request.user.id)
    snippet = Snippet(text=text, created_by=user, source_url=url)
    snippet.save()

    ih = InputHandler(text)
    print('CONVERTING')
    print(text[:100].encode('utf-8') + '...')
    converter = Converter(lines=ih.lines, debug=True, speed=speed, voice=voice)
    mp3_filename = converter.run()

    snippet.upload_to_s3(mp3_filename)
    return JsonResponse({"OK": True, "url": snippet.s3_url})


def song_download(request):
    fsock = open('%s/tmp.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=tmp.mp3"
    return response
