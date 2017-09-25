def test_filereporter():
    from covimerage.coveragepy import FileReporter

    f = FileReporter('filename')
    assert repr(f) == "<CovimerageFileReporter 'filename'>"
