import logging
import textwrap

import coverage
import pytest

from covimerage._compat import FileNotFoundError, StringIO


def test_main_import():
    from covimerage import __main__  # noqa: F401


def test_profile_repr_lines():
    from covimerage import Line, Profile, Script

    with pytest.raises(TypeError):
        Profile()

    p = Profile('profile-path')
    s = Script('script-path')
    p.scripts.append(s)
    assert repr(p.lines) == '{%r: {}}' % s
    assert repr(s) == "Script(path='script-path', sourced_count=None)"

    line = Line('line1')
    s.lines[1] = line
    assert repr(p.lines) == ('{%r: {1: %r}}' % (s, line))


def test_profile_fname_or_fobj(caplog, devnull):
    from covimerage import Profile

    with pytest.raises(FileNotFoundError) as excinfo:
        Profile('/does/not/exist').parse()
    assert str(excinfo.value) == \
        "[Errno 2] No such file or directory: '/does/not/exist'"

    with caplog.at_level(logging.DEBUG, logger='covimerage'):
        Profile(devnull).parse()
    msgs = [(r.levelname, r.message) for r in caplog.records]
    assert msgs == [('DEBUG', 'Parsing file: /dev/null')]

    fileobj = StringIO('')
    with caplog.at_level(logging.DEBUG, logger='covimerage'):
        Profile(fileobj).parse()
    msgs = [(r.levelname, r.message) for r in caplog.records]
    assert msgs[-1] == ('DEBUG', 'Parsing file: %s' % fileobj)
    assert len(msgs) == 2


def test_parse_count_and_times():
    from covimerage import parse_count_and_times

    f = parse_count_and_times
    assert f('    1              0.000035   Foo') == (1, None, 0.000035)
    assert f('    1   0.000037             Foo') == (1, 0.000037, None)
    assert f('') == (0, None, None)


def test_line():
    from covimerage import Line

    line = '    1              0.000005 Foo'
    assert repr(Line(line)) == 'Line(line=%r, count=None, total_time=None, self_time=None)' % (
        line)


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
    s = p.scripts[0]
    assert not s.lines
    assert len(s.lines) == 0
    assert s.sourced_count == 1
    msgs = [(r.name, r.levelname) for r in caplog.records]
    assert msgs == [('covimerage', 'WARNING')]
    assert caplog.records[0].message.startswith(
         "Could not parse count/times (fake:7, 'Cannot open file!'): ")
    assert 'ValueError' in caplog.records[0].message


def test_find_func_in_source():
    from covimerage import Function, Profile, Script

    s = Script('fake')
    s.parse_function(1, 'fun! <SID>Python_jump(mode, motion, flags) range')
    s.parse_function(2, 'fu g:Foo()')
    s.parse_function(3, 'fun\tsome#autoload()')
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

    fname = 'tests/fixtures/dict_function_with_same_source.profile'
    with caplog.at_level(logging.DEBUG, logger='covimerage'):
        p = Profile(fname)
        p.parse()

    assert len(p.scripts) == 1

    script_fname = 'tests/test_plugin/dict_function_with_same_source.vim'
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
        (N, '  endif'),
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
    assert 'Found multiple sources for anonymous function 1 (tests/test_plugin/dict_function_with_same_source.vim:3, tests/test_plugin/dict_function_with_same_source.vim:12).' in msgs
    assert 'Found multiple sources for anonymous function 2 (tests/test_plugin/dict_function_with_same_source.vim:3, tests/test_plugin/dict_function_with_same_source.vim:12).' in msgs
    assert 'Found already mapped dict function again (tests/test_plugin/dict_function_with_same_source.vim:3).' in msgs


def test_profile_parse_dict_function_with_continued_lines():
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
        (2, '          \\ a:arg'),
        (2, '          \\ .\'.\''),
        (2, '  else'),
        (1, '    echom a:arg'),
        (1, '  endif'),
        (N, 'endfunction'),
        (N, ''),
        (1, 'call obj.dict_function(0)'),
        (1, 'call obj.dict_function(1)'),
        (1, 'call obj.dict_function(1)')]


