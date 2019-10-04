import logging
import os
import signal

import click

from . import DEFAULT_COVERAGE_DATA_FILE, MergedProfiles, Profile
from .coveragepy import CoverageWrapper
from .exceptions import CustomClickException
from .logger import logger
from .utils import build_vim_profile_args, join_argv


def default_loglevel():
    return logging.getLevelName(logger.level).lower()


def get_version_message():
    from . import get_version

    try:
        from coverage import __version__ as coverage_version
    except ImportError as exc:
        coverage_version = 'unknown (%s)' % (exc,)

    return 'covimerage, version %s (using Coverage.py %s)' % (
        get_version(),
        coverage_version,
    )


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option('...', '-V', '--version',
                      message=get_version_message())
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
@click.option('-q', '--quiet', count=True, help='Decrease verbosity.')
@click.option('-l', '--loglevel', show_default=True,
              help=('Set logging level explicitly (overrides -v/-q).  '
                    u'[default:\xa0%s]' % default_loglevel()),
              type=click.Choice(('error', 'warning', 'info', 'debug')))
@click.option('--rcfile', type=click.Path(exists=True, dir_okay=False),
              help=(u'Configuration file.  [default:\xa0.coveragerc]'),
              required=False, nargs=1)
@click.pass_context
def main(ctx, verbose, quiet, loglevel, rcfile):
    if loglevel:
        logger.setLevel(loglevel.upper())
    elif verbose - quiet:
        logger.setLevel(max(10, logger.level - (verbose - quiet) * 10))
    ctx.obj = {'rcfile': rcfile}


@main.command(name='write_coverage')
@click.argument('profile_file', type=click.File('r'), required=True, nargs=-1)
@click.option('--data-file', required=False, type=click.Path(dir_okay=False),
              default=DEFAULT_COVERAGE_DATA_FILE,
              help=('DATA_FILE to write into.  '
                    u'[default:\xa0%s]' % DEFAULT_COVERAGE_DATA_FILE))
@click.option('--source', type=click.types.Path(exists=True), help=(
    'Source files/dirs to include.  This is necessary to include completely '
    'uncovered files.'), show_default=True, multiple=True)
@click.option('--append', is_flag=True, default=False, show_default=True,
              help='Read existing DATA_FILE for appending.')
def write_coverage(profile_file, data_file, source, append):
    """
    Parse PROFILE_FILE (output from Vim's :profile) and write it into DATA_FILE
    (Coverage.py compatible).
    """
    if append:
        m = MergedProfiles(source=source, append_to=data_file)
    else:
        m = MergedProfiles(source=source)

    m.add_profile_files(*profile_file)

    if not m.write_coveragepy_data(data_file=data_file):
        raise CustomClickException('No data to report.')


@main.command(context_settings=dict(
    # ignore_unknown_options=True,
    allow_interspersed_args=False,
))
@click.argument('args', nargs=-1, required=True, type=click.UNPROCESSED)
@click.option('--wrap-profile/--no-wrap-profile', required=False,
              default=True, show_default=True,
              help='Wrap VIM cmd with options to create a PROFILE_FILE.')
@click.option('--profile-file', required=False, metavar='PROFILE_FILE',
              type=click.Path(dir_okay=False), help=(
                  'File name for the PROFILE_FILE file '
                  '(get overwritten, but not removed).  '
                  'By default a temporary file is used '
                  '(and removed after processing).'))
@click.option('--data-file', required=False, type=click.Path(dir_okay=False),
              default=DEFAULT_COVERAGE_DATA_FILE,
              help=('DATA_FILE to write into.  '
                    u'[default:\xa0%s]' % DEFAULT_COVERAGE_DATA_FILE))
@click.option('--append', is_flag=True, default=False, show_default=True,
              help='Read existing DATA_FILE for appending.')
@click.option('--write-data/--no-write-data', is_flag=True,
              default=True, show_default=True,
              help='Write Coverage.py compatible DATA_FILE.')
@click.option('--report/--no-report', is_flag=True, default=True,
              show_default=True, help=(
                  'Automatically report.  '
                  'This avoids having to write an intermediate data file.'))
@click.option('--report-file', type=click.File('w'),
              help='Report output file.  Defaults to stdout.')
# TODO: rather handle this via real options, and pass them through?!
@click.option('--report-options', required=False,
              help='Options to be passed on to `covimerage report`.')
@click.option('--source', type=click.types.Path(exists=True), default=['.'],
              help='Source directories and/or files.',
              multiple=True, show_default=True)
