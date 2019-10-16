# this is a make/python hybrid file

# Normal make files are a make/sh hybrid.
# This makefile uses python instead of sh (or bash)

all_formatted_sources :=  cxxsrc/*/*.cxx cxxinc/*.hxx
formatted_sources_tarball := $(bak)/formatted_sources.backup.tar

revert_formatted_via_git:;$(caption)
  cmd('git checkout $(all_formatted_sources)')

revert_formatted_from_tar:;$(caption)
  cmd('tar xspvf $(formatted_sources_tarball)')

clang_format_style := -style={\
    BasedOnStyle: google, \
    IndentWidth: 2, \
    ConstructorInitializerIndentWidth: 2, \
    ContinuationIndentWidth: 2, \
    TabWidth: 2, \
    UseTab: Never, \
    ColumnLimit: 79, \
    SortIncludes: true, \
    AlignEscapedNewlines: false,\
    AlignConsecutiveAssignments: false,\
    AlignConsecutiveDeclarations: false,\
    AllowShortBlocksOnASingleLine: true,\
    AllowShortCaseLabelsOnASingleLine: true,\
    AllowShortFunctionsOnASingleLine: All,\
    AllowShortLoopsOnASingleLine: true,\
    NamespaceIndentation: All}

reformat_source:$(bak_init);$(origin)
  rm_f('$(formatted_sources_tarball)')
  tar = "gtar" if "freebsd" in sys.platform else "tar"
  cmd('cd $(root) && %s cpf $(formatted_sources_tarball) $(all_formatted_sources)' %tar)
  cmd('''cd $(root) && clang-format "$(clang_format_style)" -i $(all_formatted_sources)''')
  cmd('cd $(root) && %s --compare --file=$(formatted_sources_tarball) || true' %tar)

git_status_formatted_sources:;$(caption)
  cmd('git status $(all_formatted_sources)')

.reformat_config:;$(caption)
  run('clang-format', "$(clang_format_style)", '-dump-config')
