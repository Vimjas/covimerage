# covimerage

A tool to generate code coverage reports for Vim scripts.

## Usage

### 1. Generate profile information for your Vim script(s)

You have to basically add the following to your (tests) vimrc:

```vim
profile start /tmp/vim-profile.txt
profile! file ./*
```

This makes Neovim/Vim write a file with profiling information.

### 2. Call covimerage on the output file(s)

```sh
covimerage /tmp/vim-profile.txt
```

This will create a `.coverage` file (through a
[Coverage.py](http://coverage.readthedocs.io/) plugin), which the `coverage`
tool can use then, e.g. allowing you to run `coverage report -m` on it.

The `.coverage` file is also used with coverage reporting platforms like
<https://codecov.io/> or <https://coveralls.io> (basically via `coverage xml`,
which creates an XML report from it).

## Reference implementation

- [Neomake](https://github.com/neomake/neomake)

  TODO: link to tests' vimrc etc.

## Links

- Discussion in Coverage.py's issue tracker:
  [coverage issue 607](https://bitbucket.org/ned/coveragepy/issues/607/)
