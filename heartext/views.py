import json
import requests
import subprocess
from django.shortcuts import render
from django.http import JsonResponse  # HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index(request):
    return render(request, 'heartext/index.html')


def parse(request):
    """Gets the URL submitted and returns the text from it
    """
    def _download(url):
        r = requests.get(url)
        with open('./tmp.html', 'wb') as f:
            f.write(r.content)

    def _read():
        with open('./out.txt', 'rb') as f:
            return f.read()

    body = json.loads(request.body)
    input_url = body.get('url')
    print 'Extracting: ', input_url
    _download(input_url)

    subprocess.check_call(['java',
                           '-jar',
                           'boilerpipe-core/dist/boilerpipe-1.2-dev.jar',
                           './tmp.html',
                           'out.txt'])

    return JsonResponse({"OK": True, "text": _read()})


def pdf_to_text(pdf_document):
    pass
