# covimerage

A tool to generate code coverage reports for Vim scripts.

## Usage

### 1. Generate profile information for your Vim script(s)

You have to basically add the following to your (tests) vimrc:

```vim
profile start /tmp/vim-profile.txt
profile! file ./*
```

### 2. Call covimerage on the output file(s)

```sh
covimerage /tmp/vim-profile.txt
```

## TODO

- Use coverage as a base line tool
  see [coverage issue 607](https://bitbucket.org/ned/coveragepy/issues/607/)
