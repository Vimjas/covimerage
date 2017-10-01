import sys

import pytest


def test_logging_error_causes_exception(capfd):
    from covimerage import LOGGER

    with pytest.raises(Exception) as excinfo:
        LOGGER.info('Wrong:', 'no %s')
    assert excinfo.value.args[0] == 'Internal logging error'
    out, err = capfd.readouterr()

    lines = err.splitlines()
    assert any((l.startswith('Traceback') for l in lines))

    if not lines[-1].startswith('Logged from file test_logging.py, line '):
        assert lines[-2:] == [
            "Message: 'Wrong:'",
            "Arguments: ('no %s',)"]
    assert 'TypeError: not all arguments converted during string formatting' in lines  # noqa: E501
