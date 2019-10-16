# this is a make/python hybrid file
# see python.py for more details
#
# Normal make files are a make/sh hybrid.
# This makefile uses python instead of sh (or bash)

#
# target … : prerequisites …
#        recipe
#        …
#        …

# All recipe lines for any given target essentially become
# a python function defined in the python.py make shell
#
# So, target/prerequisites parts of a rule are still regular make
# and the recipe part can be thought of as a python function body
#
# all recipe bodies need $(origin) or $(caption) (but not both) as
# first statement
#

# export variables that we don't want
# to pass to python as macros

# project source paths
export root := $(__root)/$(project)$(in_ext)
out := $(__root)/$(project)$(out_ext)
out_init := $(out)/.init

export cxxsrc := $(root)/cxxsrc
export cxxinc := $(root)/cxxinc

testfiles := $(root)/testfiles

bin := $(out)/bin
lib := $(out)/lib
tmp := $(out)/tmp
bak := $(out)/bak

mainsrc := $(cxxsrc)/main
testsrc := $(cxxsrc)/test

main_exe := $(bin)/$(project)_main.exe
main_dynamic_lib := $(lib)/lib$(project).so
main_static_lib := $(lib)/lib$(project).a
test_exe := $(bin)/$(project)_test.exe

# project object generation paths
export obj := $(out)/objects
export pch := $(obj)/pch
obj_lib := $(obj)/lib
obj_main := $(obj)/main
obj_test := $(obj)/test

obj_lib_init := $(obj_lib)/.init
obj_main_init := $(obj_main)/.init
obj_test_init := $(obj_test)/.init

obj_dirs := $(obj_lib) $(obj_main) $(obj_test)

obj_dir_inits := $(obj_lib_init) $(obj_main_init) $(obj_test_init)

# precompliled common sysheaders paths
lib_sysheaders_pch := $(pch)/lib_sysheaders.pch
main_sysheaders_pch := $(pch)/main_sysheaders.pch
test_sysheaders_pch := $(pch)/test_sysheaders.pch

all_sysheaders_pch := \
  $(lib_sysheaders_pch) \
  $(main_sysheaders_pch) \
  $(test_sysheaders_pch)

sysheaders_hxx := $(cxxinc)/sysheaders.hxx

