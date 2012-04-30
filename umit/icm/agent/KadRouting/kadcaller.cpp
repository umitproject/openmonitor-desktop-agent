#include <iostream>
#include "maidsafe/peer.cpp"

void NodeCreator() {
	//Start a new Peer
	Peer peer; 
	peer.PrintPeers();
}

int main(int argc, char **argv){
	NodeCreator();
}