# covimerage

Generates code coverage information for Vim scripts.

It parses the output from Vim's `:profile` command, and generates data
compatible with [Coverage.py](http://coverage.readthedocs.io/).

**NOTE:** this `develop` branch will be squash-merged into master after some
stabilization (1-2 weeks).

[![codecov](https://codecov.io/gh/Vimjas/covimerage/branch/develop/graph/badge.svg)](https://codecov.io/gh/Vimjas/covimerage/branch/develop)

## Installation

Covimerage is experimental/new, so please install it from its develop branch.

NOTE: please consider using a virtualenv / or `pip install --user …`.

```sh
pip install https://github.com/Vimjas/covimerage/archive/develop.zip
```

## Usage

### 1. Generate profile information for your Vim script(s)

You have to basically add the following to your tests vimrc:

```vim
profile start /tmp/vim-profile.txt
profile! file ./*
```

This makes Neovim/Vim then write a file with profiling information.

### 2. Call covimerage on the output file(s)

```sh
covimerage /tmp/vim-profile.txt
```

This will create a `.coverage` file (marking entries for processing by a
[Coverage.py](http://coverage.readthedocs.io/) plugin (provided by
covimerage)).

### 3. Include the covimerage plugin in .coveragerc

You need to add following in your .coveragerc to call the FileReporter
plugin (this is basically all the `.coveragerc` you will need):

```
[run]
plugins = covimerage
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
  See <https://github.com/neomake/neomake/pull/1600>.

## Links

- Discussion in Coverage.py's issue tracker:
  [coverage issue 607](https://bitbucket.org/ned/coveragepy/issues/607/)

## TODO

- Line hit counts: known to covimerage, but not supported by Coverage.py
  (<https://bitbucket.org/ned/coveragepy/issues/607/#comment-40048034>).
