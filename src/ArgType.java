package jtrace ;

public abstract class ArgType {
    public String argType ;
    public abstract String toString() ; // {
    // 	return  "" ;
    // }
    public int toInt() {
    	return (-1) ;
    }
    public boolean toBoolean() {
    	return  false ;
    }
    public char toChar() {
    	return  '*' ;
    }
}

