import os
import subprocess
import shutil
import sys
import time
import datetime

print "Entering job-server loop"

started = datetime.datetime.now()

# open connection to log
# claim active job manager role (others may keep running)

# job server is externally restarted periodically
while datetime.datetime.now() < started + datetime.timedelta(minutes=120):
    print datetime.datetime.now()
    print "Checking for work"

    # pull out any open requests
    # - use a last processed job ID
    # - possibly a pair: max completed, last considered
    # agressively shed load as required
    # TDOO: take into consideration load on the system
    # restart any required jobs
    
    repo = "https://github.com"
    jobtype = "clang-modernize"
    if "clang-modernize" == jobtype:
        # TODO: add various other interesting options
        
        #cmd = "python run-clang-modernize-job.py %s" % (repo)
        # TODO: set cwd
        # TODO: async using popen and observe jobs
        #subprocess.call(cmd)
        pass
    elif "clang-tidy" == jobtype:
        print "job type unsupported"
        pass
    elif "clang-format" == jobtype:
        #cmd = "python run-clang-modernize-job.py %s" % (repo)
        # TODO: set cwd
        # TODO: async using popen and observe jobs
        #subprocess.call(cmd)
        print "job type unsupported"
        pass
    else:
        print "error: illegal job type!"

    #TODO: implement various job manager commands
    # e.g. restart, stop

    # sleep for 30 seconds, then check for new jobs
    # TODO: implement a reasonable backoff policy here, or does
    # it actually matter?
    time.sleep(30);

