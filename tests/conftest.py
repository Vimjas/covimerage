from click.testing import CliRunner
import pytest


@pytest.fixture
def runner():
    return CliRunner()
