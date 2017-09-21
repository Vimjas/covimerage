#!/bin/sh

# This should be run through tox ("make test_integration") to not touch local
# .coverage files.

set -e

prof=$(mktemp)
${VIM:-vim} --noplugin -Nu tests/test_plugin/vimrc -i NONE \
  --cmd "let g:prof_fname = '$prof'" \
  -c 'call test_plugin#integration#func1()' -c q

covimerage write_coverage "$prof"
# cat .coverage

cat > .coveragerc <<EOF
[run]
plugins = covimerage
EOF

# Fails if there is no data to report.
out=$(coverage report)

expected='Name                                                     Stmts   Miss  Cover
----------------------------------------------------------------------------
tests/test_plugin/autoload/test_plugin/integration.vim       9      3    67%'

if [ "$out" != "$expected" ]; then
  echo "coverage report does not match expectation." >&2
  printf 'expected:\n%s\ngot:\n%s\n' "$expected" "$out"
  exit 1
fi

coverage annotate

diff -u ./tests/test_plugin/autoload/test_plugin/integration.vim,cover tests/fixtures/integration.sh.cover-output.txt

find . -name '*,cover'
