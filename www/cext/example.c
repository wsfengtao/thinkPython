/* File: example.c */
#include "example.h"
int fact(int n) {
  if (n < 0){
 /* This should probably return an error, but this is simpler */
      return 0; }
  else  if (n == 0) {
          return 1;
                  }
  else {
          /* testing for overflow would be a good idea here */
          return n * fact(n-1);
        }
}

char* fact2(char * a){
    printf("%s", a);
    return a;
}