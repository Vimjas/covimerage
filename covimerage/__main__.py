def wrap_for_errormsg(f, *args, **kwargs):
    try:
        f(*args, standalone_mode=False, **kwargs)
    except Exception as exc:
        from click.exceptions import ClickException
        if isinstance(exc, ClickException):
            import sys
            from click.utils import echo

            msg = 'covimerage: error: %s' % (exc.format_message(),)
            echo(msg, err=True)
            sys.exit(exc.exit_code)


def main():
    from .cli import main
    wrap_for_errormsg(main.main, prog_name='covimerage')


def run():
    from .cli import run
    wrap_for_errormsg(run.main, prog_name='covimerage-run')


if __name__ == '__main__':
    main()
