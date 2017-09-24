#!/bin/sh

# This should be run through tox ("make test_integration") to not touch local
# .coverage files.

if [ -f .coveragerc ] || [ -f .coverage ]; then
  echo "This should be run from a temporary dir. Please use tox -e integration." >&2
  exit 1
fi

set -ex

prof=$(mktemp)
(cd "$TESTS_SRC_DIR"
  out=$(${VIM:-vim} --noplugin -Nu tests/test_plugin/vimrc -i NONE \
    --cmd "let g:prof_fname = '$prof'" \
    -c 'call test_plugin#integration#func1()' -c q 2>&1 </dev/null | cat -A))

# Setup coveragerc files for inner (tested) and outer (reporting) runs.
coveragerc_inner="$PWD/.coveragerc.inner"
cat > "$coveragerc_inner" <<EOF
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
COVERAGE_RUN_OUTER="coverage run -a --rcfile=$PWD/.coveragerc.outer"

# Test write_coverage.
$COVERAGE_RUN_OUTER -m covimerage write_coverage "$prof"

# Test report.
# Fails if there is no data to report.
out=$(cd "$TESTS_SRC_DIR" && $COVERAGE_RUN_OUTER -m coverage report --rcfile="$coveragerc_inner")
expected='Name                                                     Stmts   Miss  Cover
----------------------------------------------------------------------------
tests/test_plugin/autoload/test_plugin/integration.vim       9      3    67%'
if [ "$out" != "$expected" ]; then
  echo "coverage report does not match expectation." >&2
  printf 'expected:\n%s\ngot:\n%s\n' "$expected" "$out"
  exit 1
fi

# Test annotate.
$COVERAGE_RUN_OUTER -m coverage annotate --directory=. --rcfile="$coveragerc_inner"
annotated_file="$(find . -maxdepth 1 -name '*,cover')"
diff -u "$annotated_file" "$TESTS_SRC_DIR/tests/fixtures/integration.sh.cover-output.txt"
