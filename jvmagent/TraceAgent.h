#include <iostream>
#include <string>
#include <jvmti.h>

typedef struct {
  long timeStamp ;
  int threadIndex ;
  int methodIndex ;
  int argValue ;
  bool isCall ;
} TraceEvent ;

class AgentException {
public:
  AgentException (jvmtiError err) {
    m_error = err;
  }

  std::string what() const throw() {
    return "AgentException";
  }

  jvmtiError ErrCode() const throw() {
    return m_error;
  }

private:
  jvmtiError m_error;
} ;

class TraceAgent {
public:
  TraceAgent() throw(AgentException) ;
  ~TraceAgent() throw(AgentException) ;
  
  void initialize (JavaVM *vm) const throw (AgentException);
  void parseOptions (const char* str) const throw (AgentException);
  void addCapability () const throw (AgentException);
  void registerEvent () const throw (AgentException);
  static void JNICALL handleMethodEntry (jvmtiEnv* jvmti, JNIEnv* jni, jthread thread, jmethodID method);

private:
  static void checkException(jvmtiError error) throw(AgentException) {
    if (error != JVMTI_ERROR_NONE) {
      throw AgentException(error);
    }
  }

  static jvmtiEnv *m_jvmti;
  static char* m_filter; 

  static TraceEvent* trace ;
};
