import os

import click
import click as c

from . import DEFAULT_COVERAGE_DATA_FILE, MergedProfiles, Profile
from .__version__ import __version__
from .coveragepy import CoverageWrapper
from .logging import LOGGER


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version', prog_name='covimerage')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
@click.option('-q', '--quiet', count=True, help='Decrease verbosity.')
def main(verbose, quiet):
    if verbose - quiet:
        LOGGER.setLevel(LOGGER.level - (verbose - quiet) * 10)


@main.command()
@click.argument('profile_file', type=click.File('r'), required=False, nargs=-1)
@click.option('--data-file', required=False, show_default=True,
              default='.coverage', type=click.File(mode='w'))
def write_coverage(profile_file, data_file):
    """
    Parse PROFILE_FILE (output from Vim's :profile) and write it into DATA_FILE
    (Coverage.py compatible).
    """
    m = MergedProfiles()
    m.add_profile_files(*profile_file)
    if not m.write_coveragepy_data(data_file=data_file):
        raise click.ClickException('No data to report.')


@main.command(context_settings=dict(
    # ignore_unknown_options=True,
    allow_interspersed_args=False,
))
@c.argument('args', nargs=-1, type=click.UNPROCESSED)
@c.option('--wrap-profile/--no-wrap-profile', required=False,
          default=True, show_default=True,
          help='Wrap VIM cmd with options to create a PROFILE_FILE.')
@c.option('--profile-file', required=False, type=click.File('w'),
          metavar='PROFILE_FILE', show_default=True,
          help=('File name for the PROFILE_FILE file. '
                'By default a temporary file is used.'))
@c.option('--data-file', required=False, type=click.File('w'),
          help='DATA_FILE to write into.', show_default=True)
@c.option('--write-data/--no-write-data', is_flag=True,
          default=True, show_default=True,
          help='Write Coverage.py compatible DATA_FILE.')
@c.option('--report/--no-report', is_flag=True, default=True,
          help=('Automatically report to REPORT_FILE. '
                'This avoids having to write an intermediate data file.'))
@c.option('--report-file', type=click.File('w'),
          help='Report output file.  Defaults to stdout.')
@c.option('--report-options', required=False,
          help='Options to be passed on to `covimerage report`.')
@c.pass_context
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
    if ctx.params.get('profile_file', ()):
        return value
    return click.File('r').convert(value, param, ctx)


@main.command()
@c.argument('profile_file', type=click.File('r'), required=False, nargs=-1)
@c.option('--data-file', required=False, callback=report_data_file_cb,
          default=DEFAULT_COVERAGE_DATA_FILE, show_default=True,
          help='DATA_FILE to use in case PROFILE_FILE is not provided.')
@c.option('--show-missing', '-m', is_flag=True, default=False,
          help=('Show line numbers of statements in each file that was '
                'not executed.'))
@c.option('--include', required=False,
          help=('Include only files whose paths match one of these patterns. '
                'Accepts shell-style wildcards, which must be quoted.'))
@c.option('--omit', required=False,
          help=('Omit files whose paths match one of these patterns. '
                'Accepts shell-style wildcards, which must be quoted.'))
@c.option('--skip-covered', is_flag=True, default=False,
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
        m = MergedProfiles()
        m.add_profile_files(*profile_file)
        data = m.get_coveragepy_data()
    else:
        data = None
    CoverageWrapper(data=data, data_file=data_file).report(
        show_missing=show_missing, include=include, omit=omit,
        skip_covered=skip_covered)


@main.command()
@c.option('--data-file', required=False, type=click.File('r'),
          default=DEFAULT_COVERAGE_DATA_FILE, show_default=True)
@c.option('--include', required=False,
          help='Include only files whose paths match one of these patterns. '
          'Accepts shell-style wildcards, which must be quoted.')
@c.option('--omit', required=False,
          help='Omit files whose paths match one of these patterns. '
          'Accepts shell-style wildcards, which must be quoted.')
@c.option('--ignore-errors', is_flag=True, default=False, show_default=True,
          required=False, help='Ignore errors while reading source files.')
def xml(data_file, include, omit, ignore_errors):
    """
    A wrapper around `coverage xml`.

    This will automatically add covimerage as a plugin, and then just forwards
    most options.
    """
    CoverageWrapper(data_file=data_file).reportxml(
        include=include, omit=omit, ignore_errors=ignore_errors)
