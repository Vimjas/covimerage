import os

from click.utils import string_types


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
