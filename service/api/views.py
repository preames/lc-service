from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from models import *
import json
import datetime
import logging
import os

# By default, any unmapped URL hits this and gets a page not found
def index(request):
    raise Http404

url_whitelist = ['https://github.com/LegalizeAdulthood/refactor-test-suite',
                 'https://github.com/llvm-mirror/llvm',
                 ]

def JsonResponse(obj):
    return HttpResponse(json.dumps(obj), content_type='application/json')

def DiffResponse(fname):
    with open(fname, 'r') as ofile:
        # Surely there's a better content_type?
        response = HttpResponse(ofile.read(), content_type='text/plain')
        return response;

def find_pending_request(url, job_type):
    requests = Request.objects.all().filter(repo=url)
    # search the last 5 since we're not keyed off the job_type (FIXME)
    last_requests = requests.order_by('pk').reverse()[0:5]
    for last_request in last_requests:
        messages = LogMessage.objects.all().filter(request=last_request)
        found = False
        for message in messages:
            data = json.loads(message.payload)
            # not the right type of job. TODO: this field needs to be added 
            # to the DB table!
            if "job_type" in data:
                if data["job_type"] == job_type:
                    found = True
                break;
        if not found:
            # keep searching for a job of right type
            continue
        # We found one of the right type, is it still running?
        for message in messages:
            data = json.loads(message.payload)
            action = data["action"]
            if action in ["job_finished", "job_stop", 'job_abort']:
                return None;
        return last_request
    return None


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
    # validate it's in our whitelist (for now)
    if tainted_repo not in url_whitelist:
        # TODO: log this to a file or table, or something
        # we want to keep this list for later expansions/consideration
        raise Http404

    if "job_type" in request.REQUEST.keys():
        job_type = request.REQUEST["job_type"]
    else:
        job_type = "clang-tidy"
    
    # nop-skip - ignored by the job server, used for testing response of api
    if job_type not in ['nop-skip', 'build', 'echo', 'clang-format', 'clang-modernize', 'clang-tidy']:
        print 'Job type ' + job_type + ' unknown.'
        raise Http404

    # Check to see if there's a pending job with the same repo and request type
    # if there is, return that one so that we can combine work for two requests
    # into one.  This is crtical for handling expected load when the 
    # announcement goes out since the actual execution layer is pretty simple.
    pending = find_pending_request(tainted_repo, job_type)
    if pending:
        message_dict = {"action": "job_start", "job_type": job_type, 
                        "repository": tainted_repo, "id" : pending.id }
        return JsonResponse(message_dict)

    # First, create a record in the request table for this job, then
    # actually send a message to the job server to request it be run
    message_dict = {"action": "job_start", "job_type": job_type, 
                    "repository": tainted_repo }
    message_json = json.dumps(message_dict)
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

# Download the diff generated by an existing request
# TODO: figure out a better development solution than disabling CSRF
@csrf_exempt
def diff(request):
    if request.method not in ['GET', 'POST']:
        raise Http404('bad request type')
    if not request.REQUEST["id"]:
        raise Http404("no id");
    tainted_id = request.REQUEST["id"]
    # TODO: validate user permissions to this id
    request = get_object_or_404(Request, id=tainted_id)
    filename = request.diff_file 
    if filename == "":
        raise Http404("no file")
    if not os.path.exists(filename):
        raise Http404("missing file")
    # TODO: validate that the file is somewhere we're willing to serve from
    # as a last ditch security check.
    # As you can see, this is utterly insecure right now...
    return DiffResponse(filename)

