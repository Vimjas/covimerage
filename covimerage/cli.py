import click

from covimerage import MergedProfiles, Profile
from covimerage.__version__ import __version__

from .logging import LOGGER

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


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
