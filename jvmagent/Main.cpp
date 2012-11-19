#include <iostream>
#include <sstream>
#include <fstream>
#include <string> 
#include <vector>
#include <set>
#include <map>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <sys/types.h>

#include <jvmti.h>

// #include "TraceAgent.h"

using namespace std;

typedef struct timeval TimeStamp ;

int string_to_int (string s) {
  unsigned int i = 0 ;
  int val = 0; 
  while (i < s.size()) {
    if (s[i] >= '0' && s[i] <= '9') 
      val = val * 10 + (s[i] - '0') ;
    else 
      return val ;
    i++ ;
  } ;
  return val ;
} ;

inline long getTimeStamp (struct timeval * init) {
  TimeStamp t ;
  gettimeofday(&t, NULL) ;
  return ((t.tv_sec == init->tv_sec) ? (t.tv_usec-init->tv_usec) : ((t.tv_sec-init->tv_sec)*1000000+t.tv_usec-init->tv_usec)) ;
}

class TraceEvent {
public: 
  long timeStamp ;
  //  int threadIndex ;
  int methodIndex ;
  bool isCall ;

  TraceEvent (long ts, int mid, bool b) {
    timeStamp = ts ;
    // threadIndex = tid ;
    methodIndex = mid ;
    isCall = b ;
  } ;
};

class AgentException {
public:
  AgentException(jvmtiError err) {  m_error = err;  }
  string what() const throw() { return string("AgentException"); }
  jvmtiError ErrCode() const throw() { return m_error; }

private:
  jvmtiError m_error;
};

class TraceAgent {
public:
  int threadNum, traceLength, methodNum ;
  string testClass, outputFile, methodPrefix ;
  //  map<string, int> testMethods ; // map method names to number 
  map<jmethodID, int> *methodKeys ; // 
  vector<TraceEvent> *traces ;
  jvmtiEnv * jvmEnv ;

  TraceAgent () {
    threadNum = 2 ;
    traceLength = 100 ;
  } ;
  
  TraceAgent (int tdNum, int len) {
    threadNum = tdNum ;
    traceLength = len ;
  } ;

  ~TraceAgent() {
    // delete &testClass ;
    // delete &testMethods ;
    // delete methodKeys ;
    // delete traces ;
    // delete jvmEnv ;
  }
} ;

static TraceAgent* agent ;
static TimeStamp init_stamp ; // = malloc(sizeof(struct timeval));

void checkException(jvmtiError error) throw(AgentException) {
  if (error != JVMTI_ERROR_NONE) 
    throw AgentException(error);
} ;

inline void printAgentInfo() {
  cout << "Agent [" << agent->testClass << "]: " ;
  cout << agent->threadNum << " thread * " << agent->traceLength << " events" << endl ;
} ;

void handleMethodEntry(jvmtiEnv* env, JNIEnv* jni, jthread thread, jmethodID method) {
  jvmtiError err ;

  jvmtiThreadInfo thdInfo ;
  err = env->GetThreadInfo(thread, &thdInfo) ;
  int thID = string_to_int(thdInfo.name) ;
  env->Deallocate( (unsigned char *) thdInfo.name) ;
  
  map<jmethodID,int>::iterator it = agent->methodKeys[thID].find(method) ;
  if ( it == agent->methodKeys[thID].end() ) { // method not yet recorded 
    agent->methodKeys[thID][method] = -1 ; // default value is -1, denoting a method not to be recorded
    char* name_ptr ; 
    err = env->GetMethodName(method, &name_ptr, NULL, NULL) ;
    if ( string(name_ptr).compare(0, agent->methodPrefix.size(), agent->methodPrefix) == 0 ) { // method name matches, checking the class
      jclass methodClass ;
      char* class_sig ;
      err = env->GetMethodDeclaringClass(method, &methodClass) ;
      err = env->GetClassSignature(methodClass, &class_sig, NULL) ;
      // cout << name_ptr << ": " << class_sig << endl ;
      // string fullClassPath(class_sig) ;
      // int startPos = fullClassPath.rfind('/'), endPos = fullClassPath.rfind(';') ;
      // string classname = fullClassPath.substr(startPos+1, endPos-startPos-1) ;
      if ( agent->testClass.compare(class_sig) == 0 ) {  // method class matches, is the interesting method 
	agent->methodKeys[thID][method] = string_to_int(&name_ptr[agent->methodPrefix.size()]) ;
	cout << "TID " << thID << ": " << name_ptr << " -> " << agent->methodKeys[thID][method] << "; " << class_sig << endl ;
      }
      env->Deallocate( (unsigned char *) class_sig) ;
    }
    env->Deallocate( (unsigned char *) name_ptr) ;
  }
  int mdID = agent->methodKeys[thID][method] ;
  if (mdID >= 0) {
    //    cout << mdID << endl ;
    long ts = getTimeStamp(&init_stamp) ;
    agent->traces[thID].push_back( TraceEvent(ts, mdID, true) ) ;
  }
} ;

