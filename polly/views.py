from django.http import HttpResponse
from heartext.settings import BASE_DIR


# Create your views here.
def song_download(request):
    fsock = open('%s/sam.mp3' % BASE_DIR, 'rb')
    response = HttpResponse(fsock)
    response.content_type = 'audio/mpeg'
    response['Content-Disposition'] = "attachment; filename=test.mp3"
    return response
