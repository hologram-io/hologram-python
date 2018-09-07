# Makefile template for shared library

CC = gcc # C compiler
CXX = g++
CFLAGS = $(CFLAGS) -std=c11 -fPIC -Wall -Wextra -O2 # C flags
CXXFLAGS = $(CXXFLAGS) -std=cxx17 -fPIC -Wall -Wextra -O2 # C flags
LDFLAGS = $(LDFLAGS) -shared  # linking flags
RM = rm -f  # rm command
TARGET_LIB = libHologramCloud.so # target lib

SRCS = HologramCloud.cpp HologramException.cpp # source files
OBJS = $(SRCS:.c=.o)

.PHONY: all
all: ${TARGET_LIB}

$(TARGET_LIB): $(OBJS)
	$(CXX) ${LDFLAGS} -o $@ $^

$(SRCS:.c=.d):%.d:%.c
	$(CXX) $(CXXFLAGS) -MM $< >$@

include $(SRCS:.c=.d)

.PHONY: clean
clean:
-${RM} ${TARGET_LIB} ${OBJS} $(SRCS:.c=.d)