void handleMethodExit(jvmtiEnv* env, JNIEnv* jni, jthread thread, jmethodID method, jboolean b, jvalue v) {
  long ts = getTimeStamp(&init_stamp) ;
  jvmtiError err ;

  jvmtiThreadInfo thdInfo ;
  err = env->GetThreadInfo(thread, &thdInfo) ;
  // Map method ID to (thread ID, method ID)
  int thID = string_to_int(thdInfo.name) ;
  env->Deallocate( (unsigned char *) thdInfo.name) ;
  
  // map<jmethodID,int>::iterator it = agent->methodKeys[thID].find(method) ;
  // if ( it == agent->methodKeys[thID].end() ) { // method not yet recorded 
  //   char* name_ptr ; 
  //   err = env->GetMethodName(method, &name_ptr, NULL, NULL) ;
  //   if ( agent->testMethods.find(name_ptr) != agent->testMethods.end() ) { // method name matches, checking the class
  //     jclass methodClass ;
  //     char* class_sig ;
  //     err = env->GetMethodDeclaringClass(method, &methodClass) ;
  //     err = env->GetClassSignature(methodClass, &class_sig, NULL) ;
  //     string fullClassPath(class_sig) ;
  //     int startPos = fullClassPath.rfind('/'), endPos = fullClassPath.rfind(';') ;
  //     string classname = fullClassPath.substr(startPos+1, endPos-startPos-1) ;
  //     if ( classname == agent->testClass )   // method class matches, is the interesting method 
  // 	agent->methodKeys[thID][method] = agent->testMethods[name_ptr] ;
  //     else 
  // 	agent->methodKeys[thID][method] = -1 ;
  //     env->Deallocate( (unsigned char *) class_sig) ;
  //   }
  //   else {
  //     agent->methodKeys[thID][method] = -1 ;
  //   }
  //   env->Deallocate( (unsigned char *) name_ptr) ;
  // }
  int mdID = agent->methodKeys[thID][method] ;
  if (mdID >= 0) {
    agent->traces[thID].push_back( TraceEvent(ts, mdID, false) ) ;
  }
} ;

void initialize(JavaVM *vm) throw (AgentException) {
  jvmtiEnv *jvmti = 0;

  // Get environment
  jint ret = (vm)->GetEnv(reinterpret_cast<void**>(&jvmti), JVMTI_VERSION_1_1);
  if (ret != JNI_OK || jvmti == 0) {
    throw AgentException(JVMTI_ERROR_INTERNAL);
  }

  // Add capabilities
  jvmtiCapabilities caps ;
  memset(&caps, 0, sizeof(caps)) ;
  caps.can_generate_method_entry_events = 1 ;
  caps.can_generate_method_exit_events = 1 ;
  jvmtiError err = jvmti->AddCapabilities(&caps) ;
  checkException(err) ;

  // Register events
  jvmtiEventCallbacks callbacks;
  memset(&callbacks, 0, sizeof(callbacks));
  callbacks.MethodEntry = &(handleMethodEntry);
  callbacks.MethodExit = &(handleMethodExit);
  err = jvmti->SetEventCallbacks(&callbacks, static_cast<jint>(sizeof(callbacks)));
  //  CheckException(err);
  err = jvmti->SetEventNotificationMode(JVMTI_ENABLE, JVMTI_EVENT_METHOD_ENTRY, 0);
  //  CheckException(err);
  err = jvmti->SetEventNotificationMode(JVMTI_ENABLE, JVMTI_EVENT_METHOD_EXIT, 0);
  //  CheckException(err);

  agent->jvmEnv = jvmti;
  agent->methodPrefix = "vtMethod" ;
} ; 

