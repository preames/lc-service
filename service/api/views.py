from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from models import *
import json
import datetime
import logging

# By default, any unmapped URL hits this and gets a page not found
def index(request):
    raise Http404

def JsonResponse(obj):
    return HttpResponse(json.dumps(obj), content_type='application/json')

# Kick off a new request
# TODO: figure out a better development solution than disabling CSRF
@csrf_exempt
def start(request):
    if request.method not in ['GET', 'POST']:
        raise Http404
    if not request.REQUEST["repository"]:
        raise Http404
    for item in request.REQUEST.keys():
        if str(item) not in ['repository', 'job_type']:
            raise Http404
    tainted_repo = request.REQUEST["repository"]
    if tainted_repo == "":
        raise Http404
    # TODO: validate the repository is actual a github url
    # TODO: validate it's in our whitelist (for now)

    if "job_type" in request.REQUEST.keys():
        job_type = request.REQUEST["job_type"]
    else:
        job_type = "clang-tidy"
    
    # nop-skip - ignored by the job server, used for testing response of api
    if job_type not in ['nop-skip', 'build', 'echo', 'clang-format', 'clang-modernize', 'clang-tidy']:
        print 'Job type ' + job_type + ' unknown.'
        raise Http404

    # TODO: should we try to combine with an existing pending job?

    message_dict = {"action": "job_start", "job_type": job_type, "repository": tainted_repo }
    message_json = json.dumps(message_dict)

    # First, create a record in the request table for this job, then
    # actually send a message to the job server to request it be run
    request = Request.objects.create(datetime=datetime.datetime.now(),
                                     repo=tainted_repo,
                                     parameters=message_json)
    message_dict["id"] = request.id
    message_json = json.dumps(message_dict)

    message = LogMessage.objects.create(request=request,
                                        datetime=datetime.datetime.now(),
                                        payload=message_json)
    return JsonResponse(message_dict)

# Poll for the current status of an existing request
# TODO: figure out a better development solution than disabling CSRF
@csrf_exempt
def status(request):
    if request.method not in ['GET', 'POST']:
        raise Http404
    if not request.REQUEST["id"]:
        raise Http404
    tainted_id = request.REQUEST["id"]
    # TODO: validate user permissions to this id
    request = get_object_or_404(Request, id=tainted_id)

    # Find the last message related to this request.  We're taking advantage
    # of knowing that this table is a write only log and thus primary key
    # implies time ordering
    messages = LogMessage.objects.all().filter(request=request)
    last = messages.order_by('pk').reverse()[0:1]
    if not last:
        return JsonResponse({})
    payloads = []
    for message in messages:
        payload = json.loads(message.payload)
        payload["datetime"] = str(message.datetime)
        payloads.append(payload)
    return JsonResponse(payloads)

# Stop an existing request
# TODO: figure out a better development solution than disabling CSRF
@csrf_exempt
def stop(request):
    if request.method not in ['GET', 'POST']:
        raise Http404
    if not request.REQUEST["id"]:
        raise Http404
    tainted_id = request.REQUEST["id"]
    # TODO: validate user permissions to this id
    request = get_object_or_404(Request, id=tainted_id)

    # TODO: Check to see if a stop request already sent, report an error

    message_dict = {"action": "job_stop"}
    message_json = json.dumps(message_dict)
    message = LogMessage.objects.create(request=request,
                                        datetime=datetime.datetime.now(),
                                        payload=message_json)


    return JsonResponse({'input id' : tainted_id, 'request id' : request.id })
