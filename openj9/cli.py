# Copyright (c) 2022 Jan Vrany
#
# This program and the accompanying materials are made available under
# the terms of the MIT license, see LICENSE file.
#
# SPDX-License-Identifier: MIT

"""
OpenJ9 specific commands
"""
import gdb
import re

class __Unwind(gdb.Command):
    """
    Tries to unwind frame using registered unwinders
    Used mainly for debugging the unwinder.
    Usage: uw [FRAMENO]

    [FRAMENO] is frame number to unwind. If not specified, unwinds current frame.
    """
    def __init__(self):
        super().__init__('uw', gdb.COMMAND_MAINTENANCE)

    def invoke (self, args, from_tty):
        frameno = None

        argv = gdb.string_to_argv(args)
        if len(argv) == 1:
            try:
                frameno = int(argv[0])
            except:
                raise Exception("not a valid number ('%s')" % argv[0])
        elif len(argv) > 1:
            raise Exception("uw takes only one argument (%d given)" % len(argv))

        unwindinfo = self(frameno)
        if unwindinfo is None:
            print("All Python unwinders failed (none succeeded to unwind)")
        else:
            print(unwindinfo)
            if hasattr(unwindinfo, 'regs'):
                print('saved registers:')
                regs = getattr(unwindinfo, 'regs')
                for name in regs:
                    print("  %-5s: %s" % ( name, hex(regs[name])))

    def __call__(self, frameno = None):
        if frameno == None:
            frame = gdb.selected_frame()
        else:
            frame = gdb.newest_frame()
            for i in range(0, frameno):
                frame = frame.older()
        for unwinder in gdb.current_progspace().frame_unwinders + gdb.frame_unwinders:
            if unwinder.enabled or True:
                unwindinfo = unwinder(frame)
                if unwindinfo != None:
                    return unwindinfo
        return None

uw = __Unwind()

class __LookupMethod(gdb.Command):
    """
    Looks up a method containing given PC or matching given REGEXP.
    Usage: ls [PC]
           ls REGEXP

    PC can be given as an expression evaluating to an address
    or omitted in which case value if $pc (PC of currently
    selected frame) is used.

    If REGEXP is given, all methods whose name matches
    given regexp are looked up and printed.
    """
    def __init__(self):
        super().__init__('lm', gdb.COMMAND_DATA)

    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)
        if len(argv) > 1:
            raise Exception("ls takes only one argument (%d given)" % len(argv))
        elif len(argv) == 0:
            argv = ['$pc']
        any_found = False
        for method in self(argv[0]):
            any_found = True
            print("0x%016x - 0x%016x '%s'" % (method.startPC, method.endPC, method.name))
        if not any_found:
            print("No method found.")

    def __call__(self, pc_or_regexp = '$pc'):
        pc = None
        regexp = None
        try:
            pc = None
            if isinstance(pc_or_regexp, int):
                pc = pc_or_regexp
            elif isinstance(pc_or_regexp, gdb.Value):
                pc = int(pc)
            elif isinstance(pc_or_regexp, str):
                pc = gdb.parse_and_eval(pc_or_regexp)
            else:
                raise InvalidArgument("pc_or_regexp must be an int, str, or gdb.Value")
        except:
            regexp = re.compile(pc_or_regexp)

        def matches(method):
            if pc != None:
                return  method.startPC <= pc and pc <= method.endPC
            elif regexp != None:
                return regexp.search(method.name)
            else:
                return True

        methods = (getattr(objf, 'j9method') for objf in gdb.objfiles() if hasattr(objf, 'j9method'))
        matching = [method for method in methods if matches(method)]

        return matching

lm = __LookupMethod()

class __DumpInstructions(gdb.Command):
    def __init__(self):
        super().__init__('di', gdb.COMMAND_DATA)

    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)
        if len(argv) != 0:
            raise Exception("di takes no arguments (%d given)" % len(argv))
        self()

    def _dump1(self, insn):
        pc = int(insn['_binaryEncodingBuffer'])
        sz = int(insn['_binaryLength'])

        if sz > 0:
            node = insn['_node']

            disassmInfo = gdb.selected_inferior().architecture().disassemble(pc)

            def shorten(string, maxlen):
                if len(string) > maxlen:
                    return string[0:maxlen-3].replace('\t', ' ') + '...'
                else:
                    return string.replace('\t', ' ')

            print("0x%016x  %-30s IL %s" %( pc, shorten(disassmInfo[0]['asm'], 30), gdb.default_visualizer(node).to_string()))

    def __call__(self):
        comp = gdb.selected_frame().read_var('compiler')
        insn = comp['_codeGenerator']['_firstInstruction']
        while (int(insn) != 0): # while insn != nullptr
            self._dump1(insn)
            insn = insn['_next']

di = __DumpInstructions()


