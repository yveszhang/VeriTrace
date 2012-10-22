#! /usr/bin/env python

import sys
import subprocess 
import os
from multiprocessing import Pool
from veritest import *

# repeat = 1
# verbose = False
# keepSource = False
admitCommands = ImmutableSet(["verify", "source", "test", "simulate"])
command = ""
testConf = ""

def printUsage() :
    print "Usage: veritrace.py <command> [-verbose] [-repeat <test number>] [-keep] <test configuration>"
    print "Command can be: " 
    print "  - verify:\t generate test and simulation source, compile both, run test, run simulation."
    print "  - source:\t only generate test and simulation source, no compilation, no testing and simulation."
    print "  - test:\t compile and run test, but not simulation. Must have previously generated test source file."
    print "  - simulate:\t compile and run simulation. Must have previously generated simulation source file and test logs."

def parseCommandLine() :
    global command, testConf
    repeat = 1 
    verbose = False 
    keepSource = True
    if len(sys.argv) < 3 :
        printUsage()
        exit(-1)
    else: 
        hasTestConf = False 
        hasRepeat = False
        getRepeat = False
        command = sys.argv[1]
        if not (command in admitCommands) : 
            printUsage() 
            exit(-1)
        for s in sys.argv[2:] :
            if s[0] == "-" :
                if s[1:] == "repeat" :
                    if hasRepeat : 
                        printUsage 
                        exit (-1)
                    else :
                        getRepeat = True
                elif s[1:] == "verbose" :
                    verbose = True 
                elif s[1:] == "keep" :
                    keepSource = True
                else :
                    printUsage 
            elif getRepeat :
                repeat = int(s) 
                hasRepeat = True
                getRepeat = False
            else :
                if hasTestConf :
                    printUsage() 
                    exit (-1)
                else : 
                    testConf = s
                    testcase = parseTestConfig(vtHomePath+"/"+testConf) 
                    hasTestConf = True
        if hasTestConf :
            testcase.repeat = repeat 
            testcase.verbose = verbose
            testcase.keepsrc = keepSource
            return testcase 
        else : 
            printUsage
            exit (-1)

def generateSource(test, testPath, testClassname) :
    generateTestJavaSource(test, testPath, testClassname)
    print "Generated testing program in Java: " + testPath + "/" + testProgramName
    generateSimulateScalaSource(test, testPath, testClassname)
    print "Generated simulation program in Scala: " + testPath + "/" + simuProgramName
    return (0)

def compileTestSource(compiler, srcLanguage, testPath, srcPath, programName) : 
    print "Compiling testing program:"
    print compiler + " -Xlint:unchecked -d . " + testPath + "/" + programName
    ret = subprocess.call(compiler + " -Xlint:unchecked -d . " + testPath + "/" + programName, shell=True) 
    if ret != 0 :
        return (-1)
    else : 
        return (0)

def compileSimulateSource (compiler, srcLanguage, testPath, srcPath, programName) : 
    print "Compiling simulation program:"
    print compiler + " " + testPath + "/" + programName + " " + srcPath + "/Simulation.scala " + srcPath + "/*.java"
    ret = subprocess.call(compiler + " " + testPath + "/" + programName \
                              + " " + srcPath + "/Simulation.scala " + srcPath + "/*.java" \
                              , shell=True \
                          ) 
    if ret != 0 :
        return (-1)
    else : 
        return (0)

def runTesting (test, testClassname, logPath, logName, limit) :
    agentArgs = "=" + logPath + "/" + logName + "," + repr(test.threadNum) + "," + repr(test.traceLength) + "," \
        + test.classname + "," + str(len(test.methods)) 
    testLogFile = logPath + "/" + logName + ".testlog"
    # for i in range(0, len(test.methods)):
    #     agentArgs = agentArgs + ",vtMethod" + str(i)
    testCommand = "java -agentpath:" + agentPath + agentArgs + " " + testClassname + " " + testLogFile 
    print testCommand    
    count = 0
    ret = 1 
    while ret != 0 and count < limit : 
        ret = subprocess.check_call(testCommand + " > NULL", shell=True)
        count = count + 1
    if ret != 0 : 
        return (-1)
    else : 
        return (0)

def runSimulation (test, logPath, logName) :
    if test.verbose :
        verifCommand = "scala Simulate -v " + logPath + "/" + logName
    else : 
        verifCommand = "scala Simulate " + logPath + "/" + logName 
    print (verifCommand) 
    try : 
        ret = subprocess.check_call(verifCommand, shell=True)
        return (0, logName)
    except subprocess.CalledProcessError :
        return (1, logName)
    except : 
        return (-1, logName)

try : 
    vtHomePath = os.environ['VT_HOME'].rstrip("/ ")
except KeyError:
    print "Please set the VT_HOME environment variable!" 
    exit(0)
if vtHomePath == "" :
    print "Please set the VT_HOME environment variable!" 
    exit (0) 
os.chdir(vtHomePath)
os.putenv("CLASSPATH", vtHomePath)

