try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import logging

import coverage
import pytest


def test_main_import():
    from covimerage import __main__  # noqa: F401


def test_profile_repr_lines():
    from covimerage import Line, Profile, Script

    p = Profile('profile-path')
    s = Script('script-path')
    p.scripts.append(s)
    assert repr(p.lines) == "{Script(path='script-path'): {}}"

    l = Line('line1')
    s.lines[1] = l
    assert repr(p.lines) == ("{Script(path='script-path'): {1: %r}}" % l)


def test_parse_count_and_times():
    from covimerage import parse_count_and_times

    f = parse_count_and_times
    assert f('    1              0.000035   Foo') == (1, None, 0.000035)
    assert f('    1   0.000037             Foo') == (1, 0.000037, None)
    assert f('') == (0, None, None)


@pytest.mark.xfail
def test_line():
    from covimerage import Line

    l = Line('    1              0.000005 Foo')

    # https://github.com/python-attrs/attrs/issues/245
    assert repr(l) == "Line(line='    1              0.000005 Foo', counts=1, total_time=None, self_time=None)"  # noqa


def test_profile_parse():
    from covimerage import Line, Profile

    fname = 'tests/fixtures/test_plugin.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1

    script_fname = '/test_plugin/autoload/test_plugin.vim'
    # assert script_fname in p.scripts
    s = p.scripts[0]
    assert s.path == script_fname

    assert len(s.lines) == 8
    assert s.lines == {
        1: Line(line='function! test_plugin#func1(a) abort', count=None,
                total_time=None, self_time=None),
        2: Line(line="  echom 'func1'", count=1, total_time=None,
                self_time=3.5e-05),
        3: Line(line='endfunction', count=None, total_time=None,
                self_time=None),
        4: Line(line='', count=None, total_time=None, self_time=None),
        5: Line(line='function! test_plugin#func2(a) abort', count=1,
                total_time=None, self_time=5e-06),
        6: Line(line="  echom 'func2'", count=0, total_time=None,
                self_time=None),
        7: Line(line='endfunction', count=None, total_time=None,
                self_time=None),
        8: Line(line='', count=None, total_time=None, self_time=None)}


def test_profile_parse_handles_cannot_open_file(caplog):
    from covimerage import Profile

    file_object = StringIO('\n'.join([
        'SCRIPT  /tmp/nvimDG3tAV/801',
        'Sourced 1 time',
        'Total time:   0.046577',
        ' Self time:   0.000136',
        '',
        'count  total (s)   self (s)',
        'Cannot open file!',
    ]))
    p = Profile('fake')
    p._parse(file_object)

    assert len(p.scripts) == 1
    assert len(p.scripts[0].lines) == 0
    msgs = [r.message for r in caplog.records]
    assert msgs == [
        'Could not parse count/times from line: Cannot open file! (fake:7).']


def test_find_func_in_source():
    from covimerage import Function, Profile, Script

    s = Script('fake')
    s.parse_script_line(1, 'fun! <SID>Python_jump(mode, motion, flags) range')
    s.parse_script_line(2, 'fu g:Foo()')
    s.parse_script_line(3, 'fun\tsome#autoload()')
    p = Profile('fake', scripts=[s])

    f = p.find_func_in_source

    assert f(Function(name='<SNR>247_Python_jump')) == (s, 1)
    assert f(Function(name='Foo')) == (s, 2)
    assert f(Function(name='some#autoload')) == (s, 3)


def test_profile_parse_dict_function():
    from covimerage import Profile

    fname = 'tests/fixtures/dict_function.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1

    script_fname = '/test_plugin/dict_function.vim'
    # assert script_fname in p.scripts
    s = p.scripts[0]
    assert s.path == script_fname

    assert s.dict_functions == {3}
    assert s.mapped_dict_functions == {3}

    assert len(s.lines) == 13
    assert [l.line for l in s.lines.values()] == [
        '" Test parsing of dict function.',
        'let obj = {}',
        'function! obj.dict_function(arg) abort',
        '  if a:arg',
        '    echom a:arg',
        '  else',
        '    echom a:arg',
        '  endif',
        'endfunction',
        '',
        'call obj.dict_function(0)',
        'call obj.dict_function(1)',
        'call obj.dict_function(2)',
    ]

    assert s.lines[4].count == 3
    assert s.lines[5].count == 2


def test_profile_parse_dict_function_with_same_source(caplog):
    from covimerage import Profile

    caplog.set_level(logging.NOTSET, logger='covimerage')
    fname = 'tests/fixtures/dict_function_with_same_source.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1

    script_fname = '/test_plugin/dict_function_with_same_source.vim'
    s = p.scripts[0]
    assert s.path == script_fname

    assert s.dict_functions == {3, 12}
    assert s.mapped_dict_functions == {3, 12}

    N = None
    assert [(l.count, l.line) for l in s.lines.values()] == [
        (N, '" Test parsing of dict function (with same source).'),
        (1, 'let obj1 = {}'),
        (1, 'function! obj1.dict_function(arg) abort'),
        (1, '  if a:arg'),
        (1, '    echom a:arg'),
        (1, '  else'),
        (0, '    echom a:arg'),
        (0, '  endif'),
        (N, 'endfunction'),
        (N, ''),
        (1, 'let obj2 = {}'),
        (1, 'function! obj2.dict_function(arg) abort'),
        (3, '  if a:arg'),
        (2, '    echom a:arg'),
        (2, '  else'),
        (1, '    echom a:arg'),
        (1, '  endif'),
        (N, 'endfunction'),
        (N, ''),
        (1, 'call obj2.dict_function(0)'),
        (1, 'call obj2.dict_function(1)'),
        (1, 'call obj2.dict_function(2)'),
        (1, 'call obj1.dict_function(3)')]

    msgs = [r.message for r in caplog.records]
    assert "Found multiple sources for anonymous function 1 (/test_plugin/dict_function_with_same_source.vim:3, /test_plugin/dict_function_with_same_source.vim:12)." in msgs  # noqa
    assert "Found multiple sources for anonymous function 2 (/test_plugin/dict_function_with_same_source.vim:3, /test_plugin/dict_function_with_same_source.vim:12)." in msgs  # noqa
    assert "Found already mapped dict function again (/test_plugin/dict_function_with_same_source.vim:3)." in msgs  # noqa


