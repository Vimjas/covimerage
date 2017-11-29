import logging
import os

import click

from . import DEFAULT_COVERAGE_DATA_FILE, MergedProfiles, Profile
from .__version__ import __version__
from .coveragepy import CoverageWrapper
from .logger import LOGGER
from .utils import build_vim_profile_args, join_argv


def default_loglevel():
    return logging.getLevelName(LOGGER.level).lower()


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version', prog_name='covimerage')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
@click.option('-q', '--quiet', count=True, help='Decrease verbosity.')
@click.option('-l', '--loglevel', show_default=True,
              help=('Set logging level explicitly (overrides -v/-q).  '
                    '[default: %s]' % (default_loglevel(),)),
              type=click.Choice(('error', 'warning', 'info', 'debug')))
def main(verbose, quiet, loglevel):
    if loglevel:
        LOGGER.setLevel(loglevel.upper())
    elif verbose - quiet:
        LOGGER.setLevel(max(10, LOGGER.level - (verbose - quiet) * 10))


@main.command()
@click.argument('profile_file', type=click.File('r'), required=False, nargs=-1)
@click.option('--data-file', required=False, show_default=True,
              default=DEFAULT_COVERAGE_DATA_FILE, type=click.File(mode='w'))
@click.option('--source', type=click.types.Path(exists=True), help=(
    'Source files/dirs to include.  This is necessary to include completely '
    'uncovered files.'), show_default=True, multiple=True)
def write_coverage(profile_file, data_file, source):
    """
    Parse PROFILE_FILE (output from Vim's :profile) and write it into DATA_FILE
    (Coverage.py compatible).
    """
    m = MergedProfiles(source=source)
    m.add_profile_files(*profile_file)
    if not m.write_coveragepy_data(data_file=data_file):
        raise click.ClickException('No data to report.')


@main.command(context_settings=dict(
    # ignore_unknown_options=True,
    allow_interspersed_args=False,
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('--wrap-profile/--no-wrap-profile', required=False,
              default=True, show_default=True,
              help='Wrap VIM cmd with options to create a PROFILE_FILE.')
@click.option('--profile-file', required=False, metavar='PROFILE_FILE',
              type=click.Path(dir_okay=False),
              help='File name for the PROFILE_FILE file.  By default a temporary file is used.')  # noqa: E501
@click.option('--data-file', required=False, type=click.File('w'),
              help='DATA_FILE to write into.', show_default=True)
@click.option('--append', is_flag=True, default=False,
              help='Read existing DATA_FILE for appending.', show_default=True)
@click.option('--write-data/--no-write-data', is_flag=True,
              default=True, show_default=True,
              help='Write Coverage.py compatible DATA_FILE.')
@click.option('--report/--no-report', is_flag=True, default=True,
              help='Automatically report.  This avoids having to write an intermediate data file.')  # noqa: E501
@click.option('--report-file', type=click.File('w'),
              help='Report output file.  Defaults to stdout.')
# TODO: rather handle this via real options, and pass them through?!
@click.option('--report-options', required=False,
              help='Options to be passed on to `covimerage report`.')
@click.option('--source', type=click.types.Path(exists=True), default=['.'],
              multiple=True)
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
    if wrap_profile:
        if not profile_file:
            # TODO: remove it automatically in the end?
            profile_file = tempfile.mktemp(prefix='covimerage.profile.')
        args += build_vim_profile_args(profile_file, source)
    cmd = args
    LOGGER.info('Running cmd: %s (in %s)', join_argv(cmd), os.getcwd())

    try:
        exit_code = subprocess.call(cmd)
    except Exception as exc:
        raise click.exceptions.ClickException(
            'Failed to run %s: %s' % (cmd, exc))

    if profile_file:
        if not os.path.exists(profile_file):
            if not exit_code:
                exit = click.exceptions.ClickException(
                    'The profile file (%s) has not been created.' % (
                        profile_file))
                exit.exit_code = 1
                raise exit

        elif write_data or report:
            LOGGER.info('Parsing profile file %s.', profile_file)
            p = Profile(profile_file)
            p.parse()

            if (write_data or append) and not data_file:
                data_file = DEFAULT_COVERAGE_DATA_FILE

            if append:
                m = MergedProfiles([p], source=source, append_to=data_file)
            else:
                m = MergedProfiles([p], source=source)

            if write_data:
                m.write_coveragepy_data(data_file)

            if report:
                cov_data = m.get_coveragepy_data()
                if not cov_data:
                    raise click.ClickException('No data to report.')
                report_opts['data'] = cov_data
                ctx.invoke(report_cmd, report_file=report_file,
                           **report_opts)

    if exit_code != 0:
        exit = click.exceptions.ClickException(
            'Command exited non-zero: %d.' % exit_code)
        exit.exit_code = exit_code
        raise exit


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
def report(profile_file, data_file, show_missing, include, omit, skip_covered,
           source, report_file, data=None):
    """
    A wrapper around `coverage report`.

    This will automatically add covimerage as a plugin, and then just forwards
    most options.

    If PROFILE_FILE is provided this gets parsed, otherwise DATA_FILE is
    being used.
    """
    if data:
        data_file = None
    elif profile_file:
        data_file = None
        m = MergedProfiles(source=source)
        m.add_profile_files(*profile_file)
        data = m.get_coveragepy_data()
    CoverageWrapper(data=data, data_file=data_file).report(
        report_file=report_file,
        show_missing=show_missing, include=include, omit=omit,
        skip_covered=skip_covered)


# TODO: support / pass through --rcfile?!
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
def xml(data_file, include, omit, ignore_errors):
    """
    A wrapper around `coverage xml`.

    This will automatically add covimerage as a plugin, and then just forwards
    most options.
    """
    CoverageWrapper(data_file=data_file).reportxml(
        include=include, omit=omit, ignore_errors=ignore_errors)
