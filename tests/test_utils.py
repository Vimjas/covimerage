from covimerage import join_script_lines


def test_join_script_lines():
    assert join_script_lines([]) == []
    assert join_script_lines(['1']) == ['1']
    assert join_script_lines(['\\1']) == ['\\1']
    assert join_script_lines([
        '    line1',
        '    \\ .line2']) == ['    line1 .line2']
    assert join_script_lines([
        '    line1',
        '    \\ .line2',
        '\\line3']) == ['    line1 .line2line3']
