from covimerage.__version__ import __version__
from covimerage import cli
import pytest

import os
from subprocess import call


def test_cli():
    with pytest.raises(SystemExit) as excinfo:
        cli.write_coverage(['tests/fixtures/conditional_function.profile'])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cli.write_coverage(['file not found'])
    assert excinfo.value.code == 1


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
    assert err_lines == [
        'Usage: covimerage [OPTIONS] COMMAND [ARGS]...',
        # With click after 6.7.
        # 'Try "covimerage --help" for help.',
        '',
        'Error: No such command "file not found".']
    assert out == ''

    assert call(['covimerage', 'write_coverage', 'file not found']) == 1
    out, err = capfd.readouterr()
    err_lines = err.splitlines()
    assert err_lines == [
        'Error: Could not open file file not found: '
        "No such file or directory"]
    assert out == ''


def test_cli_call_verbosity(capfd):
    assert call(['covimerage', 'write_coverage', os.devnull]) == 0
    out, err = capfd.readouterr()
    assert out.splitlines() == ['Writing coverage file .coverage.']
    assert err == ''

    call(['covimerage', '-v', 'write_coverage', os.devnull])
    out, err = capfd.readouterr()
    assert out.splitlines() == [
        'Parsing file: /dev/null',
        'Writing coverage file .coverage.']
    assert err == ''

    call(['covimerage', '-vq', 'write_coverage', os.devnull])
    out, err = capfd.readouterr()
    assert out.splitlines() == [
        'Writing coverage file .coverage.']
    assert err == ''

    call(['covimerage', '-vqq', 'write_coverage', os.devnull])
    out, err = capfd.readouterr()
    assert out.splitlines() == []
    assert err == ''