void parseOptions(const char* s) throw (AgentException) {
  stringstream ss(s) ;
  string item ;
  vector<string> opts ;
  
  while (std::getline(ss, item, ',')) 
    if (!item.empty()) opts.push_back(item) ;
  
  if (opts.size() >= 2) {
    vector<string>::iterator it = opts.begin() ;
    string::iterator  sit = (*it).begin() ;
    agent->outputFile = string(*it) ;
    it++ ;
    agent->threadNum = string_to_int(*it) ;
    agent->traces = new vector<TraceEvent>[agent->threadNum]() ;
    agent->methodKeys = new map<jmethodID, int>[agent->threadNum]() ;
    it++ ;
    agent->traceLength = 2 * string_to_int(*it)  ;
    it++ ;
    agent->testClass = string("Ltest/"+*it+"/") ;
    it++ ;
    agent->testClass = agent->testClass + string("VT"+*it+"Test;") ;
    it++ ;
    int mdNum = string_to_int(*it) ;
    agent->methodNum = mdNum ;
    // std::stringstream ss ;
    // for (int i = 0; i < mdNum; i++) {
    //   ss.str("") ;
    //   ss.clear() ;
    //   ss << "vtMethod" << i ;
    //   agent->testMethods[ss.str()] = i ;
    //   // cout << ss.str() <<endl ;
    // }
  } ;
  
} ;

// void printTrace(String filename) {
//   for (int i = 0; i < agent->threadNum; i++) {
//     cout << "Thread " << i << ":" << endl ;
//     for (vector<TraceEvent>::iterator iter = agent->traces[i].begin(); iter != agent->traces[i].end(); iter++) {
//       // string name = agent->testMethods.find() ;
//       cout << iter->timeStamp << ": " << iter->methodIndex << " of thread " << iter->threadIndex ;
//       if (iter->isCall) 
// 	cout << " enter." << endl ;
//       else 
// 	cout << " exit." << endl ;
//     }
//   }
// }


JNIEXPORT jint JNICALL Agent_OnLoad(JavaVM *vm, char *options, void *reserved) {
  // cout << "Agent loading (" << vm << ") ..." << endl ;

  static TraceAgent newAgent(2, 100) ; // default agent with 2 threads, 100 events (or 50 method call/returns)
  agent = &newAgent ;

  try{
    initialize(vm);
    parseOptions(options);
  } catch (AgentException& e) {
    cout << "Error when enter HandleMethodEntry: " << e.what() << " [" << e.ErrCode() << "]";
    return JNI_ERR;
  }
  printAgentInfo() ;
  gettimeofday(&init_stamp, NULL) ;
    
  return JNI_OK;
} ;

JNIEXPORT void JNICALL Agent_OnUnload(JavaVM *vm) {
  // cout << "Agent unloading (" << vm << ")" << endl;
  ofstream logfile; 

  if (!(agent->outputFile).empty()) 
    logfile.open(string(agent->outputFile + ".jvmlog").c_str()) ;
    // long ts = getTimeStamp() ;
    // stringstream fs ;
    // fs << agent->testClass<< "_" << ts << ".jvmlog" ;
    // logfile.open((fs.str()).c_str()) ;
  if (logfile.is_open()) {
    logfile << "# <MethodIndex> <StartTimestamp> <EndTimestamp>" << endl ;
    logfile << agent->threadNum << " " << (int) agent->traces[0].size() << " " << agent->testClass << endl ;
    for (int i = 0; i < agent->threadNum; i++) {
      logfile << "Thread " << i << endl ;
      int mid = -1 ;
      int mCount = 0 ;
      for (vector<TraceEvent>::iterator iter = agent->traces[i].begin(); iter != agent->traces[i].end(); iter++) {
	if (iter->isCall) {
	  if (mid < 0) {
	    mid = iter->methodIndex ;
	    mCount = 0 ;
	    logfile << mid  << " " << iter->timeStamp ; 
	  } else {
	    if (mid == iter->methodIndex) mCount++ ;
	  }
	}
	else {
	  if (mid == iter->methodIndex) {
	    if (mCount == 0) {
	      logfile << " " << iter->timeStamp << endl ;
	      mid = -1 ;
	    } else {
	      mCount-- ;
	    }
	  }
	  // else 
	  //   logfile << " 0" << endl << iter->methodIndex << " 0 " << iter->timeStamp << endl ;
	  // mid = -1 ;
	}
      }
    }
    logfile.close() ;
  }
  else {
    cout << "Cannot open log file! " << endl ;
    for (int i = 0; i < agent->threadNum; i++) {
      cout << "Thread " << i << endl ;
      for (vector<TraceEvent>::iterator iter = agent->traces[i].begin(); iter != agent->traces[i].end(); iter++) {
	cout << iter->timeStamp << " " << iter->methodIndex ; //  << " " << iter->threadIndex ;
	if (iter->isCall) 
	  cout << " in" << endl ;
	else 
	  cout << " out" << endl ;
      }
    }
  }
} ;


