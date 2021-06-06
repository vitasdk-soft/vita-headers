import os
import glob


DEFAULT_BUILD_OUTDIR = 'build'

def execute(cmd, force_print=False):
    with os.popen(cmd) as r:
        for line in iter(r.readline, ""):
            if os.environ.get('VERBOSE') or force_print:
                print(line)
        return r.close()

def vita_libs_gen(yml, out):
    if execute('vita-libs-gen {} {}'.format(yml, out)):
        raise SystemExit(10)

def make(target):
    curr = os.getcwd()
    os.chdir(target)
    if execute('make -j'):
        raise SystemExit(11)
    os.chdir(curr)

def make_install(target):
    curr = os.getcwd()
    os.chdir(target)
    if execute('make install'):
        raise SystemExit(12)
    os.chdir(curr)

def definition_check():
    return execute('python .travis.d/definition_check.py', force_print=True)

def definition_ordering(yml):
    return execute('bash .travis.d/definition_ordering.sh {}'.format(yml))

if __name__ == '__main__':
    import sys
    import shutil


    outdir = DEFAULT_BUILD_OUTDIR
    if len(sys.argv) >= 2:
        outdir = sys.argv[1]

    if os.environ.get('USE_LINT'):
        if definition_check():
            raise SystemExit(1)

        for yml in glob.glob(os.path.join('db', '**', '*.yml')):
            if definition_ordering(yml):
                raise SystemExit(2)

    for yml in glob.glob(os.path.join('db', '**', '*.yml')):
        dirs, fn = (os.path.split(yml))
        _, ver = os.path.split(dirs)
        build_target = os.path.join(outdir, ver, fn)
        if os.path.exists(build_target):
            shutil.rmtree(build_target)
        os.makedirs(build_target)
        vita_libs_gen(yml, build_target)
        make(build_target)
        make_install(build_target)
