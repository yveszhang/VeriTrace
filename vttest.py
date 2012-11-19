from sets import ImmutableSet

admitArgTypes = ImmutableSet(["int", "boolean", "char", "char[]", "String"])
admitReturnTypes = ImmutableSet(["int", "obj[int]", "boolean", "char", "char[]", "String", "obj[String]", "StringBuffer"])
admitParamTypes = ImmutableSet(["Integer", "String"])

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
    def __init__(self, impath, clsname, types, opt, proc, mthds, thdNum, evtNum, outf, verb, repeat, keep) :
        self.importpath = impath
        self.classname = clsname
        self.typeParams = types
        self.methods = mthds # list of triples (methodName, args, return)
        self.threadNum = thdNum 
        self.traceLength = evtNum 
        self.optimisation = opt
        self.processors = proc
        self.outFile = outf
        self.verbose = verb
        self.repeat = repeat
        self.keepsrc = keep

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
    hasThreadNum, hasLength, hasLogName = False, False, False
    hasImport, hasClassName, hasOpt, hasProc = False, False, False, False
    mthds, mthdName, mthdArgs, mthdReturn, hasArgs, hasReturn = [], "", [], "void", False, False
    impath, optim, typeParams, proc = "", "", [], 1
    for line in f : 
        i = i+1
        l = line.strip() 
        if (l != "") and (l[0] != "#"): 
            words = filter(lambda x: x != "", map(lambda x: x.strip(), line.strip().split("=")))
            if words[0] == "thread" :
                if len(words) >= 2: 
                    if hasThreadNum :
                        raise ParseError(i, "Already have thread value") 
                    else : 
                        thdNum = int(words[1])
                        hasThreadNum = True

            elif words[0] == "tracelength" : 
                if len(words) >= 2: 
                    if hasLength :
                        raise ParseError(i, "Already have tracelength value") 
                    else : 
                        trLeng = int(words[1])
                        hasLength = True

            elif words[0] == "logname" :
                if len(words) >= 2: 
                    if hasLogName :
                        raise ParseError(i, "Already have logname value") 
                    else : 
                        outf = words[1]
                        hasLogName = True

            elif words[0] == "classname" :
                if len(words) >= 2: 
                    if hasClassName :
                        raise ParseError(i, "Already have classname value") 
                    else : 
                        nameEnd = words[1].find("<")
                        if nameEnd > 0 :
                            typeEnd = words[1].find(">")
                            if typeEnd <= nameEnd: 
                                raise ParseError(i, "Invalid class name")
                            clsname = words[1][0:nameEnd]
                            typeParams = filter(lambda x: x != "", \
                                                    map(lambda x: x.strip(), words[1][nameEnd+1:typeEnd].split(",")))
                            for t in typeParams : 
                                if not (t in admitParamTypes) :
                                    raise ParseError(i, t + " is not a supported type")
                        else : 
                            clsname = words[1] 
                        hasClassName = True

            elif words[0] == "import" :
                if hasImport :
                    raise ParseError(i, "Already have import value") 
                elif len(words) == 2: 
                    impath = words[1]
                    hasImport = True

            elif words[0] == "optimisation" :
                if len(words) >= 2: 
                    if hasOpt :
                        raise ParseError(i, "Already have optimisation value") 
                    else : 
                        optim = words[1]
                        hasOpt = True

            elif words[0] == "processors" :
                if len(words) >= 2: 
                    if hasProc :
                        raise ParseError(i, "Already have processors value") 
                    else : 
                        proc = int(words[1])
                        hasProc = True

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
    return TestCase(impath, clsname, typeParams, optim, proc, mthds, thdNum, trLeng, outf, False, 1, False) # last three arguments: verbose, repeat, keepsrc

