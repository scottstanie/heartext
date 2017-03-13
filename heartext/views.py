from django.shortcuts import render
from django.http import JsonResponse  # HttpResponse, HttpResponseRedirect


def index(request):
    return render(request, 'heartext/index.html')


def convert(request):
    """Converts a block of text into an mp3

    Text is sent as JSON through request.POST
    """
    return JsonResponse({"OK": True})


def parse(request):
    """Gets the URL submitted and returns the text from it
    """
    return JsonResponse({"OK": True})


def pdf_to_text(pdf_document):
    pass
