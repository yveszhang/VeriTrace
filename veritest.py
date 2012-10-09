from sets import ImmutableSet

admitArgTypes = ImmutableSet(["int", "boolean", "char", "char[]", "String"])
admitReturnTypes = ImmutableSet(["int", "obj[int]", "boolean", "char", "char[]", "String"])

class ParseError(Exception) : 
    def __init__(self, line, value) : 
        self.line = line
        self.value = value
    def __str__(self) :
        if self.line > 0 :
            return ("Line " + repr(self.line) + ": " + self.value)
        else : 
            return (self.value)

class TestCase :
    def __init__(self, impath, clsname, isInter, mthds, thdNum, evtNum, prog, outf, verb, repeat) :
        self.importpath = impath
        self.classname = clsname
        self.isInterface = isInter
        self.methods = mthds # list of triples (methodName, args, return)
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
    hasThreadNum, hasLength, hasLogName, hasClassName, hasImport, hasIsInterface  = False, False, False, False, False, False
    mthds, mthdName, mthdArgs, mthdReturn, hasArgs, hasReturn = [], "", [], "void", False, False
    impath, isInter = "", False
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
                    nameEnd = words[1].find("<")
                    if nameEnd > 0 :
                        typeEnd = words[1].find(">")
                        if typeEnd <= nameEnd: 
                            raise ParseError(i, "Invalid class name")
                        clsname = words[1][0:nameEnd]
                        typname = words[1][nameEnd+1:typeEnd]
                        if not (typname in admitArgTypes) :
                            raise ParseError(i, typname + " is not a supported type")
                        isInter = True
                    else : 
                        clsname = words[1] 
                    hasClassName = True

            elif words[0] == "import" :
                if hasImport :
                    raise ParseError(i, "Already have import value") 
                elif len(words) == 2: 
                    impath = words[1]
                    hasImport = True

            elif words[0] == "isInterface" :
                if hasIsInterface :
                    raise ParseError(i, "Already have isInterface value") 
                elif (len(words) == 2) and (words[1].lower() == "true") : 
                    isInter = True

            elif words[0] == "method" :
                if len(words) < 2: 
                    raise ParseError(i, "No value for method") 
                else: 
                    if mthdName != "" :
                        mthds.append((mthdName, mthdArgs, mthdReturn)) 
                        hasArgs = False
                        hasReturn = False
                        methdName = ""
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
                        if not (arg in admitArgTypes) : 
                            raise ParseError(i, arg + " is not a supported type")
                    hasArgs = True

            elif words[0] == "return" :
                if hasReturn : 
                    raise ParseError(i, "Already have return value")  
                elif len(words) < 2 : 
                    mthdReturn = "void"
                    hasReturn = True
                else : 
                    if not (words[1] in admitReturnTypes) :
                            raise ParseError(i, words[1] + " is not a supported type")
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
    return TestCase(impath, clsname, isInter, mthds, thdNum, trLeng, prog, outf, False, 1) # last two arguments: verbose, repeat

