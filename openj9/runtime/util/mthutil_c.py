import gdb

from omr.include_core.omrcomp_h import *

from openj9.runtime.oti.j9modifiers_api_h import *
from openj9.runtime.oti.rommeth_h import *


def getExtendedModifiersDataFromROMMethod(romMethod):
    extendedModifiers = gdb.Value(0)
    if J9ROMMETHOD_HAS_EXTENDED_MODIFIERS(romMethod):
        extendedModifiers = J9_EXTENDED_MODIFIERS_ADDR_FROM_ROM_METHOD(romMethod).dereference()
    return extendedModifiers

def methodAnnotationsDataFromROMMethod(romMethod):
    result = None

    exceptionInfo = J9_EXCEPTION_DATA_FROM_ROM_METHOD(romMethod)

    if J9ROMMETHOD_HAS_EXCEPTION_INFO(romMethod):
        result = J9EXCEPTIONINFO_THROWNAMES(exceptionInfo) + exceptionInfo['throwCount']
    else:
        result = exceptionInfo
    return result.cast(U_32_ptr)

def parameterAnnotationsFromROMMethod(romMethod):
    annotation = methodAnnotationsDataFromROMMethod(romMethod)
    result = None

    if J9ROMMETHOD_HAS_ANNOTATIONS_DATA(romMethod):
        result = SKIP_OVER_LENGTH_DATA_AND_PADDING(annotation)
    else:
        result = annotation
    return result.cast(U_32_ptr)

def defaultAnnotationFromROMMethod(romMethod):
    annotation = parameterAnnotationsFromROMMethod(romMethod)
    result = None

    if J9ROMMETHOD_HAS_PARAMETER_ANNOTATIONS(romMethod):
        result = SKIP_OVER_LENGTH_DATA_AND_PADDING(annotation)
    else:
        result = annotation
    return result.cast(U_32_ptr)

def methodTypeAnnotationsFromROMMethod(romMethod):
    annotation = defaultAnnotationFromROMMethod(romMethod)
    result = None

    if J9ROMMETHOD_HAS_DEFAULT_ANNOTATION(romMethod):
        result = SKIP_OVER_LENGTH_DATA_AND_PADDING(annotation)
    else:
        result = annotation
    return result.cast(U_32_ptr)


def codeTypeAnnotationsFromROMMethod(romMethod):
    annotation = methodTypeAnnotationsFromROMMethod(romMethod)
    result = None

    if J9ROMMETHOD_HAS_METHOD_TYPE_ANNOTATIONS(getExtendedModifiersDataFromROMMethod(romMethod)):
        result = SKIP_OVER_LENGTH_DATA_AND_PADDING(annotation)
    else:
        result = annotation
    return result.cast(U_32_ptr)
