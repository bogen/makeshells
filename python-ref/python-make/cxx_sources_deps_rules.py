# this is a make/python hybrid file

# Normal make files are a make/sh hybrid.
# This makefile uses python instead of sh (or bash)

test_cxx_sources ?=

checkcxxsources $(cxxsources):$(out_init)
  $(origin)
  if (this == "checkcxxsources") and (not os.path.exists(env.cxxsources)):
    leave()
  caption()

  if (this == env.cxxsources):
    lib_cxx, main_cxx = [],[]
    quote = "'"
  else:
    quote = ""

  test_cxx=[]

  for root, dirs, files in os.walk(env.cxxsrc) :
    for file in files:
      if file.endswith(".cxx"):
        cxx = quote+os.path.join(root, file)+quote
        if root.endswith("/main"):
          if (this == env.cxxsources): lib_cxx.append(cxx); main_cxx.append(cxx)
          test_cxx.append(cxx)
        elif root.endswith("/test"):
          test_cxx.append(cxx)

  test_cxx.sort()

  if (this == env.cxxsources):
    lib_cxx.sort()
    main_cxx.sort()
    with open (this, "w") as f:
      f.write("# === Generated by %s:%s ===\n\n" % (env.MAKEFILE_LIST, this))
      f.write("lib_cxx_sources := %s\n\n" % (",".join(lib_cxx)))
      f.write("main_cxx_sources := %s\n\n" % (",".join(main_cxx)))
      f.write("test_cxx_sources := %s\n\n" % (",".join(test_cxx)))
    leave()

  before = set([$(test_cxx_sources)])
  after = set(test_cxx)
  removed = str(before-after).replace(root_prefix,"")
  added = str(after-before).replace(root_prefix,"")
  removals = removed != "set()"
  additions = added != "set()"
  if removals or additions:
    print ("cxx source files were added or removed\n")
    if removals: print("removals:", removed)
    if additions: print("additions:", added)
    print ("\nForcing dependency and rule regeneration and re-link.\n")
    run(env.MAKE, "re-dep")

cxx_dep0 := $(CXX), "-E", "--trace-includes", $(DEP_CXX_FLAGS)
cxx_dep1 := "-I$(cxxinc)", cxx, "-o/dev/null"
cxx_dep := $(cxx_dep0), $(cxx_dep1)

$(cxxdeps): $(cxxsources);$(caption)
  def find_dep(cxx, q, fd_a):
    deps = []
    lines = str(fd_a.gorge($(cxx_dep))).split(r"\n")
    for line in lines:
      i = line.find("$(cxxinc)")
      if i != -1: deps.append(line[i:])
    q.put(cxx[fd_a.root:].replace("/","_").replace(".cxx","_obj_deps"))
    q.put([cxx] + sorted(deps))

  queues, process = [],[]
  fd_a=types.SimpleNamespace()
  fd_a.gorge = gorge
  fd_a.root = root_prefix_len

  prefix = "test_cxx_sources := "
  prefix_len = len(prefix)

  with open(first) as f:
    lines = f.readlines()
    for line in lines:
      if line.startswith(prefix):
        sources = line[prefix_len:].rstrip()
        test_cxx = sources.split(",")
        for _cxx in test_cxx:
          cxx = _cxx.replace("'","")
          q = multiprocessing.Queue()
          p = multiprocessing.Process(target=find_dep, args=(cxx, q, fd_a))
          process.append(p)
          queues.append(q)
          p.start()
        break

  with open (this, "w") as f:
    f.write("# === Generated by %s:%s ===\n\n" % (env.MAKEFILE_LIST, this))
    n = 1
    for q in queues:
      obj = q.get()
      deps = q.get()
      f.write("\n# %d\n%s := " % (n, obj))
      f.write(" ".join(deps))
      f.write("\n")
      n+=1

  for p in process: p.join()

