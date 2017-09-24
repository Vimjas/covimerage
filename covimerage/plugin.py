import coverage
import re


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
