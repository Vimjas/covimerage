import os
import signal
import subprocess
from subprocess import call
import sys
import tempfile
import time

import click
import pytest

from covimerage import DEFAULT_COVERAGE_DATA_FILE, cli, get_version
from covimerage.cli import get_version_message


def test_dunder_main_run(capfd):
    assert call([sys.executable, '-m', 'covimerage']) == 0
    out, err = capfd.readouterr()
    assert out.startswith('Usage: __main__')


def test_dunder_main_run_help(capfd):
    assert call([sys.executable, '-m', 'covimerage', '--version']) == 0
    out, err = capfd.readouterr()
    lines = out.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith('covimerage, version %s' % get_version())


def test_cli_write_coverage(runner, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        with pytest.raises(SystemExit) as excinfo:
            cli.write_coverage([os.path.join(
                str(old_dir), 'tests/fixtures/conditional_function.profile')])
        assert excinfo.value.code == 0
        assert os.path.exists(DEFAULT_COVERAGE_DATA_FILE)

    result = runner.invoke(cli.main, ['write_coverage', '/does/not/exist'])
    if click.__version__ < '7.0':
        assert result.output.splitlines()[-1].startswith(
            'Error: Invalid value for "profile_file": Could not open file:')
    else:
        assert result.output.splitlines()[-1].startswith(
            'Error: Invalid value for "PROFILE_FILE...": Could not open file:')
    assert result.exit_code == 2

    result = runner.invoke(cli.main, ['write_coverage'])
    if click.__version__ < '7.0':
        expected = 'Error: Missing argument "profile_file".'
    else:
        expected = 'Error: Missing argument "PROFILE_FILE...".'
    assert result.output.splitlines()[-1] == expected
    assert result.exit_code == 2


@pytest.mark.parametrize('arg', ('-V', '--version'))
def test_cli_version(arg, runner):
    result = runner.invoke(cli.main, [arg])
    assert result.output == get_version_message() + '\n'
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
        "Running cmd: echo -- --no-profile %sMARKER --cmd 'profile start /doesnotexist' --cmd 'profile! file ./*' (in {})".format(os.getcwd()),
        'Error: The profile file (/doesnotexist) has not been created.']
    assert ret == 1


def test_cli_run_subprocess_exception(runner, mocker):
    result = runner.invoke(cli.run, [os.devnull])
    out = result.output.splitlines()
    assert out[-1].startswith("Error: Failed to run ['/dev/null', '--cmd',")
    assert '[Errno 13] Permission denied' in out[-1]
    assert result.exit_code == 1


