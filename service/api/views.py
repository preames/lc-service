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
    if not request.REQUEST["repository"]:
        raise Http404;
    tainted_repo = request.REQUEST["repository"]
    # TODO: validate the repository is actual a github url
    # TODO: validate it's in our whitelist (for now)
    return HttpResponse("START " + tainted_repo)

# Poll for the current status of an existing request
def status(request):
    if request.method not in ['GET', 'POST']:
        raise Http404;
    if not request.REQUEST["id"]:
        raise Http404;
    tainted_id = request.REQUEST["id"]
    # TODO: validate user permissions to this id 
    return HttpResponse("POLL " + tainted_id)

# Stop an existing request
def stop(request):
    if request.method not in ['GET', 'POST']:
        raise Http404;
    if not request.REQUEST["id"]:
        raise Http404;
    tainted_id = request.REQUEST["id"]
    # TODO: validate user permissions to this id 
    return HttpResponse("STOP " + tainted_id)
