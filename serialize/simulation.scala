import iscas.lcs.veritrace.serialization._
import scala.util.Random
import scala.io.Source
import scala.collection.JavaConverters._

import java.io.File
import java.util.concurrent.ConcurrentLinkedQueue

object Simulation {

  def sequentialExecute (methodLog: Array[Array[MethodExec]]) (tr: List[(Int, Int)]) (init: ConcurrentLinkedQueue[Int]) = {
    var consistent = true 
    val qq: ConcurrentLinkedQueue[Int] = new ConcurrentLinkedQueue(init)
    for (mdIndex <- tr; if consistent ) {
      val msig = methodLog(mdIndex._1)(mdIndex._2)
      if (msig.name == "add") {
	val x = msig.arguments.head
	qq.add(x) ;
      }
      else {
	val x = Option(qq.poll())
	// println("Executing poll method: " + x.toString) 
	x match {
	  case Some(xx) => 
	    if (xx != msig.retValue) consistent = false
	  case None => 
	    if (msig.retValue >= 0) consistent = false
	}
      }
    }
    if (consistent) Some(qq) else None
  }

  def main (args : Array[String]) {
    if (args.length < 1) 
      println("Usage: scala Serialize [-v] <input log name>")
    else {
      val (verbose, baseName) = if (args(0) == "-v") (true, args(1)) else (false, args(0))
      val jvmName = baseName + ".jvmlog" 
      val testName = baseName + ".testlog" 
      val jvmLog = new File(jvmName) 
      val testLog = new File(testName) 
      if (jvmLog.exists()) 
	if (testLog.exists()) {
	  val mlog = Serialize.parseLog(jvmName, testName)
	  val segs = Serialize.partitionTrace(mlog) 
	  val queue: ConcurrentLinkedQueue[Int] = new ConcurrentLinkedQueue() 
	  var state: List[ (ConcurrentLinkedQueue[Int], List[(Int, Int)]) ] = List((queue, List()))
	  def transition (sts: List[ (ConcurrentLinkedQueue[Int], List[(Int, Int)]) ]) (tr: List[(Int, Int)]) = {
	    sts.toList.map( st => (sequentialExecute(mlog)(tr)(st._1), st._2 ::: tr) ).filter(_._1 != None).map{case (Some(x), y) => (x, y)}
	  }
	  // state.foreach(println)
	  var correct = true
	  for (tr <- segs if correct ) {
	    if (verbose) {
	      println("********************")
	      tr.foreach( x => println(mlog(x._1)(x._2)))
	    }
	    val interleaves = Serialize.serialize (mlog) (tr)
	    val oldState = state
	    var s: Set[List[Int]] = Set()
	    def noDuplication (q: ConcurrentLinkedQueue[Int]) = {
	      val l = (new java.util.ArrayList(q)).asScala.toList
	      if (s.contains(l)) false else {s = s + l; true}
	    }
	    state = interleaves.flatMap(tr => transition(oldState)(tr)).filter(st => noDuplication(st._1))
	    if (state.isEmpty) {
	      correct = false
	      println("There is no consistent sequential execution trace for this execution! This indicates a bug in the original program under testing.") 
	      // println(oldState.unzip._2)
	    }
	    else 
	      if (verbose) {
		print("Possible object state: ")
		state.foreach(st => print(st._1 + ", "))
		println()
	      }
	  }
	  if (correct) 
	    println("OK")
	}
	else 
	  println("Cannot find file " + testName) 
      else 
	println("Cannot find file " + jvmName) 
    }
  } // end of main

} // end of Object Serialize

