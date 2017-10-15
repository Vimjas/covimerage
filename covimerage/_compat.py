try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # noqa: F401

try:
    from shlex import quote as shell_quote
except ImportError:
    import re

    # Copy'n'paste from Python 3.6.2.
    _find_unsafe = re.compile(r'[^a-zA-Z0-9_@%+=:,./-]').search

    def shell_quote(s):
        """Return a shell-escaped version of the string *s*."""
        if not s:
            return "''"
        if _find_unsafe(s) is None:
            return s

        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + s.replace("'", "'\"'\"'") + "'"
