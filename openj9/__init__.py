import gdb
import omr
import openj9.printing
import openj9.unwinder
import openj9.cli

from vdb.cli import pr

from openj9.printing import J9UTF8, TR_MethodMetaData
from openj9.cli import uw


pr.prefixes.append('openj9')



def J9_BYTECODE_START_FROM_RAM_METHOD(j9Method):
    return j9Method['bytecodes']

def J9_ROM_METHOD_FROM_RAM_METHOD(j9Method):
    ty_J9ROMMethod = gdb.lookup_type('J9ROMMethod')
    return (J9_BYTECODE_START_FROM_RAM_METHOD(j9Method) - ty_J9ROMMethod.sizeof).cast(ty_J9ROMMethod.pointer())


def compute_bytecode_table(comp):
    bctb = []
    insn = comp['_codeGenerator']['_firstInstruction']['_next']
    while (int(insn) != 0):
        bctb.append ( (hex(int(insn['_binaryEncodingBuffer'])), int(insn['_node']['_byteCodeInfo']['_byteCodeIndex'])) )
        insn = insn['_next']
    return bctb

class CompiledCodeRegistar(gdb.Breakpoint):
    def __init__(self):
        super().__init__("TR::CompilationInfoPerThreadBase::logCompilationSuccess", internal=False)

    def stop(self):
        metaData = TR_MethodMetaData(gdb.newest_frame().read_var('metaData'))
        metaData.registerCompiled(gdb.newest_frame().read_var('compiler'))

        return True # Stop

CompiledCodeRegistar()


