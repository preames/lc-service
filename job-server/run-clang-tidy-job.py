import json
import os
import subprocess
import shutil
import sys
from common import create_working_dir, clone_repository, build_it, display_diff, common_setup, git_diff_to_file

common_setup()
from api import models

diff_base_dir = '/tmp/lc-diffs/'
if not os.path.exists(diff_base_dir):
    os.mkdir(diff_base_dir)

def run_job():
    commands = json.load(open("compile_commands.json"))
    # clang-tidy every file listed in the cmake compilation
    # database
    for cmd in commands:
         subprocess.check_call("clang-tidy -p . -checks= -fix %s" % (cmd["file"]),
                          shell=True)


def main(argv):
    assert len(argv) == 3
    repo = argv[1]
    request_id = argv[2]
    request = models.Request.objects.get(pk=request_id)

    print "Processing repository: %s" % repo
    print str(request)

    work_dir = ""
    try:
        work_dir = create_working_dir()
        print "Creating scratch working directory %s" % work_dir

        clone_repository(repo, work_dir)

        origcwd = os.getcwd()
        try:
            os.chdir(work_dir)

            if not build_it():
                print "initial build failed"
                sys.exit(-1)

            run_job()

            # TODO: if there is no diff, early exit

            # do a full build and make sure it passes.  IF it doesn't, we
            # don't want to keep this.  TODO: We'll need to be robust against
            # failures in the future, but for now, don't mess with it.
            if not build_it():
                print "build failed after format"
                sys.exit(-1)

            # TODO: other validation

            fname = "temp.diff"
            git_diff_to_file(fname)
            with open(fname, 'r') as ofile:
                print ofile.read()

            # save the diff file outside the temp directory so it doesn't get
            # destroyed and publish that location in the request record
            # TODO: should probably use a naming collision less prone to
            # collisions when we reset the test database...
            dst = diff_base_dir + str(request.id) + ".diff"
            import shutil
            shutil.move(fname, dst)
            request.diff_file = dst
            request.save()

        finally:
            # restore working dir
            os.chdir(origcwd)
    finally:
        # cleanup the tmp repo
        print "Removing scratch directory: %s" % work_dir
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)


main(sys.argv)
