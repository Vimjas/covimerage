try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
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


@pytest.fixture
def coverage_fileobj():
    return StringIO('\n'.join(['!coverage.py: This is a private format, don\'t read it directly!{"lines":{"/test_plugin/conditional_function.vim":[17,3,23,8,9,11,13,14,15]},"file_tracers":{"/test_plugin/conditional_function.vim":"covimerage.CoveragePlugin"}}']))  # noqa: E501


def test_coveragewrapper(coverage_fileobj):
    from covimerage.coveragepy import CoverageWrapper

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


def test_coveragewrapperexception():
    from covimerage.coveragepy import CoverageWrapperException

    assert CoverageWrapperException('foo').format_message() == 'foo'

    with pytest.raises(CoverageWrapperException) as excinfo:
        try:
            raise Exception('orig')
        except Exception:
            raise CoverageWrapperException('bar')
    assert excinfo.value.format_message() == "bar (Exception('orig',))"
