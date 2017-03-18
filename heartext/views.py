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
    def _download(url, filename):
        with open(filename, 'wb') as f:
            f.write(r.content)

    def _read():
        with open('./out.txt', 'rb') as f:
            return f.read()

    body = json.loads(request.body)
    input_url = body.get('url')
    print 'Extracting: ', input_url

    r = requests.get(input_url)
    ext = get_response_type(r)
    filename = './tmp.{}'.format(ext)
    _download(input_url, filename)
    subprocess.check_call(['java',
                           '-jar',
                           'boilerpipe-core/dist/boilerpipe-1.2-dev.jar',
                           filename,
                           'out.txt'])

    return JsonResponse({"OK": True, "text": _read()})


def get_response_type(response):
    content_type = response.headers.get('content-type')

    if 'application/pdf' in content_type:
        ext = '.pdf'
    elif 'text/html' in content_type:
        ext = '.html'
    else:
        ext = ''
        print 'Unknown type: {}'.format(content_type)
    return ext


def pdf_to_text(pdf_document):
    pass
