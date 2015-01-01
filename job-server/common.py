import os
import subprocess
import shutil
import sys

# really should use a three way here
def try_make_target_impl(options, target):
    try:
        output = subprocess.check_output("make %s %s" % (options, target),
                                stderr=subprocess.STDOUT,
                                shell=True)
        if "No rule to make target" in output:
            return False
        return True
    except:
        return False

def try_make_target(target):
    print "Trying make target %s" % target
    rval = try_make_target_impl("", target) 
    if rval:
        print "  -- Succeeded"
    else:
        print "  -- Failed"
    return rval;

TrivialBuildSuccess = False

# Try to build the local directory using standard build mechanisms
def build_it():
    if TrivialBuildSuccess:
        # debugging only
        return True;
    # TODO: cmake? 
    if os.path.exists("./configure"):
        print "Running configure"
        if 0 != subprocess.call("chmod u+x ./configure", shell=True):
            return Fals
        if 0 != subprocess.call("./configure", shell=True):
            return False
    if os.path.exists("Makefile"):
        # We have to build something
        if not try_make_target("build"):
            print "Running 'make'"
            if 0 != subprocess.call("make", shell=True):
                return False
        # Hopefully, this came with a test set
        if not try_make_target("check"):
            if not try_make_target("unittest"):
                try_make_target("test")

    print "No known way to build this project"
    return False