def test_profile_continued_lines():
    from covimerage import Profile

    fname = 'tests/fixtures/continued_lines.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    assert [(l.count, l.line) for l in s.lines.values()] == [
        (1, 'echom 1'),
        (1, 'echom 2'),
        (1, '      \\ 3'),
        (1, 'echom 4'),
        (1, '      \\ 5'),
    ]


def test_conditional_functions():
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
        (1, '    echom 1'),
        (N, '  endfunction'),
        (1, 'else'),
        (N, '  function Bar()'),
        (N, '    echom 1'),
        (N, '  endfunction'),
        (N, 'endif'),
        (N, ''),
        (1, 'call Bar()')]


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


def test_mergedprofiles_fixes_line_count():
    """Ref: https://github.com/vim/vim/issues/2103"""
    from covimerage import MergedProfiles, Profile

    profile = textwrap.dedent("""
    SCRIPT  /path/to/t.vim
    Sourced 1 time
    Total time:   0.000009
     Self time:   0.000009

    count  total (s)   self (s)
                                let foo = 1
        1              0.000002 let bar = 2
    """)

    p = Profile(StringIO(profile))
    p.parse()

    script = p.scripts[0]

    assert [(l.count, l.line) for l in script.lines.values()] == [
        (None, 'let foo = 1'),
        (1, 'let bar = 2'),
    ]

    m = MergedProfiles([p])
    assert [(l.count, l.line) for l in m.lines[script.path].values()] == [
        (1, 'let foo = 1'),
        (1, 'let bar = 2'),
    ]


def test_merged_profiles_get_coveragepy_data():
    from covimerage import MergedProfiles

    m = MergedProfiles([])
    cov_data = m.get_coveragepy_data()
    try:
        from coverage.data import CoverageJsonData
    except ImportError:
        assert isinstance(cov_data, coverage.CoverageData)
    else:
        assert isinstance(cov_data, CoverageJsonData)


def test_merged_profiles_write_coveragepy_data_handles_fname_and_fobj(
        mocker, caplog):
    from covimerage import MergedProfiles

    m = MergedProfiles([])
    mocked_data = mocker.Mock()
    mocker.patch.object(m, 'get_coveragepy_data', return_value=mocked_data)

    m.write_coveragepy_data()
    assert mocked_data.write_file.call_args_list == [mocker.call('.coverage')]
    assert mocked_data.write_fileobj.call_args_list == []

    mocked_data.reset_mock()
    fileobj = StringIO()
    m.write_coveragepy_data(data_file=fileobj)
    assert mocked_data.write_file.call_args_list == []
    assert mocked_data.write_fileobj.call_args_list == [mocker.call(fileobj)]
    msgs = [r.message for r in caplog.records]
    assert msgs == [
        'Writing coverage file .coverage.',
        'Writing coverage file %s.' % fileobj]


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


def test_function_in_function():
    from covimerage import Profile

    fname = 'tests/fixtures/function_in_function.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    assert [(l.count, l.line) for l in s.lines.values()] == [
        (None, '" Test for dict function in function.'),
        (None, ''),
        (1, 'function! GetObj()'),
        (1, '  let obj = {}'),
        (1, '  function obj.func()'),
        (1, '    return 1'),
        (None, '  endfunction'),
        (1, '  return obj'),
        (None, 'endfunction'),
        (None, ''),
        (1, 'let obj = GetObj()'),
        (1, 'call obj.func()')]


def test_function_in_function_count(caplog):
    from covimerage import Profile

    fname = 'tests/fixtures/function_in_function_count.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    assert [(l.count, l.line) for l in s.lines.values()] == [
        (None, '" Test for line count with inner functions.'),
        (1, 'function! Outer()'),
        (None, '  " comment1'),
        (1, '  function! Inner()'),
        (None, '    " comment2'),
        (None, '  endfunction'),
        (None, 'endfunction'),
        (1, 'call Outer()')]
    assert not caplog.records


def test_function_in_function_with_ref(caplog):
    from covimerage import Profile

    fname = 'tests/fixtures/function_in_function_with_ref.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    assert [(l.count, l.line) for l in s.lines.values()
            if not l.line.startswith('"')] == [
        (None, ''),
        (1, 'let g:refs = []'),
        (None, ''),
        (1, 'function! Outer()'),
        (1, '  function! GetObj()'),
        (1, '    let obj = {}'),
        (1, '    function obj.func()'),
        (1, '      return 1'),
        (None, '    endfunction'),
        (1, '    return obj'),
        (None, '  endfunction'),
        (None, ''),
        (1, '  let obj = GetObj()'),
        (1, '  call obj.func()'),
        (None, ''),
        (1, '  let g:refs += [obj]'),
        (None, 'endfunction'),
        (1, 'call Outer()')]

    assert not caplog.records


