// 0: add(int):boolean; 1: poll():obj[int]; 2: size():int; 
import java.util.concurrent.* ; 

import jtrace.ArgType ; 
import jtrace.ArgInt ; 
import jtrace.ArgBoolean ; 
import jtrace.TraceRecord ; 
import java.io.* ;
import java.util.Random ;
import java.util.List ;
import java.util.LinkedList ;

class TestThread extends Thread { 
  private ConcurrentLinkedQueue<Integer> data ; 
  private int elemBase ; 
  private TraceRecord[] trace ; 

  TestThread (String name, ConcurrentLinkedQueue<Integer> q, TraceRecord[] tr) { 
    super(name) ; 
    this.data = q ; 
    this.elemBase = Integer.parseInt(name) * 1000 ;  
    this.trace = tr ; 
  } 

  public void run() { 
    int len = 100 ; 
    Random r = new Random() ; 
    int add__1; 
    boolean add__ret ; 
    Object poll__ret ; 
    int size__ret ; 
    for (int i = 0; i < len; i++) { 
      LinkedList<ArgType> args = new LinkedList<ArgType> () ; 
      int mid = r.nextInt(3) ; 
      switch (mid) { 
      case 0: 
        add__1 = elemBase + r.nextInt(1000) ; 
        args.add(new ArgInt(add__1)) ; 
        add__ret = data.add(add__1) ; 
        trace[i] = new TraceRecord(args, add__ret, mid) ; 
        break ; 
      case 1: 
        poll__ret = data.poll() ; 
        if (poll__ret == null) trace[i] = new TraceRecord(args, -1, mid) ; 
        else trace[i] = new TraceRecord(args, Integer.parseInt(poll__ret.toString()), mid) ; 
        break ; 
      case 2: 
        size__ret = data.size() ; 
        trace[i] = new TraceRecord(args, size__ret, mid) ; 
        break ; 
      default :  
      } 
    } 
  } 
} 

class TestingConcurrentLinkedQueueT2L100AddPollSize { 
  public static void main(String argv[]) { 
    int tdNum = 2, mdNum = 3, trLen = 100; 
    ConcurrentLinkedQueue<Integer> testObj = new ConcurrentLinkedQueue<Integer>() ; 
    TraceRecord[][] tr = new TraceRecord[tdNum][trLen] ; 
    TestThread[] thd = new TestThread[tdNum] ; 
    for (int i = 0; i < tdNum; i++) { 
      tr[i] = new TraceRecord[trLen] ; 
      thd[i] = new TestThread(Integer.toString(i), testObj, tr[i]) ; 
      thd[i].start() ; 
    } 
    try { 
      for (int i = 0; i < tdNum; i++)  
      thd[i].join() ; 
    } catch (Exception e) { 
      e.printStackTrace() ; 
    } 
    String fn = argv[0] ; 
    try { 
      FileWriter fw = new FileWriter(fn) ; 
      BufferedWriter out = new BufferedWriter(fw) ; 
      out.write("# <MethodIndex> <ArgumentValue> <ReturnValue>\n") ; 
      out.write("2 100 ConcurrentLinkedQueue add poll size\n") ; 
      for (int i=0; i < tdNum; i++) { 
        out.write("Thread " + i + "\n") ; 
        for (int j=0; j < tr[i].length; j++) out.write(tr[i][j].toString() + "\n") ; 
      } 
      out.close() ; 
    } catch (Exception e) { 
      System.err.println("Error: " + e) ; 
    } 
  } 
} 