$(objrules): $(cxxdeps); $(caption)
  suffix = "_obj_deps"
  prefix = "cxxsrc_"
  main_prefix = prefix + "main_"
  test_prefix = prefix + "test_"
  sep = " := "
  sep_len = len(sep)
  prefix_len = len(prefix)

  main_obj0, test_obj0, lib_obj0 = [],[],[]
  main_objs, test_objs, lib_objs = {},{},{}

  cxx_ext = ".cxx"
  cxx_ext_len = len(cxx_ext)

  with open(first) as f:
    lines = f.readlines()
    for line in lines:
      if line.startswith(prefix):
        i = line.find(sep)
        if i == -1: raise RuntimeError("Source deps line not formatted correctly")
        deps = line[:i]
        sources = line [i+sep_len:]
        j = sources.find(cxx_ext)+cxx_ext_len
        if j == -1: raise RuntimeError("Source deps line not formatted correctly")
        cxxfile = sources[root_prefix_len:j]
        cxxfile_i = "need to work on ctfe wrapper..."
        deps1 = deps.replace(suffix,".o")
        deps1 = deps1.replace("cxxsrc","$$(obj)")
        deps1 = deps1.replace("_","/",2)
        obj = deps1
        if deps.startswith(main_prefix):
          lib_obj = obj.replace("$$(obj)/main","$$(obj)/lib")
          test_obj = obj.replace("$$(obj)/main/","$$(obj)/test/main__")
          main_objs[obj] = (cxxfile,deps,cxxfile_i)
          lib_objs[lib_obj] = (cxxfile,deps,cxxfile_i)
          test_objs[test_obj] = (cxxfile,deps,cxxfile_i)
          main_obj0.append(obj)
          lib_obj0.append(lib_obj)
          test_obj0.append(test_obj)
          continue
        if deps.startswith(test_prefix):
          test_objs[obj] = (cxxfile,deps,cxxfile_i)
          test_obj0.append(obj)

  def target(label, objs, rule, cxx, dest, f):
    f.write("\n\n# %s\n" % label)
    for obj, pre in objs.items():
      f.write("%s: $$(%s) %s\n  $$(caption0);" % (obj, pre[1], dest))
      f.write("""run(%s, '-D__CXX_SRCFILE__="%s"', %s)\n""" % (cxx, pre[0], rule))
      f.write("  ## %s\n\n" % (pre[2]))

  def make_quoted_list(obj): return ",".join(map(lambda x: "'"+x+"'", obj))

  with open (this, "w") as f:
    f.write("# === Generated by %s:%s ===\n\n" % (env.MAKEFILE_LIST, this))
    f.write("\nmain_exe_objects := %s\n" % (" ".join(main_obj0)))
    f.write("\nlib_so_objects := %s\n" % (" ".join(lib_obj0)))
    f.write("\ntest_exe_objects := %s\n" % (" ".join(test_obj0)))
    f.write("\n__main_exe_objects__ := %s\n" % (make_quoted_list(main_obj0)))
    f.write("\n__lib_so_objects__ := %s\n" % (make_quoted_list(lib_obj0)))
    f.write("\n__test_exe_objects__ := %s\n" % (make_quoted_list(test_obj0)))

    ipch = "'-include-pch',"
    rule = "$$(__CXX_FLAGS), '-c', '$$<', '-o$$@'"
    main = ipch + "'$$(main_sysheaders_pch)'," + rule + ", $$(MAIN_EXTRA)"
    test = ipch + "'$$(test_sysheaders_pch)'," + rule + ", $$(TEST_EXTRA)"
    lib = ipch + "'$$(lib_sysheaders_pch)'," + rule + ", $$(LIB_EXTRA)"
    cxx = "$$(CXX)"

    main_d = "$$(obj_main_init) $$(main_sysheaders_pch)"
    lib_d = "$$(obj_lib_init) $$(lib_sysheaders_pch)"
    test_d = "$$(obj_test_init) $$(test_sysheaders_pch)"

    target("main", main_objs, main, cxx, main_d, f)
    target("lib", lib_objs, lib, cxx, lib_d, f)
    target("test", test_objs, test, cxx, test_d, f)
