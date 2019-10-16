#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

# this is pure python, not a make/python hybrid

#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

import types
import subprocess
import shlex
import shutil
import os
import glob
import multiprocessing
import pathlib
import sys

#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

# allow for $(shell ...) in make
if "root" in os.environ:
  env = types.SimpleNamespace(**os.environ)
  root_prefix = env.root+"/"
  root_prefix_len = len(root_prefix)
  __root_prefix = env.__root+"/"
  __root_prefix_len = len(__root_prefix)

  __unknown__ = "//#### unknown ####//"

  this,first,newer,pre = __unknown__,__unknown__,__unknown__,__unknown__
  existed = False

thread_max = int(multiprocessing.cpu_count()*1)
jN = "-j%d" % thread_max

def origin_init(t, f, n, p, e):
  global this, first, newer, pre, existed
  (this, first, newer, pre, existed) = (t, f, n, p, e)
  return (t, f, n, p, e)


#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
def g(p):
  return glob.glob(p)


def fg(*args):
  fg.fl = []

  def add(x):
    gx = g(x)
    if len(gx) > 0:
      fg.fl += g(x)
    else:
      fg.fl += [x]

  for f in args:
    if isinstance(f, list) or isinstance(f, tuple):
      for x in f:
        add(x)
    elif isinstance(f, str):
      add(f)
  return fg.fl


def touch(*args):
  for f in fg(args):
    open(f, 'a').close()


def __rm(ignore, *args):
  errors = 0
  for f in fg(args):
    try:
      os.remove(f)
    except FileNotFoundError as e:
      if not ignore:
        errors += 1
        print(e)
  if errors > 0:
    raise FileNotFoundError()


def rm(*args):
  __rm(False, *args)


def rm_f(*args):
  __rm(True, *args)


def rmtree(*args):
  for p in fg(args):
    try:
      shutil.rmtree(p)
    except FileNotFoundError as e:
      pass


def mkdir_p(*args):
  for p in fg(args):
    os.makedirs(p, mode=0o755, exist_ok=True)

def run(*args):
  r = subprocess.run(args)
  if r.returncode != 0:
    em = "failed (rc=%d) running: %s" % (r.returncode,r.args)
    print(' '.join(shlex.quote(arg) for arg in r.args))
    raise RuntimeError(em)

def gorge(*args):
  return subprocess.check_output(args, stderr=subprocess.STDOUT, shell=False)


def shquote(*args):
  s = ""
  for a in args:
    s += shlex.quote(a)
  return s


def cmd(*args):
  rc = os.system(" ".join(args))
  if rc != 0:
    print("running %s failed: %d" % (args, rc))
    raise RuntimeError()

def remove_prefix(text, prefix):
  if text.startswith(prefix):
    return text[len(prefix):]
  return text

def remove_root(path):
  return remove_prefix(remove_prefix(path, root_prefix),__root_prefix)

def caption(begin="", end='\n'):
  _caption = "%s[%s]" % (begin,remove_root(this))
  if (newer != "") and existed:
    _caption += " due to: "
    _caption += newer.replace(root_prefix,"")
  print(_caption,end=end)

def slurp(path):
  return pathlib.Path(path).read_text()

def leave(): sys.exit(0)
