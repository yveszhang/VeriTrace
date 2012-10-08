#! /usr/bin/env python

import sys
import subprocess 
import os
import veritest

class ParseError(Exception) : 
    def __init__(self, line, value) : 
        self.line = line
        self.value = value
    def __str__(self) :
        if self.line > 0 :
            return ("Line " + repr(self.line) + ": " + self.value)
        else : 
            return (self.value)

def parseCommandLine() :
    usage = "Usage: veritrace.py [-verbose] [-repeat <test number>] <test configuration>" 
# [-import <import path>] [-thread <thread number>] [-trace <trace length>] [-output <output file>] <class name> <method name 1> ... <method name n>" 
    if len(sys.argv) < 2 :
        print usage
        exit(0)
    else: 
        hasTestConf = False 
        hasRepeat = False
        repeat = 1
        verb = False
        for s in sys.argv[1:] :
            if s[0] == "-" :
                if s[1:] == "repeat" :
                    if hasRepeat : 
                        print usage 
                    else :
                        repeat = int(s) 
                        hasRepeat = True
                elif s[1:] == "verbose" :
                    verb = True 
                else :
                    print usage 
            else :
                if hasTestConf :
                    print usage 
                else : 
                    testcase = veritest.parseTestConfig(s) 
                    hasTestConf = True
        if hasTestConf :
            testcase.repeat = repeat 
            testcase.verbose = verb
            return testcase 
        else : 
            print usage

try : 
    vtHomePath = os.environ['VT_HOME'].rstrip("/ ")
except KeyError:
    print "Please set the VT_HOME environment variable!" 
    exit(0)
if vtHomePath == "" :
    print "Please set the VT_HOME environment variable!" 
    exit (0) 

agentPath = vtHomePath + "/jvmagent/TraceAgent.dylib"
testPath = vtHomePath + "/test"
scalaPath = vtHomePath + "/serialize"
logPath = vtHomePath + "/tracelog"

try : 
    test = parseCommandLine ()
except ParseError as err :
    print "Parse error: " + str(err)
    exit(0)

print veritest.generateTestJavaSource(test)

# print "Threads: " + str(test.threadNum) 
# print "Trace: " + str(test.traceLength)
# print "Classname: " + test.classname
# print "Classpath: " + test.classpath
# print "Logfile: " + test.outFile
# for m in test.methods :
#     print "Method: " + m[0] + ", " + repr(m[1]) + ", " + m[2]

# testProgram = "Testing" + test.classname 
# outNames = map((lambda x: test.outFile + "_%d_%d_%05d" % (test.threadNum, test.traceLength, x)), range(0, test.repeat))
# for name in outNames:
#     if test.outFile == "" :
#         agentArgs = "=" 
#         testArgs = ""
#     else :
#         agentArgs = "=" + logPath + "/" + name + ","  
#         testArgs = "-" + logPath + "/" + name + " "
#     agentArgs = agentArgs + repr(test.threadNum) + "," + repr(test.traceLength) + "," + test.classname 
#     testArgs = testArgs + repr(test.threadNum) + " " + repr(test.traceLength) + " " + test.classname 
#     for methodName in test.methods:
#         agentArgs = agentArgs + "," + methodName 
#         testArgs = testArgs + " " + methodName 
#     testCommand = "java -agentpath:" + agentPath + agentArgs + " -classpath " + testPath + " " + testProgram + " " + testArgs 
#     subprocess.call(testCommand, shell=True)


# if test.outFile != "" :
#     os.chdir(scalaPath) 
#     if test.verbose :
#         verifCommand = "scala Serialize -v " + logPath + "/" 
#     else : 
#         verifCommand = "scala Serialize " + logPath + "/" 
#     caseNo = 1
#     for name in outNames: 
#         res = subprocess.check_output(verifCommand+name, shell=True)
#         print "Test case #" + str(caseNo) + ": " + res,
#         caseNo += 1
