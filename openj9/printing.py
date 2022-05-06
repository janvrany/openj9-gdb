import gdb

from gdb.printing import PrettyPrinter, register_pretty_printer
from vdb.printing import CxxPrettyPrinter, CxxCollectionPrettyPrinter

from openj9.utils import j9utf8_to_str

class J9UTF8(PrettyPrinter):
    def __init__(self, val):
        self._val = val

    def __str__(self):
        if not hasattr(self, '_str'):
            self._str = j9utf8_to_str(self._val)
        return self._str

    def to_string(self):
        return "%s \"%s\"" % (self._val.format_string(raw = True), self)

class J9(CxxCollectionPrettyPrinter):
    def __init__(self):
        super().__init__("J9")
        self.add_printer('J9UTF8'         , 'J9UTF8'          , J9UTF8)

register_pretty_printer(gdb.current_progspace(), J9(), replace=True)
