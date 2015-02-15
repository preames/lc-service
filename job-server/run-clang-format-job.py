import os
import shutil
import subprocess
import sys
from common import create_working_dir, clone_repository, build_it, display_diff

delay = 90
style = "Google"

assert delay > 0 and delay < 365*10
assert style in ["LLVM", "Google", "Chromium", "Mozilla", "WebKit"]

def run_job():
    import datetime
    now = datetime.datetime.now()
    delta = datetime.timedelta(delay)
    then = now - delta
    sThen = (then.strftime("%Y-%m-%d"))

    print "Checking for files last updated before %s" % sThen

    # Must be run in the repo
    cmd = "git --no-pager log  --pretty=format: --name-only --until=\"%s\" > _tmp " % (sThen)
    subprocess.call(cmd, shell=True)

    import os
    mod = set()
    with open("_tmp", "r") as f:
        for line in f:
            tmp = line.strip()
            # TODO: insecure
            if tmp != "" and os.path.exists(tmpdir+"/"+tmp):
                mod.add(tmp)

    if len(mod) == 0:
        print "No files to update at this time"
        sys.exit(0)

    # TODO: if no file actually changes, need to bail cleanly
    formatted = []
    for filename in mod:
        extension = os.path.splitext(filename)[1]
        if extension in [".h", ".c", ".cpp", ".cxx", ".hpp", ".hxx"]:
            # WARNING: This is dangerous, it updates in place!
            print "Formatting %s" % filename
            subprocess.check_call( "clang-format -i -style=%s %s" % (style, filename), shell=True)
            formatted.append(filename)

    if len(formatted) == 0:
        print "No formatting applied, nothing to report"
        sys.exit(0)



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
