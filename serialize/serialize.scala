package serialize

// import scala.util.Random
import scala.io.Source
// import scala.collection.JavaConverters._

// import java.io.File
// import java.util.concurrent.ConcurrentLinkedQueue

sealed abstract class TimedEvent
case class TECall (timeStamp: Int, threadID: Int, methodName: String, arguments: List[Int]) extends TimedEvent
case class TERetn (timeStamp: Int, threadID: Int, methodName: String, retValue: Int) extends TimedEvent

class MethodExec (threadID: Int, methodName: String, sts: Int, ets: Int, args: List[Int], value: Int) {
  override def toString = 
    ( "TH" + threadID +" " + methodName + ": [" 
     + ("" /: args.map(_.toString)) (_+_+",") 
     + "], " +  value + ", " + sts + "--" + ets
   )
  def timeStamp = (sts, ets) 
  def startTime = sts
  def endTime = ets
  def name = methodName
  def arguments = args
  def retValue = value
}

sealed abstract class MethodEvent 
case class MCall (threadID: Int, eventID: Int) extends MethodEvent
case class MReturn (threadID: Int, eventID: Int) extends MethodEvent

object Serialize {

  type ThreadState = Option[MethodEvent] // None for idle state
  
  def parseLog (jvmlog: String, testlog: String): Array[Array[MethodExec]] = {
    var tid = 0
    val testLines = Source.fromFile(testlog).getLines().toArray
    val jvmLines = Source.fromFile(jvmlog).getLines().toArray
    val args = testLines(1).split(' ') 
    val tdNum = args(0).toInt
    val len = args(1).toInt
    val classname = args(2) 
    val methods = args.slice(3, args.length) 
    val methodLog : Array[Array[MethodExec]] = Array.tabulate(tdNum){ (tid) => new Array[MethodExec](len) } // all methods
    val firstLines = for (tid <- 0 until tdNum) yield (jvmLines(tid*(len+1)+3).split(' ').map(_.toInt).toArray)
    val minStamp = (for (nums <- firstLines) yield (nums(1))).min - 1
    // println(minStamp)
    for (tid <- 0 until tdNum ) {
      val base = tid * (len+1) + 3
      for ( li <- 0 until len ) {
	val testNums = testLines(base+li).split(' ').map(_.toInt)
	val jvmNums = jvmLines(base+li).split(' ').map(_.toInt) 
	if (testNums(0) == jvmNums(0)) 
	  methodLog(tid)(li) = 
	    new MethodExec(tid, methods(testNums(0)), jvmNums(1)-minStamp, jvmNums(2)-minStamp, List(testNums(1)), testNums(2)) 
      }
    }
    methodLog
  }

  def partitionTrace (methodLog: Array[Array[MethodExec]]): List[List[(Int, Int)]] = {
    // Return a list of trace segments, and each segment contains events to be interleaved.
    // (Int, Int) is (thread ID, event index)
    // methodLog must be sorted in temporal order, resulted segments are all sorted (by the start time)
   val tdNum = methodLog.length 
    if (tdNum <= 0) Nil
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

  def interleave[T](ls: List[List[T]]) : List[List[T]] = {
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
  
  def quiecentInterleave (methodLog: Array[Array[MethodExec]]) (tr: List[(Int, Int)]) : List[List[(Int, Int)]] = {
    val tdNum = methodLog.length 
    val tdTrace = tr.groupBy( x => x._1 ).values.toList //.map(trEventSort)
    interleave(tdTrace)
  }

  def serialize (methodLog: Array[Array[MethodExec]]) (tr: List[(Int, Int)]) : List[List[(Int, Int)]] = {
    // Both tr and methodLog must be sorted in temporal order 
    // interleaving and preserving all temporal order 
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


  // def sequentialExecute (methodLog: Array[Array[MethodExec]]) (tr: List[(Int, Int)]) (init: ConcurrentLinkedQueue[Int]) = {
  //   var consistent = true 
  //   val qq: ConcurrentLinkedQueue[Int] = new ConcurrentLinkedQueue(init)
  //   for (mdIndex <- tr; if consistent ) {
  //     val msig = methodLog(mdIndex._1)(mdIndex._2)
  //     if (msig.name == "add") {
  // 	val x = msig.arguments.head
  // 	qq.add(x) ;
  //     }
  //     else {
  // 	val x = Option(qq.poll())
  // 	// println("Executing poll method: " + x.toString) 
  // 	x match {
  // 	  case Some(xx) => 
  // 	    if (xx != msig.retValue) consistent = false
  // 	  case None => 
  // 	    if (msig.retValue >= 0) consistent = false
  // 	}
  //     }
  //   }
  //   if (consistent) Some(qq) else None
  // }

  // def main (args : Array[String]) {
  //   if (args.length < 1) 
  //     println("Usage: scala Serialize [-v] <input log name>")
  //   else {
  //     val (verbose, baseName) = if (args(0) == "-v") (true, args(1)) else (false, args(0))
  //     val jvmName = baseName + ".jvmlog" 
  //     val testName = baseName + ".testlog" 
  //     val jvmLog = new File(jvmName) 
  //     val testLog = new File(testName) 
  //     if (jvmLog.exists()) 
  // 	if (testLog.exists()) {
  // 	  val mlog = parseLog(jvmName, testName)
  // 	  val segs = partitionTrace(mlog) 
  // 	  val queue: ConcurrentLinkedQueue[Int] = new ConcurrentLinkedQueue() 
  // 	  var state: List[ (ConcurrentLinkedQueue[Int], List[(Int, Int)]) ] = List((queue, List()))
  // 	  def transition (sts: List[ (ConcurrentLinkedQueue[Int], List[(Int, Int)]) ]) (tr: List[(Int, Int)]) = {
  // 	    sts.toList.map( st => (sequentialExecute(mlog)(tr)(st._1), st._2 ::: tr) ).filter(_._1 != None).map{case (Some(x), y) => (x, y)}
  // 	  }
  // 	  // state.foreach(println)
  // 	  var correct = true
  // 	  for (tr <- segs if correct ) {
  // 	    if (verbose) {
  // 	      println("********************")
  // 	      tr.foreach( x => println(mlog(x._1)(x._2)))
  // 	    }
  // 	    val interleaves = serialize (mlog) (tr)
  // 	    val oldState = state
  // 	    var s: Set[List[Int]] = Set()
  // 	    def noDuplication (q: ConcurrentLinkedQueue[Int]) = {
  // 	      val l = (new java.util.ArrayList(q)).asScala.toList
  // 	      if (s.contains(l)) false else {s = s + l; true}
  // 	    }
  // 	    state = interleaves.flatMap(tr => transition(oldState)(tr)).filter(st => noDuplication(st._1))
  // 	    if (state.isEmpty) {
  // 	      correct = false
  // 	      println("There is no consistent sequential execution trace for this execution! This indicates a bug in the original program under testing.") 
  // 	      // println(oldState.unzip._2)
  // 	    }
  // 	    else 
  // 	      if (verbose) {
  // 		print("Possible object state: ")
  // 		state.foreach(st => print(st._1 + ", "))
  // 		println()
  // 	      }
  // 	  }
  // 	  if (correct) 
  // 	    println("OK")
  // 	}
  // 	else 
  // 	  println("Cannot find file " + testName) 
  //     else 
  // 	println("Cannot find file " + jvmName) 
  //   }
  // } // end of main

} // end of Object Serialize

