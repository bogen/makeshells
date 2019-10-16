# switch to a python shell, use spaces rather than tabs

# We are not using any builtins
MAKEFLAGS:= --warn-undefined-variables \
            --no-builtin-rules \
            --no-builtin-variables \
            --output-sync=target \
            --silent

.RECIPEPREFIX +=
.ONESHELL:
.SHELLFLAGS :=

export __root := $(PWD)
project := sample
project_label := SAMPLE

LD_FLAGS := "-lpthread" # , "-lreadline"
CXX_FLAGS := "-std=gnu++17", "-pthread", "-O2"

out_ext := -out
in_ext := .src

export python_make := $(__root)/python-make

SHELL :=  $(python_make)/python.py

include $(python_make)/main.py
