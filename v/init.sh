#!/usr/bin/env bash

set -x

rm -rf makeshell_bin
mkdir -p makeshell_bin
v -o makeshell_bin/makeshell makeshell_src/makeshell.v
