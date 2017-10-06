try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys

import attr
import coverage
import pytest


def test_filereporter():
    from covimerage.coveragepy import FileReporter

    f = FileReporter('/doesnotexist')
    assert repr(f) == "<CovimerageFileReporter '/doesnotexist'>"

    with pytest.raises(coverage.misc.NoSource) as excinfo:
        f.lines()
    assert excinfo.value.args == (
        "[Errno 2] No such file or directory: '/doesnotexist'",)


def test_filereporter_source_handles_latin1(tmpdir):
    from covimerage.coveragepy import FileReporter

    with tmpdir.as_cwd():
        with open('iso.txt', 'wb') as f:
            f.write(b'Hellstr\xf6m')
        with open('utf8.txt', 'wb') as f:
            f.write(b'Hellstr\xc3\xb6m')

        assert FileReporter('iso.txt').source().encode(
            'utf-8') == b'Hellstr\xc3\xb6m'
        assert FileReporter('iso.txt').source().encode(
            'utf-8') == b'Hellstr\xc3\xb6m'


@pytest.mark.skipif(sys.version_info[0] == 3 and sys.version_info[1] < 5,
                    reason='Failed to patch open with py33/py34.')
def test_filereporter_source_exception(mocker, devnull):
    from covimerage.coveragepy import CoverageWrapperException, FileReporter

    class CustomException(Exception):
        pass

    m = mocker.mock_open()
    m.return_value.read.side_effect = CustomException
    mocker.patch('covimerage.coveragepy.open', m)

    f = FileReporter(devnull.name)
    with pytest.raises(CoverageWrapperException) as excinfo:
        f.source()

    assert isinstance(excinfo.value.orig_exc, CustomException)


@pytest.fixture
def coverage_fileobj():
    return StringIO('\n'.join(['!coverage.py: This is a private format, don\'t read it directly!{"lines":{"/test_plugin/conditional_function.vim":[17,3,23,8,9,11,13,14,15]},"file_tracers":{"/test_plugin/conditional_function.vim":"covimerage.CoveragePlugin"}}']))  # noqa: E501


def test_coveragewrapper(coverage_fileobj, devnull):
    from covimerage.coveragepy import CoverageWrapper, CoverageWrapperException

    with pytest.raises(TypeError):
        CoverageWrapper()

    with pytest.raises(TypeError):
        CoverageWrapper(data_file='foo', data='bar')

    cov = CoverageWrapper(data_file=coverage_fileobj)
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        cov.data = 'foo'

    assert cov.lines == {
        '/test_plugin/conditional_function.vim': [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}

    assert isinstance(cov._cov_obj, coverage.control.Coverage)
    assert cov._cov_obj.data is cov.data

    with pytest.raises(CoverageWrapperException) as excinfo:
        CoverageWrapper(data_file=devnull.name)
    assert excinfo.value.args == (
        'Coverage could not read data_file: /dev/null',)


def test_coveragewrapperexception():
    from covimerage.coveragepy import CoverageWrapperException

    assert CoverageWrapperException('foo').format_message() == 'foo'

    with pytest.raises(CoverageWrapperException) as excinfo:
        try:
            raise Exception('orig')
        except Exception as orig_exc:
            raise CoverageWrapperException('bar', orig_exc=orig_exc)
    assert excinfo.value.format_message() == "bar (Exception('orig',))"
