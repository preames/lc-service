# A 'job server' which actually runs the requests.  At the moment this is
# simply a proof of concept.  It runs one job at a time and has no 
# provisions for supporting multiple job managers or multiple in flight jobs.
# This job-server will try to run jobs which haven't been started before, but 
# will not retry jobs which have previously run and failed (for *any* reason)

import os
import subprocess
import shutil
import sys
import time
import datetime
import json
from common import common_setup, add_message_to_log

# For simplicity, we're going to use django's orm interface for accessing the
# database.  The avoids having the (autogenerated) db field names hard coded.
common_setup()
from api import models

# open connection to log
# claim active job manager role (others may keep running)

# A generator routine which enumerates the set of pending jobs to be run
def pending_jobs():
    messages = models.LogMessage.objects.all()
    jobs = dict()
    for message in messages:
        data = json.loads(message.payload)
        action = data["action"]
        if action == "job_start":
            assert not message.request.id in jobs
            jobs[message.request.id] = True
        elif action in ["job_started", "job_finished", "job_stop"]:
            assert message.request.id in jobs
            jobs[message.request.id] = False
        elif action in ["job_finished"]:
            assert message.request.id in jobs
            assert not jobs[message.request.id]

    for key, value in jobs.items():
        # A true value implies this job hasn't yet run...
        if value:
            # TODO: shed if too old or load too high
            # TODO: error handling
            request = models.Request.objects.get(pk=key)
            request.parameters = json.loads(request.parameters)
            yield request

def run_job(job):
    jobtype = job.parameters["job_type"]
    print "Running job: " + jobtype + " " +str(job)

    if "nop-skip" == jobtype:
        # used when testing the frontend, we just ignore it. We do not
        # want to adjust the status here.
        return
    
    # Before actually starting the job, record the fact we're about to do so.
    # If we see this job in the log after a restart, we don't want it to 
    # rerun (since it may have caused us to crash in the first place)
    message_dict = {"action": "job_started"}
    add_message_to_log(message_dict, job)

    # TODO: async using popen and observe jobs
    # TODO: logging, log files?
    # TODO: set cwd
    # TODO: remove shell=True via explicit command path
    if jobtype == "echo":
        print "echo: " + str(job)
    elif jobtype in ["build", "clang-modernize", "clang-tidy", "clang-format"]:
        repo = job.repo
        cmd = "python run-%s-job.py %s %s" % (jobtype, repo, job.id)
        subprocess.call(cmd, shell=True)
        pass
    else:
        print "error: illegal job type!"

    # Record the fact the job finished (normally)
    # TODO: add 'job_aborted'
    message_dict = {"action": "job_finished"}
    add_message_to_log(message_dict, job)


print "Entering job-server loop"
started = datetime.datetime.now()
# job server is externally restarted periodically
while datetime.datetime.now() < started + datetime.timedelta(minutes=120):
    print "Checking for work @" +str(datetime.datetime.now())

    # pull out any open requests
    # - use a last processed job ID
    # - possibly a pair: max completed, last considered
    # agressively shed load as required
    # TDOO: take into consideration load on the system
    

    # Batch process pending job requests - this is currently strictly FIFO,
    # but more complicated policies can and should be applied.
    for job in pending_jobs():
        print "pending: " + str(job)
        
        # Note: Need to rate limit the work somehow, for now, this is 
        # handled by having a single blocking call per job
    
        run_job(job)
        

    #TODO: implement various job manager commands
    # e.g. restart, stop

    # sleep for X seconds, then check for new jobs
    # TODO: implement a reasonable backoff policy here, or does
    # it actually matter?
    time.sleep(5);

# TODO: When we get around to implementing a parallelization 
# scheme, implement graceful shutdown for jobs running at timeout.
