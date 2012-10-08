package iscas.lcs.veritrace.test ;

public class TraceRecord {
    final int methodIndex ;
    final ArgType retValue ;
    final List<ArgType> arguments ;
    TraceRecord(List<ArgType> args, ArgType ret, int idx) {
	this.arguments = args ;
	this.retValue = ret ;
	this.methodIndex = idx ;
    }

    public String toString() {
	String str = Integer.toString(this.methodIndex) + " " + retValue.toString() ;
	for (int i = 0; i < arguments.size(); i++) 
	    str = str + " " + arguments.get(i).toString() ;
	return str ;
    }
}
