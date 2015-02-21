import sys
from django.utils import six
if six.PY2:
    from cStringIO import StringIO
elif six.PY3:
    from io import StringIO


class StdOutTrap(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout