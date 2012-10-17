package jtrace

// import scala.util.Random
import scala.io.Source
import scala.collection.JavaConverters._

// import java.io.File
// import java.util.concurrent.ConcurrentLinkedQueue

class MethodExec (tid: Int, mid: Int, mName: String, sts: Int, ets: Int, mArgs: List[ArgType], mValue: ArgType) {
  require (ets >= sts) 
  def this (tid: Int, mid: Int, mName: String, sts: Int, ets: Int, mArgs: java.util.List[ArgType], mValue: ArgType) = 
    this(tid, mid, mName, sts, ets, mArgs.asScala.toList, mValue)
  override def toString = 
    ( "TH" + tid +" M" + mid + "(" + mName + "): [" 
     + ("" /: mArgs.map(_.toString())) (_+_+",") 
     + "], " +  mValue.toString() + ", " + sts + "--" + ets
   )
  def timeStamp = (sts, ets) 
  def startTime = sts
  def endTime = ets
  def methodID = mid
  def name = mName
  def arguments = mArgs
  def retValue = mValue
}

// private sealed abstract class TimedEvent
// case class TECall (timeStamp: Int, threadID: Int, methodName: String, arguments: List[Int]) extends TimedEvent
// case class TERetn (timeStamp: Int, threadID: Int, methodName: String, retValue: Int) extends TimedEvent

// private sealed abstract class MethodEvent 
// case class MCall (threadID: Int, eventID: Int) extends MethodEvent
// case class MReturn (threadID: Int, eventID: Int) extends MethodEvent

abstract class Simultation (logName: String) {
  type T 
  type SimuState = List[(T, List[(Int, Int)])]
  type MethodTable = Array[Array[MethodExec]] 

  def parseTestLine (line: String) : List[ArgType]
  
  def parseLog () = {
    var tid = 0
    val testLines = Source.fromFile(logName+".testlog").getLines().toArray
    val jvmLines = Source.fromFile(logName+".jvmlog").getLines().toArray
    val args = testLines(1).split(' ') 
    val tdNum = args(0).toInt
    val len = args(1).toInt
    val classname = args(2) 
    val methods = args.slice(3, args.length) 
    val mlog : MethodTable = Array.tabulate(tdNum){ (tid) => new Array[MethodExec](len) } // all methods
    val firstLines = for (tid <- 0 until tdNum) yield (jvmLines(tid*(len+1)+3).split(' ').map(_.toInt).toArray)
    val minStamp = (for (nums <- firstLines) yield (nums(1))).min - 1
    for (tid <- 0 until tdNum ) {
      val base = tid * (len+1) + 3
      for ( li <- 0 until len ) {
	val testLine = testLines(base+li)
	val mid = (testLine.split(' '))(0).toInt
	val jvmLine = jvmLines(base+li).split(' ').map(_.toInt) 
	if (mid == jvmLine(0)) {
	  val mRetArgs = parseTestLine (testLine) 
	  mlog(tid)(li) = 
	    new MethodExec(tid, mid, methods(mid), jvmLine(1)-minStamp, jvmLine(2)-minStamp, mRetArgs.tail, mRetArgs.head) 
	}
      }
    }
    mlog
  }

  lazy val methodLog : MethodTable = parseLog 

  private def partitionTrace () = {
    // Return a list of trace segments, and each segment contains events to be interleaved.
    // (Int, Int) is (thread ID, event index), i.e., methodLog(tid)(eid)
    // methodLog must be sorted in temporal order, resulted segments are all sorted (by the start time)
    val tdNum = methodLog.length 
    if (tdNum <= 0) 
      Nil
    else {
      def insertTS (ts: (Int, Int), frame: List[(Int, Int)]) : List[(Int, Int)] =  
	frame match {
	  case Nil => List(ts) 
	  case ts0 :: tsfr => if (ts._2 <= ts0._2) (ts :: frame) else (ts0 :: (insertTS(ts, tsfr)) ) 
	}
      val tdActive: Array[Boolean] = Array.fill(tdNum){ false } // false indicates non-active thread
      val tdIndex: Array[Int] = Array.fill(tdNum)(0)
      var active = 0 
      val evNum = (0 /: methodLog) ((x, y) => x + y.length)
      var tsFrame = (for (i <- 0 until tdNum) yield (i, methodLog(i)(0).startTime)).toList.sortBy(x => x._2)
      var segments: List[List[(Int, Int)]] = Nil
      var aseg: List[(Int, Int)] = Nil
      while (tsFrame.length > 0) {
	val (tid, ts) = tsFrame.head
	if (tdActive(tid)) {
	  tdActive(tid) = false
	  active = active - 1
	  if (active == 0) {
	    segments = aseg.reverse :: segments
	    aseg = Nil 
	  }
	  tdIndex(tid) = tdIndex(tid) + 1
	  if (tdIndex(tid) < methodLog(tid).length) {
	    val newTS = (tid, methodLog(tid)(tdIndex(tid)).startTime)
	    tsFrame = insertTS(newTS, tsFrame.tail)
	  }
	  else 
	    tsFrame = tsFrame.tail
	}
	else {
	  tdActive(tid) = true 
	  active = active + 1
	  aseg = (tid, tdIndex(tid)) :: aseg
	  val newTS = (tid, methodLog(tid)(tdIndex(tid)).endTime)
	  tsFrame = insertTS(newTS, tsFrame.tail)
	}
      }
      segments.reverse
    }
  }

  lazy val traceSegmentation : List[List[(Int,Int)]] = partitionTrace

  private def interleave[T](ls: List[List[T]]) : List[List[T]] = {
    // a pure interleaving of lists, preserving only the order in every single list
    val lss = ls.filter((x) => x != Nil) 
    lss.length match {
      case 0 => Nil
      case 1 => List(lss(0))
      case _ => {
	def removeNthHead (n: Int) = { lss.slice(0,n).toList ::: (lss(n).tail :: lss.slice(n+1, lss.length).toList) }
	val heads = (0 until lss.length).toList.map( i => (lss(i).head, removeNthHead(i))) 
	def addHead (x: (T, List[List[T]])) = { interleave(x._2).map( (l) => x._1 :: l) }
	heads.flatMap(addHead)
      }
    }
  }
  
  def quiecentInterleave (tr: List[(Int, Int)]) : List[List[(Int, Int)]] = {
    val tdNum = methodLog.length 
    val tdTrace = tr.groupBy( x => x._1 ).values.toList //.map(trEventSort)
    interleave(tdTrace)
  }

  def serialize (tr: List[(Int, Int)]) : List[List[(Int, Int)]] = {
    // Both tr and methodLog must be sorted in temporal order 
    // The method does interleaving of tr, preserving temporal order 
    val tdNum = methodLog.length 
    // def trEventSort (es: List[(Int, Int)]) = 
    //   es.sortWith( (e1, e2) => methodLog(e1._1)(e1._2).timeStamp._1 <= methodLog(e2._1)(e2._2).timeStamp._1 )
    val tdTrace = tr.groupBy( x => x._1 ).values.toList //.map(trEventSort)
    val allInterleaving = interleave(tdTrace)
    def isTemporal (tr: List[(Int, Int)]) = {
      val lastStart = Array.fill(tdNum)(-1)
      var yes = true 
      for ((tid, eid) <- tr if yes) {
	val (sts, ets) = methodLog(tid)(eid).timeStamp
	lastStart(tid) = sts
	for (i <- 0 until tdNum if i != tid && yes) 
	  if (lastStart(i) >= 0 && ets < lastStart(i)) yes = false 
      }
      yes 
    }
    allInterleaving.filter(isTemporal)
  }

  val initSimuState : SimuState

  def sequentialExecute (tr: List[(Int, Int)]) (init: T) : Option[T]

  private def transition (sts: SimuState) (tr: List[(Int, Int)]) : SimuState = {
    var objSet: Set[T] = Set() 
    for {
      (initObj, initTrace) <- sts 
      res = sequentialExecute (tr) (initObj) 
      if res != None
      newObj = res.get 
      if !(objSet.contains(newObj)) 
    } yield { objSet = objSet + newObj; (newObj, initTrace ::: tr) }
  }

  private def executeRec (st: SimuState) (segs: List[List[(Int,Int)]]) : SimuState = {
    val interleaves = serialize (segs.head) 
    val newState = interleaves.flatMap(transition (st) )
    if (newState.isEmpty) {
      println("There is no consistent sequential execution trace for this execution! This indicates a bug in the original program under testing.") 
      newState 
    }
    else 
      executeRec (newState) (segs.tail) 
  }

  def execute () = executeRec (initSimuState) (traceSegmentation) 

} // end of abstract class Simulation