def test_profile_parse_dict_function_with_continued_lines(caplog):
    from covimerage import Profile

    fname = 'tests/fixtures/dict_function_with_continued_lines.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    assert s.dict_functions == {3}
    assert s.mapped_dict_functions == {3}

    N = None
    assert [(l.count, l.line) for l in s.lines.values()] == [
        (N, '" Test parsing of dict function with continued lines.'),
        (1, 'let obj = {}'),
        (1, 'function! obj.dict_function(arg) abort'),
        (3, '  if a:arg'),
        (2, '    echom'),
        (N, '          \\ a:arg'),
        (2, '  else'),
        (1, '    echom a:arg'),
        (1, '  endif'),
        (N, 'endfunction'),
        (N, ''),
        (1, 'call obj.dict_function(0)'),
        (1, 'call obj.dict_function(1)'),
        (1, 'call obj.dict_function(1)')]


def test_profile_continued_lines(caplog):
    from covimerage import Profile

    fname = 'tests/fixtures/continued_lines.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    N = None
    assert [(l.count, l.line) for l in s.lines.values()] == [
        (N, 'echom 1'),
        (1, 'echom 2'),
        (N, '      \\ 3'),
        (1, 'echom 4')]


def test_conditional_functions(caplog):
    from covimerage import Profile

    fname = 'tests/fixtures/conditional_function.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    N = None
    assert [(l.count, l.line) for l in s.lines.values()] == [
        (N, '" Test for detection of conditional functions.'),
        (N, ''),
        (1, 'if 0'),
        (N, '  function Foo()'),
        (N, '    return 1'),
        (N, '  endfunction'),
        (N, 'else'),
        (1, '  function Foo()'),
        (1, '    return 1'),
        (N, '  endfunction'),
        (1, 'endif'),
        (N, ''),
        (1, 'if Foo()'),
        (1, '  function Bar()'),
        (0, '    echom 1'),
        (N, '  endfunction'),
        (1, 'else'),
        (N, '  function Bar()'),
        (N, '    echom 1'),
        (N, '  endfunction'),
        (N, 'endif'),
        (N, ''),
        (1, 'Bar()')]


def test_merged_profiles():
    from covimerage import MergedProfiles, Profile

    p1 = Profile('tests/fixtures/merge-1.profile')
    p1.parse()
    p2 = Profile('tests/fixtures/merge-2.profile')
    p2.parse()
    assert p1.scriptfiles == p2.scriptfiles

    m = MergedProfiles([p1, p2])

    assert list(m.scripts) == p1.scripts + p2.scripts
    assert m.scriptfiles == p1.scriptfiles

    N = None
    s_fname = '/test_plugin/merged_profiles.vim'
    assert [(l.count, l.line) for lnum, l in m.lines[s_fname].items()] == [
        (N, '" Generate profile output for merged profiles.'),
        (N, '" Used merged_profiles-init.vim'),
        (2, "if !exists('s:conditional')"),
        (1, '  function! F()'),
        (1, '    echom 1'),
        (N, '  endfunction'),
        (1, '  let s:conditional = 1'),
        (1, '  echom 1'),
        (1, '  call F()'),
        (N, '  call NeomakeTestsProfileRestart()'),
        (N, "  exe 'source ' . expand('<sfile>')"),
        (1, 'else'),
        (1, '  function! F()'),
        (1, '    echom 2'),
        (N, '  endfunction'),
        (1, '  echom 2'),
        (1, '  call F()'),
        (1, 'endif'),
        (N, '')]


def test_merged_profiles_get_coveragepy_data():
    from covimerage import MergedProfiles

    m = MergedProfiles([])
    cov_data = m.get_coveragepy_data()
    assert isinstance(cov_data, coverage.CoverageData)
    assert repr(cov_data) == '<CoverageData lines={0} arcs=None tracers={0} runs=[0]>'  # noqa: E501


def test_merged_profiles_write_coveragepy_data_handles_fname_and_fobj(mocker):
    from covimerage import MergedProfiles

    m = MergedProfiles([])
    mocked_data = mocker.Mock()
    mocker.patch.object(m, 'get_coveragepy_data', return_value=mocked_data)

    m.write_coveragepy_data()
    mocked_data.write_file.call_args_list == [mocker.call('.coverage')]
    mocked_data.write_fileobj.call_args_list == []

    mocked_data.reset_mock()
    fileobj = StringIO()
    m.write_coveragepy_data(data_file=fileobj)
    mocked_data.write_file.call_args_list == []
    mocked_data.write_fileobj.call_args_list == [mocker.call(fileobj)]


def test_mergedprofiles_caches_coveragepy_data(mocker):
    from covimerage import MergedProfiles, Profile

    m = MergedProfiles([])
    spy = mocker.spy(m, '_get_coveragepy_data')

    m.get_coveragepy_data()
    assert spy.call_count == 1
    m.get_coveragepy_data()
    assert spy.call_count == 1

    m.profiles += [Profile('foo')]
    m.get_coveragepy_data()
    assert spy.call_count == 2

    m.profiles = [Profile('bar')]
    m.get_coveragepy_data()
    assert spy.call_count == 3