def generateTestJavaSource(test, testPath, pkgName, classname): 
    testClassname = "Testing" + classname
    srcFilename = testPath + "/" + testClassname + ".java"
    f = open(srcFilename, "w") 

    firstline = "// "
    mid = 0
    for m in test.methods : 
        firstline = firstline + str(mid) + ": " + m[0] + "(" 
        aid = 0 
        for arg in m[1] :
            firstline  = firstline + arg 
            aid = aid + 1
            if aid < len(m[1]) :
                firstline = firstline + "," 
        firstline = firstline + "):" + m[2] + "; "
        mid = mid + 1
    tdRange = 100 
    strRange = 100000
    mdNum = len(test.methods)
    
    f.write(firstline + "\n" ) ;
    f.write("package " + pkgName + " ; \n") 
    if test.importpath != "" :
        f.write("import " + test.importpath + " ; \n")
    f.write("\n")    
    
    f.write("import jtrace.ArgType ; \n") 
    f.write("import jtrace.ArgInt ; \n")
    f.write("import jtrace.ArgBoolean ; \n")
    f.write("import jtrace.ArgChar ; \n")
    f.write("import jtrace.ArgString ; \n")
    f.write("import jtrace.TraceRecord ; \n")
    # f.write("import jtrace.* ; \n")
    f.write("import java.io.* ;\n")
    f.write("import java.util.Random ;\n")
    f.write("import java.util.List ;\n")
    f.write("import java.util.LinkedList ;\n\n")

    param = ""
    if test.typeParams != [] :
        param = "<"
        for i in range(0, len(test.typeParams)) : 
            param = param + test.typeParams[i] 
            if i+1 < len(test.typeParams) : 
                param = param + ","
        param = param + ">"
    testObjectClass = "VT" + test.classname + "Test" 

    f.write("class " + testObjectClass + " { \n")
    f.write("  private " + test.classname + param + " data ; \n")
    f.write("  " + testObjectClass + " () { \n")
    f.write("    this.data = new " + test.classname + param + "() ; \n")
    f.write("  } \n")
    for i in range(len(test.methods)) :
        m = test.methods[i] 
        mDef = "vtMethod" + str(i) + "(" 
        mCall = m[0] + "(" 
        j = 0 
        for argtype in m[1] :
            j = j + 1
            varname = "x" + str(j) 
            mDef = mDef + argtype + " " + varname 
            mCall = mCall + varname 
            if j < len(m[1]) :
                mDef = mDef + ", " 
                mCall = mCall + ", "
        mDef = mDef + ")"
        mCall = mCall + ")"
        if m[2] == "obj[int]" :
            f.write("    public Integer " + mDef + " { return data." + mCall + "; } \n") 
        elif m[2] == "obj[String]" : 
            f.write("    public String " + mDef + " { return data." + mCall + "; } \n") 
        elif m[2] == "void" :
            f.write("    public void " + mDef + " { data." + mCall + "; } \n") 
        else :
            f.write("    public " + m[2] + " " + mDef + " { return data." + mCall + " ; } ; \n") 
    f.write("} \n\n")


    f.write("class TestThread extends Thread { \n")
    f.write("  private " + testObjectClass + " data ; \n")
    f.write("  private int elemBase ; \n")
    # f.write("  private static int methodNum = " + str(mdNum) + "; \n")
    f.write("  private TraceRecord[] trace ; \n")
    f.write("\n") 
    
    f.write("  TestThread (String name, " + testObjectClass + " q, TraceRecord[] tr) { \n" )
    f.write("    super(name) ; \n") 
    f.write("    this.data = q ; \n") 
    f.write("    this.elemBase = 0 ; \n ") # Integer.parseInt(name) * " + str(tdRange) + " ;  \n") 
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
            f.write("    Integer " + m[0] + "__ret ; \n") 
        elif m[2] == "obj[String]" : 
            f.write("    String " + m[0] + "__ret ; \n") 
        elif m[2] != "void" :
            f.write("    " + m[2] + " " + m[0] + "__ret ; \n") 
    f.write("    for (int i = 0; i < len; i++) { \n") 
    f.write("      LinkedList<ArgType> args = new LinkedList<ArgType> () ; \n") 
    f.write("      int mid = r.nextInt(" + str(mdNum) + ") ; \n")
    f.write("      switch (mid) { \n")
    for i in range(0, mdNum) :
        m = test.methods[i]
        f.write("      case " + str(i) + ": \n") 
        methodCall = "data.vtMethod" + str(i) + "("
        j = 0
        for arg in m[1] :
            j = j+1
            if arg == "int" : 
                f.write("        " + m[0] + "__" + str(j) + " = elemBase + r.nextInt(" + str(tdRange) + ") ; \n") 
                f.write("        args.add(new ArgInt(" + m[0] + "__" + str(j) + ")) ; \n") 
            elif arg == "boolean" :
                f.write("        " + m[0] + "__" + str(j) + " = r.nextBoolean(); \n")
                f.write("        args.add(new ArgBoolean(" + m[0] + "__" + str(j) + ")) ; \n") 
            elif arg == "char" : 
                f.write("        " + m[0] + "__" + str(j) + " = (char) (65+r.nextInt(26)); \n")
                f.write("        args.add(new ArgChar(" + m[0] + "__" + str(j) + ")) ; \n") 
            else : 
                f.write("        " + m[0] + "__" + str(j) \
                            + " =  ArgType.encode(r.nextInt(120000)) + ArgType.encode(r.nextInt(120000)); \n")
                f.write("        args.add(new ArgString(" + m[0] + "__" + str(j) + ")) ; \n") 
            methodCall = methodCall + m[0] + "__" + str(j) 
            if j < len(m[1]) : 
                methodCall = methodCall + ", " 
        methodCall = methodCall + ")"
        f.write("        try { \n")
        if m[2] == "void" :
            f.write("          " + methodCall + " ; \n")
            f.write("          trace[i] = new TraceRecord(args, -1, mid, false) ; \n") 
        elif m[2] == "obj[int]" :
            f.write("          " + m[0] + "__ret = " + methodCall + " ; \n")
            f.write("          if (" + m[0] + "__ret == null) trace[i] = new TraceRecord(args, -1, mid, false) ; \n")
            f.write("          else trace[i] = new TraceRecord(args, Integer.parseInt(" + m[0] \
                        + "__ret.toString()), mid, false ) ; \n")
        else:
            f.write("          " + m[0] + "__ret = " + methodCall + " ; \n")
            f.write("          trace[i] = new TraceRecord(args, " + m[0] + "__ret, mid, false ) ; \n") 
        f.write("        } catch (Exception e) { \n")
        f.write("          trace[i] = new TraceRecord(args, -1, mid, true) ; \n") 
        f.write("        } \n")
        f.write("        break ; \n") 
    f.write("      default :  \n") 
    f.write("      } \n") 
    f.write("    } \n") 
    f.write("  } \n") 
    f.write("} \n\n") 

    f.write("class " + testClassname + " { \n") 
    f.write("  public static void main(String argv[]) { \n")
    f.write("    int tdNum = " + str(test.threadNum) + ", mdNum = " + str(mdNum) + ", trLen = " + str(test.traceLength) + "; \n")
    f.write("    " + testObjectClass + " testObj = new " + testObjectClass + "() ; \n") 
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
    f.write("    String fn = argv[0] ; \n")
    f.write("    try { \n")
    f.write("      FileWriter fw = new FileWriter(fn) ; \n")
    f.write("      BufferedWriter out = new BufferedWriter(fw) ; \n")
    f.write("      out.write(\"# <MethodIndex> <ArgumentValue> <ReturnValue>\\n\") ; \n")
    f.write("      out.write(\"" + str(test.threadNum) + " " + str(test.traceLength) + " " + test.classname)
    for m in test.methods : 
        f.write(" " + m[0])
    f.write("\\n\") ; \n")
    f.write("      for (int i=0; i < tdNum; i++) { \n")
    f.write("        out.write(\"Thread \" + i + \"\\n\") ; \n")
    f.write("        for (int j=0; j < tr[i].length; j++) out.write(tr[i][j].toString() + \"\\n\") ; \n")
    f.write("      } \n")
    f.write("      out.close() ; \n")
    f.write("    } catch (Exception e) { \n")
    f.write("      System.err.println(\"Error: \" + e) ; \n")
    f.write("    } \n")
    f.write("  } \n")
    f.write("} \n")

    f.close() ;
    return "OK"

