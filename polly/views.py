import json
from django.http import HttpResponse, JsonResponse

from heartext.settings import BASE_DIR
from txt_to_mp3 import InputHandler, Converter

from pydub import AudioSegment
from pydub.effects import speedup


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    body = json.loads(request.body)
    text = body.get('text')

    ih = InputHandler(text)
    print('CONVERTING')
    print(text[:100].encode('utf-8') + '...')
    converter = Converter(lines=ih.lines, debug=True)
    mp3_filename = converter.run()

    speed = float(body.get('speed'))
    if speed > 1:
        print "Speeding up by %s" % speed
        song = AudioSegment.from_mp3(mp3_filename)
        sped_up = speedup(song, playback_speed=speed)
        # Overwrite (possibly should do different, then swap names)
        print "Done speeding"
        print "Writing final file"
        sped_up.export(mp3_filename, format='mp3')
    return JsonResponse({"OK": True})


def song_download(request):
    fsock = open('%s/tmp.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=tmp.mp3"
    return response
