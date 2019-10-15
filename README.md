# covimerage

Generates code coverage information for Vim scripts.

It parses the output from Vim's `:profile` command, and generates data
compatible with [Coverage.py](http://coverage.readthedocs.io/).

[![Build Status](https://circleci.com/gh/Vimjas/covimerage/tree/master.svg?style=shield)](https://circleci.com/gh/Vimjas/covimerage)
[![codecov](https://codecov.io/gh/Vimjas/covimerage/branch/master/graph/badge.svg)](https://codecov.io/gh/Vimjas/covimerage/branch/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/548eb25f726646fbbe660dc9fb6d392a)](https://www.codacy.com/app/blueyed/covimerage)

## Installation

You can install covimerage using pip:

```sh
pip install covimerage
```

## Simple usage

You can use `covimerage run` to wrap the call to Neovim/Vim with necessary
boilerplate:

```sh
covimerage run vim -Nu test/vimrc -c 'Vader! test/**'
```

This will write the file `.coverage_covimerage` by default (use `--data-file`
to configure it), which is compatible with Coverage.py.
A report is automatically generated (on stdout).

You can then call `covimerage xml` to create a `coverage.xml` file
(Cobertura-compatible), which tools like [Codecov](https://codecov.io/)'s
`codecov` tool can consume, e.g. via `codecov -f coverage.xml`.

## Manual/advanced usage

### 1. Generate profile information for your Vim script(s)

You have to basically add the following to your tests vimrc:

```vim
profile start /tmp/vim-profile.txt
profile! file ./*
```

This makes Neovim/Vim then write a file with profiling information.

### 2. Call covimerage on the output file(s)

```sh
covimerage write_coverage /tmp/vim-profile.txt
```

This will create a file `.coverage_covimerage` (the default for `--data-file`),
with entries marked for processing by a
[Coverage.py](http://coverage.readthedocs.io/) plugin (provided by
covimerage)).

### 3. Include the covimerage plugin in .coveragerc

When using `coverage` on the generated output (data file), you need to add
the `covimerage` plugin to the `.coveragerc` file (which Coverage.py uses).
This is basically all the `.coveragerc` you will need, but you could use
other settings here (for Coverage.py), e.g. to omit some files:

```
[run]
plugins = covimerage
data_file = .coverage_covimerage
```

### 4. Create the report(s)

You can now call e.g. `coverage report -m`, and you should be able to use
coverage reporting platforms like <https://codecov.io/> or
<https://coveralls.io>, which are basically using `coverage xml`.

## Reference implementation

- [Neomake](https://github.com/neomake/neomake) is the first adopter of this.
  It has an advanced test setup (including Docker based builds), and looking at
  tis setup could be helpful when setting up covimerage for your
  plugin/project.

  - [Neomake's coverage report on codecov.io](https://codecov.io/gh/neomake/neomake/tree/master)
  - [PR/change to integrate it in
    Neomake](https://github.com/neomake/neomake/pull/1600) (Neomake's test
    setup is rather advanced, so do not let that scare you!)

## Caveats

Coverage information for a function may get wiped if the function is re-defined
after testing it. This is a known limitation that does not depend on the
implementation of covimerage, but on the vim profiler itself, since profiling
data for a function, used to extract coverage data, is reset when the function
is re-defined, even if the definition is identical.

This can be an issue if the source files being checked for coverage are
reloaded with `runtime` between tests for some reasons, e.g. when mocking some
function. To prevent coverage information from being lost, one solution is to
write such tests in a different suite that is run separately, and combine the
coverage results with `covimerage run --append`.

## Links

- Discussion in Coverage.py's issue tracker:
  [coverage issue 607](https://bitbucket.org/ned/coveragepy/issues/607/)

## TODO

- Line hit counts: known to covimerage, but not supported by Coverage.py
  (<https://bitbucket.org/ned/coveragepy/issues/607/#comment-40048034>).
