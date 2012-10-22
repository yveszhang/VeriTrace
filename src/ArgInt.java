package jtrace ;

public class ArgInt extends ArgType {
    private int value ;
    public ArgInt(int v) {
	argType = "int" ;
	value = v ;
    }
    public ArgInt(String t) {
	argType = t ;
	value = -1 ;
    }
    public ArgInt(int v, boolean b) {
	if (b) argType = "exception" ; 
	else argType = "int" ;
	value = v ;
	isException = b ;
    }
    public int toInt () {
	return value ;
    }
    public String toString () {
	if (argType == "void") return ("void") ;
	else return ( Integer.toString(value)) ;
    }
}

