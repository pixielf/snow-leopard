import contextlib
import io


class Stream(io.StringIO):
    def writeline(self, s: str, end: str = '\n'):
        self.write(str(s) + str(end))

    @contextlib.contextmanager
    def temporary_seek(self, position: int, whence: int = io.SEEK_SET):
        original = self.tell()

        try:
            self.seek(position, whence)
            yield
        finally:
            # restore original position
            self.seek(original, io.SEEK_SET)

    def fullread(self) -> str:
        """ Return the full text of the stream, restoring the cursor position once finished. """
        with self.temporary_seek(0):
            return self.read()


def brace(s: str) -> str:
    """ Return the string wrapped in braces.

    >>> brace('a string')
    '{a string}'
    """
    return r'{' + str(s) + r'}'
