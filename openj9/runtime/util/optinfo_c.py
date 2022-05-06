import gdb


from openj9.runtime.oti.j9modifiers_api_h import *
from openj9.runtime.util.mthutil_c import *



def methodDebugInfoFromROMMethod(romMethod):
    annotation = codeTypeAnnotationsFromROMMethod(romMethod)
    result = None

    # skip the TypeAnnotations section if there is some
    if J9ROMMETHOD_HAS_CODE_TYPE_ANNOTATIONS(getExtendedModifiersDataFromROMMethod(romMethod)):
        result = SKIP_OVER_LENGTH_DATA_AND_PADDING(annotation)
    else:
        result = annotation
    return result.cast(gdb.lookup_type('J9MethodDebugInfo').pointer())

def getMethodDebugInfoFromROMMethod(romMethod):
    if (J9ROMMETHOD_HAS_DEBUG_INFO(romMethod)):
        debugInfo = methodDebugInfoFromROMMethod(romMethod);
        return debugInfo
    return None

def getMethodDebugInfoStructureSize(methodDebugInfo):
    if 1 == (int(methodDebugInfo['lineNumberCount']) & 0x1):
        return sizeof('J9MethodDebugInfo') + sizeof(U_8)
    else:
        return sizeof('J9MethodDebugInfo')

def getLineNumberTable(methodDebugInfo):
    if 0 != int(methodDebugInfo['lineNumberCount']):
        return methodDebugInfo.cast(U_8_ptr) + getMethodDebugInfoStructureSize(methodDebugInfo)
    return None

def getLineNumberCount(methodDebugInfo):
    if 0 == (int(methodDebugInfo['lineNumberCount']) & 1):
        return (int(methodDebugInfo['lineNumberCount']) >> 1) & 0x7FFF
    else:
        return int(methodDebugInfo['lineNumberCount']) >> 1

def getNextLineNumberFromTable(currentLineNumberPtr, previousLine, previousLoc):
    """
    Returns tuple: ( nextLineNumber, (line, bytecode PC) )
    """
    b1 = int(currentLineNumberPtr.dereference())
    if 0 == (b1 & 0x80):
        #/* 1 byte encoded : 0xxxxxyy */
        newLoc = previousLoc + ((b1 >> 2) & 0x1F)
        newLine = previousLine+ ( b1       & 0x3)
        newLineNumberPtr = currentLineNumberPtr + 1
    elif 0x80 == (b1 & 0xC0):
        m = 1 << (9 - 1)

        #/* 2 bytes encoded : 10xxxxxY YYYYYYYY */
        b2 = int((currentLineNumberPtr + 1).dereference())

        encoded = (b1 << 8) | b2

        ulineNumber = encoded & 0x1FF
        ilineNumber = (ulineNumber ^ m) - m # /* sign extend from 9bit */

        newLoc = previousLoc + ((encoded >> 9) & 0x1F);
        newLine = previousLine + ilineNumber;
        newLineNumberPtr = currentLineNumberPtr + 2
    else:
        raise Exception('Not implemented :-(')

    return ( newLineNumberPtr, ( newLine, newLoc ) )
