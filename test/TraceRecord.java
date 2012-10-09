package test ;

import java.util.List ;

public class TraceRecord {
    final int methodIndex ;
    final ArgType retValue ;
    final List<ArgType> arguments ;
    public TraceRecord(List<ArgType> args, ArgType ret, int idx) {
	this.arguments = args ;
	this.retValue = ret ;
	this.methodIndex = idx ;
    }

    public TraceRecord(List<ArgType> args, int ret, int idx) {
	this.arguments = args ;
	this.retValue = new ArgInt(ret) ;
	this.methodIndex = idx ;
    }

    public TraceRecord(List<ArgType> args, boolean ret, int idx) {
	this.arguments = args ;
	this.retValue = new ArgBoolean(ret) ;
	this.methodIndex = idx ;
    }

    public String toString() {
	String str = Integer.toString(this.methodIndex) + " " + retValue.toString() ;
	for (int i = 0; i < arguments.size(); i++) 
	    str = str + " " + arguments.get(i).toString() ;
	return str ;
    }
}
