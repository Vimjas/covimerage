from click.utils import string_types


def get_fname_and_fobj_and_str(fname_or_fobj):
    if isinstance(fname_or_fobj, string_types):
        return fname_or_fobj, None, fname_or_fobj
    try:
        fname = fname_or_fobj.name
    except AttributeError:
        return None, fname_or_fobj, str(fname_or_fobj)
    return fname, fname_or_fobj, fname
