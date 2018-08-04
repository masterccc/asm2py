#include<stdio.h>

int pgcd(int a, int b)
{

	register int r,x,y;

	if (a>b){
		x=b;
		r=a%b;
	} else {
		x=a;
		r=b%a;
	}

	while(r!=0){
		y=x;
		x=r;
		r=y%x;          
	}
	
	return x ;
}

int main(void){

	printf("pgcd(512,768) = %d\n", pgcd(512,768));

	return 0 ;
}