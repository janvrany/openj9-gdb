# Copyright (c) 2022 Jan Vrany
#
# This program and the accompanying materials are made available under
# the terms of the MIT license, see LICENSE file.
#
# SPDX-License-Identifier: MIT

"""
This module contains a JIT stack unwinder for OpenJ9

References:

 [1]: https://sourceware.org/gdb/current/onlinedocs/gdb/Unwinding-Frames-in-Python.html#Unwinding-Frames-in-Python
 [2]: https://github.com/tromey/spidermonkey-unwinder
 [3]: http://icedtea.classpath.org/people/adinn/unwinder/file/f50e52519fb9
#

"""

import re
import gdb
import gdb.unwinder

from functools import lru_cache as cache
from collections import namedtuple

def _lookup_jit_method_by_pc(pc):
    for objf in gdb.objfiles():
        if hasattr(objf, 'j9method'):
            j9mthd = getattr(objf, 'j9method')
            if j9mthd.startPC <= pc and pc <= j9mthd.endPC:
                return j9mthd
    return None

def _lookup_jit_helper_by_pc(pc):
    """
    Return gdb.Symbol representing the helper at given PC
    or None, if no helper is at that PC.
    """

    # ...helpers are in libj9jit29.so...
    library = gdb.current_progspace().solib_name(int(pc))
    if library == None or not library.endswith('libj9jit29.so'):
        return None

    # ...and implemented in assembly so there's no debug info.
    # Therefore GDB is not able to find a function for the PC,
    # if it is, it's not helper.
    block = gdb.current_progspace().block_for_pc(int(pc))
    if block != None and block.function != None:
        return None

    # As there's no Python access to minimal symbols, hack
    # around it by parsing output of gdb.format_address().
    # Sigh!
    searcher = re.compile("<([^+>]+)\+?[0-9]*>")
    match = searcher.search(gdb.format_address(int(pc)))
    if match != None:
        return gdb.lookup_global_symbol(match.group(1))

    return None

class UnwindInfo(object):
    """
    This is a simple mock of GDB's UnwindInfo class that
    can be used to test Unwinder interactively. Just pass
    gdb.Frame as a pending_frame to unwinder.
    """

    def __init__(self, id):
        self.id = id
        self.regs = {}

    def add_saved_register(self, reg, value):
        self.regs[reg] = value

    def __str__(self):
        return "<unwind info: CFA 0x%016x PC 0x%016x>" % ( int(self.id.sp), int(self.id.pc) )

class FrameId(object):
    """
    A helper class used by GDB to identify a frame, see [1]

    [1]: https://sourceware.org/gdb/current/onlinedocs/gdb/Unwinding-Frames-in-Python.html#Unwinding-Frames-in-Python

    """
    def __init__(self, sp, pc):
        self.sp = sp
        self.pc = pc

JITPrologueInfo = namedtuple('PrologueInfo', ['jitEntry', 'frameAllocd', 'frameBuilt'])

