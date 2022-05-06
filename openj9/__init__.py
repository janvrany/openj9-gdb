import sys
import gdb
import omr
import openj9.printing
import openj9.unwinder
import openj9.cli

from vdb.cli import pr, do

from openj9.utils import MethodInfo
from openj9.cli import uw, lm, dm, di

pr.prefixes.append('openj9')

class MethodInfoRegistrar(gdb.Breakpoint):
    def __init__(self):
        super().__init__("TR::CompilationInfoPerThreadBase::logCompilationSuccess", internal=False)

    def stop(self):
        metaData = gdb.newest_frame().read_var('metaData')
        compiler = gdb.newest_frame().read_var('compiler')

        methodInfo = MethodInfo(metaData, compiler)
        methodInfo.registerCompiled()

        return True # Stop

# Install MethodInfoRegistrar if not already installed.
__registrar = None
for bp in gdb.breakpoints():
    if bp.__class__.__name__ == 'MethodInfoRegistrar':
        __registrar = bp
if __registrar == None:
    __registrar = MethodInfoRegistrar()


# Install automatic debugging hook
def autodebug(typ, value, tb):
    if False: # hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(typ, value, tb)
    else:
        import traceback, pdb
        # we are NOT in interactive mode, print the exception...
        if tb is None:
            print("EXECEPTION IN PYTHON CODE:")
            traceback.print_last()
        else:
            print("EXECEPTION IN PYTHON CODE, ENTERING DEBUGGER:")
            traceback.print_exception(typ, value, tb)
            # ...then start the debugger in post-mortem mode.
            # pdb.pm() # deprecated
            pdb.post_mortem(tb) # more "modern"

sys.excepthook = autodebug


