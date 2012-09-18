#include <iostream>
#include <string> 
#include <jvmti.h>

#include "TraceAgent.h"

using namespace std;

static string opt;

JNIEXPORT jint JNICALL Agent_OnLoad(JavaVM *vm, char *options, void *reserved) {
  cout << "Agent_OnLoad(" << vm << ")" << endl;

  if (options != 0) 
    opt = new string(options) ;

  // try{
  //   TraceAgent* agent = new TraceAgent();
  //   agent->Init(vm);
  //   agent->ParseOptions(options);
  //   agent->AddCapability();
  //   agent->RegisterEvent();
  // } catch (AgentException& e) {
  //   cout << "Error when enter HandleMethodEntry: " << e.what() << " [" << e.ErrCode() << "]";
  //   return JNI_ERR;
  // }
    
  return JNI_OK;
} ;

JNIEXPORT void JNICALL Agent_OnUnload(JavaVM *vm) {
    cout << "Agent_OnUnload(" << vm << ")" << endl;
    if (!opt.empty())  
      cout << "Got the option string: " << opt << endl ;
} ;
