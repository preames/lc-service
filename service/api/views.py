from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

# By default, any unmapped URL hits this and gets a page not found
def index(request):
    raise Http404;

# Kick off a new request
def start(request):
    if request.method not in ['GET', 'POST']:
        raise Http404;
    return HttpResponse("START")

# Poll for the current status of an existing request
def status(request):
    if request.method not in ['GET', 'POST']:
        raise Http404;
    return HttpResponse("POLL")

# Stop an existing request
def stop(request):
    if request.method not in ['GET', 'POST']:
        raise Http404;
    return HttpResponse("STOP")