class JITFrameInfo(object):
    def __init__(self, pc, method = None):
        self.pc = pc
        if method == None:
            method = _lookup_jit_method_by_pc(pc)
            assert method != None, "No method for given PC: %s" % hex(pc)
        self.method = method

    def create_prologue_info(self):
        jitEntry = self.method.startPC + self.method.numParamSlots() * 4
        frameAllocd = jitEntry + 4 + 4
        frameBuilt = frameAllocd # FIXME!!!
        return JITPrologueInfo(jitEntry=jitEntry, frameAllocd=frameAllocd, frameBuilt=frameBuilt)


    def create_unwind_info(self, pending_frame):
        # First, compute SP (frame pointer in fact) and RA (return address)
        # register values.
        #
        # As for SP: cannot just read SP register as we may be in the middle
        # of prologue and (or epilogue) therefore SP register value may
        # not yet / no longer contain SP for this frame.
        #
        # As for RA: if we're in prologue, we may must read RA from register
        # as it may not yet be stored in a frame. Else, we read it from frame
        # as it may have been clobbered by some call done by the method.
        #
        # FIXME: Here we assume that SP is constant though the
        # lifetime of if the frame. Validate.
        #
        # NOTE: OpenJ9 uses s11 as java stack pointer, see RVPrivateLinkage.cpp
        #
        # NOTE: We define method frame's CFA as the value of SP (s11) once the
        #       frame is built. This is unusual, but matches what's in (some) OpenJ9
        #       code is called (java) BP (base pointer)
        #
        # NOTE: Here we assume the prologue is always in the same form:
        #
        # intEntry:
        #   0x0000003f5b636024 <+0>:     ld  a0,0(s11)    ; load this from (java) stack into regs
        #                                                 ; ...load arguments if any into regs
        # jitEntry:
        #   0x0000003f5b636028 <+4>:     sd  ra,-8(s11)   ; store return address to frame (SP not adjusted)
        #   0x0000003f5b63602c <+8>:     addi s11,s11,-16 ; allocate frame of 16 bytes (RA + this)
        #   0x0000003f5b636030 <+12>:    ld  t3,80(s10)   ; stack check
        #   0x0000003f5b636034 <+16>:    blt s11,t3,0x3f5b636048
        #   0x0000003f5b636038 <+20>:    sd  a0,16(s11)   ; store this into frame
        #                                                 ; ...store preserved (callee-saved) if any registers into frame
        #                                                 ; ...store arguments if any into frame
        #
        # NOTE: Also, we assume that return is always in the same form:
        #
        #  0x0000003f5b63605c <+56>:    ...               ; reload of preserved (callee-saved) regs
        #  0x0000003f5b636060 <+60>:    ld  s1,24(s11)    ; dtto
        #  0x0000003f5b636064 <+64>:    addi    s11,s11,48; destroy frame
        #  0x0000003f5b636068 <+68>:    ld  ra,-8(s11)    ; reload return address
        #  0x0000003f5b63606c <+72>:    ret               ; return
        #
        # This return sequence can be inlined into the code multiple times.

        num_frame_slots = self.method.numFrameSlots()
        num_param_slots = self.method.numParamSlots()

        frame_size_in_bytes = num_frame_slots*8 + 8

        prologue = self.create_prologue_info()

        if self.pc < prologue.frameAllocd:
            # We're inside the prologue before the frame is allocated and SP (s11) adjusted
            cfa = pending_frame.read_register('s11') - frame_size_in_bytes
            ra = pending_frame.read_register('ra')
        else:
            try:
                maybe_ret = bytes(gdb.selected_inferior().read_memory(self.pc + 4, 4))
            except gdb.MemoryError:
                maybe_ret = None
            if maybe_ret == b'\x67\x80\x00\x00':
                # We're inside epilogue after frame has been destoyed and SP (s11) adjusted
                cfa = pending_frame.read_register('s11') + frame_size_in_bytes
            else:
                # We're somewhere in between...
                cfa = pending_frame.read_register('s11')
            ra = cfa.cast(cfa.type.pointer())[num_frame_slots]

        # Ugh, this is hacky. Since OpenJ9 uses continuation-passing style. In case returning from
        # interpreter.  return address is "faked" and points to "return trampoline" and not past
        # the call to JITed code (which is done in c_cInterpreter).
        #
        # Here we have two options - unwind to frame JITted code was called from (c_cInterpreter)
        # or to frame for that "return trampoline" which is the code that will be executing once
        # this JITted code returns.
        #
        # Here we decided to go for the first option, assuming the person debugging is more interested
        # in "how on earth I got here" rather than "where would I go if I continue from here".
        helper = _lookup_jit_helper_by_pc(ra)
        if helper != None and helper.name.startswith('returnFromJIT'):
            # Okay, this JITed method have been called from interpreter.
            # "Fake" the return address back to point to c_cInterpreter from where
            # this method have been called.
            jalr_offset = 0x3ff7cf98e2 - 0x3ff7cf98b0 # Magic constant :-)
            jarl_address = int(gdb.lookup_global_symbol('cInterpreter').value().address) + jalr_offset
            ra = gdb.Value(jarl_address)


        id = FrameId(cfa, self.pc)
        if hasattr(pending_frame, 'create_unwind_info'):
            ui = pending_frame.create_unwind_info(id)
        else:
            ui = UnwindInfo(id)

        # Now, for each (preserved) register overwritten
        # in THIS frame we have to `add_save_register()`
        # with CALLER's register value. See [1]:
        #
        #    Use `add_saved_register()` to specify caller registers
        #    that have been saved in this frame.
        #
        # [1]: https://sourceware.org/gdb/current/onlinedocs/gdb/Unwinding-Frames-in-Python.html#Unwinding-Frames-in-Python
        #
        ui.add_saved_register('s11', cfa + frame_size_in_bytes)
        ui.add_saved_register('ra',  ra)
        ui.add_saved_register('pc',  ra)
        ui.add_saved_register('sp',  pending_frame.read_register('sp'))

        return ui

class JITUnwinder(gdb.unwinder.Unwinder):
    """
    Custom unwinder to unwind JIT-compiled methods.
    """
    def __init__(self):
        super().__init__('OpenJ9-JIT')

    def sniff(self, pending_frame):
        """
        Tries to 'sniff' on a pending_frame and if it looks like
        a JIT frame, return a FrameInfo. Otherwise, return None
        """

        # for now, only RV64 is supported...
        assert pending_frame.architecture().name() == 'riscv:rv64'

        pc = pending_frame.read_register('pc')
        method = _lookup_jit_method_by_pc(pc)
        if method != None:
            return JITFrameInfo(pc, method)
            return None

    def __call__(self, pending_frame):
        """
        The main unwinding method. It examines (sniffs at) a given frame and returns
        an object (an instance of gdb.UnwindInfo class) describing it. If
        an unwinder does not recognize a frame, it should return None.
        """
        fi = self.sniff(pending_frame)
        if fi == None:
            return None
        else:
            return fi.create_unwind_info(pending_frame)

# register the unwinders (globally):
gdb.unwinder.register_unwinder(None, JITUnwinder(), True)











