def wrap_for_errormsg(f, *args, **kwargs):
    try:
        f(*args, standalone_mode=False, **kwargs)
    except Exception as exc:
        from click.exceptions import ClickException
        if isinstance(exc, ClickException):
            import re, sys
            from click.utils import echo
            from ._compat import StringIO

            # Use `show()` to get extended message with UsageErrors.
            out = StringIO()
            exc.show(file=out)
            out.seek(0)
            msg = re.sub("^Error: ", "covimerage: error: ", out.read(), flags=re.MULTILINE)
            echo(msg, err=True, nl=False)
            sys.exit(exc.exit_code)
        raise


def main():
    from .cli import main
    wrap_for_errormsg(main.main, prog_name='covimerage')


def run():
    from .cli import run
    wrap_for_errormsg(run.main, prog_name='covimerage-run')


if __name__ == '__main__':
    main()
