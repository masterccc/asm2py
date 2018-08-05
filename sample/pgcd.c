#include<stdio.h>

int pgcd(int p, int s)
{

	register int c,d,r;

	if (p > s)
	{
		c = p;
		d = s;
	} else {
		c=s;
		d=p;
	}

	r= c % d;

	while(r!=0){
		c = d;
		d = r;
		r = c % d;
	}

	return d ;
}

int main(void){

	printf("pgcd(758,306) = %d\n", pgcd(758,306));

	return 0 ;
}
