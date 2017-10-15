def test_shell_quote():
    from covimerage._compat import shell_quote

    assert shell_quote('') == "''"
    assert shell_quote('word') == 'word'
    assert shell_quote('two words') == "'two words'"
