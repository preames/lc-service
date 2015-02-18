import os
import shutil
import subprocess
import sys
from common import create_working_dir, clone_repository, build_it, display_diff

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
    assert len(argv) == 2
    repo = argv[1]

    print "Processing repository: %s" % repo

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

            # TODO: move the diff file somewhere outside the temp directory
            # and save it
        finally:
            # restore working dir
            os.chdir(origcwd)
    finally:
        # cleanup the tmp repo
        print "Removing scratch directory: %s" % work_dir
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)


main(sys.argv)
