package jtrace ;

public class ArgBoolean extends ArgType {
    private boolean value ;
    public ArgBoolean(boolean v) {
	argType = "boolean" ;
	value = v ;
    }
    public boolean toBoolean () {
	return value ;
    }
    public String toString () {
	if (value) return "1" ;
	else return "0" ;
    }
}

