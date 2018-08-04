#include <stdio.h>

int fibbo();

int main(void){

    printf("Fibbo(15) = %d", fibbo());
}

int fibbo()
{
        register int n ;
        register int first ;
        register int second;
        register int next ;
        register int c;
        
        n = 15 ;
        first = 0 ;
        second = 1; 

        for (c = 0; c < n; c++){
            if (c <= 1){
                next = c;
            } else {
              next = first + second;
              first = second;
              second = next;
          }
        }

        return next;
}
