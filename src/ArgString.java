package jtrace ;

public class ArgString extends ArgType {
    private String value ;
    public ArgString(String v) {
	argType = "string" ;
	value = v ;
    }
    public String toString () {
	return value ;
    }
}

