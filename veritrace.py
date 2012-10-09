#! /usr/bin/env python

import sys
import subprocess 
import os
from veritest import *

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
        getRepeat = False
        for s in sys.argv[1:] :
            if s[0] == "-" :
                if s[1:] == "repeat" :
                    if hasRepeat : 
                        print usage 
                    else :
                        getRepeat = True
                elif s[1:] == "verbose" :
                    verb = True 
                else :
                    print usage 
            elif getRepeat :
                repeat = int(s) 
                hasRepeat = True
                getRepeat = False
            else :
                if hasTestConf :
                    print usage 
                else : 
                    testcase = parseTestConfig(s) 
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

print "Threads: " + str(test.threadNum) 
print "Trace: " + str(test.traceLength)
print "Classname: " + test.classname
print "Classpath: " + test.importpath
print "Logfile: " + test.outFile
for m in test.methods :
    print "Method: " + m[0] + ", " + repr(m[1]) + ", " + m[2]

testProgram = generateTestJavaSource(test)
subprocess.call("javac -Xlint:unchecked " + testProgram + ".java", shell=True) 

outNames = map((lambda x: test.outFile + "_%d_%d_%05d" % (test.threadNum, test.traceLength, x)), range(0, test.repeat))
for name in outNames:
    if test.outFile == "" :
        agentArgs = "=" 
        testArgs = ""
    else :
        agentArgs = "=" + logPath + "/" + name + ","  
        testLogFile = logPath + "/" + name + ".testlog"
    agentArgs = agentArgs + repr(test.threadNum) + "," + repr(test.traceLength) + "," + test.classname 
    for m in test.methods:
        agentArgs = agentArgs + "," + m[0]
    testCommand = "java -agentpath:" + agentPath + agentArgs + " " + testProgram + " " + testLogFile # " -classpath " + testPath + " " + testProgram
    print testCommand    
    subprocess.call(testCommand, shell=True)


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
