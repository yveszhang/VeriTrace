package iscas.lcs.veritrace.test ;

import iscas.lcs.veritrace.test.ArgType ;

public class ArgInt extends ArgType {
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

