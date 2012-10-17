// 0: add(int):boolean; 1: poll():obj[int]; 2: size():int; 
import java.util.concurrent._ ; 

import jtrace.ArgType ; 
import jtrace.ArgInt ; 
import jtrace.ArgBoolean ; 
import jtrace.Simulation ; 
import java.io.File ;
import scala.collection.JavaConverters._; 

class SimulateConcurrentLinkedQueueT2L100AddPollSize(logName: String, verbose: Boolean) extends Simulation(logName, verbose) { 
  type T = ConcurrentLinkedQueue[Int] 
  val methodLog : MethodTable = parseLog 
  val traceSegmentation : List[List[(Int,Int)]] = partitionTrace 
  val initSimuState : SimuState = List( (new T(), Nil) ) 

  // optimization code can be supplied here by defining ST and encodeObject 
  type ST = List[Int]
  def encodeObject(o: T) = (new java.util.ArrayList(o)).asScala.toList

  def parseTestLine (line: String) : List[ArgType]= { 
    val words = line.split(' ') 
    words(0).toInt match { 
      case 0 => { 
        val mRet = if (words(1).toInt == 1) new ArgBoolean(true) else new ArgBoolean(false) 
        val arg__2 = new ArgInt(words(2).toInt) 
        List(mRet, arg__2) 
      } 
      case 1 => { 
        val mRet = new ArgInt(words(1).toInt) 
        List(mRet) 
      } 
      case 2 => { 
        val mRet = new ArgInt(words(1).toInt) 
        List(mRet) 
      } 
      case _ => { 
        val mRet = new ArgInt(-1) 
        List(mRet) 
      } 
    } 
  } 

  def sequentialExecute (tr: List[(Int, Int)]) (init: T) = { 
    var consistent = true  
    val obj: T = new T(init) 
    for ((tid, midx) <- tr; if consistent ) { 
      val mEvent = methodLog(tid)(midx) 
      mEvent.methodID match { 
        case 0 => { 
          val arg__0= mEvent.arguments(0).toInt 
          val ret = obj.add(arg__0)
          if (ret != mEvent.retValue.toBoolean) { consistent = false } 
        } 
        case 1 => { 
          val ret = Option(obj.poll()) 
          ret match { 
            case Some(x) => if (x != mEvent.retValue.toInt) { consistent = false }  
            case None => if (mEvent.retValue.toInt >= 0) { consistent = false }  
          } 
        } 
        case 2 => { 
          val ret = obj.size()
          if (ret != mEvent.retValue.toInt) { consistent = false } 
        } 
      } 
    } 
    if (consistent) Some(obj) else None 
  } 
} 

object Simulate { 
  def main (args : Array[String]) { 
  val (verbose, logName) = if (args(0) == "-v") (true, args(1)) else (false, args(0)) 
  val simu : Simulation = new SimulateConcurrentLinkedQueueT2L100AddPollSize(logName, verbose) 
  val finalState = simu.execute () 
  if (! finalState.isEmpty) exit(0) else exit(1) 
  } 
} 
