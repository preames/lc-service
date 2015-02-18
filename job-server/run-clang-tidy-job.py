import json
import os
import subprocess
import shutil
import sys
from common import create_working_dir, clone_repository, build_it, display_diff


def run_job():
    commands = json.load(open("compile_commands.json"))
    # clang-tidy every file listed in the cmake compilation
    # database
    for cmd in commands:
         subprocess.check_call("clang-tidy -p . -checks= -fix %s" % (cmd["file"]),
                          shell=True)


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

            # TODO: other validation

            # TODO: delivery options

            display_diff()

        finally:
            # restore working dir
            os.chdir(origcwd)
    finally:
        # cleanup the tmp repo
        print "Removing scratch directory: %s" % work_dir
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)


main(sys.argv)
