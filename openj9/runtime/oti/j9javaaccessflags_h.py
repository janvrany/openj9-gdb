
from enum import IntFlag

class J9Acc(IntFlag):
    Abstract = 0x400
    Annotation = 0x2000
    Bridge = 0x40

    ClassHasIdentity = 0x20
    ClassIsValueBased = 0x40
    ClassHiddenOptionNestmate = 0x80
    ClassHiddenOptionStrong = 0x100
    ClassAnnnotionRefersDoubleSlotEntry = 0x80000
    ClassAnonClass = 0x800
    ClassArray = 0x10000
    ClassBytecodesModified = 0x100000
    ClassCloneable = 0x80000000
    ClassCompatibilityMask = 0x7FFF
    ClassDepthMask = 0xFFFF
    ClassDying = 0x8000000
    ClassFinalizeNeeded = 0x40000000
    ClassGCSpecial = 0x800000
    ClassHasBeenOverridden = 0x100000
    ClassHasClinit = 0x4000000
    ClassHasEmptyFinalize = 0x200000
    ClassIsUnmodifiable = 0x400000
    ClassHasFinalFields = 0x2000000
    ClassHasJDBCNatives = 0x400000
    ClassHasNonStaticNonAbstractMethods = 0x8000000
    ClassHasVerifyData = 0x800000
    ClassHotSwappedOut = 0x4000000
    ClassInnerClass = 0x4000
    ClassHidden = 0x8000
    ClassNeedsStaticConstantInit = 0x10000
    ClassIntermediateDataIsClassfile = 0x20000
    ClassInternalPrimitiveType = 0x20000
    ClassIsContended = 0x1000000
    ClassOwnableSynchronizer = 0x200000
#define J9AccClassUnused200 0x200
#define J9AccClassUnused400 0x400
    ClassRAMArray = 0x10000
    ClassRAMShapeShift = 0x10
    ClassReferenceMask = 0x30000000
    ClassReferencePhantom = 0x30000000
    ClassReferenceShift = 0x1C
    ClassReferenceSoft = 0x20000000
    ClassReferenceWeak = 0x10000000
    ClassRomToRamMask = 0xF3000000
    ClassUnsafe = 0x40000
    ClassUseBisectionSearch = 0x2000
    EmptyMethod = 0x4000
    Enum = 0x4000
    Final = 0x10
    ForwarderMethod = 0x2000
    GetterMethod = 0x200
    Interface = 0x200
    Mandated = 0x8000
    MethodCallerSensitive = 0x100000
    MethodAllowFinalFieldWrites = 0x1000000
    MethodFrameIteratorSkip = 0x80000
    MethodHasBackwardBranches = 0x200000
    MethodHasDebugInfo = 0x40000
    MethodHasDefaultAnnotation = 0x80000000
    MethodHasExceptionInfo = 0x20000
    MethodHasExtendedModifiers = 0x4000000
    MethodHasGenericSignature = 0x2000000
    MethodHasMethodAnnotations = 0x20000000
    MethodHasMethodHandleInvokes = 0x8000000
    MethodHasMethodParameters = 0x800000
    MethodHasParameterAnnotations = 0x40000000
    MethodHasStackMap = 0x10000000
    MethodHasTypeAnnotations = 0x4000000
    MethodObjectConstructor = 0x400000
#define J9AccMethodReturn0 0x0
#define J9AccMethodReturn1 0x40000
#define J9AccMethodReturn2 0x80000
    MethodReturnA = 0x140000
    MethodReturnD = 0x100000
    MethodReturnF = 0xC0000
    MethodReturnMask = 0x1C0000
    MethodReturnShift = 0x12
    MethodVTable = 0x10000
    Native = 0x100
    Private = 0x2
    Protected = 0x4
    Public = 0x1
    Static = 0x8
    Strict = 0x800
    Super = 0x20
    Synchronized = 0x20
    Synthetic = 0x1000
    Transient = 0x80
    ValueType = 0x100
    VarArgs = 0x80
    Volatile = 0x40
    PermitsValue = 0x40
    Record = 0x400
    Sealed = 0x200
    PrimitiveValueType = 0x800
#define J9StaticFieldRefBaseType 0x1
#define J9StaticFieldRefDouble 0x2
#define J9StaticFieldRefVolatile 0x4
#define J9StaticFieldRefBoolean 0x8
#define J9StaticFieldRefPutResolved 0x10
#define J9StaticFieldRefFinal 0x20
#define J9StaticFieldRefFlagBits 0x3F