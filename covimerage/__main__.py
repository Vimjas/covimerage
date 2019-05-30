def wrap_for_prefix(f, *args, **kwargs):
    import logging
    from .logger import handler

    handler.setFormatter(logging.Formatter('covimerage: %(message)s'))

    try:
        f(*args, standalone_mode=False, **kwargs)
    except Exception as exc:
        from click.exceptions import ClickException
        if isinstance(exc, ClickException):
            import re
            import sys
            from click.utils import echo
            from ._compat import StringIO

            # Use `show()` to get extended message with UsageErrors.
            out = StringIO()
            exc.show(file=out)
            out.seek(0)
            msg = re.sub("^Error: ", "covimerage: Error: ", out.read(),
                         flags=re.MULTILINE)
            echo(msg, err=True, nl=False)
            sys.exit(exc.exit_code)
        raise


def main():
    from .cli import main
    wrap_for_prefix(main.main, prog_name='covimerage')


if __name__ == '__main__':
    main()
