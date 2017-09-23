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

This will create a `.coverage` file (marking entries for processing by a
[Coverage.py](http://coverage.readthedocs.io/) plugin).

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
  It has a quite advanced test setup (e.g. Docker based builds), and therefore
  could be helpful when you want to use covimerage for your plugin/project.
  See <https://github.com/neomake/neomake/pull/1600>.

## Links

- Discussion in Coverage.py's issue tracker:
  [coverage issue 607](https://bitbucket.org/ned/coveragepy/issues/607/)

## TODO

- Line hit counts: known to covimerage, but not supported by Coverage.py
  (<https://bitbucket.org/ned/coveragepy/issues/607/#comment-40048034>).
