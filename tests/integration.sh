#!/bin/sh

# This should be run through tox ("make test_integration") to not touch local
# .coverage files.

if [ -f .coveragerc ]; then
  echo "This should be run from a temporary dir. Please use tox -e integration." >&2
  exit 1
fi

set -ex

prof=$(mktemp)
(cd "$TESTS_SRC_DIR"
  ${VIM:-vim} --noplugin -Nu tests/test_plugin/vimrc -i NONE \
    --cmd "let g:prof_fname = '$prof'" \
    -c 'call test_plugin#integration#func1()' -c q)

covimerage write_coverage "$prof"

cat > .coveragerc <<EOF
[run]
plugins = covimerage
data_file = $PWD/.coverage
EOF

cat > .coveragerc.outer <<EOF
[run]
data_file = $PWD/.coverage.outer
branch = true
source = covimerage
EOF

tmp_dir="$PWD"
# Fails if there is no data to report.
out=$(cd "$TESTS_SRC_DIR" && coverage run --rcfile="$tmp_dir/.coveragerc.outer" -m coverage report --rcfile="$tmp_dir/.coveragerc")

expected='Name                                                     Stmts   Miss  Cover
----------------------------------------------------------------------------
tests/test_plugin/autoload/test_plugin/integration.vim       9      3    67%'

if [ "$out" != "$expected" ]; then
  echo "coverage report does not match expectation." >&2
  printf 'expected:\n%s\ngot:\n%s\n' "$expected" "$out"
  exit 1
fi

coverage annotate
find . -name '*,cover' -ls

diff -u "$TESTS_SRC_DIR/tests/test_plugin/autoload/test_plugin/integration.vim,cover" \
  "$TESTS_SRC_DIR/tests/fixtures/integration.sh.cover-output.txt"
