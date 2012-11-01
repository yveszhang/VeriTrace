// 0: add(int):boolean; 1: remove(int):boolean; 
import concurrency._ ; 

import jtrace.ArgType ; 
import jtrace.ArgInt ; 
import jtrace.ArgBoolean ; 
import jtrace.ArgChar ; 
import jtrace.ArgString ; 
import jtrace.Simulation ; 
import java.io.File ;
import scala.collection.JavaConverters._; 

class SimulateLockFreeListT2L200AddRemove(logName: String, verbose: Boolean) extends Simulation(logName, verbose) { 
  type T = LockFreeList[java.lang.Integer] 
  val methodLog : MethodTable = parseLog 
  val traceSegmentation : List[List[(Int,Int)]] = partitionTrace 
  val initSimuState : SimuState = List( (new T(), Nil) ) 

    type ST = String
    def encodeObject (o: T) = o.toString

  def parseTestLine (line: String) : List[ArgType]= { 
    val words = line.split(' ') 
    val isExcept = (words(0) == "E") 
    val methodID = if (isExcept) words(1).toInt else words(0).toInt 
    methodID match { 
      case 0 => { 
        val mRet = if (isExcept) new ArgInt(-1, true) else if (words(1).toInt == 1) new ArgBoolean(true) else new ArgBoolean(false) 
        val arg__2 = new ArgInt(words(2).toInt) 
        List(mRet, arg__2) 
      } 
      case 1 => { 
        val mRet = if (isExcept) new ArgInt(-1, true) else if (words(1).toInt == 1) new ArgBoolean(true) else new ArgBoolean(false) 
        val arg__2 = new ArgInt(words(2).toInt) 
        List(mRet, arg__2) 
      } 
      case _ => { 
        val mRet = new ArgInt(-1) 
        List(mRet) 
      } 
    } 
  } 

  def sequentialExecute (tr: List[(Int, Int)]) (init: T) (verbose: Boolean) = { 
    var consistent = true  
    val obj: T = init.clone
    for ((tid, midx) <- tr; if consistent ) { 
      val mEvent = methodLog(tid)(midx) 
      mEvent.methodID match { 
        case 0 => { 
          val arg__0= mEvent.arguments(0).toInt 
          try { 
            val ret = obj.add(arg__0) 
            if (ret != mEvent.retValue.toBoolean) { consistent = false } 
            if (verbose) println("Execute method {" + mEvent.toString + "} gets: " + ret.toString) 
          } catch { 
            case ex : java.lang.Exception => if (! mEvent.retValue.isException) { consistent = false } 
          } 
        } 
        case 1 => { 
          val arg__0= mEvent.arguments(0).toInt 
          try { 
            val ret = obj.remove(arg__0) 
            if (ret != mEvent.retValue.toBoolean) { consistent = false } 
            if (verbose) println("Execute method {" + mEvent.toString + "} gets: " + ret.toString) 
          } catch { 
            case ex : java.lang.Exception => if (! mEvent.retValue.isException) { consistent = false } 
          } 
        } 
      } 
    } 
    if (consistent) Some(obj) else None 
  } 
} 

object Simulate { 
  def main (args : Array[String]) { 
  val (verbose, logName) = if (args(0) == "-v") (true, args(1)) else (false, args(0)) 
  val simu : Simulation = new SimulateLockFreeListT2L200AddRemove(logName, verbose) 
  val finalState = simu.execute () 
  if (! finalState.isEmpty) sys.exit(0) else sys.exit(1) 
  } 
} 
