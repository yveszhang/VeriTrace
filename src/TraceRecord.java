package jtrace ;

import java.util.List ;

public class TraceRecord {
    final int methodIndex ;
    final ArgType retValue ;
    final List<ArgType> arguments ;
    final boolean isException ; 
    public TraceRecord(List<ArgType> args, ArgType ret, int idx, boolean e) {
	this.arguments = args ;
	this.retValue = ret ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public TraceRecord(List<ArgType> args, int ret, int idx, boolean e) {
	this.arguments = args ;
	this.retValue = new ArgInt(ret) ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public TraceRecord(List<ArgType> args, boolean ret, int idx, boolean e) {
	this.arguments = args ;
	this.retValue = new ArgBoolean(ret) ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public TraceRecord(List<ArgType> args, char ret, int idx, boolean e) {
	this.arguments = args ;
	this.retValue = new ArgChar(ret) ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public TraceRecord(List<ArgType> args, String ret, int idx, boolean e) {
	this.arguments = args ;
	this.retValue = new ArgString(ret) ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public TraceRecord(List<ArgType> args, char[] ret, int idx, boolean e) {
	this.arguments = args ;
	this.retValue = new ArgString(new String(ret)) ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public TraceRecord(List<ArgType> args, StringBuffer ret, int idx, boolean e) {
	this.arguments = args ; 
	this.retValue = new ArgString(ret.toString()) ;
	this.methodIndex = idx ;
	this.isException = e ;
    }

    public String toString() {
	String str ; 
	if (isException) 
	    str = "E " + Integer.toString(this.methodIndex) ;
	else 
	    str = Integer.toString(this.methodIndex) + " " + retValue.toString() ;
	for (int i = 0; i < arguments.size(); i++) 
	    str = str + " " + arguments.get(i).toString() ;
	return str ;
    }
}
