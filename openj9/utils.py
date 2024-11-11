import gdb

from functools import lru_cache as cache

from openj9.runtime.util.optinfo_c import *

# TODO: move to openj9.runtime.???
def J9_BYTECODE_START_FROM_RAM_METHOD(j9Method):
    return j9Method['bytecodes']

# TODO: move to openj9.runtime.???
def J9_ROM_METHOD_FROM_RAM_METHOD(j9Method):
    ty_J9ROMMethod = gdb.lookup_type('J9ROMMethod')
    return (J9_BYTECODE_START_FROM_RAM_METHOD(j9Method) - ty_J9ROMMethod.sizeof).cast(ty_J9ROMMethod.pointer())

def j9utf8_to_str(j9utf8Val):
    length = j9utf8Val['length']
    data = bytes([int(j9utf8Val['data'][i]) for i in range(0, length)])
    return data.decode(errors='replace')

class RangeMap:
    """
    Utility class to map (integer) ranges to (integer) values.
    Used to map native code to bytecode and bytecode to line numbers.
    """
    def __init__(self, mapping = []):
        self._mapping = []
        for start, value in mapping:
            self[start] = value

    def __setitem__(self, start, value):
        assert start >= 0
        assert len(self._mapping) == 0 or self._mapping[-1][0] < start
        self._mapping.append( (start, value) )

    def __getitem__(self, lookup):
        assert len(self._mapping) > 0
        previous_start = None
        previous_value = None
        for start, value in self._mapping:
            if lookup < start:
                break
            else:
                previous_start = start
                previous_value = value
        if previous_value == None:
            raise KeyError()
        return previous_value

    def __iter__(self):
        return iter(self._mapping)

    def __repr__(self):
        return "RangeMap(%s)" % repr(self._mapping)

class MethodPrologueInfo(object):
    """
    A helper object that describes method's prologue.
    """

    def __init__(self, method):
        self._method = method
        # FIXME: RISC-V specific
        self._jitEntry = self._method.startPC + self._method.numParamSlots() * 4
        self._frameAllocd = self._jitEntry + 4 + 4
        self._stackChecked = self._frameAllocd + 4 + 4
        self._frameBuilt = self._stackChecked # FIXME!!!

    @property
    def startPC(self):
        return self._method.startPC

    @property
    def jitEntry(self):
        return self._jitEntry

    @property
    def frameAllocd(self):
        return self._frameAllocd

    @property
    def stackChecked(self):
        return self._stackChecked

    @property
    def frameBuilt(self):
        return self._frameBuilt

    @property
    def endPC(self):
        return self.frameBuilt


class MethodInfo(object):
    def __init__(self, metaDataVal, compilerVal = None, bytecodeTable = None):
        assert compilerVal != None or bytecodeTable != None
        self._metaDataVal = metaDataVal

        if bytecodeTable != None:
            self._bytecodeTable = RangeMap(bytecodeTable._mapping)
        else:
            # We have to extract PC-to-bytecode table eagerly here
            # as compiler object is transient and might be gone
            # by the time we need the table
            self._bytecodeTable = RangeMap()

            insn = compilerVal['_codeGenerator']['_firstInstruction']['_next'] # The very first instruction is descriptor word!
            prevBC = -1
            while (int(insn) != 0): # while insn != nullptr
                if int(insn['_binaryLength']) > 0:
                    # `insn` is not a pseudo instruction (label, BBstart, ...)
                    currBC = int(insn['_node']['_byteCodeInfo']['_byteCodeIndex'])
                    if prevBC != currBC:
                        currPC = int(insn['_binaryEncodingBuffer'])
                        self._bytecodeTable[currPC] = currBC
                        prevBC = currBC
                insn = insn['_next']

    def __repr__(self):
        return "<MethodInfo name=%s>" % self.name

    @property
    def bytecodeTable(self):
        return self._bytecodeTable

    @property
    def lineNumberTable(self):
        ramMethod = self._metaDataVal['ramMethod']
        romMethod = J9_ROM_METHOD_FROM_RAM_METHOD(ramMethod)
        methodDebugInfo = getMethodDebugInfoFromROMMethod(romMethod)

        if methodDebugInfo != None:
            lineNumberTablePtr = getLineNumberTable(methodDebugInfo)
            if lineNumberTablePtr != None:
                lineNumberTable = RangeMap()
                line = 0
                location = 0
                for i in range(0, getLineNumberCount(methodDebugInfo)):
                    lineNumberTablePtr, ( line, location) = getNextLineNumberFromTable(lineNumberTablePtr, line, location)
                    lineNumberTable[location] = line
                return lineNumberTable
        return None

    @property
    @cache
    def className(self):
        return j9utf8_to_str(self._metaDataVal['className'])

    @property
    @cache
    def methodName(self):
        return j9utf8_to_str(self._metaDataVal['methodName'])

    @property
    @cache
    def methodSignature(self):
        return j9utf8_to_str(self._metaDataVal['methodSignature'])

    @property
    @cache
    def name(self):
        return self.className + '.' + self.methodName + self.methodSignature

    @property
    def startPC(self):
        return int(self._metaDataVal['startPC'])

    @property
    def endPC(self):
        return int(self._metaDataVal['endPC'])

    def numFrameSlots(self):
        """
        Return a number of frame slots for this method,
        including:
          * return address
          * saved registers
          * temporaries
          * outgoing parameters
        """
        return int(self._metaDataVal['totalFrameSize'])

    def numParamSlots(self):
        """
        Return a number of parameters including
        `this`
        """
        return int(self._metaDataVal['slots'])

    @property
    @cache
    def prologueInfo(self):
        return MethodPrologueInfo(self)

    def linetable(self):
        """
        Return GDB linetable for this method
        """
        lineTable = []
        pc = self.startPC
        prologue = self.prologueInfo
        while pc < self.endPC:
            line = self.lineNumberTable[self.bytecodeTable[pc]]
            is_stmt = pc >= prologue.endPC      # is this a good place to place breakpoint for given line?
            prologue_end = pc == prologue.endPC # is this the first instruction after prologue?
            lineTable.append(gdb.LineTableEntry(line, pc, is_stmt, prologue_end))
            pc = pc + 4
        return lineTable

    def registerCompiled(self):
        """
        Register method in GDB.
        """

        # We use simplistic approach where for every compiled method
        # an objfile, compunit and a single "function" block is created.

        self._objfile = gdb.Objfile(self.name)
        compunit = gdb.Compunit(self.name, self._objfile, self.startPC, self.endPC, 3)

        symtab = gdb.Symtab(self.className + '.java', compunit)
        gdb.LineTable(symtab, self.linetable())

        block = gdb.Block(compunit.static_block(), self.startPC, self.endPC)

        ftype = gdb.selected_inferior().architecture().void_type().function(None)
        symbol = gdb.Symbol(self.name, symtab, ftype,
                                  gdb.SYMBOL_FUNCTION_DOMAIN, gdb.SYMBOL_LOC_BLOCK,
                                  block)

        compunit.static_block().add_symbol(symbol)

        self._objfile.j9method = self

# Upon reload, replace existing instances of MethodInfo
for objfile in gdb.objfiles():
    if hasattr(objfile, 'j9method'):
        old = getattr(objfile, 'j9method')
        new = MethodInfo(old._metaDataVal, bytecodeTable=old._bytecodeTable)
        new._objfile = old._objfile

        setattr(objfile, 'j9method', new)
