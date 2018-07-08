import click


class CustomClickException(click.ClickException):
    """Wrap click.ClickException for exit_code."""
    def __init__(self, *args, **kwargs):
        self.exit_code = kwargs.pop('exit_code', 1)
        super(CustomClickException, self).__init__(*args, **kwargs)


class CoverageWrapperException(CustomClickException):
    """Inherit from CustomClickException for automatic handling."""
    def __init__(self, message, orig_exc=None):
        self.orig_exc = orig_exc
        super(CoverageWrapperException, self).__init__(message)

    def format_message(self):
        """Append information about original exception if any."""
        msg = super(CoverageWrapperException, self).format_message()
        if self.orig_exc:
            return '%s (%s: %s)' % (
                msg,
                self.orig_exc.__class__.__name__,
                self.orig_exc)
        return msg

    def __str__(self):
        return self.format_message()

    def __repr__(self):
        return 'CoverageWrapperException(message=%r, orig_exc=%r)' % (
            self.message, self.orig_exc)
