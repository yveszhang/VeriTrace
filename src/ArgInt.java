package jtrace ;

public class ArgInt extends ArgType {
    private int value ;
    public ArgInt(int v) {
	argType = "int" ;
	value = v ;
    }
    public int toInt () {
	return value ;
    }
    public String toString () {
	return Integer.toString(value) ;
    }
}