def test_cli_run_args(runner, mocker, devnull, tmpdir):
    m = mocker.patch('subprocess.Popen')
    m_wait = m.return_value.wait

    m_wait.return_value = 1
    result = runner.invoke(
        cli.run, ['--no-wrap-profile', 'printf', '--headless'])
    assert m.call_args[0] == (['printf', '--headless'],)
    assert result.output.splitlines() == [
        'Running cmd: printf --headless (in %s)' % os.getcwd(),
        'Error: Command exited non-zero: 1.']
    assert result.exit_code == 1

    m_wait.return_value = 2
    result = runner.invoke(
        cli.run, ['--no-wrap-profile', '--', 'printf', '--headless'])
    assert m.call_args[0] == (['printf', '--headless'],)
    assert result.output.splitlines() == [
        'Running cmd: printf --headless (in %s)' % os.getcwd(),
        'Error: Command exited non-zero: 2.']
    assert result.exit_code == 2

    m_wait.return_value = 3
    result = runner.invoke(
        cli.run, ['--no-wrap-profile', 'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        'Running cmd: printf -- --headless (in %s)' % os.getcwd(),
        'Error: Command exited non-zero: 3.']
    assert result.exit_code == 3

    result = runner.invoke(cli.run, [
        '--no-wrap-profile', '--no-report', '--profile-file', devnull.name,
        '--no-write-data', 'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        'Running cmd: printf -- --headless (in %s)' % os.getcwd(),
        'Error: Command exited non-zero: 3.']

    result = runner.invoke(cli.run, [
        '--no-wrap-profile', '--no-report', '--profile-file', devnull.name,
        '--source', devnull.name,
        '--write-data', 'printf', '--', '--headless'])
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        'Running cmd: printf -- --headless (in %s)' % os.getcwd(),
        'Parsing profile file /dev/null.',
        'Not writing coverage file: no data to report!',
        'Error: Command exited non-zero: 3.']

    # Write data with non-sources only.
    m_wait.return_value = 0
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        result = runner.invoke(cli.run, [
            '--no-wrap-profile', '--no-report',
            '--profile-file', profile_file,
            '--write-data',
            'printf', '--', '--headless'])
        assert not os.path.exists(DEFAULT_COVERAGE_DATA_FILE)
    assert m.call_args[0] == (['printf', '--', '--headless'],)
    out = result.output.splitlines()
    assert out == [
        'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
        'Parsing profile file %s.' % profile_file,
        'Ignoring non-source: %s' % str(tmpdir.join(
            'tests/test_plugin/conditional_function.vim')),
        'Not writing coverage file: no data to report!']

    profiled_file = 'tests/test_plugin/conditional_function.vim'
    profiled_file_content = open(profiled_file, 'r').read()
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        tmpdir.join('not-profiled.vim').write('')
        tmpdir.join('not-a-vim-file').write('')
        result = runner.invoke(cli.run, [
            '--no-wrap-profile', '--no-report',
            '--profile-file', profile_file,
            '--write-data',
            'printf', '--', '--headless'])

        # Read coverage.
        from covimerage.coveragepy import CoverageWrapper
        cov = CoverageWrapper(data_file=DEFAULT_COVERAGE_DATA_FILE)

    assert m.call_args[0] == (['printf', '--', '--headless'],)
    assert result.output.splitlines() == [
        'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
        'Parsing profile file %s.' % profile_file,
        'Writing coverage file %s.' % DEFAULT_COVERAGE_DATA_FILE]
    assert result.exit_code == 0

    expected_cov_lines = {
        str(tmpdir.join('not-profiled.vim')): [],
        str(tmpdir.join('tests/test_plugin/conditional_function.vim')): [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}
    assert cov.lines == expected_cov_lines


def test_cli_run_subprocess_wait_exception(runner, mocker, devnull, tmpdir):
    mocker.patch('subprocess.Popen').return_value.wait.side_effect = Exception(
        'custom_err')

    result = runner.invoke(cli.run, ['--no-wrap-profile', 'true'])
    assert result.output.splitlines() == [
        'Running cmd: true (in %s)' % os.getcwd(),
        "Error: Failed to run ['true']: custom_err"]
    assert result.exit_code == 1


@pytest.mark.parametrize('with_append', (True, False))
def test_cli_run_can_skip_writing_data(with_append, runner, tmpdir):
    profiled_file = 'tests/test_plugin/conditional_function.vim'
    profiled_file_content = open(profiled_file, 'r').read()
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        args = ['--no-wrap-profile', '--profile-file', profile_file,
                '--no-write-data', 'printf', '--', '--headless']
        if with_append:
            args.insert(0, '--append')
        result = runner.invoke(cli.run, args)
    assert result.output.splitlines() == [
        'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
        'Parsing profile file %s.' % profile_file,
        'Name                                         Stmts   Miss  Cover',
        '----------------------------------------------------------------',
        'tests/test_plugin/conditional_function.vim      13      5    62%']
    assert not tmpdir.join(DEFAULT_COVERAGE_DATA_FILE).exists()


def test_cli_write_coverage_with_append(runner, tmpdir, covdata_header):
    profiled_file = 'tests/test_plugin/conditional_function.vim'
    profiled_file_content = open(profiled_file, 'r').read()
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        args = ['--append', profile_file]
        result = runner.invoke(cli.write_coverage, args)

        assert result.output.splitlines() == [
            'Writing coverage file .coverage_covimerage.',
        ]
        assert tmpdir.join(DEFAULT_COVERAGE_DATA_FILE).exists()

        data = open('.coverage_covimerage').read()
        assert data.startswith(covdata_header)

        # Not changed if appending the same.
        result = runner.invoke(cli.write_coverage, args)
        assert len(open('.coverage_covimerage').read()) == len(data)


def test_cli_run_report_fd(capfd, tmpdir, devnull):
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
    exit_code = call(['covimerage', '--rcfile', devnull.name, 'run'] + args)
    out, err = capfd.readouterr()
    assert exit_code == 0, err
    assert out.splitlines() == [
        'Name                                         Stmts   Miss  Cover',
        '----------------------------------------------------------------',
        'tests/test_plugin/conditional_function.vim      13      5    62%']
    assert err.splitlines() == [
        'Running cmd: true (in %s)' % str(os.getcwd()),
        'Parsing profile file %s.' % tmp_profile_fname,
        'Writing coverage file %s.' % data_file]

    # Same, but to some file.
    ofname = str(tmpdir.join('ofname'))
    exit_code = call(['covimerage', '--rcfile', devnull.name, 'run', '--report-file', ofname] + args)
    out, err = capfd.readouterr()
    assert exit_code == 0, err
    assert out == ''
    assert err.splitlines() == [
        'Running cmd: true (in %s)' % str(os.getcwd()),
        'Parsing profile file %s.' % tmp_profile_fname,
        'Writing coverage file %s.' % data_file]
    assert open(ofname).read().splitlines() == [
        'Name                                         Stmts   Miss  Cover',
        '----------------------------------------------------------------',
        'tests/test_plugin/conditional_function.vim      13      5    62%']


def test_cli_call(capfd):
    assert call(['covimerage', '--version']) == 0
    out, err = capfd.readouterr()
    assert out == get_version_message() + '\n'

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
        'Error: Invalid value for "%s": Could not open file: file not found: No such file or directory' % (
            "profile_file" if click.__version__ < '7.0' else "PROFILE_FILE...",))
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

    fname = tempfile.mktemp()
    result = runner.invoke(cli.main, ['write_coverage', '--data-file', fname,
                           'tests/fixtures/conditional_function.profile'])
    assert result.output == '\n'.join([
        'Writing coverage file %s.' % fname,
        ''])
    assert result.exit_code == 0

    cov = CoverageWrapper(data_file=fname)
    assert cov.lines == {
        os.path.abspath('tests/test_plugin/conditional_function.vim'): [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}


def test_cli_writecoverage_source(runner, devnull):
    from covimerage.coveragepy import CoverageWrapper

    fname = tempfile.mktemp()
    result = runner.invoke(cli.main, [
        'write_coverage', '--data-file', fname, '--source', '.',
        'tests/fixtures/conditional_function.profile'])
    assert result.output == '\n'.join([
        'Writing coverage file %s.' % fname,
        ''])
    assert result.exit_code == 0

    cov = CoverageWrapper(data_file=fname)
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

    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith('COV_') or k == 'PATH'
    }
    env.update({
        'COVERAGE_FILE': tmpfile,
        'COVERAGE_STORAGE': 'json',  # for coveragepy 5
    })
    exit_code = call([
        'coverage', 'annotate', '--rcfile', coveragerc, '--directory',
        str(tmpdir),
    ], env=env)
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


def test_report_missing_data_file(runner, tmpdir):
    from covimerage.cli import DEFAULT_COVERAGE_DATA_FILE

    with tmpdir.as_cwd():
        result = runner.invoke(cli.main, ['report'])
        assert result.output.splitlines()[-1] == \
            'Error: Invalid value for "--data-file": Could not open file: %s: No such file or directory' % (
                DEFAULT_COVERAGE_DATA_FILE)
        assert result.exit_code == 2


def test_report_profile_or_data_file(runner, tmpdir):
    from covimerage.cli import DEFAULT_COVERAGE_DATA_FILE

    result = runner.invoke(cli.main, [
        'report', '--data-file', '/does/not/exist'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "--data-file": Could not open file: /does/not/exist: No such file or directory'
    assert result.exit_code == 2

    result = runner.invoke(cli.main, [
        'report', '--data-file', os.devnull])
    cov_exc = 'CoverageException: Doesn\'t seem to be a coverage.py data file'
    assert result.output.splitlines()[-1] == \
        'Error: Coverage could not read data_file: /dev/null (%s)' % cov_exc
    assert result.exit_code == 1

    with tmpdir.as_cwd():
        result = runner.invoke(cli.main, ['report'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "--data-file": Could not open file: %s: No such file or directory' % DEFAULT_COVERAGE_DATA_FILE
    assert result.exit_code == 2

    result = runner.invoke(cli.main, ['report', '/does/not/exist'])
    assert result.output.splitlines()[-1] == \
        'Error: Invalid value for "%s": Could not open file: /does/not/exist: No such file or directory' % (
            'profile_file' if click.__version__ < '7.0' else '[PROFILE_FILE]...',)
    assert result.exit_code == 2

    result = runner.invoke(cli.main, [
        '--rcfile', os.devnull,
        'report', 'tests/fixtures/merged_conditionals-0.profile'])
    assert result.output.splitlines() == [
        'Name                                        Stmts   Miss  Cover',
        '---------------------------------------------------------------',
        'tests/test_plugin/merged_conditionals.vim      19     12    37%']
    assert result.exit_code == 0


def test_report_rcfile_and_include(tmpdir, runner):
    profiled_file = 'tests/test_plugin/conditional_function.vim'
    profiled_file_content = open(profiled_file, 'r').read()

    # Works without rcfile.
    with tmpdir.as_cwd() as old_cwd:
        profile_file = str(old_cwd.join(
            'tests/fixtures/conditional_function.profile'))
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        result = runner.invoke(cli.main, ['report', profile_file])
        assert result.exit_code == 0
        assert profiled_file in result.output

        coveragerc = 'customrc'
        with open(coveragerc, 'w') as f:
            f.write('[report]\ninclude = doesnotexist/*')

        result = runner.invoke(cli.main, [
            '--rcfile', coveragerc,
            'report', profile_file])
        assert result.output.splitlines() == [
            'Name    Stmts   Miss  Cover',
            '---------------------------',
            'Error: No data to report. (CoverageException)',
        ]
        assert result.exit_code == 1


def test_report_source(runner, tmpdir, devnull):
    with tmpdir.as_cwd():
        result = runner.invoke(cli.main, ["report", "--source", ".", "/does/not/exist"])
        assert (
            result.output.splitlines()[-1]
            == 'Error: Invalid value for "%s": Could not open file: /does/not/exist: No such file or directory' % (
                'profile_file' if click.__version__ < '7.0' else '[PROFILE_FILE]...',)
        )
        assert result.exit_code == 2

        fname = "foo/bar/test.vim"
        tmpdir.join(fname).ensure().write("echom 1")
        tmpdir.join("foo/bar/test2.vim").ensure().write("echom 2")
        result = runner.invoke(cli.main, ["report", "--source", ".", devnull.name])
        out = result.output.splitlines()
        assert any(l.startswith(fname) for l in out)  # pragma: no branch
        assert out[-1].startswith("TOTAL")
        assert out[-1].endswith(" 0%")
        assert result.exit_code == 0

        result = runner.invoke(cli.main, ["report", devnull.name, "--source", "."])
        out = result.output.splitlines()
        assert any(fname in l for l in out)  # pragma: no branch
        assert out[-1].startswith("TOTAL")
        assert out[-1].endswith(" 0%")
        assert result.exit_code == 0

        result = runner.invoke(cli.main, ["report", "--source", "."])
        out = result.output.splitlines()
        assert out[-1] == "Error: --source can only be used with PROFILE_FILE."
        assert result.exit_code == 2

    result = runner.invoke(
        cli.main,
        [
            "--rcfile",
            devnull.name,
            "report",
            "--source",
            "tests/test_plugin/merged_conditionals.vim",
            "tests/fixtures/merged_conditionals-0.profile",
        ],
    )
    assert (
        result.output.splitlines()
        == [
            "Name                                        Stmts   Miss  Cover",
            "---------------------------------------------------------------",
            "tests/test_plugin/merged_conditionals.vim      19     12    37%",
        ]
    )
    assert result.exit_code == 0


def test_cli_xml(runner, tmpdir):
    """Smoke test for the xml command."""
    result = runner.invoke(cli.main, [
        'write_coverage', '--data-file', str(tmpdir.join('.coverage')),
        'tests/fixtures/merged_conditionals-0.profile'])
    with tmpdir.as_cwd() as old_cwd:
        result = runner.invoke(cli.main, [
            'xml', '--data-file', '.coverage'])
        assert result.exit_code == 0

        with open('coverage.xml') as f:
            xml = f.read()
        assert 'filename="%s/tests/test_plugin/merged_conditionals.vim' % (
            old_cwd) in xml

        # --rcfile is used.
        coveragerc = 'customrc'
        with open(coveragerc, 'w') as f:
            f.write('[xml]\noutput = custom.xml')

        result = runner.invoke(cli.main, [
            '--rcfile', coveragerc,
            'xml', '--data-file', '.coverage'])
        assert result.output == ''
        assert result.exit_code == 0
        with open('custom.xml') as f:
            xml = f.read()
        assert 'filename="%s/tests/test_plugin/merged_conditionals.vim' % (
            old_cwd) in xml

        # --rcfile is used.
        coveragerc = 'customrc'
        with open(coveragerc, 'w') as f:
            f.write('[report]\ninclude = doesnotexist/*')

        result = runner.invoke(cli.main, [
            '--rcfile', coveragerc,
            'xml', '--data-file', '.coverage'])
        assert result.output == 'Error: No data to report. (CoverageException)\n'
        assert result.exit_code == 1


def test_rcfile_invalid_option(runner, tmpdir, covdata_empty):
    with tmpdir.as_cwd():
        coveragerc = '.coveragerc'
        with open(coveragerc, 'w') as f:
            f.write('[report]\nunknown_option = 1')

        with open(DEFAULT_COVERAGE_DATA_FILE, 'w') as f:
            f.write(covdata_empty)
            f.close()

            result = runner.invoke(cli.main, ['report'])
        assert result.output.splitlines() == [
            "Error: Unrecognized option '[report] unknown_option=' in config file .coveragerc (CoverageException)",
        ]
        assert result.exit_code == 1


def test_run_handles_exit_code_from_python_fd(capfd):
    ret = call(['covimerage', 'run',
                'python', '-c', 'print("output"); import sys; sys.exit(42)'])
    out, err = capfd.readouterr()
    assert 'Error: Command exited non-zero: 42.' in err.splitlines()
    assert out == 'output\n'
    assert ret == 42


def test_run_handles_exit_code_from_python_pty_fd(capfd):
    ret = call(['covimerage', 'run', '--profile-file', '/not/used',
                'python', '-c',
                "import pty; pty.spawn(['/bin/sh', '-c', "
                "'printf output; exit 42'])"])
    out, err = capfd.readouterr()
    assert ('Error: The profile file (/not/used) has not been created.' in
            err.splitlines())
    assert out == 'output'
    assert ret == 1


def test_run_append_with_empty_data(runner, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        data_file = '.covimerage_covimerage'
        with open(data_file, 'w') as f:
            f.write('')
        result = runner.invoke(cli.run, [
            '--append', '--no-wrap-profile', '--profile-file', profile_file,
            '--data-file', data_file, 'printf', '--', '--headless'])
        assert result.output.splitlines() == [
            'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
            'Parsing profile file %s.' % profile_file,

            'Error: Coverage could not read data_file: .covimerage_covimerage '
            "(CoverageException: Couldn't read data from '.covimerage_covimerage': "
            "CoverageException: Doesn't seem to be a coverage.py data file)",
        ]
        assert result.exit_code == 1


@pytest.mark.parametrize('with_data_file', (True, False))
def test_run_append_with_data(with_data_file, runner, tmpdir, covdata_header):
    profiled_file = 'tests/test_plugin/conditional_function.vim'
    profiled_file_content = open(profiled_file, 'r').read()
    tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)

    def run_args(profile_file):
        args = []
        if with_data_file:
            args += ['--data-file', DEFAULT_COVERAGE_DATA_FILE]
        return args + [
            '--append', '--no-wrap-profile', '--profile-file', profile_file,
            'printf', '--', '--headless']

    with tmpdir.as_cwd() as old_dir:
        profile_file = str(old_dir.join(
            'tests/fixtures/conditional_function.profile'))
        result = runner.invoke(cli.run, run_args(profile_file))
        assert result.output.splitlines() == [
            'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
            'Parsing profile file %s.' % profile_file,
            'Writing coverage file .coverage_covimerage.',
            'Name                                         Stmts   Miss  Cover',
            '----------------------------------------------------------------',
            'tests/test_plugin/conditional_function.vim      13      5    62%']
        assert result.exit_code == 0

        assert open('.coverage_covimerage').read().startswith(covdata_header)

        # The same again.
        result = runner.invoke(cli.run, run_args(profile_file))
        assert result.output.splitlines() == [
            'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
            'Parsing profile file %s.' % profile_file,
            'Writing coverage file .coverage_covimerage.',
            'Name                                         Stmts   Miss  Cover',
            '----------------------------------------------------------------',
            'tests/test_plugin/conditional_function.vim      13      5    62%']
        assert result.exit_code == 0

        # Append another profile.
        another_profiled_file = 'tests/test_plugin/merged_conditionals.vim'
        tmpdir.join(another_profiled_file).write(
            old_dir.join(another_profiled_file).read(), ensure=True)
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        profile_file = str(old_dir.join(
            'tests/fixtures/merged_conditionals-0.profile'))
        tmpdir.join(profiled_file).write(profiled_file_content, ensure=True)
        result = runner.invoke(cli.run, run_args(profile_file))
        assert result.output.splitlines() == [
            'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
            'Parsing profile file %s.' % profile_file,
            'Writing coverage file .coverage_covimerage.',
            'Name                                         Stmts   Miss  Cover',
            '----------------------------------------------------------------',
            'tests/test_plugin/conditional_function.vim      13      5    62%',
            'tests/test_plugin/merged_conditionals.vim       19     12    37%',
            '----------------------------------------------------------------',
            'TOTAL                                           32     17    47%']
        assert result.exit_code == 0


def test_run_report_without_data(tmpdir, runner, devnull):
    with tmpdir.as_cwd():
        result = runner.invoke(cli.run, [
            '--no-write-data', '--no-wrap-profile',
            '--profile-file', devnull.name,
            'printf', '--', '--headless'])
    assert result.output.splitlines() == [
        'Running cmd: printf -- --headless (in %s)' % str(tmpdir),
        'Parsing profile file %s.' % devnull.name,
        'Error: No data to report.']
    assert result.exit_code == 1


def test_run_forwards_sighup(devnull):
    proc = subprocess.Popen([
            sys.executable, '-m', 'covimerage', 'run',
            '--no-write-data', '--no-wrap-profile',
            '--profile-file', devnull.name,
            sys.executable, '-c',
            'import signal, sys, time; '
            'signal.signal(signal.SIGHUP, lambda *args: sys.exit(89)); '
            'time.sleep(2)'],
                          stderr=subprocess.PIPE)
    time.sleep(1)
    proc.send_signal(signal.SIGHUP)
    _, stderr = proc.communicate()
    exit_code = proc.returncode

    stderr = stderr.decode()
    assert 'Command exited non-zero: 89' in stderr
    assert exit_code == 89


def test_run_cmd_requires_args(runner):
    result = runner.invoke(cli.run, [])
    assert 'Error: Missing argument "%s".' % (
        'args' if click.__version__ < '7.0' else 'ARGS...',
    ) in result.output.splitlines()
    assert result.exit_code == 2


def test_get_version_message_importerror(monkeypatch_importerror):
    exc = ImportError('failed')
    with monkeypatch_importerror(('coverage',), raise_exc=exc):
        assert get_version_message() == (
            'covimerage, version %s (using Coverage.py unknown (failed))'
            % (get_version(),)
        )
    exc = ImportError
    with monkeypatch_importerror(('coverage',), raise_exc=exc):
        assert get_version_message() == (
            'covimerage, version %s (using Coverage.py unknown ())'
            % (get_version(),)
        )
