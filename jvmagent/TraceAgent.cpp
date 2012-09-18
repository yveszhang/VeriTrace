#include <iostream>
#include <string>
#include <time.h>
#include <fstream>
#include <jvmti.h>
#include "TraceAgent.h"

using namespace std;

TraceAgent::~TraceAgent() throw(AgentException) {
  // if (trace != 0) free(trace) ;
}

void TraceAgent::initialize (JavaVM *vm) const throw (AgentException) {
  jvmtiEnv *jvmti = 0;
  jint ret = vm->GetEnv(reinterpret_cast<void**>(&jvmti), JVMTI_VERSION_1_0);
}

void TraceAgent::parseOptions (const char *str) const throw (AgentException) {
  if (str == 0) return ;
  cout << str << endl ;
}

void TraceAgent::addCapability () const throw (AgentException) {
  
}

void TraceAgent::registerEvent () const throw (AgentException) {

}

void JNICALL TraceAgent::handleMethodEntry (jvmtiEnv *jvmti, JNIEnv *jni, jthread thread, jmethodID method) {

}

// void thread_info_into_file(char* info_ptr_name,char* info)
// {
// 	if(strcmp(info_ptr_name,"1")==0)
// 		 {

// 			 ofstream f1;
// 			 f1.open("F:\\test\\thread-1.txt",ios::app);
// 			 f1<<info;
// 			 f1.close();
// 		 }
//    if(strcmp(info_ptr_name,"2")==0)
// 		 {
// 			 ofstream f2;
// 			 f2.open("F:\\test\\thread-2.txt",ios::app);
// 			 f2<<info;
// 			 f2.close();
// 		 }
// }
// void thread_info_into_file(char* info_ptr_name,string info)
// {
// 	if(strcmp(info_ptr_name,"1")==0)
// 		 {

// 			 ofstream f1;
// 			 f1.open("F:\\test\\thread-1.txt",ios::app);
// 			 f1<<info;
// 			 f1.close();
// 		 }
//     if(strcmp(info_ptr_name,"2")==0)
// 		 {
// 			 ofstream f2;
// 			 f2.open("F:\\test\\thread-2.txt",ios::app);
// 			 f2<<info;
// 			 f2.close();
// 		 }
// }

// void thread_info_into_file(char* info_ptr_name,jint info)
// {
// 	if(strcmp(info_ptr_name,"1")==0)
// 		 {

// 			 ofstream f1;
// 			 f1.open("F:\\test\\thread-1.txt",ios::app);
// 			 f1<<info;
// 			 f1.close();
// 		 }
//     if(strcmp(info_ptr_name,"2")==0)
// 		 {
// 			 ofstream f2;
// 			 f2.open("F:\\test\\thread-2.txt",ios::app);
// 			 f2<<info;
// 			 f2.close();
// 		 }
// }

// char* getSystemTime()
// {
//     SYSTEMTIME lpsystime;
//     GetLocalTime(&lpsystime);

//    char *Year,*Month,*Day,*Hour,*Minute,*Second,*Milliseconds,*time;
//    Year = (char*)malloc(4); Month = (char*)malloc(2); Day = (char*)malloc(2);Hour = (char*)malloc(2);
//    Minute = (char*)malloc(2);Second = (char*)malloc(2);Milliseconds= (char*)malloc(3);
//    time = (char*)malloc(40);

//    sprintf(Year,"%u",lpsystime.wYear);
//    sprintf(Month,"%u",lpsystime.wMonth);
//    sprintf(Day,"%u",lpsystime.wDay); sprintf(Hour,"%u",lpsystime.wHour);
//    sprintf(Minute,"%u",lpsystime.wMinute); sprintf(Second,"%u",lpsystime.wSecond);
//    sprintf(Milliseconds,"%u",lpsystime.wMilliseconds);
//    sprintf(time,"%s%s%s%s%s%s%s%s%s%s%s%s%s%s"," System time: ",Year,"/",Month,"/",Day,"  ",Hour,":",Minute,":",Second,":",Milliseconds); 
//    return time;
// }

// void JNICALL cb_method_entry(jvmtiEnv *env,
//             JNIEnv* jni_env,
//             jthread thread,
//             jmethodID method)
// {
//     // Get name of method
 
