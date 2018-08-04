#include<stdio.h>

int pgcd(int p, int s)
{

	register int a,b,r,x,y;


	if (p>s){
		x=p;
		y=s;
	} else {
		x=s;
		y=p;
	}

	r = a% b ;

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