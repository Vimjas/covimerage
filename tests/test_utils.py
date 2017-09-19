# Not used currently, but inlined.
# from covimerage import join_script_lines


# def join_script_lines(lines):
#     """Join lines from scripts to match lines from functions."""
#     new = []
#     buf = None
#     for l in lines:
#         if buf:
#             m = re.match(RE_CONTINUING_LINE, l)
#             if m:
#                 buf += l[m.end():]
#                 continue
#         if buf is not None:
#             new.append(buf)
#         buf = l
#     if buf is not None:
#         new.append(buf)
#     return new
#
#
# def test_join_script_lines():
#     assert join_script_lines([]) == []
#     assert join_script_lines(['1']) == ['1']
#     assert join_script_lines(['\\1']) == ['\\1']
#     assert join_script_lines([
#         '    line1',
#         '    \\ .line2']) == ['    line1 .line2']
#     assert join_script_lines([
#         '    line1',
#         '    \\ .line2',
#         '\\line3']) == ['    line1 .line2line3']
