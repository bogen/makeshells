#!/usr/bin/env python3

# this is pure python, not a make/python hybrid
# this is the make shell
#!/usr/bin/env pypy3


#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

import sys
import traceback
import os.path

#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

from python_make import origin_init, __unknown__, rm

#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

this = __unknown__
first = __unknown__
newer = __unknown__
pre = __unknown__
existed = False


def init(t, f, n, p):
  global this, first, newer, pre, existed
  (this, first, newer, pre) = (t, f, n, p)
  existed = os.path.exists(this)
  return origin_init(t=this, f=first, n=newer, p=pre, e=existed)


#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####
#### #### #### #### #### #### #### #### #### #### #### #### #### #### ####


def __make__main():
  try:
    template0 = "# %s\nfrom python_make import *\n"
    template1 = "# content from makefile starts on line #5\n#\n%s"
    template = template0 + template1
    recipe = template % (sys.argv[0], sys.argv[1])
    try:
      exec(recipe)
    except Exception as e:
      print()
      print(traceback.format_exc())
      n = 1
      print('File "<string>":')
      for line in recipe.split('\n'):
        print("  %02d: %s" % (n, line.rstrip()))
        n += 1
      print()
      if os.path.exists(this):
        print("Removing", this)
        rm(this)
      else:
        print(this, "was not created")
      print()
      sys.exit(-1)
  except IndexError as e:
    print(traceback.format_exc())
    print("Usage: %s '<multiline script text as a single argument>'" %
          sys.argv[0])
    sys.exit(-1)


__make__main()
