install:
	g++ -std=gnu++0x -c -fPIC *.cc
	# g++ -std=gnu++0x -c transport.pb.cc -o transport.pb.cc.o
	# g++ -std=gnu++0x -c contact.cc -o contact.cc.o
	# g++ -std=gnu++0x -c message_handler.cc -o message_handler.cc.o
	# g++ -std=gnu++0x -c rudp_parameters.cc -o rudp_parameters.cc.o
	# g++ -std=gnu++0x -c rudp_acceptor.cc -o rudp_acceptor.cc.o
	# g++ -std=gnu++0x -c rudp_connection.cc -o rudp_connection.cc.o
	# g++ -std=gnu++0x -c rudp_multiplexer.cc -o rudp_multiplexer.cc.o
	# g++ -std=gnu++0x -c rudp_socket.cc -o rudp_socket.cc.o
	# g++ -std=gnu++0x -c nat_detection_rpcs.cc -o nat_detection_rpcs.cc.o
	# g++ -std=gnu++0x -c nat_detection.cc -o nat_detection.cc.o
	# g++ -std=gnu++0x -c rudp_message_handler.cc -o rudp_message_handler.cc.o
	# g++ -std=gnu++0x -c rudp_transport.cc -o rudp_transport.cc.o
	# g++ -std=gnu++0x -c tcp_transport.cc -o tcp_transport.cc.o
	# g++ -std=gnu++0x -c udp_transport.cc -o udp_transport.cc.o
	# g++ -std=gnu++0x -c utils.cc -o utils.cc.o

	# -L../common/protobuf.so 
	# g++ -shared -Wl,-soname,libtransport.so -o libtransport.so *.o -L../common/glog.so -L../common/gmock.so -L../common/protobuf.so -lc
clean:
	rm *.o