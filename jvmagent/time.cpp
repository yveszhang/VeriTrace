#include <time.h>
#include <sys/types.h>
#include <sys/time.h>
#include <iostream>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

using namespace std ;
int main () {

/*   struct timespec ts; */

/* #ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time */
/*   clock_serv_t cclock; */
/*   mach_timespec_t mts; */
/*   host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &cclock); */
/*   clock_get_time(cclock, &mts); */
/*   mach_port_deallocate(mach_task_self(), cclock); */
/*   ts.tv_sec = mts.tv_sec; */
/*   ts.tv_nsec = mts.tv_nsec; */
/* #else */
/*   clock_gettime(CLOCK_REALTIME, &ts); */
/* #endif */
  
  struct timeval tt ;
  gettimeofday(&tt, NULL) ;
  cout << tt.tv_sec << " seconds, " << tt.tv_usec << " micro-seconds." << endl ;
  long ts = tt.tv_sec % 100 * 1000000 + tt.tv_usec ;
  cout << ts <<endl ;;
  //  printf("%d seconds, %d useconds\n", ts.tv_sec, ts.tv_usec) ;
}