def generateTestJavaSource(test): 
    testClassname = "Testing" + test.classname + "T" + str(test.threadNum) + "L" + str(test.traceLength) 
    codeline = "// "
    mid = 0
    for m in test.methods : 
        testClassname = testClassname + m[0].capitalize()
        codeline = codeline + str(mid) + ": " + m[0] + "(" 
        aid = 0 
        for arg in m[1] :
            codeline  = codeline + arg 
            aid = aid + 1
            if aid < len(m[1]) :
                codeline = codeline + "," 
        codeline = codeline + "):" + m[2] + "; "
        mid = mid + 1
    srcFilename = testClassname + ".java"
    tdRange = 1000 
    mdNum = len(test.methods)
    
    f = open(srcFilename, "w") 
    f.write(codeline + "\n" ) ;
    if test.importpath != "" :
        codeline = "import " + test.importpath + " ;"
        f.write(codeline + "\n") ;
    f.write("\n")    
    
    f.write("import test.ArgType ; \n") 
    f.write("import test.ArgInt ; \n")
    f.write("import test.ArgBoolean ; \n")
    f.write("import test.TraceRecord ; \n")
    f.write("import java.io.* ;\n")
    f.write("import java.util.Random ;\n")
    f.write("import java.util.List ;\n")
    f.write("import java.util.LinkedList ;\n\n")

    f.write("class TestThread extends Thread { \n")
    if test.isInterface :
        f.write("  private " + test.classname + "<Integer> data ; \n")
    else :
        f.write("  private " + test.classname + "<Integer> data ; \n")
    f.write("  private int elemBase ; \n")
    # f.write("  private static int methodNum = " + str(mdNum) + "; \n")
    f.write("  private TraceRecord[] trace ; \n")
    f.write("\n") 
    
    if test.isInterface :
        f.write("  TestThread (String name, " + test.classname + "<Integer> q, TraceRecord[] tr) { \n" )
    else :
        f.write("  TestThread (String name, " + test.classname + "<Integer> q, TraceRecord[] tr) { \n" )
    f.write("    super(name) ; \n") 
    f.write("    this.data = q ; \n") 
    f.write("    this.elemBase = Integer.parseInt(name) * " + str(tdRange) + " ;  \n") 
    # f.write("    this.range = base ; \n") 
    # f.write("    this.methodNum = mdNum ; \n") 
    f.write("    this.trace = tr ; \n") 
    f.write("  } \n\n")
    
    f.write("  public void run() { \n") 
    f.write("    int len = " + str(test.traceLength) + " ; \n")
    f.write("    Random r = new Random() ; \n") 
    for m in test.methods : 
        i = 0
        for arg in m[1] :
            i = i + 1
            f.write("    " + arg + " " + m[0] + "__" + str(i) + "; \n") 
        if m[2] == "obj[int]" :
            f.write("    Object " + m[0] + "__ret ; \n") 
        else :
            f.write("    " + m[2] + " " + m[0] + "__ret ; \n") 
    f.write("    for (int i = 0; i < len; i++) { \n") 
    f.write("      LinkedList<ArgType> args = new LinkedList<ArgType> () ; \n") 
    f.write("      int mid = r.nextInt(" + str(mdNum) + ") ; \n")
    f.write("      switch (mid) { \n")
    for i in range(0, mdNum) :
        m = test.methods[i]
        f.write("      case " + str(i) + ": \n") 
        methodCall = "data." + m[0] + "("
        j = 0
        for arg in m[1] :
            j = j+1
            if arg == "int" : 
                f.write("        " + m[0] + "__" + str(j) + " = elemBase + r.nextInt(" + str(tdRange) + ") ; \n") 
                f.write("        args.add(new ArgInt(" + m[0] + "__" + str(j) + ")) ; \n") 
            elif arg == "boolean" :
                f.write("        boolean " + m[0] + "__" + str(j) + " = r.nextBoolean(); \n")
                f.write("        args.add(new ArgBoolean(" + m[0] + "__" + str(j) + ")) ; \n") 
            methodCall = methodCall + m[0] + "__" + str(j) 
            if j < len(m[1]) : 
                methodCall = methodCall + ", " 
        methodCall = methodCall + ")"
        if m[2] == "void" :
            f.write("        " + methodCall + " ; \n")
            f.write("        trace[i] = new TraceRecord(args, -1, mid) ; \n") 
        elif m[2] == "obj[int]" :
            f.write("        " + m[0] + "__ret = " + methodCall + " ; \n")
            f.write("        if (" + m[0] + "__ret == null) trace[i] = new TraceRecord(args, -1, mid) ; \n")
            f.write("        else trace[i] = new TraceRecord(args, Integer.parseInt(" + m[0] + "__ret.toString()), mid) ; \n")
        else:
            f.write("        " + m[0] + "__ret = " + methodCall + " ; \n")
            f.write("        trace[i] = new TraceRecord(args, " + m[0] + "__ret, mid) ; \n") 
        f.write("        break ; \n") 
    f.write("      default :  \n") 
    f.write("      } \n") 
    f.write("    } \n") 
    f.write("  } \n") 
    f.write("} \n\n") 

    f.write("class " + testClassname + " { \n") 
    f.write("  public static void main(String argv[]) { \n")
    f.write("    int tdNum = " + str(test.threadNum) + ", mdNum = " + str(mdNum) + ", trLen = " + str(test.traceLength) + "; \n")
    if test.isInterface :
        f.write("    " + test.classname + "<Integer> testObj = new " + test.classname + "<Integer>() ; \n") 
    else :
        f.write("    " + test.classname + " testObj = new " + test.classname + "() ; \n") 
    f.write("    TraceRecord[][] tr = new TraceRecord[tdNum][trLen] ; \n")
    f.write("    TestThread[] thd = new TestThread[tdNum] ; \n")
    f.write("    for (int i = 0; i < tdNum; i++) { \n")
    f.write("      tr[i] = new TraceRecord[trLen] ; \n")
    f.write("      thd[i] = new TestThread(Integer.toString(i), testObj, tr[i]) ; \n")
    f.write("      thd[i].start() ; \n")
    f.write("    } \n")
    f.write("    try { \n")
    f.write("      for (int i = 0; i < tdNum; i++)  \n")
    f.write("      thd[i].join() ; \n")
    f.write("    } catch (Exception e) { \n")
    f.write("      e.printStackTrace() ; \n")
    f.write("    } \n")
    # if test.outFile == "" :
    #     f.write("    String fn = \"" + test.classname + "-\" + System.currentTimeMillis() + \".testlog\"; \n")
    # else :
    #     f.write("    String fn = \"" + test.outFile + "-\" + System.currentTimeMillis() + \".testlog\"; \n")
    # f.write("    try { \n")
    # f.write("      FileWriter fw = new FileWriter(fn) ; \n")
    # f.write("      BufferedWriter out = new BufferedWriter(fw) ; \n")
    f.write("    System.out.println(\"# <MethodIndex> <ArgumentValue> <ReturnValue>\") ; \n")
    f.write("    System.out.println(\"" + str(test.threadNum) + " " + str(test.traceLength) + " " + test.classname)
    for m in test.methods : 
        f.write(" " + m[0])
    f.write("\") ; \n")
    f.write("    for (int i=0; i < tdNum; i++) { \n")
    f.write("      System.out.println(\"Thread \" + i + \"\") ; \n")
    f.write("      for (int j=0; j < tr[i].length; j++) System.out.println(tr[i][j].toString() + \"\") ; \n")
    f.write("    } \n")
    # f.write("      out.close() ; \n")
    # f.write("    } catch (Exception e) { \n")
    # f.write("      System.err.println(\"Error: \" + e) ; \n")
    # f.write("    } \n")
    f.write("  } \n")
    f.write("} \n")

    f.close() ;
    return testClassname
