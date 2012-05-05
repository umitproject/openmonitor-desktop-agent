%module kadcaller

%{
#define SWIG_FILE_WITH_INIT
#include "KadRouting/maidsafe/MaidSafe-DHT/src/maidsafe/dht/demo/demo_main.h"
%}

int PeerCreator();