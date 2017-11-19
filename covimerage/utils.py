import os
import re

from click.utils import string_types

from ._compat import shell_quote

# Empty (whitespace only), comments, continued, or `end` statements.
RE_NON_EXECED = re.compile(r'^\s*("|\\|end|$)')


def get_fname_and_fobj_and_str(fname_or_fobj):
    if isinstance(fname_or_fobj, string_types):
        return fname_or_fobj, None, fname_or_fobj
    try:
        fname = fname_or_fobj.name
    except AttributeError:
        return None, fname_or_fobj, str(fname_or_fobj)
    return fname, fname_or_fobj, fname


def build_vim_profile_args(profile_fname, sources):
    args = ['--cmd', 'profile start %s' % profile_fname]
    for source in sources:
        if os.path.isdir(source):
            pattern = '%s/*'
        else:
            pattern = '%s'
        args += ['--cmd', 'profile! file %s' % (pattern % source)]
    return args


def is_executable_filename(filename):
    # We're only interested in files that look like reasonable Vim
    # files:
    # Must end with .vim or start with vim, and must not have
    # certain funny characters that probably mean they are editor
    # junk.
    if re.match(r'[^.][^#~!$@%^&*()+=,]*\.n?vim$', filename):
        return True
    if re.match(r'[^#~!$@%^&*()+=,]*vimrc[^#~!$@%^&*()+=,]*$', filename):
        return True
    return False


def find_executable_files(src_dir):
    for (dirpath, _, filenames) in os.walk(src_dir):
        for filename in filenames:
            if is_executable_filename(filename):
                yield os.path.join(dirpath, filename)


def is_executable_line(line):
    return not RE_NON_EXECED.match(line)


def join_argv(argv):
    return ' '.join(shell_quote(s) for s in argv)
