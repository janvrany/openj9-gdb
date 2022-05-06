from openj9.runtime.oti.j9javaaccessflags_h import *
from openj9.runtime.oti.cfr_h import *

def _J9_ARE_ALL_BITS_SET(testedModifiers):
    def __J9_ARE_ALL_BITS_SET(actualModifiers):
        return (int(actualModifiers) & int(testedModifiers)) == int(testedModifiers)
    return __J9_ARE_ALL_BITS_SET

def _J9_ARE_ANY_BITS_SET(testedModifiers):
    def _J9_ARE_ANY_BITS_SET(actualModifiers):
        return (int(actualModifiers) & int(testedModifiers)) != 0
    return _J9_ARE_ANY_BITS_SET

#define _J9ROMCLASS_J9MODIFIER_IS_SET(romClass,j9Modifiers) \
#                J9_ARE_ALL_BITS_SET((romClass)->extraModifiers, j9Modifiers)
#define _J9ROMCLASS_J9MODIFIER_IS_ANY_SET(romClass,j9Modifiers) \
#                J9_ARE_ANY_BITS_SET((romClass)->extraModifiers, j9Modifiers)

#define _J9ROMMETHOD_J9MODIFIER_IS_SET(romMethod,j9Modifiers) \
#                J9_ARE_ALL_BITS_SET((romMethod)->modifiers, j9Modifiers)
def _J9ROMMETHOD_J9MODIFIER_IS_SET(j9Modifiers):
    def __J9ROMMETHOD_J9MODIFIER_IS_SET(romMethod):
        return (int(romMethod['modifiers']) & int(j9Modifiers) ) == int(j9Modifiers)
    return __J9ROMMETHOD_J9MODIFIER_IS_SET

def _J9ROMMETHOD_J9MODIFIER_IS_ANY_SET(j9Modifiers):
    def __J9ROMMETHOD_J9MODIFIER_IS_ANY_SET(romMethod):
        return (int(romMethod['modifiers']) & int(j9Modifiers) ) != 0
    return __J9ROMMETHOD_J9MODIFIER_IS_ANY_SET

def _J9ROMMETHOD_J9EXTENDEDMODIFIER_IS_SET(j9Modifiers):
    def __J9ROMMETHOD_J9EXTENDEDMODIFIER_IS_SET(romMethod):
        return (int(__getExtendedModifiersDataFromROMMethod(romMethod)) & int(j9Modifiers) ) == int(j9Modifiers)
    return __J9ROMMETHOD_J9MODIFIER_IS_SET

def _J9ROMMETHOD_J9EXTENDEDMODIFIER_IS_ANY_SET(j9Modifiers):
    def __J9ROMMETHOD_J9EXTENDEDMODIFIER_IS_ANY_SET(romMethod):
        return (int(__getExtendedModifiersDataFromROMMethod(romMethod)) & int(j9Modifiers) ) != 0
    return __J9ROMMETHOD_J9MODIFIER_IS_ANY_SET



#define _J9ROMMETHOD_J9MODIFIER_IS_ANY_SET(romMethod,j9Modifiers) \
#                J9_ARE_ANY_BITS_SET((romMethod)->modifiers, j9Modifiers)

#define _J9ROMCLASS_SUNMODIFIER_IS_SET(romClass,sunModifiers) \
#                J9_ARE_ALL_BITS_SET((romClass)->modifiers, sunModifiers)
#define _J9ROMCLASS_SUNMODIFIER_IS_ANY_SET(romClass,sunModifiers) \
#                J9_ARE_ANY_BITS_SET((romClass)->modifiers, sunModifiers)


J9ROMMETHOD_IS_GETTER = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.GetterMethod)
J9ROMMETHOD_IS_FORWARDER = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.ForwarderMethod)
J9ROMMETHOD_IS_EMPTY = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.EmptyMethod)
J9ROMMETHOD_HAS_VTABLE = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodVTable)
J9ROMMETHOD_HAS_EXCEPTION_INFO = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasExceptionInfo)
J9ROMMETHOD_HAS_DEBUG_INFO = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasDebugInfo)
J9ROMMETHOD_HAS_BACKWARDS_BRANCHES = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasBackwardBranches)
J9ROMMETHOD_HAS_GENERIC_SIGNATURE = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasGenericSignature)
J9ROMMETHOD_HAS_STACK_MAP = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasStackMap)
J9ROMMETHOD_HAS_ANNOTATIONS_DATA = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasMethodAnnotations)
J9ROMMETHOD_HAS_PARAMETER_ANNOTATIONS = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasParameterAnnotations)
J9ROMMETHOD_HAS_METHOD_PARAMETERS = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasMethodParameters)
J9ROMMETHOD_HAS_CODE_TYPE_ANNOTATIONS = _J9_ARE_ALL_BITS_SET(CFR_METHOD_EXT_HAS_CODE_TYPE_ANNOTATIONS)
J9ROMMETHOD_HAS_METHOD_TYPE_ANNOTATIONS = _J9_ARE_ALL_BITS_SET(CFR_METHOD_EXT_HAS_METHOD_TYPE_ANNOTATIONS)
J9ROMMETHOD_HAS_SCOPED_ANNOTATION = _J9_ARE_ALL_BITS_SET(CFR_METHOD_EXT_HAS_SCOPED_ANNOTATION)
J9ROMMETHOD_HAS_DEFAULT_ANNOTATION = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasDefaultAnnotation)
J9ROMMETHOD_HAS_EXTENDED_MODIFIERS = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodHasExtendedModifiers)
J9ROMMETHOD_IS_OBJECT_CONSTRUCTOR = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodObjectConstructor)
J9ROMMETHOD_IS_CALLER_SENSITIVE = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.MethodCallerSensitive)
J9ROMMETHOD_IS_STATIC = _J9ROMMETHOD_J9MODIFIER_IS_SET(J9Acc.Static)

