package test ;

import java.util.List ;

class ArgType {
    public String argType ;
    public String toString() {
	return  "" ;
    }
}

class ArgInt extends ArgType {
    private int value ;
    public ArgInt(int v) {
	argType = "int" ;
	value = v ;
    }
    public int getValue () {
	return value ;
    }
    public String toString () {
	return Integer.toString(value) ;
    }
}

class ArgBoolean extends ArgType {
    private boolean value ;
    public ArgBoolean(boolean v) {
	argType = "boolean" ;
	value = v ;
    }
    public boolean getValue () {
	return value ;
    }
    public String toString () {
	return Boolean.toString(value) ;
    }
}

class TraceRecord {
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

