import json
from django.http import HttpResponse, JsonResponse

from heartext.settings import BASE_DIR
from txt_to_mp3 import InputHandler, Converter


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    body = json.loads(request.body)
    text = body.get('text')
    ih = InputHandler(text)
    print('CONVERTING')
    print(text[:100] + '...')
    converter = Converter(lines=ih.lines, debug=True)
    converter.run()
    return JsonResponse({"OK": True})


def song_download(request):
    fsock = open('%s/tmp.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=tmp.mp3"
    return response