export exes := $(bin)/*.exe
export dynamic_libs := $(lib)/*.so
export static_libs := $(lib)/*.a

bin_init := $(bin)/.init
lib_init := $(lib)/.init
tmp_init := $(tmp)/.init
bak_init := $(bak)/.init

# compilers and flags

CC := "clang"
CXX := "clang++"

CXX_FLAGS0 := '-D__project_root_dir="$(root)"', "-working-directory=$(root)"
CXX_FLAGS1 := $(CXX_FLAGS0), $(CXX_FLAGS), "-I/usr/local/include"
CXX_FLAGS2 := $(CXX_FLAGS1), "-Werror", "-Wall", "-Wextra"
CXX_FLAGS3 := $(CXX_FLAGS2), "-Wnull-dereference", "-Wdouble-promotion"
CXX_FLAGS4 := $(CXX_FLAGS3), "-Wno-ignored-qualifiers", "-Wshadow"
__CXX_FLAGS := $(CXX_FLAGS4), "-fomit-frame-pointer", "-I$(cxxinc)"

DEP_CXX_FLAGS := $(CXX_FLAGS1)

__LD_FLAGS := "-Wl,-Bdynamic", "-lstdc++", "-L/usr/local/lib",  $(LD_FLAGS)
LD_TEST_FLAGS := $(__LD_FLAGS)  #, "-lgtest_main", "-lgtest"

UNIT_TESTING_DEF := $(project_label)_UNIT_TESTING
MAIN_DEF := $(project_label)_MAIN

TEST_DEF := '-DTEST_TMP="$(tmp)"', '-DTESTFILES="$(testfiles)"'

TEST_EXTRA0 := $(TEST_DEF), "-Wno-sign-compare"
TEST_EXTRA := "-D$(UNIT_TESTING_DEF)=1", "-D$(MAIN_DEF)=0", $(TEST_EXTRA0)
MAIN_EXTRA := "-D$(UNIT_TESTING_DEF)=0", "-D$(MAIN_DEF)=1"
LIB_EXTRA := "-D$(UNIT_TESTING_DEF)=0", "-D$(MAIN_DEF)=0", "-fPIC"

PCH_X := "-xc++-header"

# miscellaneous variables

export MAKEFILE_LIST
export MAKE

export cxxsources := $(out)/cxxsources
export cxxdeps := $(out)/cxxdeps
export objrules := $(out)/objrules

# python macros
export origin = (this,first,newer,pre,existed)=init(t="${@}",f="$<",n="$?",p="$^")
export caption = $(origin); caption()
export caption0 = $(origin); caption(begin="\033[2K\r",end=" ")
export caption1 = $(origin); caption(begin="\033[2K\r")

noop:
  pass

include $(python_make)/cxx_sources_deps_rules.py
include $(python_make)/reformat_rules.py
include $(cxxsources)
include $(cxxdeps)
include $(objrules)

format:;$(caption);run(env.MAKE,"reformat_source")

.vars: $(cxxsources);$(caption)
  for a in ["cxxsrc", "cxxinc", "root", "exes", "cxxsources", "obj_dirs"]:
    print("%s: %s" % (a, os.environ[a]))

clean-exes-libs:;$(caption)
  rm_f(env.exes, env.dynamic_libs, env.static_libs)

re-dep:clean-exes-libs;$(caption)
  rm_f(env.cxxsources, env.cxxdeps, env.objrules)

clean:re-dep;$(caption); rmtree(env.obj)

clean-pch:;$(caption); rmtree(env.pch)

clean-all:clean;$(caption);
  rmtree("$(out)", env.python_make+"/__pycache__")

# python macros
pch_common0 = $(caption); mkdir_p(env.pch)
pch_common1 = $(CC), $(PCH_X), first, "-o"+this, $(__CXX_FLAGS)

# rules to build precompiled headers
$(lib_sysheaders_pch): $(sysheaders_hxx);$(pch_common0)
  run($(pch_common1), $(LIB_EXTRA))

$(main_sysheaders_pch): $(sysheaders_hxx);$(pch_common0)
  run($(pch_common1), $(MAIN_EXTRA))

$(test_sysheaders_pch): $(sysheaders_hxx);$(pch_common0)
  run($(pch_common1), $(TEST_EXTRA))

.sysheaders:;$(origin);$(all_sysheaders_pch)

sysheaders:;$(caption);run(env.MAKE, ".sysheaders", jN)

$(out_init) $(tmp_init) $(bak_init) $(bin_init) $(lib_init) $(obj_dir_inits):
  $(caption)
  mkdir_p(os.path.dirname(this))
  touch(this)

main_exe_objects ?=
lib_so_objects ?=
test_exe_objects ?=

$(main_exe): $(bin_init) $(main_exe_objects)
  $(caption1)
  run($(CXX), "-o$@", $(__main_exe_objects__), $(__LD_FLAGS))

$(main_dynamic_lib): $(lib_init) $(lib_so_objects)
  $(caption1)
  run($(CXX), "-shared", "-o$@", $(__lib_so_objects__), $(__LD_FLAGS))

$(main_static_lib): $(lib_init) $(lib_so_objects)
  $(caption1)
  run("ar", "rcs", "$@", $(__lib_so_objects__))

$(test_exe): $(bin_init) $(tmp_init) $(test_exe_objects)
  $(caption1)
  run($(CXX), "-o$@", $(__test_exe_objects__), $(LD_TEST_FLAGS))

.build:$(main_exe) $(main_static_lib) $(main_dynamic_lib) $(test_exe);$(origin)

build1:checkcxxsources;$(caption);run(env.MAKE, ".build", "-j1")

build:checkcxxsources;$(caption);run(env.MAKE, ".build", jN)

.lib:$(main_static_lib) $(main_dynamic_lib);$(origin)
.exe:$(main_exe);$(origin)
.test:$(test_exe);$(origin)

_lib:;$(origin);run(env.MAKE, ".lib", jN)
_exe:;$(origin);run(env.MAKE, ".exe", jN)
_test:;$(origin);run(env.MAKE, ".test", jN)

lib:checkcxxsources _lib;$(caption);
exe run:checkcxxsources _exe;$(caption);run("$(main_exe)")
test:checkcxxsources _test;$(caption);run("$(test_exe)");print("+++passed")

repl:checkcxxsources _exe;$(caption);run("$(main_exe)","--repl")

all:build;$(caption)

refresh:re-dep build;$(caption)

fail:;$(caption)
  touch(this)
  __really__should__not__be__defined__
  yes

warn:;$(caption)
  $(__really__should__not__be__defined__)
  pass

pass:;$(caption);$@

.make:;$(caption);print("make is", env.MAKE)

skeleton:
  if not "newsrc" in os.environ:
    print ("usage: newsrc=<some new project directory> make skeleton")
    leave()

  mkdir_p(env.newsrc+"/cxxinc")
  mkdir_p(env.newsrc+"/cxxsrc/main")
  mkdir_p(env.newsrc+"/cxxsrc/test")
  mkdir_p(env.newsrc+"/testfiles")

.os-name:;$(caption)
  print(os.name)
  print(sys.platform)
