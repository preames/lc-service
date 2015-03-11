import json
import os
import subprocess
import shutil
import sys
from common import create_working_dir, clone_repository, build_it, display_diff, common_setup, git_diff_to_file, generate_compile_command_file

common_setup()
from api import models

diff_base_dir = '/tmp/lc-diffs/'
if not os.path.exists(diff_base_dir):
    os.mkdir(diff_base_dir)

def run_job():
    # clang-modernize every file listed in the cmake compilation
    # database
    subprocess.check_call("clang-modernize -p ./ -include ./",
                          shell=True)


# TODO: pass the job configuration in via JSON?  Or just the request ID?
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

            if not generate_compile_command_file():
                print "initial build failed"
                sys.exit(-1)

            run_job()

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

            # Skip the build step if there's nothing for us to actually build
            diff_file = request.diff_file
            if "" == diff_file or not os.path.exists(diff_file):
                print "no diff to build"
                sys.exit(0)

            with open(diff_file, 'r') as ofile:
                if "" == ofile.read():
                    print "diff is empty"
                    sys.exit(0)

            # do a full build and make sure it passes.  IF it doesn't, we
            # don't want to keep this.  TODO: We'll need to be robust against
            # failures in the future, but for now, don't mess with it.
            if not build_it():
                print "build failed after format"
                sys.exit(-1)

            # TODO: other validation
        finally:
            # restore working dir
            os.chdir(origcwd)
    finally:
        # cleanup the tmp repo
        print "Removing scratch directory: %s" % work_dir
        if os.path.exists(work_dir):
            import shutil
            shutil.rmtree(work_dir)


main(sys.argv)
