try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
from subprocess import call

import pytest

from covimerage import cli
from covimerage.__version__ import __version__


def test_cli():
    with pytest.raises(SystemExit) as excinfo:
        cli.write_coverage(['tests/fixtures/conditional_function.profile'])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cli.write_coverage(['file not found'])
    assert excinfo.value.code == 1


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

    assert call(['covimerage', 'write_coverage', 'file not found']) == 1
    out, err = capfd.readouterr()
    err_lines = err.splitlines()
    assert err_lines == [
        'Error: Could not open file file not found: '
        'No such file or directory']
    assert out == ''


def test_cli_call_verbosity_fd(capfd, mocker):
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
    f = StringIO()
    result = runner.invoke(cli.main, ['write_coverage', '--data-file', f,
                           'tests/fixtures/conditional_function.profile'])
    assert result.output == '\n'.join([
        'Writing coverage file %s.' % f,
        ''])
    assert result.exit_code == 0

    f.seek(0)
    assert f.readlines() == [
        "!coverage.py: This is a private format, don't read it "
        'directly!{"lines":{"/test_plugin/conditional_function.vim":[3,8,9,11,13,14,15,17,23]},"file_tracers":{"/test_plugin/conditional_function.vim":"covimerage.CoveragePlugin"}}']  # noqa: E501
