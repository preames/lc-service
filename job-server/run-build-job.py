
import os
import subprocess
import shutil
import sys

assert len(sys.argv) == 3
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
            print "build failed"
            sys.exit(-1)

    finally:
        # restore working dir
        os.chdir(origcwd)
finally:
    # cleanup the tmp repo
    print "Removing scratch directory: %s" % tmpdir
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)