def generateSimulateScalaSource(test, testPath, optPath, pkgName, classname): 
    testClassname = "Simulate" + classname 
    srcFilename = testPath + "/" + testClassname + ".scala"
    f = open(srcFilename, "w") 

    firstline = "// "
    mid = 0
    for m in test.methods : 
        firstline = firstline + str(mid) + ": " + m[0] + "(" 
        aid = 0 
        for arg in m[1] :
            firstline  = firstline + arg 
            aid = aid + 1
            if aid < len(m[1]) :
                firstline = firstline + "," 
        firstline = firstline + "):" + m[2] + "; "
        mid = mid + 1
    mdNum = len(test.methods)
    
    f.write(firstline + "\n" ) ;
    f.write("package " + pkgName + " ; \n") 
    if test.importpath != "" :
        f.write("import " + test.importpath.replace('*', '_') + " ; \n")
    f.write("\n")    
    
    f.write("import jtrace.ArgType ; \n") 
    f.write("import jtrace.ArgInt ; \n")
    f.write("import jtrace.ArgBoolean ; \n")
    f.write("import jtrace.ArgChar ; \n")
    f.write("import jtrace.ArgString ; \n")
    f.write("import jtrace.Simulation ; \n")
    # f.write("import jtrace.* ; \n")
    f.write("import java.io.File ;\n")
    f.write("import scala.collection.JavaConverters._; \n\n")

    f.write("class " + testClassname + "(logName: String, verbose: Boolean) extends Simulation(logName, verbose) { \n") 
    param = ""
    if test.typeParams != [] :
        for i in range(0, len(test.typeParams)) : 
            if test.typeParams[i] == "Integer" :
                param = param + "java.lang.Integer"
            else : 
                param = param + test.typeParams[i] 
            if i+1 < len(test.typeParams) : 
                param = param + ","
        f.write("  type T = " + test.classname + "[" + param + "] \n")
    else :
        f.write("  type T = " + test.classname + " \n")
    f.write("  val methodLog : MethodTable = parseLog \n")
    f.write("  val traceSegmentation : List[List[(Int,Int)]] = partitionTrace \n")
    f.write("  val initSimuState : SimuState = List( (new T(), Nil) ) \n")
    f.write("\n") 

    if test.optimisation == "" :
        f.write("  // optimization code can be supplied here by defining ST and encodeObject \n") 
        f.write("  type ST = T \n") 
        f.write("  def encodeObject (o: T) = o \n\n")
    else : 
        fopt = open(optPath, "r")
        for line in fopt : 
            f.write("  " + line) 
        fopt.close()
        f.write("\n")
    
    f.write("  def parseTestLine (line: String) : List[ArgType]= { \n")
    f.write("    val words = line.split(\' \') \n") 
    f.write("    val isExcept = (words(0) == \"E\") \n")
    f.write("    val methodID = if (isExcept) words(1).toInt else words(0).toInt \n")
    f.write("    methodID match { \n") 
    for i in range(0, mdNum) :
        m = test.methods[i]
        f.write("      case " + str(i) + " => { \n")
        if m[2] == "void" :
            f.write("        val mRet = if (isExcept) new ArgInt(-1, true) else new ArgInt(\"void\") \n")
        elif m[2] == "int" or m[2] == "obj[int]" : 
            f.write("        val mRet = if (isExcept) new ArgInt(-1, true) else new ArgInt(words(1).toInt) \n")
        elif m[2] == "boolean" :                     
            f.write("        val mRet = if (isExcept) new ArgInt(-1, true) else if (words(1).toInt == 1) new ArgBoolean(true) else new ArgBoolean(false) \n")
        elif m[2] == "char" :                     
            f.write("        val mRet = if (isExcept) new ArgInt(-1, true) else new ArgChar(words(1)(0)) \n")
        else : 
            f.write("        val mRet = if (isExcept) new ArgInt(-1, true) else new ArgString(words(1)) \n")
        j = 1
        listConstruct = "        List(mRet" 
        for arg in m[1] :
            j = j+1
            if arg == "int" : 
                f.write("        val arg__" + str(j) + " = new ArgInt(words(" + str(j) + ").toInt) \n")
            elif arg == "boolean" :
                f.write("        val arg__" + str(j) \
                            + " = if (words(" + str(j) \
                            + ").toInt == 1) new ArgBoolean(true) else new ArgBoolean(false) \n")
            elif arg == "char" : 
                f.write("        val arg__" + str(j) + " = new ArgChar(words(" + str(j) + ")(0)) \n")
            else : 
                f.write("        val arg__" + str(j) + " = new ArgString(words(" + str(j) + ")) \n")
            listConstruct = listConstruct + ", arg__" + str(j)
        f.write(listConstruct + ") \n") 
        f.write("      } \n")
    f.write("      case _ => { \n")
    f.write("        val mRet = new ArgInt(-1) \n") 
    f.write("        List(mRet) \n")
    f.write("      } \n")
    f.write("    } \n")
    f.write("  } \n\n")
    
    f.write("  def sequentialExecute (tr: List[(Int, Int)]) (init: T) (verbose: Boolean) = { \n")
    f.write("    var consistent = true  \n")
    f.write("    val obj: T = new T(init) \n")
    f.write("    for ((tid, midx) <- tr; if consistent ) { \n")
    f.write("      val mEvent = methodLog(tid)(midx) \n")
    f.write("      mEvent.methodID match { \n")
    for i in range(0, mdNum) :
        m = test.methods[i] 
        f.write("        case " + str(i) + " => { \n")
        j = 0
        methodCall = "obj." + m[0] + "(" 
        for arg in m[1] : 
            if arg == "int" :
                f.write("          val arg__" + str(j) + "= mEvent.arguments(" + str(j) + ").toInt \n")
            elif arg == "boolean" :
                f.write("          val arg__" + str(j) + "= mEvent.arguments(" + str(j) + ").toBoolean \n")
            elif arg == "char" :
                f.write("          val arg__" + str(j) + "= mEvent.arguments(" + str(j) + ").toChar \n")
            else :
                f.write("          val arg__" + str(j) + "= mEvent.arguments(" + str(j) + ").toString \n")
            methodCall = methodCall + "arg__" + str(j) 
            j = j+1    
            if j < len(m[1]) : 
                methodCall = methodCall + ", " 
        methodCall = methodCall + ")"
        f.write("          try { \n")
        if m[2] == "obj[int]" or m[2] == "obj[String]" : 
            f.write("            val ret = Option(" + methodCall + ") \n") 
        else : 
            f.write("            val ret = " + methodCall + " \n") 
        if m[2] == "int" : 
            f.write("            if (ret != mEvent.retValue.toInt) { consistent = false } \n")
        elif m[2] == "boolean" : 
            f.write("            if (ret != mEvent.retValue.toBoolean) { consistent = false } \n")
        elif m[2] == "char" : 
            f.write("            if (ret != mEvent.retValue.toChar) { consistent = false } \n")
        elif m[2] == "obj[int]" : 
            f.write("            ret match { \n") 
            f.write("              case Some(x) => if (x != mEvent.retValue.toInt) { consistent = false }  \n") 
            f.write("              case None => if (mEvent.retValue.toInt >= 0) { consistent = false }  \n") 
            f.write("            } \n") 
        elif m[2] == "obj[String]" : 
            f.write("            ret match { \n") 
            f.write("              case Some(x) => if (x != mEvent.retValue.toString) { consistent = false }  \n") 
            f.write("              case None => if (mEvent.retValue.toString != \"null\") { consistent = false }  \n") 
            f.write("            } \n") 
        f.write("            if (verbose) println(\"Execute method {\" + mEvent.toString + \"} gets: \" + ret.toString) \n") 
        f.write("          } catch { \n")
        f.write("            case ex : java.lang.Exception => if (! mEvent.retValue.isException) { consistent = false } \n") 
        f.write("          } \n")
        f.write("        } \n")
    f.write("      } \n") 
    f.write("    } \n") 
    f.write("    if (consistent) Some(obj) else None \n")
    f.write("  } \n")
    f.write("} \n\n")


    f.write("object Simulate { \n") 
    f.write("  def main (args : Array[String]) { \n")
    f.write("  val (verbose, logName) = if (args(0) == \"-v\") (true, args(1)) else (false, args(0)) \n")
    f.write("  val simu : Simulation = new " + testClassname + "(logName, verbose) \n")
    f.write("  val finalState = simu.execute () \n")
    f.write("  if (! finalState.isEmpty) sys.exit(0) else sys.exit(1) \n")
    f.write("  } \n")
    f.write("} \n") 

    f.close() ;
    return testClassname
 
