#! /usr/bin/env python

import sys
import subprocess 
import os
from multiprocessing import Pool
from vttest import *

admitCommands = ImmutableSet(["verify", "source", "test", "simulate"])
command = ""
testConf = ""

def readConfig(fn) :
    f = open(fn) 
    javac, scalac, testLimit, repeatLimit = "", "", 50, 100
    for line in f : 
        line = line.strip() 
        if line != "" and line[0] != '#' :
            words = filter(lambda x: x != "", map(lambda x: x.strip(), line.split("=")))
            if words[0] == "JavaCompiler" :
                javac = words[1]
            elif words[0] == "ScalaCompiler" : 
                scalac = words[1] 
            elif words[0] == "TestLimit" :
                testLimit = int(words[1])
            elif words[0] == "RepeatLimit" :
                repeatLimit = int(words[1])
            elif words[0] == "Processors" :
                processors = int(words[1])
    f.close()
    return (javac, scalac, testLimit, repeatLimit, processors) 

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

def generateSource(test, testTargetPath, optPath, pkgName, testClassname) :
    # print testTargetPath + ": " + testClassname
    generateTestJavaSource(test, testTargetPath, pkgName, testClassname)
    print "Generated testing program in Java: " + testTargetPath + "/" + testProgramName
    generateSimulateScalaSource(test, testTargetPath, optPath, pkgName, testClassname)
    print "Generated simulation program in Scala: " + testTargetPath + "/" + simuProgramName
    return (0)

def compileTestSource(compiler, srcLanguage, testTargetPath, srcPath, programName) : 
    print "Compiling testing program:"
    print compiler + " -Xlint:unchecked " + testTargetPath + "/" + programName
    ret = subprocess.call(compiler + " -Xlint:unchecked " + testTargetPath + "/" + programName, shell=True) 
    if ret != 0 :
        return (-1)
    else : 
        return (0)

def compileSimulateSource (compiler, srcLanguage, testTargetPath, srcPath, programName) : 
    print "Compiling simulation program:"
    print compiler + " " + testTargetPath + "/" + programName + " " + srcPath + "/Simulation.scala " + srcPath + "/*.java"
    ret = subprocess.call(compiler + " " + testTargetPath + "/" + programName \
                              + " " + srcPath + "/Simulation.scala " + srcPath + "/*.java" \
                              , shell=True \
                          ) 
    if ret != 0 :
        return (-1)
    else : 
        return (0)

def runTesting (test, targetDir, testPathClass, logPath, logName, limit) :
    agentArgs = "=" + logPath + "/" + logName + "," + repr(test.threadNum) + "," + repr(test.traceLength) + "," \
        + targetDir + "," + test.classname + "," + str(len(test.methods)) 
    testLogFile = logPath + "/" + logName + ".testlog"
    testCommand = "java -agentpath:" + agentPath + agentArgs + " " + testPathClass + " " + testLogFile 
    print testCommand    
    count = 0
    ret = 1 
    while ret != 0 and count < limit : 
        ret = subprocess.check_call(testCommand + " > /dev/null", shell=True)
        count = count + 1
    if ret != 0 : 
        return (-1)
    else : 
        return (0) # successful testing run

def runSimulation (test, simuPathClass, logPath, logName) :
    if test.verbose :
        verifCommand = "scala " + simuPathClass + " -v " + logPath + "/" + logName
    else : 
        verifCommand = "scala " + simuPathClass + " " + logPath + "/" + logName 
    print (verifCommand) 
    try : 
        ret = subprocess.check_call(verifCommand, shell=True)
        return (0, logName)
    except subprocess.CalledProcessError :
        return (1, logName)
    except : 
        return (-1, logName)

def singleVerify (test, testPathClass, simuPathClass, logPath, logName, testLimit) :
    vCount = 0 
    ret = 0
    while ret == 0 and vCount < repeatLimit : 
        print "\nTest try #" + str(vCount+1) + ": "
        retTest = runTesting(test, targetDir, testPathClass, logPath, logName, testLimit) 
        if retTest != 0 : 
            print "Could not generate testing logs!"
            exit (-1) 
        (ret, _) = runSimulation(test, simuPathClass, logPath, logName) 
        if ret == 0 : 
            print "OK!"
        vCount = vCount + 1
    if ret == 0 : 
        print "Checked the test case for " + str(repeatLimit) + " times and no error found!" 
        exit (0) 
    else : 
        print 
        exit (-1) 

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

vtOS = os.uname()[0]
if vtOS == "Darwin" :
    agentPath = vtHomePath + "/jvmagent/TraceAgent.dylib"
else :
    agentPath = vtHomePath + "/jvmagent/TraceAgent.so"
testPath = vtHomePath + "/test"
srcPath = vtHomePath + "/src"
logPath = vtHomePath + "/tracelog"

try : 
    javaCompiler, scalaCompiler, testLimit, repeatLimit, processors = readConfig(vtHomePath+"/vt.conf")
