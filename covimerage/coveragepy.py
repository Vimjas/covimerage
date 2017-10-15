import re

import attr
import click
import coverage

from ._compat import FileNotFoundError
from .logger import LOGGER
from .utils import get_fname_and_fobj_and_str, is_executable_line

RE_EXCLUDED = re.compile(
    r'"\s*(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(cover|COVER)')


class CoverageWrapperException(click.ClickException):
    """Inherit from ClickException for automatic handling."""
    def __init__(self, message, orig_exc=None):
        self.orig_exc = orig_exc
        super(CoverageWrapperException, self).__init__(message)

    def format_message(self):
        """Append information about original exception if any."""
        msg = super(CoverageWrapperException, self).format_message()
        if self.orig_exc:
            return '%s (%r)' % (msg, self.orig_exc)
        return msg

    def __str__(self):
        return self.format_message()

    def __repr__(self):
        return 'CoverageWrapperException(message=%r, orig_exc=%r)' % (
            self.message, self.orig_exc)


@attr.s(frozen=True)
class CoverageData(object):
    cov_data = attr.ib(default=None)
    data_file = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.cov_data and self.data_file:
            raise TypeError('data and data_file are mutually exclusive.')
        if self.cov_data:
            if not isinstance(self.cov_data, coverage.data.CoverageData):
                raise TypeError(
                    'data needs to be of type coverage.data.CoverageData')
            return
        cov_data = coverage.data.CoverageData()
        if self.data_file:
            fname, fobj, fstr = get_fname_and_fobj_and_str(self.data_file)
            try:
                if fobj:
                    cov_data.read_fileobj(fobj)
                else:
                    cov_data.read_file(fname)
            except coverage.CoverageException as exc:
                raise CoverageWrapperException(
                    'Coverage could not read data_file: %s' % fstr,
                    orig_exc=exc)
        object.__setattr__(self, 'cov_data', cov_data)

    @property
    def lines(self):
        data = self.cov_data
        return {f: sorted(data.lines(f)) for f in data.measured_files()}

    def add_lines(self, lines):
        self.cov_data.add_lines(lines)


@attr.s(frozen=True)
class CoverageWrapper(object):
    """Wrap Coveragepy related functionality."""
    data = attr.ib(default=None)
    data_file = attr.ib(default=None)

    _cached_cov_obj = None

    def __attrs_post_init__(self):
        if not isinstance(self.data, CoverageData):
            data = CoverageData(cov_data=self.data, data_file=self.data_file)
            object.__setattr__(self, 'data', data)
        elif self.data_file:
            raise TypeError('data and data_file are mutually exclusive.')

    @property
    def lines(self):
        return self.data.lines

    @property
    def _cov_obj(self):
        if not self._cached_cov_obj:
            object.__setattr__(self, '_cached_cov_obj', self._get_cov_obj())
        return self._cached_cov_obj

    def _get_cov_obj(self):
        class CoverageW(coverage.Coverage):
            """Wrap/shortcut _get_file_reporter to return ours."""
            def _get_file_reporter(self, morf):
                return FileReporter(morf)

        cov_coverage = CoverageW(config_file=False)
        cov_coverage._init()
        cov_coverage.data = self.data.cov_data
        return cov_coverage

    def report(self, report_file=None, show_missing=None,
               include=None, omit=None, skip_covered=None):
        self._cov_obj.report(
            file=report_file, show_missing=show_missing, include=include,
            omit=omit, skip_covered=skip_covered)

    def reportxml(self, report_file=None, include=None, omit=None,
                  ignore_errors=None):
        self._cov_obj.xml_report(
            outfile=report_file, include=include, omit=omit,
            ignore_errors=ignore_errors)


class FileReporter(coverage.FileReporter):
    _split_lines = None

    def __repr__(self):
        return '<CovimerageFileReporter {0!r}>'.format(self.filename)

    def source(self):
        try:
            with open(self.filename, 'rb') as f:
                source = f.read()
                try:
                    return source.decode('utf8')
                except UnicodeDecodeError:
                    LOGGER.debug('UnicodeDecodeError in %s for utf8. '
                                 'Trying iso-8859-15.', self.filename)
                    return source.decode('iso-8859-15')
        except FileNotFoundError as exc:
            LOGGER.warning('%s', exc)
            raise coverage.misc.NoSource(str(exc))
        except Exception as exc:
            raise CoverageWrapperException(
                'Could not read source for %s.' % self.filename, orig_exc=exc)

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
            if is_executable_line(l):
                lines.append(lnum)
        return set(lines)

    def excluded_lines(self):
        lines = []
        for lnum, l in enumerate(self.split_lines, start=1):
            # TODO: exclude until end of block (by using vimlparser?!)
            if RE_EXCLUDED.search(l):
                lines.append(lnum)
        return set(lines)


class CoveragePlugin(coverage.CoveragePlugin):
    def file_reporter(self, filename):
        return FileReporter(filename)