@click.pass_context
def run(ctx, args, wrap_profile, profile_file, write_data, data_file,
        report, report_file, report_options, source, append):
    """
    Run VIM wrapped with :profile instructions.

    """
    import subprocess
    import tempfile

    if report:
        report_cmd = main.get_command(ctx, 'report')
        if report_options:
            report_args = click.parser.split_arg_string(report_options)
            parser = report_cmd.make_parser(ctx)
            try:
                report_opts, _, _ = parser.parse_args(args=report_args)
            except click.exceptions.UsageError as exc:
                raise click.exceptions.UsageError(
                    'Failed to parse --report-options: %s' % exc.message,
                    ctx=ctx)
        else:
            report_opts = {}

    args = list(args)
    unlink_profile_file = False
    if wrap_profile:
        if not profile_file:
            profile_file = tempfile.mktemp(prefix='covimerage.profile.')
            unlink_profile_file = True
        args += build_vim_profile_args(profile_file, source)
    cmd = args
    logger.info('Running cmd: %s (in %s)', join_argv(cmd), os.getcwd())

    try:
        proc = subprocess.Popen(cmd)

        def forward_signals(signalnum, stackframe):
            """Forward SIGHUP to the subprocess."""
            proc.send_signal(signalnum)
        signal.signal(signal.SIGHUP, forward_signals)

        try:
            exit_code = proc.wait()
        except Exception:
            proc.kill()
            proc.wait()
            raise
    except Exception as exc:
        raise CustomClickException('Failed to run %s: %s' % (cmd, exc))

    if profile_file:
        if not os.path.exists(profile_file):
            if not exit_code:
                raise CustomClickException(
                    'The profile file (%s) has not been created.' % (
                        profile_file))

        elif write_data or report:
            logger.info('Parsing profile file %s.', profile_file)
            p = Profile(profile_file)
            p.parse()

            if append:
                m = MergedProfiles([p], source=source, append_to=data_file)
            else:
                m = MergedProfiles([p], source=source)

            if write_data:
                m.write_coveragepy_data(data_file)

            if report:
                cov_data = m.get_coveragepy_data()
                if not cov_data:
                    raise CustomClickException('No data to report.')
                report_opts['data'] = cov_data
                ctx.invoke(report_cmd, report_file=report_file,
                           **report_opts)
        if unlink_profile_file:
            try:
                os.unlink(profile_file)
            except Exception:  # ignore FileNotFoundError (OSError on py2).
                if os.path.exists(profile_file):
                    raise

    if exit_code != 0:
        raise CustomClickException(
            'Command exited non-zero: %d.' % exit_code,
            exit_code=exit_code
        )


def report_data_file_cb(ctx, param, value):
    """Use click.File for data_file only if it is used, to prevent an error
    if it does not exist (click tries to open it always)."""
    if ctx.params.get('profile_file', ()):
        return value
    return click.File('r').convert(value, param, ctx)


def report_source_cb(ctx, param, value):
    if value and not ctx.params.get('profile_file', ()):
        raise click.exceptions.UsageError(
            '--source can only be used with PROFILE_FILE.')
    return value


@main.command()
@click.argument('profile_file', type=click.File('r'), required=False, nargs=-1,
                is_eager=True)
@click.option('--data-file', required=False, show_default=True, help=(
    'DATA_FILE to use in case PROFILE_FILE is not provided.'),
              callback=report_data_file_cb,
              default=DEFAULT_COVERAGE_DATA_FILE)
@click.option('--show-missing', '-m', is_flag=True, default=False, help=(
    'Show line numbers of statements in each file that was not executed.'))
@click.option('--include', required=False, multiple=True, help=(
    'Include only files whose paths match one of these patterns. '
    'Accepts shell-style wildcards, which must be quoted.'))
@click.option('--omit', required=False, multiple=True, help=(
    'Omit files whose paths match one of these patterns. '
    'Accepts shell-style wildcards, which must be quoted.'))
@click.option('--skip-covered', is_flag=True, default=False,
              help='Skip files with 100% coverage.')
@click.option('--source', type=click.types.Path(exists=True), help=(
    'Source dirs/files to include (only when PROFILE_FILE is used - otherwise '
    'it is expected to be in the data already).'),
              callback=report_source_cb,
              show_default=True, default=None, multiple=True)
@click.option('--report-file', type=click.File('w'),
              help='Report output file.  Defaults to stdout.')
@click.pass_context
def report(ctx, profile_file, data_file, show_missing, include, omit,
           skip_covered, source, report_file, data=None):
    """
    A wrapper around `coverage report`.

    This will automatically add covimerage as a plugin, and then just forwards
    most options.

    If PROFILE_FILE is provided this gets parsed, otherwise DATA_FILE is used.
    """
    # Use None instead of empty set, for coveragepy to use the config file.
    include = include if include else None
    omit = omit if omit else None

    if data:
        data_file = None
    elif profile_file:
        data_file = None
        m = MergedProfiles(source=source)
        m.add_profile_files(*profile_file)
        data = m.get_coveragepy_data()
    config_file = ctx.obj.get('rcfile') if ctx.obj else None
    CoverageWrapper(
        data=data,
        data_file=data_file,
        config_file=config_file,
    ).report(
        report_file=report_file,
        show_missing=show_missing,
        include=include,
        omit=omit,
        skip_covered=skip_covered,
    )


@main.command()
@click.option('--data-file', required=False, type=click.File('r'),
              default=DEFAULT_COVERAGE_DATA_FILE, show_default=True)
@click.option('--include', required=False, multiple=True, help=(
    'Include only files whose paths match one of these patterns. '
    'Accepts shell-style wildcards, which must be quoted.'))
@click.option('--omit', required=False, multiple=True, help=(
    'Omit files whose paths match one of these patterns. '
    'Accepts shell-style wildcards, which must be quoted.'))
@click.option('--ignore-errors', is_flag=True, default=False,
              show_default=True, required=False,
              help='Ignore errors while reading source files.')
@click.pass_context
def xml(ctx, data_file, include, omit, ignore_errors):
    """
    A wrapper around `coverage xml`.

    This will automatically add covimerage as a plugin, and then just forwards
    most options.
    """
    # Use None instead of empty set, for coveragepy to use the config file.
    include = include if include else None
    omit = omit if omit else None

    config_file = ctx.obj.get('rcfile') if ctx.obj else None
    CoverageWrapper(
        data_file=data_file,
        config_file=config_file,
    ).reportxml(
        include=include,
        omit=omit,
        ignore_errors=ignore_errors,
    )
