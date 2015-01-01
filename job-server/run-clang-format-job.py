
repo = "../dbglib/"
delay = 90
style = "Google"

assert delay > 0 and delay < 365*10
assert style in ["LLVM", "Google", "Chromium", "Mozilla", "WebKit"]

import os
import subprocess
import shutil
import sys

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
        
        if not build_it():
            print "initial build failed"
            sys.exit(-1)

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

        # do a full build and make sure it passes.  IF it doesn't, we 
        # don't want to keep this.  TODO: We'll need to be robust against
        # failures in the future, but for now, don't mess with it.
        if not build_it():
            print "build failed after format"
            sys.exit(-1)


        # TODO: multiple delivery options
        # 1) diff via email
        # 2) commit and push
        # 3) repo fork and pull request
        # 4) publish diff to known location (website)
        #    formatted nicely, with raw patch for apply
        #    generate a json output file, parse this to make
        #    a pretty webpage later.  Put the diffs into own subtree

        output_format = "diff-web"
        if output_format == "diff-web":
            # make a output sub-directory
            os.mkdir("./.livingcode-output")
            # single unified diff
            subprocess.call("git --no-pager diff > ./.livingcode-output/combined.diff", shell=True)
            # per file diff with unique file
            for i in xrange(len(formatted)): 
                subprocess.call("git --no-pager diff %s > ./.livingcode-output/%d.diff" % (formatted[i],i), shell=True)
            # temporary, show the dir tree since we're about to delete it
            subprocess.call("wc ./.livingcode-output/*", shell=True)
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

    finally:
        # restore working dir
        os.chdir(origcwd)
finally:
    # cleanup the tmp repo
    print "Removing scratch directory: %s" % tmpdir
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)



