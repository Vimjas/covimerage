import sys

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
    from pipes import quote as shell_quote  # noqa: F401

if sys.version_info < (3,):
    string_types = (str, unicode)  # noqa: F821
else:
    string_types = str
