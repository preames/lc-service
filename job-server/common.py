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
    print "Trying make target '%s'" % target
    rval = try_make_target_impl("", target) 
    if rval:
        print "  -- Succeeded"
    else:
        print "  -- Failed"
    return rval;

TrivialBuildSuccess = False

# Try to build the local directory using standard build mechanisms
def build_it(require_build=True, require_tests=False):
    if TrivialBuildSuccess:
        # debugging only
        return True;

    # Prefer a cmake build over a configure style one, either way, configure
    # in the source directory for maximum applicability.  We're assumed to be
    # a temporary checkout.
    if os.path.exists("./CMakeLists.txt"):
        print "Running cmake"
        if 0 != subprocess.call("cmake .", shell=True,
                                stderr = subprocess.STDOUT):
            return False
    elif os.path.exists("./configure"):
        print "Running configure"
        if 0 != subprocess.call("chmod u+x ./configure", shell=True):
            return Fals
        if 0 != subprocess.call("./configure", shell=True):
            return False
    else:
        print "Neither configure or cmake found"

    # TODO: support ninja?
    if os.path.exists("Makefile"):
        print "Found Makefile"
        # We have to build something
        if not try_make_target("build"):
            if not try_make_target(''):
            
                #if 0 != subprocess.call("make", shell=True):
                print "Could not build project"
                return False
        print "Build step succeeeded, trying tests.."

        # Hopefully, this came with a test set
        if not try_make_target("check"):
            if not try_make_target("unittest"):
                if not try_make_target("test"):
                    if require_tests:
                        print "No tests found, tests were required, FAILURE"
                        return False
                    else:
                        print "No tests found, skipping test step"
                        return True
        print "Test step passed"
        return True
    else:
        print "No known way to build this project"
        return False

