%module kadcaller

%{
	#define SWIG_FILE_WITH_INIT
	#include "kadcaller.cpp"	
%}

void NodeCreator();