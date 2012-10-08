from sets import ImmutableSet

admitJavaTypes = ImmutableSet(["int", "bool", "char", "char[]", "String"])

class TestCase :
    def __init__(self, clspath, clsname, mthds, thdNum, evtNum, prog, outf, verb, repeat) :
        self.classpath = clspath
        self.classname = clsname
        self.methods = mthds
        self.threadNum = thdNum 
        self.traceLength = evtNum 
        self.testProgram = prog
        self.outFile = outf
        self.verbose = verb
        self.repeat = repeat

    def __repr__(self) :
        if len(self.methods) <= 0 :
            return "Testing " + self.classname + ": no method is given."
        str = self.methods[0]
        if len(self.methods) > 1 :
            for s in self.methods[1:] :
                str = str + ", " + s 
        return "Testing " + self.classname + " (" + str + ") with " + repr(self.threadNum) + " threads." 

def parseTestConfig(filename):
    f = open(filename, "r")
    i = 0
    hasThreadNum, hasLength, hasLogName, hasClassName, hasPath  = False, False, False, False, False
    mthds, mthdName, mthdArgs, mthdReturn, hasArgs, hasReturn = [], "", [], "void", False, False
    for line in f : 
        i = i+1
        l = line.strip() 
        if (l != "") and (l[0] != "#"): 
            words = map(lambda x: x.strip(), line.strip().split("="))
            if words[0] == "thread" :
                if len(words) < 2: 
                    raise ParseError(i, "No value for thread") 
                elif hasThreadNum :
                    raise ParseError(i, "Already have thread value") 
                else : 
                    thdNum = int(words[1])
                    hasThreadNum = True
            elif words[0] == "tracelength" : 
                if len(words) < 2: 
                    raise ParseError(i, "No value for tracelength") 
                elif hasLength :
                    raise ParseError(i, "Already have tracelength value") 
                else : 
                    trLeng = int(words[1])
                    hasLength = True
            elif words[0] == "logname" :
                if len(words) < 2: 
                    raise ParseError(i, "No value for logname") 
                elif hasLogName :
                    raise ParseError(i, "Already have logname value") 
                else : 
                    outf = words[1]
                    hasLogName = True
            elif words[0] == "classname" :
                if len(words) < 2: 
                    raise ParseError(i, "No value for classname") 
                elif hasClassName :
                    raise ParseError(i, "Already have classname value") 
                else : 
                    clsname = words[1]
                    hasClassName = True
            elif words[0] == "classpath" :
                if hasPath :
                    raise ParseError(i, "Already have classpath value") 
                elif len(words) < 2: 
                    path = ""
                else : 
                    path = words[1]
                    hasPath = True
            elif words[0] == "method" :
                if len(words) < 2: 
                    raise ParseError(i, "No value for method") 
                else: 
                    if mthdName != "" :
                        mthds.append((mthdName, mthdArgs, mthdReturn)) 
                        hasArgs = False
                        hasReturn = False
                        mthdArgs = [] 
                        mthdReturn = "void"
                    mthdName = words[1] 
            elif words[0] == "arguments" :
                if hasArgs : 
                    raise ParseError(i, "Already have arguments value")  
                elif len(words) < 2 : 
                    mthdArgs = [] 
                    hasArgs = True 
                else : 
                    mthdArgs = words[1].split() 
                    for arg in mthdArgs : 
                        if not (arg in admitJavaTypes) : 
                            raise ParseError(i, arg + " is not a supported type")
                    hasArgs = True
            elif words[0] == "return" :
                if hasReturn : 
                    raise ParseError(i, "Already have return value")  
                elif len(words) < 2 : 
                    mthdReturn = "void"
                    hasReturn = True
                else : 
                    mthdReturn = words[1]
                    hasReturn = True
    if mthdName != "" :
        mthds.append((mthdName, mthdArgs, mthdReturn)) 
    if not hasThreadNum :
        raise ParseError(-1, "No value for thread") 
    if not hasLength :
        raise ParseError(-1, "No value for tracelength") 
    if not hasLogName :
        raise ParseError(-1, "No value for logname") 
    if not hasClassName :
        raise ParseError(-1, "No value for classname") 
    if mthds == [] :
        raise ParseError(-1, "No method for testing") 
    prog = "testing" + clsname + ".java"
    return TestCase(path, clsname, mthds, thdNum, trLeng, prog, outf, False, 1) # last two arguments: verbose, repeat

def generateTestJavaSource(test): 
    srcFilename = "test" + "_T" + str(test.threadNum) + "_L" + str(test.traceLength) + "_" + test.classname
    for m in test.methods : 
        srcFilename = srcFilename + "_" + m[0]
    srcFilename = srcFilename + ".java"
    return srcFilename
