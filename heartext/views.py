import json
import requests
import urllib
from django.shortcuts import render
from django.http import JsonResponse  # HttpResponse, HttpResponseRedirect


def index(request):
    return render(request, 'heartext/index.html')



def parse(request):
    """Gets the URL submitted and returns the text from it
    """
    body = json.loads(request.body)
    input_url = body.get('url')
    print 'Extracting: ', input_url

    api_url = 'http://boilerpipe-web.appspot.com/extract?url={input_url}'

    request_params = {
        'extractor': 'ArticleExtractor',
        'output': 'text',
        'extractImages': '',
    }

    encoded_url = urllib.quote_plus(input_url)
    response = requests.get(api_url.format(input_url=encoded_url),
                            params=request_params)
    print response.text

    return JsonResponse({"OK": True, "text": response.text})


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    return JsonResponse({"OK": True})


def pdf_to_text(pdf_document):
    pass
