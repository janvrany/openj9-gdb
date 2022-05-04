#
# This makefile is provisional, should be replaced with
# autoconf / cmake.
#

JAVA_BINARIES ?= ../openj9-openjdk-jdk11/build/linux-riscv64-normal-server-slowdebug/images/jdk/bin/java

JAVA_SCRIPTS=$(patsubst %,%-gdb.py,$(JAVA_BINARIES))

all: $(JAVA_SCRIPTS)

$(JAVA_SCRIPTS): java-gdb.py.in
	sed -e "s#@OPENJ9_GDB_DIR@#$(shell realpath $(shell dirname $<))#g" $< > $@

clean:
	rm $(JAVA_SCRIPTS)