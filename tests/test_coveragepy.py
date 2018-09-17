import sys

import attr
import coverage
import pytest

from covimerage._compat import StringIO


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
    return StringIO('\n'.join(['!coverage.py: This is a private format, don\'t read it directly!{"lines":{"/test_plugin/conditional_function.vim":[17,3,23,8,9,11,13,14,15]},"file_tracers":{"/test_plugin/conditional_function.vim":"covimerage.CoveragePlugin"}}']))


def test_coveragedata(coverage_fileobj):
    import coverage
    from covimerage.coveragepy import (
        CoverageData, CoveragePyData, CoverageWrapperException)

    with pytest.raises(TypeError) as excinfo:
        CoverageData(data_file='foo', cov_data=CoveragePyData())
    assert excinfo.value.args == (
        'data and data_file are mutually exclusive.',)

    data = CoverageData()
    try:
        from coverage.data import CoverageJsonData
    except ImportError:
        assert isinstance(data.cov_data, coverage.data.CoverageData)
    else:
        assert isinstance(data.cov_data, CoverageJsonData)

    with pytest.raises(TypeError) as excinfo:
        CoverageData(cov_data='foo')
    try:
        from coverage.data import CoverageJsonData
    except ImportError:
        assert excinfo.value.args == (
            'data needs to be of type coverage.data.CoverageData',)
    else:
        assert excinfo.value.args == (
            'data needs to be of type coverage.data.CoverageJsonData',)

    with pytest.raises(CoverageWrapperException) as excinfo:
        CoverageData(data_file='/does/not/exist')
    assert excinfo.value.args == (
        'Coverage could not read data_file: /does/not/exist',)
    assert isinstance(excinfo.value.orig_exc, coverage.misc.CoverageException)

    f = StringIO()
    with pytest.raises(CoverageWrapperException) as excinfo:
        CoverageData(data_file=f)
    e = excinfo.value
    assert isinstance(e.orig_exc, coverage.misc.CoverageException)
    assert e.message == 'Coverage could not read data_file: %s' % f
    assert e.format_message() == "%s (CoverageException: Doesn't seem to be a coverage.py data file)" % (e.message,)
    assert str(e) == e.format_message()
    assert repr(e) == 'CoverageWrapperException(message=%r, orig_exc=%r)' % (
        e.message, e.orig_exc)

    cov_data = CoverageData(data_file=coverage_fileobj)
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        cov_data.data = 'foo'

    assert cov_data.lines == {
        '/test_plugin/conditional_function.vim': [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}


def test_coveragedata_empty(covdata_empty):
    from covimerage.coveragepy import CoverageData

    f = StringIO()
    data = CoverageData()
    try:
        write_fileobj = data.cov_data.write_fileobj
    except AttributeError:
        # coveragepy 5
        write_fileobj = data.cov_data._write_fileobj
    write_fileobj(f)
    f.seek(0)
    assert f.read() == covdata_empty


def test_coveragewrapper(coverage_fileobj, devnull):
    import coverage
    from covimerage.coveragepy import (
        CoverageData, CoveragePyData, CoverageWrapper, CoverageWrapperException)

    cov_data = CoverageWrapper()
    assert cov_data.lines == {}
    assert isinstance(cov_data.data, CoverageData)

    cov_data = CoverageWrapper(data=CoveragePyData())
    assert cov_data.lines == {}
    assert isinstance(cov_data.data, CoverageData)

    with pytest.raises(TypeError):
        CoverageWrapper(data_file='foo', data='bar')

    with pytest.raises(TypeError):
        CoverageWrapper(data_file='foo', data=CoveragePyData())

    cov = CoverageWrapper(data_file=coverage_fileobj)
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        cov.data = 'foo'

    assert cov.lines == {
        '/test_plugin/conditional_function.vim': [
            3, 8, 9, 11, 13, 14, 15, 17, 23]}

    assert isinstance(cov._cov_obj, coverage.control.Coverage)
    if hasattr(cov._cov_obj, '_data'):
        # coveragepy 5
        assert cov._cov_obj._data is cov.data.cov_data
    else:
        assert cov._cov_obj.data is cov.data.cov_data

    with pytest.raises(CoverageWrapperException) as excinfo:
        CoverageWrapper(data_file=devnull.name)
    assert excinfo.value.args == (
        'Coverage could not read data_file: /dev/null',)

    f = StringIO()
    with pytest.raises(CoverageWrapperException) as excinfo:
        CoverageWrapper(data_file=f)
    e = excinfo.value
    assert isinstance(e.orig_exc, coverage.misc.CoverageException)
    assert e.message == 'Coverage could not read data_file: %s' % f
    assert e.format_message() == "%s (CoverageException: Doesn't seem to be a coverage.py data file)" % (e.message,)
    assert str(e) == e.format_message()
    assert repr(e) == 'CoverageWrapperException(message=%r, orig_exc=%r)' % (
        e.message, e.orig_exc)


def test_coveragewrapper_requires_jsondata():
    pytest.importorskip('coverage.sqldata')
    from covimerage.coveragepy import CoverageWrapper

    with pytest.raises(TypeError) as excinfo:
        CoverageWrapper(data=coverage.sqldata.CoverageSqliteData())

    assert excinfo.value.args[0] == (
        'data needs to be of type coverage.data.CoverageJsonData')


def test_coveragewrapper_uses_config_file(tmpdir, capfd):
    from covimerage.coveragepy import CoverageWrapper, CoverageWrapperException

    with tmpdir.as_cwd() as old_dir:
        vim_src = '%s/tests/test_plugin/conditional_function.vim' % old_dir
        coverage_fileobj = StringIO('!coverage.py: This is a private format, don\'t read it directly!{"lines":{"%s":[17,3,23,8,9,11,13,14,15]},"file_tracers":{"%s":"covimerage.CoveragePlugin"}}' % (vim_src, vim_src))

        cov = CoverageWrapper(data_file=coverage_fileobj)
        assert cov._cov_obj.config.report_include is None
        assert cov.lines == {vim_src: [3, 8, 9, 11, 13, 14, 15, 17, 23]}
        cov.report()
        out, err = capfd.readouterr()
        assert 'test_plugin/conditional_function.vim' in out
        assert err == ''

        coveragerc = str(tmpdir.join('.coveragerc'))
        with open(coveragerc, 'w') as f:
            f.write('[report]\ninclude = foo/*,bar/*')
        coverage_fileobj.seek(0)
        cov = CoverageWrapper(data_file=coverage_fileobj)
        assert cov._cov_obj.config.report_include == ['foo/*', 'bar/*']
        with pytest.raises(CoverageWrapperException) as excinfo:
            cov.report()
        assert excinfo.value.args == ('No data to report. (CoverageException)',)
        out, err = capfd.readouterr()
        assert out.splitlines() == [
            'Name    Stmts   Miss  Cover',
            '---------------------------']
        assert err == ''


def test_coveragewrapper_accepts_data():
    from covimerage.coveragepy import CoverageData, CoverageWrapper

    data = CoverageData()
    cov = CoverageWrapper(data=data)
    assert cov.data is data


def test_coveragewrapperexception():
    from covimerage.coveragepy import CoverageWrapperException

    assert CoverageWrapperException('foo').format_message() == 'foo'

    with pytest.raises(CoverageWrapperException) as excinfo:
        try:
            raise Exception('orig')
        except Exception as orig_exc:
            raise CoverageWrapperException('bar', orig_exc=orig_exc)
    assert excinfo.value.format_message() == "bar (Exception: orig)"
