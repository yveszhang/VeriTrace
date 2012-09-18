JDK_HOME = /Library/Java/JavaVirtualMachines/jdk1.7.0_06.jdk/Contents/Home
JAVA_HOME = /System/Library/Frameworks/JavaVM.framework/Versions/Current

C = g++
CXX = g++
OPT = -O2
DEBUG = -g
INCDIR = -I.
LIBDIR = -L.
CFLAGS = -Wall -DSC_INCLUDE_FX  

JDK_INCL = -I$(JDK_HOME)/include -I$(JDK_HOME)/include/darwin
DYLIB_FLAGS = -dynamiclib -flat_namespace -undefined suppress 

CXXCOMPILE = $(CXX) -c $(CFLAGS) $(INCDIR) $(LIBDIR) $(JDK_INCL)
CXXLINK = $(CXX) $(CFLAGS) $(LIBDIR) $(DYLIB_FLAGS)
LIBS = -lm 


EXEC = TraceAgent.dylib
HEADS = 
IMPLS = $(HEADS:.h=.cpp) 
SRCS = Main.cpp $(IMPLS)
OBJS = $(SRCS:.cpp=.o)
COMMON = 

all: $(EXEC)

$(EXEC): $(OBJS)
	$(CXXLINK) -o $(EXEC) $(OBJS) $(LIBS) 

Main.o: Main.cpp $(HEADS) $(COMMON)
	$(CXXCOMPILE) -o $@ $<

%.o: %.cpp %.h $(COMMON)
	$(CXXCOMPILE) -o $@ $< 

clean:
	rm $(EXEC) $(OBJS) *~ 