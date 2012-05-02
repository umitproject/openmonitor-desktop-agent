clean:
	rm kadwrapper kadcaller_wrap.cxx kadcaller.py* kadcaller _kadcaller.so

install:
	swig -c++ -python kadcaller.i 
	g++ -c -std=gnu++0x kadcaller.cpp -o kadcaller
	g++ -c -std=gnu++0x kadcaller_wrap.cxx -o kadwrapper -I/usr/include/python2.7 -lpython2.7
	g++ -shared kadwrapper -o _kadcaller.so