//     std::string theName,theSignature,theGen;
//     char* name;
//     char* signature;
//     char* gen;
//     env->GetMethodName(method, &name, &signature, &gen);
//     if (name) {
//         theName.assign(name);
//         env->Deallocate(reinterpret_cast<unsigned char*>(name));
//     }
//     if (signature) {
// 		theSignature.assign(signature);
//         env->Deallocate(reinterpret_cast<unsigned char*>(signature));
//     }
//     if (gen) {
// 		theGen.assign(gen);
//         env->Deallocate(reinterpret_cast<unsigned char*>(gen));
//     }

// 	//get the method Arguement size
// 	jint size_ptr;
// 	env->GetArgumentsSize(method,&size_ptr);

// 	//get the thread information
//     jvmtiThreadInfo info_ptr ;
// 	env->GetThreadInfo(thread,&info_ptr);

// 	//get the localvariable
// 	jint entry_count_ptr;
// 	jvmtiLocalVariableEntry* table_ptr;
// 	env->GetLocalVariableTable(method,&entry_count_ptr,&table_ptr);

//     // Are we interested?
//     if (theName == "add"||theName == "poll")
// 	{   
// 		 thread_info_into_file(info_ptr.name,"Thread :");
// 		 thread_info_into_file(info_ptr.name,info_ptr.name);
// 		 thread_info_into_file(info_ptr.name," Entering method:  ");
// 		 thread_info_into_file(info_ptr.name,theName);
// 	     thread_info_into_file(info_ptr.name," signature: ");
// 		 thread_info_into_file(info_ptr.name,theSignature);
// 		 thread_info_into_file(info_ptr.name,getSystemTime());
// 		 thread_info_into_file(info_ptr.name,"\n");
// 	}
// }

// void JNICALL
// cb_method_exit(jvmtiEnv *env,
//             JNIEnv* jni_env,
//             jthread thread,
//             jmethodID method,
//             jboolean was_popped_by_exception,
//             jvalue return_value)
// {
// 	// Get name of method
 
//     std::string theName,theSignature,theGen;
//     char* name;
//     char* signature;
//     char* gen;
//     env->GetMethodName(method, &name, &signature, &gen);
//     if (name) {
//         theName.assign(name);
//         env->Deallocate(reinterpret_cast<unsigned char*>(name));
//     }
//     if (signature) {
// 		theSignature.assign(signature);
//         env->Deallocate(reinterpret_cast<unsigned char*>(signature));
//     }
//     if (gen) {
// 		theGen.assign(gen);
//         env->Deallocate(reinterpret_cast<unsigned char*>(gen));
//     }

// 	//get the return value

// 	//Get the name of the thread
// 	jvmtiThreadInfo info_ptr ;
// 	env->GetThreadInfo(thread,&info_ptr);

//     // Are we interested?
//     if (theName == "add"||theName == "poll")
// 	{   
// 		 thread_info_into_file(info_ptr.name,"Thread :");
// 		 thread_info_into_file(info_ptr.name,info_ptr.name);
// 		 thread_info_into_file(info_ptr.name," Exiting method:  ");
// 		 thread_info_into_file(info_ptr.name,theName);
// 	     thread_info_into_file(info_ptr.name," signature: ");
// 		 thread_info_into_file(info_ptr.name,theSignature);
// 		 thread_info_into_file(info_ptr.name," int return value: ");
// 		 thread_info_into_file(info_ptr.name,return_value.i);
// 		 thread_info_into_file(info_ptr.name,getSystemTime());
// 		 thread_info_into_file(info_ptr.name,"\n");
// 	}
// }
 
// void init_jvmti_callbacks(JavaVM* vm)
// {   
//     std::cout <<"Initing JVMTI callbacks" <<std::endl;
//     jvmtiEnv* env;
//     vm->GetEnv(reinterpret_cast<void**>(&env), JVMTI_VERSION);
       
//     jvmtiCapabilities capabilities = { 1 };
//     jvmtiEventCallbacks callbacks = { 0 };
 
//     capabilities.can_generate_method_entry_events = 1;
//     env->AddCapabilities(&capabilities);
//     env->SetEventNotificationMode(JVMTI_ENABLE, JVMTI_EVENT_METHOD_ENTRY, NULL);   
//     callbacks.MethodEntry = &cb_method_entry;
// 	env->SetEventCallbacks(&callbacks, sizeof(callbacks));
    
// 	capabilities.can_generate_method_exit_events = 1;
//     env->AddCapabilities(&capabilities);
//     env->SetEventNotificationMode(JVMTI_ENABLE, JVMTI_EVENT_METHOD_EXIT, NULL);   
// 	callbacks.MethodExit = &cb_method_exit;
//     env->SetEventCallbacks(&callbacks, sizeof(callbacks));

// }
 
