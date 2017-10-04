import os

from click.testing import CliRunner
import pytest


@pytest.fixture(scope='session', autouse=True)
def ensure_no_coverage_data_changed_in_cwd():
    fname = '.coverage'
    old_coverage = os.stat(fname) if os.path.exists(fname) else None
    yield
    if os.path.exists(fname):  # pragma: no cover
        if old_coverage is None:
            pytest.fail('Test created a .coverage data file.  Use a tmpdir.')
        elif old_coverage != os.stat('.coverage'):
            pytest.fail('Test changed an existing .coverage data file. '
                        'Use a tmpdir.')


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def devnull():
    with open(os.devnull) as f:
        yield f
