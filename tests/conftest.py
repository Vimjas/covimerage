import os

from click.testing import CliRunner
import pytest


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def devnull():
    with open(os.devnull) as f:
        yield f
