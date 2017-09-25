import logging

import click

from covimerage import MergedProfiles, Profile
from covimerage.__version__ import __version__

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


logger = logging.getLogger('covimerage')


@click.group()
@click.version_option(__version__, '-V', '--version', prog_name='covimerage')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
@click.option('-q', '--quiet', count=True, help='Decrease verbosity.')
def main(verbose, quiet):
    if verbose - quiet:
        logger.setLevel(logger.level - (verbose - quiet) * 10)


@main.command()
@click.argument('filename', required=True, nargs=-1)
def write_coverage(filename):
    """Parse FILENAME (output from Vim's :profile)."""
    profiles = []
    for f in filename:
        p = Profile(f)
        try:
            p.parse()
        except FileNotFoundError as exc:
            raise click.FileError(f, exc.strerror)
        profiles.append(p)

    m = MergedProfiles(profiles)
    m.write_coveragepy_data()


@main.command()
@click.argument('cmd', required=False)
@click.option('--vim', required=False, default='nvim')
@click.option('--vimrc', required=False, default='NORC')
def run(cmd, vim, vimrc):
    from subprocess import run

    if True or not vimrc:
        vimrc = 'tests/test_plugin/vimrc'

    # if cmd:
    #     import pdb
    #     pdb.set_trace()

    cmd = [vim, '--noplugin', '-N',
           '-u', vimrc,
           '--cmd', 'profile start /tmp/covimerage.profile',
           '--cmd', 'profile! file ./**',
           '-c', 'call test_plugin#integration#func1()',
           '-cq']

    print(cmd)
    run(cmd)
