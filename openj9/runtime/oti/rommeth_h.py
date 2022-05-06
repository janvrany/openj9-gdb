from vdb.utils.C import *
from omr.include_core.omrcomp_h import *
from openj9.runtime.oti.j9modifiers_api_h import *

#define J9EXCEPTIONINFO_HANDLERS(info) ((J9ExceptionHandler *) (((U_8 *) (info)) + sizeof(J9ExceptionInfo)))
def J9EXCEPTIONINFO_HANDLERS(info):
    return (info.cast(U_8_ptr) + sizeof('J9ExceptionInfo')).cast(gdb.lookup_type('J9ExceptionHandler').pointer())

#define J9_BYTECODE_START_FROM_ROM_METHOD(romMethod) (((U_8 *) (romMethod)) + sizeof(J9ROMMethod))
def J9_BYTECODE_START_FROM_ROM_METHOD(romMethod):
    return romMethod.cast(U_8_ptr) + sizeof('J9ROMMethod')

#define J9_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod) \
#    (((UDATA) (romMethod)->bytecodeSizeLow) + (((UDATA) (romMethod)->bytecodeSizeHigh) << 16))
def J9_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod):
    return romMethod['bytecodeSizeLow'] + (romMethod['bytecodeSizeHigh'] << 16)

#define J9_ROUNDED_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod) ((J9_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod) + 3) & ~(UDATA)3)
def J9_ROUNDED_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod):
    return ((J9_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod) + 3) & ~3)

def J9_EXTENDED_MODIFIERS_ADDR_FROM_ROM_METHOD(romMethod):
    return (J9_BYTECODE_START_FROM_ROM_METHOD(romMethod) + J9_ROUNDED_BYTECODE_SIZE_FROM_ROM_METHOD(romMethod)).cast(U_32_ptr)

#define J9_GENERIC_SIG_ADDR_FROM_ROM_METHOD(romMethod)
def J9_GENERIC_SIG_ADDR_FROM_ROM_METHOD(romMethod):
    if J9ROMMETHOD_HAS_EXTENDED_MODIFIERS(romMethod):
        return J9_EXTENDED_MODIFIERS_ADDR_FROM_ROM_METHOD(romMethod) + 1
    else:
        return J9_EXTENDED_MODIFIERS_ADDR_FROM_ROM_METHOD(romMethod)

#define J9_EXCEPTION_DATA_FROM_ROM_METHOD(romMethod) ((J9ExceptionInfo *) (J9_GENERIC_SIG_ADDR_FROM_ROM_METHOD(romMethod) + (J9ROMMETHOD_HAS_GENERIC_SIGNATURE(romMethod) ? 1 : 0)))
def J9_EXCEPTION_DATA_FROM_ROM_METHOD(romMethod):
    if J9ROMMETHOD_HAS_GENERIC_SIGNATURE(romMethod):
        exceptionInfo = J9_GENERIC_SIG_ADDR_FROM_ROM_METHOD(romMethod) + 1
    else:
        exceptionInfo = J9_GENERIC_SIG_ADDR_FROM_ROM_METHOD(romMethod)
    return exceptionInfo.cast(gdb.lookup_type('J9ExceptionInfo').pointer())

