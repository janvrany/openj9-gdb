import gdb

from functools import lru_cache as cache
from gdb.printing import PrettyPrinter, register_pretty_printer
from vdb.printing import CxxPrettyPrinter, CxxCollectionPrettyPrinter

class J9UTF8(PrettyPrinter):
    def __init__(self, val):
        self._val = val

    def __str__(self):
        if not hasattr(self, '_str'):
            length = self._val['length']
            data = bytes([int(self._val['data'][i]) for i in range(0, length)])
            self._str = data.decode(errors='replace')
        return self._str

    def to_string(self):
        return "%s \"%s\"" % (self._val.format_string(raw = True), self)

class TR_MethodMetaData(CxxPrettyPrinter):
    @property
    @cache
    def className(self):
        return str(J9UTF8(self._val['className']))

    @property
    @cache
    def methodName(self):
        return str(J9UTF8(self._val['methodName']))

    @property
    @cache
    def methodSignature(self):
        return str(J9UTF8(self._val['methodSignature']))

    @property
    @cache
    def name(self):
        return self.className + '.' + self.methodName + self.methodSignature

    @property
    def startPC(self):
        return int(self._val['startPC'])

    @property
    def endPC(self):
        return int(self._val['endPC'])

    def numFrameSlots(self):
        """
        Return a number of frame slots for this method,
        including:
          * slots for arguments and (if applicable) `this`
          * return address
          * saved registers
          * temporaries
          * outgoing parameters
        """
        return int(self._val['totalFrameSize'])

    def numParamSlots(self):
        """
        Return a number of parameters including
        `this`
        """
        return int(self._val['slots'])

    def registerCompiled(self, compiler):
        """
        Register method in GDB.
        """

        self._objfile = gdb.Objfile(self.name)
        self._symtab = gdb.Symtab(self._objfile, self.className + '.java')
        self._block = self._symtab.add_block(self.name, self.startPC, self.endPC)

        self._objfile.j9method = self

class J9(CxxCollectionPrettyPrinter):
    def __init__(self):
        super().__init__("J9")
        self.add_printer('J9UTF8'         , 'J9UTF8'          , J9UTF8)
        self.add_printer('MethodMetaData' , 'TR_MethodMetaData',TR_MethodMetaData)

register_pretty_printer(gdb.current_progspace(), J9(), replace=True)
