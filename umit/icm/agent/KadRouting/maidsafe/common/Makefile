install:
	g++ -std=gnu++0x -c log.cc -o log.cc.o
	g++ -std=gnu++0x -c asio_service.cc -o asio_service.cc.o
	g++ -std=gnu++0x -c crypto.cc -o crypto.cc.o
	g++ -std=gnu++0x -c rsa.cc -o rsa.cc.o
	g++ -std=gnu++0x -c safe_encrypt.pb.cc -o safe_encrypt.pb.cc.o
	g++ -std=gnu++0x -c utils.cc -o utils.cc.o
	g++ -lpthread -std=gnu++0x asio_service.cc.o crypto.cc.o log.cc.o rsa.cc.o safe_encrypt.pb.cc.o utils.cc.o -o common.o

# Google Logging
# -Lgoogle/glog/libglog_la-vlog_is_on.o -Lgoogle/glog/libglog_la-utilities.o -Lgoogle/glog/libglog_la-symbolize.o -Lgoogle/glog/libglog_la-signalhandler.o -Lgoogle/glog/libglog_la-raw_logging.o -Lgoogle/glog/libglog_la-logging.o -Lgoogle/glog/libglog_la-demangle.o 


# g++ -shared -Wl,-soname,protobuf.so -o protobuf.so google/protobuf/src/*.o -lc

# Must Add :
# -I/usr/local/include/boost/filesystem/v3 -Lprotobuf.so

# g++ -shared -Wl,-soname,glog.so -o glog.so google/glog/libglog_la-demangle.o google/glog/libglog_la-logging.o google/glog/libglog_la-raw_logging.o google/glog/libglog_la-signalhandler.o google/glog/libglog_la-symbolize.o google/glog/libglog_la-utilities.o google/glog/libglog_la-vlog_is_on.o -lc

# g++ -shared -Wl,-soname,gmock.so -o gmock.so google/googlemock/src/gmock-all.o -lc

# g++ -shared -Wl,-soname,cryptopp.so -o cryptopp.so cryptopp/objs/*.cpp.o -lc

# g++ -shared -Wl,-soname,libcommon.so -o libcommon.so *.o -Lcryptopp.so -Lglog.so -Lgmock.so -Lprotobuf.so -lc

clean:
	rm asio_service.cc.o crypto.cc.o log.cc.o rsa.cc.o safe_encrypt.pb.cc.o utils.cc.o