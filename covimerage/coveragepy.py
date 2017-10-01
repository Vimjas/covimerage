import re

import attr
from click.utils import string_types
import coverage

from .logging import LOGGER


@attr.s(frozen=True)
class CoverageWrapper(object):
    """Wrap Coveragepy related functionality."""
    data = attr.ib(default=None)
    data_file = attr.ib(default=None)

    _cached_cov_obj = None

    def __attrs_post_init__(self):
        if self.data is None:
            if not self.data_file:
                raise TypeError('data or data_file needs to be provided.')
            cov_data = coverage.data.CoverageData()
            if isinstance(self.data_file, string_types):
                cov_data.read_file(self.data_file)
            else:
                cov_data.read_fileobj(self.data_file)
            object.__setattr__(self, 'data', cov_data)
        elif self.data_file is not None:
            raise TypeError('data and data_file are mutually exclusive.')

    @property
    def lines(self):
        data = self.data
        return {f: sorted(data.lines(f)) for f in data.measured_files()}

    @property
    def _cov_obj(self):
        if not self._cached_cov_obj:
            object.__setattr__(self, '_cached_cov_obj', self._get_cov_obj())
        return self._cached_cov_obj

    def _get_cov_obj(self):
        cov_config = coverage.config.CoverageConfig()
        cov_config.plugins = ['covimerage']

        cov_coverage = coverage.Coverage(config_file=False)
        cov_coverage.config = cov_config
        cov_coverage._init()
        cov_coverage.data = self.data
        return cov_coverage

    def report(self, report_file=None, show_missing=None,
               include=None, omit=None, skip_covered=None):
        try:
            self._cov_obj.report(
                file=report_file, show_missing=show_missing, include=include,
                omit=omit, skip_covered=None)
        except coverage.CoverageException as exc:
            LOGGER.warning('Exception from coverage: %r', exc)
            if exc.args == ('No data to report.',):
                return False
            raise

    def reportxml(self, report_file=None, include=None, omit=None):
        self._cov_obj.xml_report(
            outfile=report_file, include=include, omit=omit)


class FileReporter(coverage.FileReporter):
    # Empty (whitespace only), comments, continued, or `end` statements.
    RE_NON_EXECED = re.compile(r'^\s*("|\\|end|$)')
    RE_EXCLUDED = re.compile(
        r'"\s*(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(cover|COVER)')

    _split_lines = None

    def __repr__(self):
        return '<CovimerageFileReporter {0!r}>'.format(self.filename)

    @property
    def split_lines(self):
        if self._split_lines is None:
            self._split_lines = self.source().splitlines()
        return self._split_lines

    # NOTE: should be done before already, to end up in .coverage already.
    # def translate_lines(self, lines):
    #     if (1 not in lines and
    #             lines and re.match(RE_FUNC_PREFIX, self.split_lines[0])):
    #         lines.append(1)
    #     return set(lines)

    def lines(self):
        lines = []
        for lnum, l in enumerate(self.split_lines, start=1):
            if self.RE_NON_EXECED.match(l):
                continue
            lines.append(lnum)
        return set(lines)

    def excluded_lines(self):
        lines = []
        for lnum, l in enumerate(self.split_lines, start=1):
            # TODO: exclude until end of block (by using vimlparser?!)
            if self.RE_EXCLUDED.search(l):
                lines.append(lnum)
        return set(lines)


class CoveragePlugin(coverage.CoveragePlugin):
    def file_reporter(self, filename):
        return FileReporter(filename)
