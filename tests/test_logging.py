try:
    from importlib import reload
except ImportError:
    from imp import reload
import logging

import click
import pytest


def test_logging_error_causes_exception(capfd):
    from covimerage import logger

    with pytest.raises(Exception) as excinfo:
        logger.info('Wrong:', 'no %s')
    assert excinfo.value.args[0] == 'Internal logging error'
    out, err = capfd.readouterr()

    lines = err.splitlines()
    assert any((l.startswith('Traceback') for l in lines))  # pragma: no branch

    if not lines[-1].startswith('Logged from file test_logging.py, line '):
        assert lines[-2:] == [
            "Message: 'Wrong:'",
            "Arguments: ('no %s',)"]
    assert 'TypeError: not all arguments converted during string formatting' in lines


def test_loglevel(mocker, runner, devnull):
    from covimerage import cli

    logger = cli.logger

    m = mocker.patch.object(logger, 'setLevel')

    def assert_output(result):
        if click.__version__ < '7.0':
            assert result.output.splitlines() == [
                'Error: no such option: --nonexistingoption']
        else:
            assert result.output.splitlines() == [
                'Usage: main report [OPTIONS] [PROFILE_FILE]...',
                'Try "main report -h" for help.',
                '',
                'Error: no such option: --nonexistingoption']

    for level in ['error', 'warning', 'info', 'debug']:
        result = runner.invoke(cli.main, [
            '--loglevel', level,
            'report', '--nonexistingoption'])
        assert_output(result)
        assert result.exit_code == 2

        level_name = level.upper()
        assert m.call_args_list[-1] == mocker.call(level_name)

    # -v should not override -l.
    m.reset_mock()
    result = runner.invoke(cli.main, [
            '-l', 'warning', '-vvv',
            'report', '--nonexistingoption'])
    assert_output(result)
    assert result.exit_code == 2
    assert m.call_args_list == [mocker.call('WARNING')]

    # -q should not override -l.
    m.reset_mock()
    result = runner.invoke(cli.main, [
            '-l', 'warning', '-qqq',
            'report', '--nonexistingoption'])
    assert_output(result)
    assert result.exit_code == 2
    assert m.call_args_list == [mocker.call('WARNING')]


@pytest.mark.parametrize('default', (None, 'INFO', 'WARNING'))
def test_loglevel_default(default, mocker, runner):
    from covimerage import cli
    from covimerage.logger import logger

    if default:
        mocker.patch.object(logger, 'level', getattr(logging, default))
    else:
        default = 'INFO'
    reload(cli)

    result = runner.invoke(cli.main, ['-h'])

    assert logging.getLevelName(logger.level) == default
    lines = result.output.splitlines()
    assert lines, result
    idx = lines.index('  -l, --loglevel [error|warning|info|debug]')
    indent = ' ' * 34
    assert lines[idx+1:idx+3] == [
        indent + 'Set logging level explicitly (overrides',
        indent + u'-v/-q).  [default:\xa0%s]' % (default.lower(),),
    ]
    assert result.exit_code == 0
