from covimerage._compat import StringIO


def test_build_vim_profile_args(devnull, tmpdir):
    from covimerage.utils import build_vim_profile_args

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
    from covimerage.utils import get_fname_and_fobj_and_str

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
    assert is_executable_filename('minimal.vimrc')
    assert is_executable_filename('another-minimal.vimrc')
    assert is_executable_filename('another.minimal.vimrc')
    assert is_executable_filename('foo.bar.vim')

    assert not is_executable_filename('.hidden.vim')
    assert not is_executable_filename('foo.txt')
    assert not is_executable_filename('vim')
