#!/usr/bin/env python
import attr
import copy
# from collections import defaultdict
# from functools import partial
import itertools
import logging
import re
import sys

logger = logging.getLogger('covimerage')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

RE_FUNC_PREFIX = re.compile(
    r'^\s*fu(?:n(?:(?:c(?:t(?:i(?:o(?:n)?)?)?)?)?)?)?!?\s+')
RE_CONTINUING_LINE = r'\s*\\'


@attr.s
class Line(object):
    line = attr.ib()
    count = attr.ib(default=None)
    total_time = attr.ib(default=None)
    self_time = attr.ib(default=None)
    _parsed_line = None

    # @property
    # def count(self):
    #     if not self._parsed_line:
    #         self._parsed_line = parse_count_and_times(self.line)
    #     return self._parsed_line[0]


@attr.s(hash=True)
class Script(object):
    path = attr.ib()
    lines = attr.ib(default=attr.Factory(dict), repr=False, hash=False)
    # List of line numbers for dict functions.
    dict_functions = attr.ib(default=attr.Factory(set), repr=False, hash=False)
    # List of line numbers for dict functions that have been mapped already.
    mapped_dict_functions = attr.ib(default=attr.Factory(set), repr=False,
                                    hash=False)
    # func_to_lnums = attr.ib(default=attr.Factory(partial(defaultdict, list)))
    func_to_lnums = attr.ib(default=attr.Factory(dict), repr=False, hash=False)

    def parse_script_line(self, lnum, line):
        m = re.match(RE_FUNC_PREFIX, line)
        if m:
            f = line[m.end():].split('(', 1)[0]
            if '.' in f:
                self.dict_functions.add(lnum)

            if f.startswith('<SID>'):
                f = 's:' + f[5:]
            elif f.startswith('g:'):
                f = f[2:]
            self.func_to_lnums.setdefault(f, []).append(lnum)
            # if f not in self.func_to_lnums:
            #     self.func_to_lnums = [lnum]
            # else:
            #     self.func_to_lnums[f].append(lnum)

    # def get_script_lines_for_func_lines(func_lnum):
    #     lines = join_script_lines(self.lines)
    #
    #
    # source_lnum_to_joined_lnum = {}
    # def join_script_lines(self):
    #     """Join lines from scripts to match lines from functions."""
    #     source_lnums = []
    #     for i, l in enumerate(self.lines, start=1):
    #         source_lnums.append(i)
    #         m = re.match(RE_CONTINUING_LINE, l)
    #         if m:
    #             continue
    #         self.joined_[i] = joined_lnum
    #         if buf:


@attr.s
class Function(object):
    name = attr.ib()
    calls = attr.ib(default=None)
    total_time = attr.ib(default=None)
    self_time = attr.ib(default=None)
    lines = attr.ib(default=attr.Factory(dict), repr=False)


@attr.s
class MergedProfiles(object):
    profiles = attr.ib(default=attr.Factory(list))

    @property
    def scripts(self):
        return itertools.chain.from_iterable(p.scripts for p in self.profiles)

    @property
    def scriptfiles(self):
        return {s.path for s in self.scripts}

    @property
    def lines(self):
        def merge_lines(line1, line2):
            assert line1.line == line2.line
            new = Line(line1.line)
            if line1.count is None:
                new.count = line2.count
            elif line2.count is None:
                new.count = line1.count
            else:
                new.count = line1.count + line2.count
            return new

        lines = {}
        for p in self.profiles:
            for s, s_lines in p.lines.items():
                if s.path in lines:
                    new = lines[s.path]
                    for lnum, line in s_lines.items():
                        if lnum in new:
                            new[lnum] = merge_lines(new[lnum], line)
                        else:
                            new[lnum] = copy.copy(line)
                else:
                    lines[s.path] = copy.copy(s_lines)
        return lines

    def get_coveragepy_data(self):
        import coverage

        cov_data = coverage.data.CoverageData()
        cov_dict = {}
        cov_file_tracers = {}

        # TODO: should be absolute fname?!  (tests / verify with coveragepy)
        for fname, lines in self.lines.items():
            cov_dict[fname] = {
                # lnum: line.count for lnum, line in lines.items()
                # XXX: coveragepy does not support hit counts?!
                lnum: None for lnum, line in lines.items() if line.count
            }
            cov_file_tracers[fname] = 'covimerage.CoveragePlugin'

        cov_data.add_lines(cov_dict)
        cov_data.add_file_tracers(cov_file_tracers)
        return cov_data

    def write_coveragepy_data(self, data_file='.coverage'):
        from click.utils import string_types

        cov_data = self.get_coveragepy_data()

        logger.info('Writing coverage file %s.', data_file)
        if isinstance(data_file, string_types):
            cov_data.write_file(data_file)
        else:
            cov_data.write_fileobj(data_file)


