package jtrace ;

public abstract class ArgType {
    public String argType ;
    public boolean isException = false ;
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
    public static String encode(int x) {
	String v = "" + (char) (x % 7 + 65) ;
	x = x / 7 ;
	while (x != 0) {
	    v = v + (char) (x % 7 + 65) ;
	    x = x / 7 ;
	}
	return v ;
    }
}

