package jtrace ;

public class ArgChar extends ArgType {
    private char value ;
    public ArgChar(char v) {
	argType = "char" ;
	value = v ;
    }
    public char toChar () {
	return value ;
    }
    public String toString () {
	return Character.toString(value) ;
    }
}