@attr.s
class Profile(object):
    fname = attr.ib()
    scripts = attr.ib(default=attr.Factory(list))
    anonymous_functions = attr.ib(default=attr.Factory(dict))

    @property
    def scriptfiles(self):
        return {s.path for s in self.scripts}

    @property
    def lines(self):
        return {s: s.lines for s in self.scripts}

    def get_anon_func_script_line(self, func):
        funcname = func.name
        try:
            return self.anonymous_functions[funcname]
        except KeyError:
            len_func_lines = len(func.lines)
            found = []
            for s in self.scripts:
                for lnum in s.dict_functions:
                    script_lnum = lnum + 1
                    len_script_lines = len(s.lines)

                    func_lnum = 0
                    script_is_func = True
                    script_line = s.lines[script_lnum].line
                    while (script_lnum <= len_script_lines and
                           func_lnum < len_func_lines):
                        script_lnum += 1
                        next_line = s.lines[script_lnum].line
                        m = re.match(RE_CONTINUING_LINE, next_line)
                        if m:
                            script_line += next_line[m.end():]
                            continue
                        func_lnum += 1
                        if script_line != func.lines[func_lnum].line:
                            script_is_func = False
                            break
                        script_line = s.lines[script_lnum].line

                    if script_is_func:
                        found.append((s, lnum))

            if found:
                if len(found) > 1:
                    logger.warning(
                        'Found multiple sources for anonymous function %s (%s).',  # noqa
                        funcname, (', '.join('%s:%d' % (f[0].path, f[1])
                                             for f in found)))

                for s, lnum in found:
                    if lnum in s.mapped_dict_functions:
                        # More likely to happen with merged profiles.
                        logger.debug('Found already mapped dict function again (%s:%d).', s.path, lnum)  # noqa
                        continue
                    s.mapped_dict_functions.add(lnum)
                    self.anonymous_functions[funcname] = (s, lnum)
                    return (s, lnum)
                return found[0]

    def find_func_in_source(self, func):
        funcname = func.name
        if funcname.isdigit():
            # This is an anonymous function, which we need to lookup based on
            # its source contents.
            return self.get_anon_func_script_line(func)

        m = re.match('^<SNR>\d+_', funcname)
        if m:
            funcname = 's:' + funcname[m.end():]

        found = []
        for script in self.scripts:
            try:
                lnums = script.func_to_lnums[funcname]
            except KeyError:
                continue

            for script_lnum in lnums:
                if self.source_contains_func(script, script_lnum, func):
                    found.append((script, script_lnum))
        if found:
            if len(found) > 1:
                logger.warning('Found multiple sources for function %s (%s).',
                               func, (', '.join('%s:%d' % (f[0].path, f[1])
                                                for f in found)))
            return found[0]
        return None

        # funcname = func.name
        # m = re.match('^<SNR>\d+_', funcname)
        # if m:
        #     funcname = '(?:s:|<SID>)' + funcname[m.end():]
        # elif funcname.isdigit():
        #     # This is an anonymous function, which we need to lookup based on
        #     # its source contents.
        #     return self.get_anon_func_script_line(func)
        # else:
        #     funcname = '(?:g:)?' + funcname
        #
        # found = []
        # for s in self.scripts:
        #     for [lnum, line] in s.lines.items():
        #         if re.search(RE_FUNC_PREFIX + '{}\('.format(funcname),
        #                      line.line):
        #             found += (s, lnum)
        # return found

    @staticmethod
    def source_contains_func(script, script_lnum, func):
        for [f_lnum, f_line] in func.lines.items():
            s_line = script.lines[script_lnum + f_lnum]

            # XXX: might not be the same, since function lines
            # are joined, while script lines might be spread
            # across several lines (prefixed with \).
            script_source = s_line.line
            if script_source != f_line.line:
                while True:
                    # try:
                    peek = script.lines[script_lnum +
                                        f_lnum + 1]
                    # except KeyError:
                    #     pass
                    if True:
                        m = re.match(RE_CONTINUING_LINE, peek.line)
                        if m:
                            script_source += peek.line[m.end():]
                            script_lnum += 1
                            # script_lines.append(peek)
                            continue
                        if script_source == f_line.line:
                            break

                        return False
        return True

    def parse(self):
        in_script = False
        in_function = False
        lnum = 0

        def skip_to_count_header():
            while True:
                next_line = next(fo)
                if next_line.startswith('count'):
                    # lnum = 0
                    break

        logger.debug('Parsing file: %s', self.fname)
        with open(self.fname, 'r') as fo:
            for line in fo:
                line = line.rstrip('\r\n')
                if line == '':
                    if in_function:
                        func_name = in_function.name
                        script_line = self.find_func_in_source(in_function)
                        if not script_line:
                            logger.error('Could not find source for function: %s', func_name)  # noqa
                            in_function = False
                            continue

                        # Assign counts from function to script.
                        script, script_lnum = script_line
                        for [f_lnum, f_line] in in_function.lines.items():
                            s_line = script.lines[script_lnum + f_lnum]

                            # XXX: might not be the same, since function lines
                            # are joined, while script lines might be spread
                            # across several lines (prefixed with \).
                            script_source = s_line.line
                            if script_source != f_line.line:
                                while True:
                                    try:
                                        peek = script.lines[script_lnum +
                                                            f_lnum + 1]
                                    except KeyError:
                                        pass
                                    else:
                                        m = re.match(RE_CONTINUING_LINE, peek.line)  # noqa
                                        if m:
                                            script_source += peek.line[m.end():]  # noqa
                                            script_lnum += 1
                                            # script_lines.append(peek)
                                            continue
                                    if script_source == f_line.line:
                                        break

                                    assert 0, 'Script line matches function line.'  # noqa

                            if f_line.count is not None:
                                if s_line.count:
                                    s_line.count += f_line.count
                                else:
                                    s_line.count = f_line.count
                            if f_line.self_time:
                                if s_line.self_time:
                                    s_line.self_time += f_line.self_time
                                else:
                                    s_line.self_time = f_line.self_time
                            if f_line.total_time:
                                if s_line.total_time:
                                    s_line.total_time += f_line.total_time
                                else:
                                    s_line.total_time = f_line.total_time

                    in_script = False
                    in_function = False
                    continue

                if in_script or in_function:
                    lnum += 1
                    count, total_time, self_time = parse_count_and_times(line)
                    source_line = line[28:]

                    if in_script:
                        in_script.lines[lnum] = Line(
                            line=source_line, count=count,
                            total_time=total_time, self_time=self_time)
                        if count or lnum == 1:
                            # Parse line 1 always, as a workaround for
                            # https://github.com/vim/vim/issues/2103.  # noqa
                            in_script.parse_script_line(lnum, source_line)
                    elif in_function:
                        if count is None:
                            # Functions do not have continued lines, assume 0.
                            count = 0
                        line = Line(line=source_line, count=count,
                                    total_time=total_time, self_time=self_time)
                        in_function.lines[lnum] = line

                elif line.startswith('SCRIPT  '):
                    fname = line[8:]
                    in_script = Script(fname)
                    logger.debug('Parsing script %s', in_script)
                    self.scripts.append(in_script)
                    skip_to_count_header()
                    lnum = 0

                elif line.startswith('FUNCTION  '):
                    func_name = line[10:-2]
                    in_function = Function(name=func_name)
                    logger.debug('Parsing function %s', in_function)
                    skip_to_count_header()
                    lnum = 0


def parse_count_and_times(line):
    count = line[0:5]
    if count == '':
        return 0, None, None
    if count == '     ':
        count = None
    else:
        count = int(count)
    total_time = line[8:16]
    if total_time == '        ':
        total_time = None
    else:
        total_time = float(total_time)
    self_time = line[19:27]
    if self_time == '        ':
        self_time = None
    else:
        self_time = float(self_time)

    return count, total_time, self_time


def coverage_init(reg, options):
    from covimerage.plugin import CoveragePlugin

    reg.add_file_tracer(CoveragePlugin())
