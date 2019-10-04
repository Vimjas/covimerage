from contextlib import contextmanager
from glob import glob
import os
import sys

from click.testing import CliRunner
import pytest


@pytest.fixture(autouse=True)
def ensure_no_coverage_data_changed_in_cwd():
    fnames = glob('.coverage')
    old_coverage = {
        fname: os.stat(fname) if os.path.exists(fname) else None
        for fname in fnames}
    yield
    new_fnames = glob('.coverage')
    for new_fname in new_fnames:  # pragma: no cover
        old_stat = old_coverage.get(new_fname)
        if old_stat is None:
            pytest.fail('Test created a data file: %s.' % new_fname)
        elif old_stat != os.stat(new_fname):
            pytest.fail('Test changed an existing data file: %s.' % (
                new_fname))


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def devnull():
    with open(os.devnull) as f:
        yield f


@pytest.fixture(scope='session')
def covdata_header():
    return "!coverage.py: This is a private format, don't read it directly!"


@pytest.fixture(scope='session')
def covdata_empty():
    return "!coverage.py: This is a private format, don't read it directly!{}"


@pytest.fixture
def monkeypatch_importerror(monkeypatch):
    @contextmanager
    def cm(mocked_imports, raise_exc=ImportError):
        orig_import = __import__

        def import_mock(name, *args):
            if name in mocked_imports:
                raise raise_exc
            return orig_import(name, *args)

        with monkeypatch.context() as m:
            if sys.version_info >= (3,):
                m.setattr('builtins.__import__', import_mock)
            else:
                m.setattr('__builtin__.__import__', import_mock)
            yield m
    return cm
