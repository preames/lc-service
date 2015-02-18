import os
import subprocess
import shutil
import sys

import multiprocessing
cpu_count = multiprocessing.cpu_count()

# really should use a three way here
def try_make_target_impl(options, target):
    try:
        num_threads = min(1,cpu_count-1)
        output = subprocess.check_output("make -j %d %s %s" % (num_threads,
                                                               options, target),
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
        if 0 != subprocess.call("cmake -D CMAKE_EXPORT_COMPILE_COMMANDS=true .", 
                                shell=True,
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


def create_working_dir():
    # create a local tempory directory
    import tempfile
    # TODO: this is insecure FIXME
    tmpdir = tempfile.mktemp()
    # Note: The directory does not exist here, this is only the name

    os.mkdir(tmpdir)
    return tmpdir


def clone_repository(repo, work_dir):
    # clone the repository
    cmd = "git --no-pager clone %s %s" % (repo, work_dir)
    subprocess.call(cmd, shell=True)


def git_diff_to_file(fname):
    subprocess.call("git --no-pager diff > %s" % (fname), shell=True)

# TODO: inline this to callers
def display_diff():
    fname = "temp.diff"
    git_diff_to_file(fname)
    with open(fname, 'r') as ofile:
        print ofile.read()

def scratch_code():
    # TODO: multiple delivery options
    # 0) downloadable diff file
    # 1) diff via email
    # 2) commit and push
    # 3) repo fork and pull request
    # 4) publish diff to known location (website)
    #    formatted nicely, with raw patch for apply
    #    generate a json output file, parse this to make
    #    a pretty webpage later.  Put the diffs into own subtree
    # 5) pull request on github
    # 6) phabricator review
    # 7) reviewboard review
    # Current planned order: 0, 5, 7, ...

    output_format = "diff-web"
    if output_format == "diff-web":
        # For now, just show the diff
        print "Here's the diff:"
        subprocess.call("git --no-pager diff", shell=True)

        # make a output sub-directory
        # os.mkdir("./.livingcode-output")
        # single unified diff
        # subprocess.call("git --no-pager diff > ./.livingcode-output/combined.diff", shell=True)
        # per file diff with unique file
        # for i in xrange(len(formatted)):
        #     subprocess.call("git --no-pager diff %s > ./.livingcode-output/%d.diff" % (formatted[i],i), shell=True)
        # temporary, show the dir tree since we're about to delete it
        # subprocess.call("wc ./.livingcode-output/*", shell=True)
        # TODO: generate json file listing all
        # TODO: preserve the output tree
        pass
    elif output_format == "diff-email":
        # not yet implemented
        assert False
    elif output_format == "commit-push":
        # do a local commit
        subprocess.check_call("git --no-pager commit -a -m \"Applying automatic formatting changes via clang-format for files which haven't been touched recently\"", shell=True)

        # pull rebase -- if it's not up to date, BAIL - long term be more sophsticated
        # do a push (eventually)
    else:
        # unknown out requested
        assert False
