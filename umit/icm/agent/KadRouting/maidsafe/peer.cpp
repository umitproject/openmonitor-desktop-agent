#include<iostream>
#include "vector"

class Peer{
	std::vector<std::string> PeerList;
	public:
		Peer(){
			std::cout<<"Peer class is created\n\n";
		}

		void PrintPeers(){
			PeerList.push_back("Node1");
			PeerList.push_back("Node2");
			for(std::vector<std::string>::iterator it = PeerList.begin() ; it != PeerList.end() ; ++it)
				std::cout<<(*it)<<"\n";
		}

};

/*int main(int argc,char **argv){
	Peer peer;
	peer.PrintPeers();
}*/