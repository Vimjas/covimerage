try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
from subprocess import call
import sys

import pytest

from covimerage import DEFAULT_COVERAGE_DATA_FILE, cli
from covimerage.__version__ import __version__


def test_dunder_main_run(capfd):
    assert call([sys.executable, '-m', 'covimerage']) == 0
    out, err = capfd.readouterr()
    assert out.startswith('Usage: __main__')


def test_dunder_main_run_help(capfd):
    assert call([sys.executable, '-m', 'covimerage', '--version']) == 0
    out, err = capfd.readouterr()
    assert out == 'covimerage, version %s\n' % __version__


def test_cli(runner, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        with pytest.raises(SystemExit) as excinfo:
            cli.write_coverage([os.path.join(
                str(old_dir), 'tests/fixtures/conditional_function.profile')])
        assert excinfo.value.code == 0
        assert os.path.exists(DEFAULT_COVERAGE_DATA_FILE)

    result = runner.invoke(cli.main, ['write_coverage', '/does/not/exist'])
    assert result.output.splitlines()[-1].startswith(
        'Error: Invalid value for "profile_file": Could not open file:')
    assert result.exit_code == 2


@pytest.mark.parametrize('arg', ('-V', '--version'))
def test_cli_version(arg, runner):
    result = runner.invoke(cli.main, [arg])
    assert result.output == 'covimerage, version %s\n' % __version__
    assert result.exit_code == 0


@pytest.mark.parametrize('arg', ('-h', '--help'))
def test_cli_help(arg, runner):
    result = runner.invoke(cli.main, [arg])
    assert result.output.startswith('Usage:')
    assert result.exit_code == 0

    result = runner.invoke(cli.main, ['write_coverage', arg])
    assert result.output.startswith('Usage:')
    assert result.exit_code == 0


def test_cli_run_with_args_fd(capfd):
    ret = call(['covimerage', 'run', '--profile-file', '/doesnotexist',
                'echo', '--', '--no-profile', '%sMARKER'])
    out, err = capfd.readouterr()
    lines = err.splitlines()
    assert lines == [
    "Running cmd: ['echo', '--', '--no-profile', '%sMARKER', '--cmd', 'profile start /doesnotexist', '--cmd', 'profile! file ./*']",  # noqa: E501
        'Error: The profile file (/doesnotexist) has not been created.']
    assert ret == 1


def test_cli_run_subprocess_exception(runner, mocker):
    result = runner.invoke(cli.run, [os.devnull])
    out = result.output.splitlines()
    assert out[-1].startswith("Error: Failed to run ['/dev/null', '--cmd',")
    assert out[-1].endswith("']: [Errno 13] Permission denied")
    assert result.exit_code == 1


def test_cli_run_args(runner, mocker, devnull, tmpdir):
    m = mocker.patch('subprocess.call')
    m.return_value = 1
    result = runner.invoke(
        cli.run, ['--no-wrap-profile', 'printf', '--headless'])
    assert m.call_args[0] == (['printf', '--headless'],)
    assert result.output.splitlines() == [
        "Running cmd: ['printf', '--headless']",
        'Error: Command exited non-zero: 1.']
    assert result.exit_code == 1

    m.return_value = 2
    result = runner.invoke(
        cli.run, ['--no-wrap-profile', '--', 'printf', '--headless'])
    assert m.call_args[0] == (['printf', '--headless'],)
    assert result.output.splitlines() == [
        "Running cmd: ['printf', '--headless']",
        'Error: Command exited non-zero: 2.']
    assert result.exit_code == 2

    m.return_value = 3
    result = runner.invoke(
        cli.run, ['--no-wrap-profile', 'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        "Running cmd: ['printf', '--', '--headless']",
        'Error: Command exited non-zero: 3.']
    assert result.exit_code == 3

    result = runner.invoke(cli.run, [
        '--no-wrap-profile', '--no-report', '--profile-file', devnull,
        '--no-write-data', 'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        "Running cmd: ['printf', '--', '--headless']",
        'Error: Command exited non-zero: 3.']

    result = runner.invoke(cli.run, [
        '--no-wrap-profile', '--no-report', '--profile-file', devnull,
        '--source', devnull.name,
        '--write-data', 'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        "Running cmd: ['printf', '--', '--headless']",
        'Parsing profile file /dev/null.',
        'Not writing coverage file: no data to report!',
        'Error: Command exited non-zero: 3.']

    # Write data with non-sources only.
    f = StringIO()
    m.return_value = 0
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        result = runner.invoke(cli.run, [
            '--no-wrap-profile', '--no-report',
            '--profile-file', profile_file,
            '--write-data', '--data-file', f,
            'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    out = result.output.splitlines()
    assert out == [
        "Running cmd: ['printf', '--', '--headless']",
        'Parsing profile file %s.' % profile_file,
        'Ignoring non-source: %s' % str(tmpdir.join(
            'tests/test_plugin/conditional_function.vim')),
        'Not writing coverage file: no data to report!']
    f.seek(0)
    assert f.read() == ''

    profiled_file = 'tests/test_plugin/conditional_function.vim'
    profiled_file_content = open(
        'tests/test_plugin/conditional_function.vim', 'r').read()
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        tmpdir.join('not-profiled.vim').write('')
        tmpdir.join('not-a-vim-file').write('')
        result = runner.invoke(cli.run, [
            '--no-wrap-profile', '--no-report',
            '--profile-file', profile_file,
            '--write-data', '--data-file', f,
            'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        "Running cmd: ['printf', '--', '--headless']",
        'Parsing profile file %s.' % profile_file,
        'Writing coverage file %r.' % f]
    f.seek(0)

    m.exit_code == 0
    from covimerage.coveragepy import CoverageWrapper
    cov = CoverageWrapper(data_file=f)
    expected = {
        str(tmpdir.join('not-profiled.vim')): [],
        str(tmpdir.join('tests/test_plugin/conditional_function.vim')): [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}
    assert cov.lines == expected


def test_cli_run_report_fd(capfd, tmpdir):
    profile_fname = 'tests/fixtures/conditional_function.profile'
    with open(profile_fname, 'r') as f:
        profile_lines = f.readlines()
    profile_lines[0] = 'SCRIPT  tests/test_plugin/conditional_function.vim\n'

    tmp_profile_fname = str(tmpdir.join('tmp.profile'))
    with open(tmp_profile_fname, 'w') as f:
        f.writelines(profile_lines)
    data_file = str(tmpdir.join('datafile'))
    args = ['--no-wrap-profile', '--profile-file', tmp_profile_fname,
            '--source', 'tests/test_plugin/conditional_function.vim',
            '--data-file', data_file, 'true']
    exit_code = call(['covimerage', 'run'] + args)
    out, err = capfd.readouterr()
    assert exit_code == 0, err
    assert out.splitlines() == [
        'Name                                         Stmts   Miss  Cover',
        '----------------------------------------------------------------',
        'tests/test_plugin/conditional_function.vim      13      5    62%']
    assert err.splitlines() == [
        "Running cmd: ['true']",
        'Parsing profile file %s.' % tmp_profile_fname,
        'Writing coverage file %s.' % data_file]

    # Same, but to some file.
    ofname = str(tmpdir.join('ofname'))
    exit_code = call(['covimerage', 'run', '--report-file', ofname] + args)
    out, err = capfd.readouterr()
    assert exit_code == 0, err
    assert out == ''
    assert err.splitlines() == [
        "Running cmd: ['true']",
        'Parsing profile file %s.' % tmp_profile_fname,
        'Writing coverage file %s.' % data_file]
    assert open(ofname).read().splitlines() == [
        'Name                                         Stmts   Miss  Cover',
        '----------------------------------------------------------------',
        'tests/test_plugin/conditional_function.vim      13      5    62%']


def test_cli_call(capfd):
    assert call(['covimerage', '--version']) == 0
    out, err = capfd.readouterr()
    assert out == 'covimerage, version %s\n' % __version__

    assert call(['covimerage', '--help']) == 0
    out, err = capfd.readouterr()
    assert out.startswith('Usage:')

    assert call(['covimerage', 'file not found']) == 2
    out, err = capfd.readouterr()
    err_lines = err.splitlines()
    assert err_lines[0] == 'Usage: covimerage [OPTIONS] COMMAND [ARGS]...'
    # click after 6.7 (9cfea14) includes: 'Try "covimerage --help" for help.'
    assert err_lines[-2:] == [
        '',
        'Error: No such command "file not found".']
    assert out == ''

    assert call(['covimerage', 'write_coverage', 'file not found']) == 2
    out, err = capfd.readouterr()
    err_lines = err.splitlines()
    assert err_lines[-1] == (
        'Error: Invalid value for "profile_file": Could not open file: file not found: No such file or directory')  # noqa: E501
    assert out == ''


def test_cli_call_verbosity_fd(capfd):
    assert call(['covimerage', 'write_coverage', os.devnull]) == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert err.splitlines() == [
        'Not writing coverage file: no data to report!',
        'Error: No data to report.']

    assert call(['covimerage', '-v', 'write_coverage', os.devnull]) == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert err.splitlines() == [
        'Parsing file: /dev/null',
        'source_files: []',
        'Not writing coverage file: no data to report!',
        'Error: No data to report.']

    assert call(['covimerage', '-vvvv', 'write_coverage', os.devnull]) == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert err.splitlines() == [
        'Parsing file: /dev/null',
        'source_files: []',
        'Not writing coverage file: no data to report!',
        'Error: No data to report.']

    assert call(['covimerage', '-vq', 'write_coverage', os.devnull]) == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert err.splitlines() == [
        'Not writing coverage file: no data to report!',
        'Error: No data to report.']

    assert call(['covimerage', '-qq', 'write_coverage', os.devnull]) == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert err == 'Error: No data to report.\n'


def test_cli_writecoverage_without_data(runner):
    result = runner.invoke(cli.main, ['write_coverage', os.devnull])
    assert result.output == '\n'.join([
        'Not writing coverage file: no data to report!',
        'Error: No data to report.',
        ''])
    assert result.exit_code == 1


def test_cli_writecoverage_datafile(runner):
    from covimerage.coveragepy import CoverageWrapper

    f = StringIO()
    result = runner.invoke(cli.main, ['write_coverage', '--data-file', f,
                           'tests/fixtures/conditional_function.profile'])
    assert result.output == '\n'.join([
        'Writing coverage file %s.' % f,
        ''])
    assert result.exit_code == 0

    f.seek(0)
    cov = CoverageWrapper(data_file=f)
    assert cov.lines == {
        os.path.abspath('tests/test_plugin/conditional_function.vim'): [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}


def test_cli_writecoverage_source(runner):
    from covimerage.coveragepy import CoverageWrapper

    f = StringIO()
    result = runner.invoke(cli.main, [
        'write_coverage', '--data-file', f, '--source', '.',
        'tests/fixtures/conditional_function.profile'])
    assert result.output == '\n'.join([
        'Writing coverage file %s.' % f,
        ''])
    assert result.exit_code == 0

    f.seek(0)
    cov = CoverageWrapper(data_file=f)
    assert cov.lines[
        os.path.abspath('tests/test_plugin/conditional_function.vim')] == [
            3, 8, 9, 11, 13, 14, 15, 17, 23]
    assert cov.lines[
        os.path.abspath('tests/test_plugin/autoload/test_plugin.vim')] == []


def test_coverage_plugin_for_annotate_merged_conditionals(runner, capfd,
                                                          tmpdir):
    tmpfile = str(tmpdir.join('.coverage'))
    result = runner.invoke(cli.main, [
        'write_coverage', '--data-file', tmpfile,
        'tests/fixtures/merged_conditionals-0.profile',
        'tests/fixtures/merged_conditionals-1.profile',
        'tests/fixtures/merged_conditionals-2.profile'])
    assert result.output == '\n'.join([
        'Writing coverage file %s.' % tmpfile,
        ''])
    assert result.exit_code == 0

    coveragerc = str(tmpdir.join('.coveragerc'))
    with open(coveragerc, 'w') as f:
        f.write('[run]\nplugins = covimerage')

    exit_code = call(['env', 'COVERAGE_FILE=%s' % tmpfile,
                      'coverage', 'annotate', '--rcfile', coveragerc,
                      '--directory', str(tmpdir)])
    out, err = capfd.readouterr()
    assert exit_code == 0, (err, out)
    ann_fname = 'tests_test_plugin_merged_conditionals_vim,cover'
    annotated_lines = tmpdir.join(ann_fname).read().splitlines()
    assert annotated_lines == [
        '> " Generate profile output for merged profiles.',
        "> let cond = get(g:, 'test_conditional', 0)",
        '  ',
        '> if cond == 1',
        '>   let foo = 1',
        '> elseif cond == 2',
        '>   let foo = 2',
        '> elseif cond == 3',
        '!   let foo = 3',
        '! else',
        ">   let foo = 'else'",
        '> endif',
        '  ',
        '> function F(...)',
        '>   if a:1 == 1',
        '>     let foo = 1',
        '>   elseif a:1 == 2',
        '>     let foo = 2',
        '>   elseif a:1 == 3',
        '!     let foo = 3',
        '!   else',
        ">     let foo = 'else'",
        '>   endif',
        '> endfunction',
        '  ',
        '> call F(cond)',
    ]


def test_report_profile_or_data_file(runner, tmpdir):
    from covimerage.cli import DEFAULT_COVERAGE_DATA_FILE

    result = runner.invoke(cli.main, [
        'report', '--data-file', '/does/not/exist'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "--data-file": Could not open file: /does/not/exist: No such file or directory'  # noqa: E501
    assert result.exit_code == 2

    result = runner.invoke(cli.main, [
        'report', '--data-file', os.devnull])
    cov_exc = 'CoverageException("Doesn\'t seem to be a coverage.py data file",)'  # noqa: E501
    assert result.output.splitlines()[-1] == \
        'Error: Coverage could not read data_file: /dev/null (%s)' % cov_exc
    assert result.exit_code == 1

    with tmpdir.as_cwd():
        result = runner.invoke(cli.main, ['report'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "--data-file": Could not open file: %s: No such file or directory' % DEFAULT_COVERAGE_DATA_FILE  # noqa: E501
    assert result.exit_code == 2

    result = runner.invoke(cli.main, ['report', '/does/not/exist'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "profile_file": Could not open file: /does/not/exist: No such file or directory'  # noqa: E501
    assert result.exit_code == 2

    result = runner.invoke(cli.main, [
        'report', 'tests/fixtures/merged_conditionals-0.profile'])
    assert result.output.splitlines() == [
        'Name                                        Stmts   Miss  Cover',
        '---------------------------------------------------------------',
        'tests/test_plugin/merged_conditionals.vim      19     12    37%']
    assert result.exit_code == 0


def test_report_source(runner, tmpdir, devnull):
    result = runner.invoke(cli.main, [
        'report', '--source', '.', '/does/not/exist'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "profile_file": Could not open file: /does/not/exist: No such file or directory'  # noqa: E501
    assert result.exit_code == 2

    result = runner.invoke(cli.main, [
        'report', '--source', '.', devnull.name])
    out = result.output.splitlines()
    assert any(l.startswith('tests/test_plugin/vimrc')  # pragma: no branch
               for l in out)
    testplugin_fname = 'tests/test_plugin/autoload/test_plugin.vim'
    assert any(testplugin_fname in l for l in out)  # pragma: no branch
    assert out[-1].startswith('TOTAL')
    assert out[-1].endswith(' 0%')
    assert result.exit_code == 0

    result = runner.invoke(cli.main, [
        'report', devnull.name, '--source', '.'])
    out = result.output.splitlines()
    assert any(testplugin_fname in l for l in out)  # pragma: no branch
    assert out[-1].startswith('TOTAL')
    assert out[-1].endswith(' 0%')
    assert result.exit_code == 0

    result = runner.invoke(cli.main, [
        'report', '--source', '.'])
    out = result.output.splitlines()
    assert out[-1] == 'Error: --source can only be used with PROFILE_FILE.'
    assert result.exit_code == 2

    result = runner.invoke(cli.main, [
        'report', '--source', 'tests/test_plugin/merged_conditionals.vim',
        'tests/fixtures/merged_conditionals-0.profile'])
    assert result.output.splitlines() == [
        'Name                                        Stmts   Miss  Cover',
        '---------------------------------------------------------------',
        'tests/test_plugin/merged_conditionals.vim      19     12    37%']
    assert result.exit_code == 0


def test_cli_xml(runner, tmpdir):
    """Smoke test for the xml command."""
    result = runner.invoke(cli.main, [
        'write_coverage', '--data-file', str(tmpdir.join('.coverage')),
        'tests/fixtures/merged_conditionals-0.profile'])
    with tmpdir.as_cwd():
        result = runner.invoke(cli.main, ['xml', '--data-file', '.coverage'])
        assert result.exit_code == 0

        with open('coverage.xml') as f:
            xml = f.read()
    assert 'filename="%s/tests/test_plugin/merged_conditionals.vim' % (
        os.getcwd()) in xml