except IOError as e :
    try :
        javaCompiler = subprocess.check_output("which javac", shell=True).strip()
    except :
        print "No java compiler is found!"
        exit (-1)
    try :
        scalaCompiler = subprocess.check_output("which scalac", shell=True).strip()
    except : 
        print "No java compiler is found!"
        exit (-1)
    testLimit = 50
    repeatLimit = 100

try : 
    test = parseCommandLine ()
except ParseError as err :
    print "Parse error: " + str(err)
    exit(0)

testClassname = test.classname + "T" + str(test.threadNum) + "L" + str(test.traceLength) 
targetDir = test.classname
optPath = testPath + "/" + test.optimisation
pkgName = "test." + test.classname
if test.outFile == "" :
    logPrefix = test.classname.lower() 
else : 
    logPrefix = test.outFile
mid = 0
for m in test.methods : 
    testClassname = testClassname + m[0].capitalize()
    targetDir = targetDir + m[0].capitalize()
    pkgName = pkgName + m[0].capitalize()
    logPrefix = logPrefix + "_" + m[0].lower()
testTargetPath = "test/" + targetDir

testProgramName = "Testing" + testClassname + ".java" 
simuProgramName = "Simulate" + testClassname + ".scala"
testClassFull = pkgName + ".Testing" + testClassname 
simuClassFull = pkgName + ".Simulate"

def parallelTesting(log) :
    ret = runTesting(test, targetDir, testClassFull, logPath, log, testLimit)
    return (log, ret)

def parallelSimulation(log) :
    ret = runSimulation(test, simuClassFull, logPath, log)
    return ret

if (command == "verify") or command == "source" :
    if not os.path.exists(vtHomePath+"/"+testTargetPath) :
        os.mkdir(vtHomePath+"/"+testTargetPath, 0755)
    generateSource(test, testTargetPath, optPath, pkgName, testClassname) 
    print "Source files generated!" 

if command == "verify" or command == "test" :
    ret = compileTestSource(javaCompiler, "java", testTargetPath, srcPath, testProgramName) 
    if ret == 0 : 
        print "Testing file compiled!" 
    else : 
        print "Compilation of test failed! exit."
        exit (-1)

if command == "verify" or command == "simulate" :
    ret = compileSimulateSource(scalaCompiler, "scala", testTargetPath, srcPath, simuProgramName) 
    if ret == 0 :
        print "Simulation file compiled!"
    else : 
        print "Compilation of simulateion failed! exit."
        exit (-1)

if test.repeat == 1 :
    logName = logPrefix + ".temp" 
    if command == "verify" :
        singleVerify (test, testClassFull, simuClassFull, logPath, logName, testLimit) 
    elif command == "test" : 
        ret = runTesting(test, targetDir, testClassFull, logPath, logName, testLimit) 
        if ret != 0 : 
            print "Could not generate testing logs!"
            exit (-1) 
        else : 
            print "Testing logs in " + logPath + ": " + logName + ".jvmlog, " + logName + ".testlog" 
            exit (0)
else :
    testLogs = map((lambda x: logPrefix + "_%d_%d_%05d" % (test.threadNum, test.traceLength, x)), range(0, test.repeat))
    logNames = [] 
    if __name__ == "__main__" :
        if command == "verify" or command == "test" : 
            if processors/test.threadNum > 1 :
                testpool = Pool(processors/test.threadNum)
                rets = testpool.map(parallelTesting, testLogs)
            else : 
                rets = map(parallelTesting, testLogs) 
            logNames = map(lambda x: x[0], filter(lambda x : x[1] == 0, rets))
        if command == "verify" : 
            if processors > 1 :
                simpool = Pool(processors)
                simRets = simpool.map(parallelSimulation, logNames)
            else :
                simRets = map(parallelSimulation, logNames) 
            for (ret, name) in simRets : 
                 if ret > 0 : 
                     print "-> Test " + name + " has no linearizable execution."
                 else : 
                     print "-> Simulation error with " + name
            
if command == "simulate" : 
    logNames = [logPrefix + ".temp" ]
    for logCount in range(repeatLimit) : 
        logNames.append(logPrefix + "_%d_%d_%05d" % (test.threadNum, test.traceLength, logCount) )
    logNames = filter(lambda x : os.path.isfile (logPath+"/"+x+".jvmlog") and os.path.isfile (logPath+"/"+x+".testlog"), logNames)
    if __name__ == "__main__" :
        if processors > 1 :
            simpool = Pool(processors)
            simRets = simpool.map(parallelSimulation, logNames) 
        else : 
            simRets = map(parallelSimulation, logNames) 
        for (ret, logName) in simRets : 
            if ret > 0 : 
                print "-> Test " +logName + " has no linearizable execution."
            elif ret < 0: 
                print "-> Simulation error with " + logName
    exit (0) 
                

