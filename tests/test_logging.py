import pytest


def test_logging_error_causes_exception(capfd):
    from covimerage import LOGGER

    with pytest.raises(Exception) as excinfo:
        LOGGER.info('Wrong:', 'no %s')
    assert excinfo.value.args[0] == 'Internal logging error'
    out, err = capfd.readouterr()
    assert err.splitlines()[-2:] == [
        "Message: 'Wrong:'",
        "Arguments: ('no %s',)"]
