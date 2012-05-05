install:
	g++ peer.cpp -o peer;

	# g++ -std=gnu++0x -L/usr/lib/libboost* -Lcommon/cryptopp.so -Lcommon/glog.so -Lcommon/gmock.so -Lcommon/libcommon.so -Lcommon/protobuf.so -Ltransport/libtransport.so -Ldht/libdht.so demo_main.cc -o demo_main.o
	# g++ -std=gnu++0x demo_main.cc -o demo_main.o common/*.o common/cryptopp/*.o common/google/glog/*.o common/google/protobuf/src/*.o common/google/googlemock/src/*.o common/cryptopp/*.a common/*.o transport/*.o dht/*.o -L/usr/lib/libboost*  
	
	
	
	# g++ -std=gnu++0x demo_main.cc -o demo_main.o common/*.o common/cryptopp/*.o common/google/glog/libglog_la-demangle.o common/google/glog/libglog_la-logging.o common/google/glog/libglog_la-raw_logging.o common/google/glog/libglog_la-signalhandler.o common/google/glog/libglog_la-symbolize.o common/google/glog/libglog_la-utilities.o common/google/glog/libglog_la-vlog_is_on.o common/google/protobuf/src/*.o  common/cryptopp/*.a common/*.o transport/*.o dht/*.o -lpthread -L/home/sunshadow/Documents/boost_1_49_0/stage/lib/ -lboost_filesystem -lboost_system -lboost_thread -lboost_iostreams -lboost_program_options -Xlinker -zmuldefs -lz


#common/google/googlemock/src/*.o


clean:
	rm peer;
