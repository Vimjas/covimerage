import logging
import sys

LOGGER = logging.getLogger('covimerage')
LOGGER.setLevel(logging.INFO)


class StdoutStreamHandler(logging.StreamHandler):
    @property
    def stream(self):
        return sys.stdout

    @stream.setter
    def stream(self, value):
        pass


class _StderrHandler(logging.StreamHandler):
    """
    This class is like a StreamHandler using sys.stderr, but always uses
    whatever sys.stderr is currently set to rather than the value of
    sys.stderr at handler construction time.
    """
    def __init__(self, level=logging.NOTSET):
        """
        Initialize the handler.
        """
        logging.Handler.__init__(self, level)

    @property
    def stream(self):
        return sys.stderr

    def handleError(self, record):
        super(_StderrHandler, self).handleError(record)
        # t, v, tb = sys.exc_info()
        raise Exception('Internal logging error')


# logger.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.addHandler(_StderrHandler())
