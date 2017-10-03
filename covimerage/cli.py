import os

import click

from . import MergedProfiles, Profile
from .__version__ import __version__
from ._compat import FileNotFoundError
from .coveragepy import CoverageWrapper
from .logging import LOGGER

DEFAULT_COVERAGE_DATA_FILE = '.coverage.covimerage'


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version', prog_name='covimerage')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
@click.option('-q', '--quiet', count=True, help='Decrease verbosity.')
def main(verbose, quiet):
    if verbose - quiet:
        LOGGER.setLevel(LOGGER.level - (verbose - quiet) * 10)


@main.command()
@click.argument('filename', required=True, nargs=-1)
@click.option('--data-file', required=False, show_default=True,
              default='.coverage', type=click.File(mode='w'))
def write_coverage(filename, data_file):
    """
    Parse FILENAME (output from Vim's :profile) and write it into DATA_FILE
    (Coverage.py compatible).
    """
    profiles = []
    for f in filename:
        p = Profile(f)
        try:
            p.parse()
        except FileNotFoundError as exc:
            raise click.FileError(f, exc.strerror)
        profiles.append(p)

    m = MergedProfiles(profiles)
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
@click.option('--profile-file', required=False, type=click.File('w'),
              metavar='PROFILE_FILE', show_default=True,
              help='File name for the PROFILE_FILE file.  By default a temporary file is used.')  # noqa: E501
@click.option('--data-file', required=False, type=click.File('w'))
@click.option('--write-data', '-w', is_flag=True, default=False)
@click.option('--report/--no-report', is_flag=True, default=True,
              help='Automatically report.  This avoids having to write an intermediate data file.')  # noqa: E501
@click.option('--report-file', type=click.File('w'),
              help='Report output file.  Defaults to stdout.')
@click.option('--report-options', required=False,
              help='Options to be passed on to `covimerage report`.')
@click.pass_context
def run(ctx, args, wrap_profile, profile_file, write_data, data_file,
        report, report_file, report_options):
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
            profile_file_name = tempfile.mktemp(prefix='covimerage.profile.')
        else:
            profile_file_name = profile_file.name
        args += ['--cmd', 'profile start %s' % profile_file_name,
                 '--cmd', 'profile! file ./*']
    else:
        profile_file_name = profile_file.name if profile_file else None
    cmd = args
    LOGGER.info('Running cmd: %s', cmd)

    try:
        exit_code = subprocess.call(cmd, close_fds=False)
    except Exception as exc:
        raise click.exceptions.ClickException(
            'Failed to run %s: %s' % (cmd, exc))
    if exit_code != 0:
        LOGGER.error('Command exited non-zero: %d.', exit_code)

    if profile_file_name:
        if not os.path.exists(profile_file_name):
            msg = 'The profile file (%s) has not been created.'
            raise click.exceptions.ClickException(msg % profile_file_name)
        elif write_data or report:
            LOGGER.info('Parsing profile file %s.', profile_file_name)
            p = Profile(profile_file_name)
            p.parse()
            m = MergedProfiles([p])

            if write_data and not data_file:
                data_file = DEFAULT_COVERAGE_DATA_FILE
            if data_file:
                m.write_coveragepy_data(data_file)

            if report:
                cov_data = m.get_coveragepy_data()
                if not cov_data:
                    raise click.ClickException('No data to report.')
                CoverageWrapper(data=cov_data).report(
                    report_file=report_file, **report_opts)


def report_data_file_cb(ctx, param, value):
    """Use click.File for data_file only if it is used, to prevent an error
    if it does not exist (click tries to open it always)."""
    if not ctx.params.get('profile_file', ()):
        value = click.File('r').convert(value, param, ctx)
        return param.convert()
    return value


@main.command()
@click.argument('profile_file', type=click.File('r'), required=False,
                nargs=-1)
@click.option('--data-file', required=False, callback=report_data_file_cb,
              default=DEFAULT_COVERAGE_DATA_FILE, show_default=True,
              help='DATA_FILE to use in case PROFILE_FILE is not provided.')
@click.option('--show-missing', '-m', is_flag=True, default=False,
              help='Show line numbers of statements in each file that were not executed.')  # noqa: E501
@click.option('--include', required=False,
              help='Include only files whose paths match one of these patterns. Accepts shell-style wildcards, which must be quoted.')  # noqa: E501
@click.option('--omit', required=False,
              help='Omit files whose paths match one of these patterns. Accepts shell-style wildcards, which must be quoted.')  # noqa: E501
@click.option('--skip-covered', is_flag=True, default=False,
              help='Skip files with 100% coverage.')
def report(profile_file, data_file, show_missing, include, omit, skip_covered):
    """
    A wrapper around `coverage report`.

    This will automatically add covimerage as a plugin, and then just forwards
    most options.

    If PROFILE_FILE is provided this gets parsed, otherwise DATA_FILE is
    being used.
    """
    if profile_file:
        data_file = None
        profiles = []
        for f in profile_file:
            p = Profile(f)
            try:
                p.parse()
            except FileNotFoundError as exc:
                raise click.FileError(f, exc.strerror)
            profiles.append(p)

        m = MergedProfiles(profiles)
        data = m.get_coveragepy_data()
    else:
        data = None
    CoverageWrapper(data=data, data_file=data_file).report(
        show_missing=show_missing, include=include, omit=omit,
        skip_covered=skip_covered)


@main.command()
@click.option('--data-file', required=False, type=click.File('r'),
              default=DEFAULT_COVERAGE_DATA_FILE, show_default=True)
@click.option('--include', required=False,
              help='Include only files whose paths match one of these patterns. Accepts shell-style wildcards, which must be quoted.')  # noqa: E501
@click.option('--omit', required=False,
              help='Omit files whose paths match one of these patterns. Accepts shell-style wildcards, which must be quoted.')  # noqa: E501
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
