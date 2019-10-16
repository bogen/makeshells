MAKEFLAGS:= --warn-undefined-variables \
            --no-builtin-rules \
            --no-builtin-variables \
            --output-sync=target \
            --silent

.RECIPEPREFIX +=
.ONESHELL:
.SHELLFLAGS :=

makeshell := ./makeshell_bin/makeshell

export ms_cc_extra := -I$(PWD)/ms_c_aux
export ms_cc := tcc

SHELL := $(makeshell)

$(makeshell): makeshell_src/makeshell.v
  println("rebuilding $< -> $@")
  os.system("./init.sh")

_ := $(makeshell)

noop:
  //

greet := msa.greet()

hello4:
  abc := "hello v 2 from make!!"
  println(abc)
  println("$@")

  args := ["echo1","a", "b", "c"]
  msa.run(args)
  $(greet)
