import pytest


def test_filereporter():
    from covimerage.coveragepy import FileReporter

    f = FileReporter('filename')
    assert repr(f) == "<CovimerageFileReporter 'filename'>"


def test_coveragewrapper():
    from covimerage.coveragepy import CoverageWrapper

    with pytest.raises(TypeError):
        CoverageWrapper()

    with pytest.raises(TypeError):
        CoverageWrapper(data_file='foo', data='bar')