javaCompiler = "/usr/bin/javac"
scalaCompiler = "/usr/local/share/scala/bin/fsc"

agentPath = vtHomePath + "/jvmagent/TraceAgent.dylib"
testPath = vtHomePath + "/test"
srcPath = vtHomePath + "/src"
logPath = vtHomePath + "/tracelog"

testLimit = 50
repeatLimit = 100

try : 
    test = parseCommandLine ()
except ParseError as err :
    print "Parse error: " + str(err)
    exit(0)

# print "Threads: " + str(test.threadNum) 
# print "Trace: " + str(test.traceLength)
# print "Classname: " + test.classname
# print "Classpath: " + test.importpath
# print "Logfile: " + test.outFile
# for m in test.methods :
#     print "Method: " + m[0] + ", " + repr(m[1]) + ", " + m[2]

testClassname = test.classname + "T" + str(test.threadNum) + "L" + str(test.traceLength) 
mid = 0
for m in test.methods : 
    testClassname = testClassname + m[0].capitalize()

testProgramName = "Testing" + testClassname + ".java" 
simuProgramName = "Simulate" + testClassname + ".scala" 

if (command == "verify") or command == "source" :
    generateSource(test, testPath, testClassname) 
    print "Source files generated!" 

if command == "verify" or command == "test" :
    ret = compileTestSource(javaCompiler, "java", testPath, srcPath, testProgramName) 
    if ret == 0 : 
        print "Testing file compiled!" 
    else : 
        print "Compilation of test failed! exit."
        exit (-1)

if command == "verify" or command == "simulate" :
    ret = compileSimulateSource(scalaCompiler, "scala", testPath, srcPath, simuProgramName) 
    if ret == 0 :
        print "Simulation file compiled!"
    else : 
        print "Compilation of simulateion failed! exit."
        exit (-1)

if test.repeat == 1 :
    if test.outFile == "" :
        logName = testConf + ".temp" 
    else : 
        logName = test.outFile + ".temp" 
    if command == "verify" :
        vCount = 0 
        ret = 0
        while ret == 0 and vCount < repeatLimit : 
            print "\nTest try #" + str(vCount+1) + ": "
            retTest = runTesting(test, "Testing"+testClassname, logPath, logName, testLimit) 
            if retTest != 0 : 
                print "Could not generate testing logs!"
                exit (-1) 
            (ret, _) = runSimulation(test, logPath, logName) 
            if ret == 0 : 
                print "OK!"
            vCount = vCount + 1
        if ret == 0 : 
            print "Checked the test case for " + str(repeatLimit) + " times and no error found!" 
            exit (0) 
        else : 
            print 
            exit (-1) 
    elif command == "test" : 
        ret = runTesting(test, "Testing"+testClassname, logPath, logName, testLimit) 
        if ret != 0 : 
            print "Could not generate testing logs!"
            exit (-1) 
        else : 
            print "Testing logs in " + logPath + ": " + logName + ".jvmlog, " + logName + ".testlog" 
            exit (0)
else :
    if test.outFile == "" : 
        testLogs = map((lambda x: testConf + "_%d_%d_%05d" % (test.threadNum, test.traceLength, x)), range(0, test.repeat))
    else : 
        testLogs = map((lambda x: test.outFile + "_%d_%d_%05d" % (test.threadNum, test.traceLength, x)), range(0, test.repeat))
    logNames = [] 
    for testLog in testLogs:
        if command == "verify" or command == "test" : 
            retTest = runTesting(test, "Testing"+testClassname, logPath, testLog, testLimit) 
            if retTest == 0 : 
                logNames.append(testLog) 
            print "Generated test log: " + str(testLog) 
    if command == "verify" : 
        # pool = multiprocessing.Pool(test.processors)
        # for (ret, logName) in pool.map(lambda name: runSimulation (test, logPath, name), logNames) :
        for logName in logNames : 
            (ret, name) = runSimulation(test, logPath, logName) 
            if ret == 0 : 
                print "-> Test " +logName + " has a linearizable execution."
            elif ret > 0 : 
                print "-> Test " +logName + " has no linearizable execution."
            else : 
                print "-> Simulation error with " + logName
            
if command == "simulate" : 
    logNames = [testConf + ".temp", test.outFile + ".temp" ]
    logPrefix = test.outFile + "_%d_%d" % (test.threadNum, test.traceLength)
    for logCount in range(repeatLimit) : 
        logNames.append(logPrefix + "_%05d" % (logCount) )
    logNames = filter(lambda x : os.path.isfile (logPath+"/"+x+".jvmlog") and os.path.isfile (logPath+"/"+x+".testlog"), logNames)
    for logName in logNames : 
        (ret, name) = runSimulation(test, logPath, logName) 
        if ret == 0 : 
            print "-> Test " +logName + " has a linearizable execution."
        elif ret > 0 : 
            print "-> Test " +logName + " has no linearizable execution."
        else : 
            print "-> Simulation error with " + logName
    exit (0) 
                