def test_map_functions(caplog):
    from covimerage import Function, Profile

    p = Profile('fake')

    p.map_functions([])
    assert not caplog.records

    funcs = [Function(name='missing')]
    p.map_functions(funcs)
    assert len(funcs) == 1
    assert caplog.record_tuples == [
        ('covimerage', 40, 'Could not find source for function: missing')]


def test_duplicate_s_function(caplog):
    from covimerage import Profile

    fname = 'tests/fixtures/duplicate_s_function.profile'
    p = Profile(fname)
    p.parse()

    assert len(p.scripts) == 2

    N = None
    assert [(l.count, l.line)
            for l in p.scripts[0].lines.values()
            if not l.line.startswith('"')] == [
                (1, 'function! s:function(name) abort'),
                (1, '  echom a:name'),
                (N, 'endfunction'),
                (N, ''),
                (1, "call s:function('name')"),
                (1, "call test_plugin#function#function('name')"),
            ]

    assert [(l.count, l.line)
            for l in p.scripts[1].lines.values()
            if not l.line.startswith('"')] == [
                (1, 'function! s:function(name) abort'),
                (1, '  echom a:name'),
                (N, 'endfunction'),
                (N, ''),
                (1, 'function! test_plugin#function#function(name) abort'),
                (1, '  call s:function(a:name)'),
                (N, 'endfunction')]

    assert not caplog.records


@pytest.mark.parametrize("defined_lnum", (-1, 1))
@pytest.mark.parametrize("defined_format", ("old", "new"))
@pytest.mark.parametrize("platform", ("linux", "win32"))
def test_handles_unmatched_defined(platform, defined_format, defined_lnum, caplog):
    from covimerage import Profile

    if platform == "win32":
        script = "C:\\invalid_defined.vim"
    else:
        script = "/invalid_defined.vim"
    defined = "Defined: " + script
    if defined_format == "old":
        defined += " line " + str(defined_lnum)
    else:
        defined += ":" + str(defined_lnum)

    file_object = StringIO(textwrap.dedent(
        """
        SCRIPT  {script}
        Sourced 1 time
        Total time:   0.000037
         Self time:   0.000032

        count  total (s)   self (s)
            1              0.000015 execute "function! F_via_execute_1()\\nreturn 0\\nendfunction"
            1   0.000011   0.000007 call F_via_execute_1()
            1   0.000006   0.000005 call F_via_execute_1()

        FUNCTION  F_via_execute_1()
            {defined}
        Called 2 times
        Total time:   0.000005
         Self time:   0.000005

        count  total (s)   self (s)
            2              0.000003 return 0

        FUNCTIONS SORTED ON TOTAL TIME
        count  total (s)   self (s)  function
            2   0.000005             F_via_execute_1()

        FUNCTIONS SORTED ON SELF TIME
        count  total (s)   self (s)  function
            2              0.000005  F_via_execute_1()
        """.format(
            script=script,
            defined=defined
        )))

    p = Profile(file_object)
    p.parse()

    assert len(p.scripts) == 1
    s = p.scripts[0]

    assert [(l.count, l.line) for l in s.lines.values()
            if not l.line.startswith('"')] == [
        (1, 'execute "function! F_via_execute_1()\\nreturn 0\\nendfunction"'),
        (1, 'call F_via_execute_1()'),
        (1, 'call F_via_execute_1()'),
    ]

    logmsgs = [x[1:] for x in caplog.record_tuples]
    if defined_lnum == -1:
        assert logmsgs == [
            (30, "Could not find script line for function F_via_execute_1 (-1, 1)"),
            (40, "Could not find source for function: F_via_execute_1"),
        ]
    else:
        assert defined_lnum == 1
        assert logmsgs == [
            (30, "Script line does not match function line, ignoring: 'call F_via_execute_1()' != 'return 0'."),
            (40, "Could not find source for function: F_via_execute_1"),
        ]
