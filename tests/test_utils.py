from covimerage import get_fname_and_fobj_and_str
from covimerage._compat import StringIO
from covimerage.utils import build_vim_profile_args


def test_build_vim_profile_args(devnull, tmpdir):
    F = build_vim_profile_args

    fname = devnull.name
    dname = str(tmpdir)

    assert F(fname, [fname]) == [
        '--cmd', 'profile start %s' % fname,
        '--cmd', 'profile! file %s' % fname]
    assert F(fname, [dname]) == [
        '--cmd', 'profile start %s' % fname,
        '--cmd', 'profile! file %s/*' % dname]
    assert F(fname, [fname, dname]) == [
        '--cmd', 'profile start %s' % fname,
        '--cmd', 'profile! file %s' % fname,
        '--cmd', 'profile! file %s/*' % dname]


def test_get_fname_and_fobj_and_str(devnull):
    F = get_fname_and_fobj_and_str
    assert F('foo') == ('foo', None, 'foo')
    assert F(None) == (None, None, 'None')
    assert F(devnull) == ('/dev/null', devnull, '/dev/null')
    s = StringIO('')
    assert F(s) == (None, s, str(s))


def test_is_executable_filename():
    from covimerage.utils import is_executable_filename

    assert is_executable_filename('foo.vim')
    assert is_executable_filename('foo.nvim')
    assert is_executable_filename('vimrc')
    assert is_executable_filename('.vimrc')

    assert not is_executable_filename('.hidden.vim')
    assert not is_executable_filename('foo.txt')

# Not used currently, but inlined.
# from covimerage import join_script_lines


# def join_script_lines(lines):
#     """Join lines from scripts to match lines from functions."""
#     new = []
#     buf = None
#     for l in lines:
#         if buf:
#             m = re.match(RE_CONTINUING_LINE, l)
#             if m:
#                 buf += l[m.end():]
#                 continue
#         if buf is not None:
#             new.append(buf)
#         buf = l
#     if buf is not None:
#         new.append(buf)
#     return new
#
#
# def test_join_script_lines():
#     assert join_script_lines([]) == []
#     assert join_script_lines(['1']) == ['1']
#     assert join_script_lines(['\\1']) == ['\\1']
#     assert join_script_lines([
#         '    line1',
#         '    \\ .line2']) == ['    line1 .line2']
#     assert join_script_lines([
#         '    line1',
#         '    \\ .line2',
#         '\\line3']) == ['    line1 .line2line3']
