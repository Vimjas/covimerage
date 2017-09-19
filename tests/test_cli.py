from covimerage.__version__ import __version__
from covimerage import cli
import pytest

from subprocess import call


def test_cli():
    with pytest.raises(SystemExit) as excinfo:
        cli(['tests/fixtures/conditional_function.profile'])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cli(['file not found'])
    assert excinfo.value.code == 1


def test_cli_call(capfd):
    assert call(['covimerage', '--version']) == 0
    out, err = capfd.readouterr()
    assert out == 'covimerage, version %s\n' % __version__

    assert call(['covimerage', '--help']) == 0
    assert call(['covimerage', 'file not found']) == 1
