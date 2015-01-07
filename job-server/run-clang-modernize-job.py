
import os
import subprocess
import shutil
import sys

assert len(sys.argv) == 2
repo = sys.argv[1]

def build_it():
    import common
    return common.build_it()

print "Processing repository: %s" % repo

# create a local tempory directory
import tempfile
# TODO: this is insecure FIXME
tmpdir = tempfile.mktemp()
# Note: The directory does not exist here, this is only the name
import os
try:
    print "Creating scratch working directory %s" % tmpdir
    os.mkdir(tmpdir)

    # clone the repository
    import subprocess
    cmd = "git --no-pager clone %s %s" % (repo, tmpdir)
    subprocess.call(cmd, shell=True)

    origcwd = os.getcwd()
    try:
        os.chdir(tmpdir)

        if not build_it():
            print "initial build failed"
            sys.exit(-1)
            
        # clang-modernize every file listed in the cmake compilation
        # database
        subprocess.check_call("clang-modernize -p ./ -include ./", 
                                  shell=True)

        # TODO: if there is no diff, early exit

        # do a full build and make sure it passes.  IF it doesn't, we 
        # don't want to keep this.  TODO: We'll need to be robust against
        # failures in the future, but for now, don't mess with it.
        if not build_it():
            print "build failed after format"
            sys.exit(-1)

        # TODO: other validation

        # TODO: delivery options

        # For now, just show the diff
        print "Here's the diff:"
        subprocess.call("git --no-pager diff", shell=True)

    finally:
        # restore working dir
        os.chdir(origcwd)
finally:
    # cleanup the tmp repo
    print "Removing scratch directory: %s" % tmpdir
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)



