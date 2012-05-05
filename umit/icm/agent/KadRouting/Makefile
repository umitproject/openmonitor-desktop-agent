clean:
	rm kadwrapper.o kadcaller_wrap.cxx kadcaller_wrap.o kadcaller.py* kadcaller.o _kadcaller.so

install:
	# swig -c++ -python kadcaller.i 
	# g++ -c -fPIC -std=gnu++0x kadcaller.cpp -o kadcaller.o 
	# g++ -c -fPIC -std=gnu++0x kadcaller_wrap.cxx -o kadwrapper.o -I/usr/include/python2.7 -lpython2.7
	# g++ -shared -Wl,-soname,_kadcaller.so.1 -o _kadcaller.so.1.0.1 kadwrapper.o -Xlinker -zmuldefs

	swig -c++ -python kadcaller.i 
	#g++ -c -std=gnu++0x kadcaller.cpp -o kadcaller.o 
	g++ -c -std=gnu++0x kadcaller.cpp kadcaller_wrap.cxx -I/usr/include/python2.7 -lpython2.7
	#g++ -shared -Wl,-soname,_kadcaller.so.1 -o _kadcaller.so.1.0.1 kadwrapper.o -Xlinker -zmuldefs
	g++ -shared kadcaller.o kadcaller_wrap.o maidsafe/demo_main.o maidsafe/common/*.o maidsafe/common/cryptopp/*.o maidsafe/common/google/glog/libglog_la-demangle.o maidsafe/common/google/glog/libglog_la-logging.o maidsafe/common/google/glog/libglog_la-raw_logging.o maidsafe/common/google/glog/libglog_la-signalhandler.o maidsafe/common/google/glog/libglog_la-symbolize.o maidsafe/common/google/glog/libglog_la-utilities.o maidsafe/common/google/glog/libglog_la-vlog_is_on.o maidsafe/common/google/protobuf/src/*.o maidsafe/common/*.o maidsafe/transport/*.o maidsafe/dht/*.o -o _kadcaller.so -lpthread -L/home/sunshadow/Documents/boost_1_49_0/stage/lib/ -lboost_filesystem -lboost_system -lboost_thread -lboost_iostreams -lboost_program_options -Xlinker -zmuldefs

	# g++ -std=gnu++0x kadcaller.cpp maidsafe/demo_main.o maidsafe/common/*.o maidsafe/common/cryptopp/*.o maidsafe/common/google/glog/libglog_la-demangle.o maidsafe/common/google/glog/libglog_la-logging.o maidsafe/common/google/glog/libglog_la-raw_logging.o maidsafe/common/google/glog/libglog_la-signalhandler.o maidsafe/common/google/glog/libglog_la-symbolize.o maidsafe/common/google/glog/libglog_la-utilities.o maidsafe/common/google/glog/libglog_la-vlog_is_on.o maidsafe/common/google/protobuf/src/*.o maidsafe/common/*.o maidsafe/transport/*.o maidsafe/dht/*.o -o kadcaller -lpthread -L/home/sunshadow/Documents/boost_1_49_0/stage/lib/ -lboost_filesystem -lboost_system -lboost_thread -lboost_iostreams -lboost_program_options -Xlinker -zmuldefs