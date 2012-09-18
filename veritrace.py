#! /usr/bin/env python

import sys
import subprocess 

class TestCase :
    def __init__(self, clspath, clsname, mthds, thdNum, evtNum, prog, outf) :
        self.importPath = clspath
        self.classname = clsname
        self.methods = mthds
        self.threadNum = thdNum 
        self.traceLength = evtNum 
        self.testProgram = prog
        self.outFile = outf

    def __repr__(self) :
        if len(self.methods) <= 0 :
            return "Testing " + self.classname + ": no method is given."
        str = self.methods[0]
        if len(self.methods) > 1 :
            for s in self.methods[1:] :
                str = str + ", " + s 
        return "Testing " + self.classname + " (" + str + ") with " + repr(self.threadNum) + " threads." 

def parseCommandLine() :
    usage = "Usage: veritrace.py [-import <import path>] [-thread <thread number>] [-trace <trace length>] [-output <output file>] <class name> <method name 1> ... <method name n>" 
    if len(sys.argv) < 2 :
        print usage
        exit(0)
    else: 
        thdNum = 2
        trLeng = 100 
        path = []
        mthds = [] 
        clsname = ""
        outf = ""
        # tag = 0: class name; 1: method name; 2: import path; 3: thread number; 4: trace length; 5: output 
        tag = 0
        gotClass = False
        for s in sys.argv[1:] :
            if s[0] == "-" :
                if s[1:] == "import" :
                    tag = 2
                elif s[1:] == "thread" :
                    tag = 3 
                elif s[1:] == "trace" :
                    tag = 4
                elif s[1:] == "output" :
                    tag = 5
            else: 
                if tag == 0 :
                    clsname = s 
                    gotClass = True
                    tag = 1 
                elif tag == 1 :
                    mthds.append(s) 
                    if gotClass : 
                        tag = 1
                    else :
                        tag = 0
                elif tag == 2 :
                    path.append(s)
                    if gotClass : 
                        tag = 1
                    else :
                        tag = 0
                elif tag == 3 : 
                    thdNum = int(s) 
                    if gotClass : 
                        tag = 1
                    else :
                        tag = 0
                elif tag == 4 : 
                    trLeng = int(s) 
                    if gotClass : 
                        tag = 1
                    else :
                        tag = 0
                elif tag == 5 : 
                    outf = s 
                    if gotClass : 
                        tag = 1
                    else :
                        tag = 0

        if clsname == "" :
            print "Error: no test class is given!" 
            print usage
        elif mthds == [] :
            print "Error: no test method is given!" 
            print usage 
        prog = "testing" + clsname + ".java"
        return TestCase(path, clsname, mthds, thdNum, trLeng, prog, outf)

test = parseCommandLine ()

agentPath = "/Users/zhang/mycode/VeriTrace/jvmagent/TraceAgent.dylib"
testPath = "/Users/zhang/mycode/VeriTrace/test"
testProgram = "Testing" + test.classname 
if test.outFile == "" :
    agentArgs = "=" 
    testArgs = ""
else :
    agentArgs = "=" + test.outFile + "," 
    testArgs = "-" + test.outFile + " " 
agentArgs = agentArgs + repr(test.threadNum) + "," + repr(test.traceLength) + "," + test.classname 
testArgs = testArgs + repr(test.threadNum) + " " + repr(test.traceLength) + " " + test.classname 
for methodName in test.methods:
    agentArgs = agentArgs + "," + methodName 
    testArgs = testArgs + " " + methodName 
testCommand = "java -agentpath:" + agentPath + agentArgs + " -classpath " + testPath + " " + testProgram + " " + testArgs 
print testCommand
subprocess.call(testCommand, shell=True)
