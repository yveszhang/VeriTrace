import java.io.* ;
import java.util.Random ;
import java.util.concurrent.*;

class TraceRecord {
    final int argument, retValue, methodIndex ;
    TraceRecord(int x, int y, int idx) {
	this.argument = x ;
	this.retValue = y ;
	this.methodIndex = idx ;
    }
}

class TestThread extends Thread {
    private ConcurrentLinkedQueue data ;
    private int elemBase ;
    private TraceRecord[] trace ;
    private String filename ;

    TestThread (String name, ConcurrentLinkedQueue q, int base, TraceRecord[] tr) {
	super(name) ;
	this.data = q ;
	this.elemBase = base * Integer.parseInt(name) ; 
	this.trace = tr ;
    }

    public void run() {
	int elem = elemBase, len = trace.length ;
	Random r = new Random() ;
	Object x ;

	for (int i = 0; i < len; i++) {
	    if (r.nextBoolean()) { // add an element
		data.add(elem) ;
		trace[i] = new TraceRecord(elem, 0, 0) ;
		elem++ ;
	    }
	    else { // remove an element
		if ((x = data.poll()) == null) 
		    trace[i] = new TraceRecord(0, -1, 1) ;
		else 
		    trace[i] = new TraceRecord(0, Integer.parseInt(x.toString()), 1) ;
	    }
	}

    } // end of Run method

} // end of TestThread class

object TestingConcurrentLinkedQueue {
    public static void main(String argv[]) {
	if (argv.length < 4) {
	    System.out.println("Usage: java <TestClass> [-<outputFile>] <ThreadNumber> <TraceLength> <ClassName> <MethodName1> ... <MethodNameN>"); 
	    System.exit(-1) ;
	}

	ConcurrentLinkedQueue testObj = new ConcurrentLinkedQueue() ;
	String fn, classname; 
	int tdNum, trLength, mdArgPos ; 
	if (argv[0].charAt(0) == '-') { 
	    fn = argv[0].substring(1) + ".testlog" ;
	    tdNum = Integer.parseInt(argv[1]) ;
	    trLength = Integer.parseInt(argv[2]) ;  
	    classname = argv[3] ;
	    mdArgPos = 4 ;
	}
	else {
	    fn = argv[2] + "-" + System.currentTimeMillis() + ".testlog";
	    tdNum = Integer.parseInt(argv[0]) ;
	    trLength = Integer.parseInt(argv[1]) ;
	    classname = argv[2] ;
	    mdArgPos = 3 ;
	}  
	int elemBase = 1, x = trLength ;
	while (x != 0) {
	    elemBase = elemBase * 10 ;
	    x = x / 10 ;
	} 
	int mdNum = 2 ;
	
	int len = trLength / tdNum + 1 ;
	TraceRecord[][] tr = new TraceRecord[tdNum][len] ;
	TestThread[] thd = new TestThread[tdNum] ;
	for (int i = 0; i < tdNum; i++) {
	    tr[i] = new TraceRecord[len] ;
	    thd[i] = new TestThread(Integer.toString(i), testObj, elemBase, tr[i]) ;
	    thd[i].start() ;
	}
	try {
	    for (int i = 0; i < tdNum; i++) 
		thd[i].join() ;
	} catch (Exception e) {
	    e.printStackTrace() ;
	}
	
	try {
	    FileWriter fw = new FileWriter(fn) ;
	    BufferedWriter out = new BufferedWriter(fw) ;
	    out.write("# <MethodIndex> <ArgumentValue> <ReturnValue>\n") ;
	    out.write(Integer.toString(tdNum) + " " + Integer.toString(len) + " " + classname) ;
	    for (int i = mdArgPos; i < argv.length; i++) 
		out.write(" " + argv[i]) ;
	    out.write("\n") ;
	    for (int i=0; i < tdNum; i++) {
		out.write("Thread " + i + "\n") ;
		for (int j=0; j < tr[i].length; j++) 
		out.write("" + tr[i][j].methodIndex + " " + tr[i][j].argument + " " + tr[i][j].retValue + "\n") ;
	    }
	    out.close() ;
	} catch (Exception e) {
	    System.err.println("Error: " + e) ;
	}
	
    }
}

