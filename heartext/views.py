import json
import requests
import subprocess
import textract
import mimetypes

from django.shortcuts import render
from django.http import JsonResponse  # HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Snippet, User

@ensure_csrf_cookie
def index(request):
    return render(request, 'heartext/index.html')


# TODO: the server will be overwriting files that users submit
def upload(request):
    def _handle_uploaded_file(file_, filename='tmp.pdf'):
        """Write the submitted file to a temporary pdf"""
        with open(filename, 'wb+') as destination:
            for chunk in file_.chunks():
                destination.write(chunk)

    user_file = request.FILES.get('file')
    if not user_file:
        return JsonResponse({"OK": False})

    if user_file.content_type != 'application/pdf':
        print "Can only handle PDF files right now"
        return JsonResponse({"OK": False})

    filename = 'tmp.pdf'
    _handle_uploaded_file(user_file, filename)
    out_text = extract_pdf(filename)
    # Save the output text file for now to analyze
    with open(filename.replace('.pdf', '.txt'), 'w') as f:
        f.write(out_text)
    return JsonResponse({"OK": True, "text": out_text})


def extract_pdf(filename):
    """Use the textract library to get plain text from the pdf"""
    if mimetypes.guess_type(filename)[0] != 'application/pdf':
        return ''
    return textract.process(filename)


def parse(request):
    """Gets the URL submitted and returns the text from it
    """
    def _download(url, filename):
        with open(filename, 'wb') as f:
            f.write(r.content)

    def _read():
        with open('./out.txt', 'rb') as f:
            return f.read()

    def _get_response_type(response):
        content_type = response.headers.get('content-type')

        if 'application/pdf' in content_type:
            ext = '.pdf'
        elif 'text/html' in content_type:
            ext = '.html'
        else:
            ext = ''
            print 'Unknown type: {}'.format(content_type)
        return ext

    body = json.loads(request.body)
    input_url = body.get('url')
    print 'Extracting: ', input_url

    r = requests.get(input_url)
    ext = _get_response_type(r)
    filename = './tmp.{}'.format(ext)
    _download(input_url, filename)
    subprocess.check_call(['java',
                           '-jar',
                           'boilerpipe-core/dist/boilerpipe-1.2-dev.jar',
                           filename,
                           'out.txt'])

    return JsonResponse({"OK": True, "text": _read()})


def profile(request):
    snippets = Snippet.objects.filter(created_by=request.user).order_by('-created_at')
    context = {'snippets': snippets}
    return render(request, 'heartext/profile.html', context)
