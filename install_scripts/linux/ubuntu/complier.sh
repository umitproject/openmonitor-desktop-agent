#!/bin/bash

echo "======================="
echo "deb create 1"
echo "======================="

cd icm-agent
sudo dpkg-buildpackage
cd ..

echo "======================="
echo "deb unzip"
echo "======================="
sudo dpkg -x icm-agent_0.1RC-0ubuntu1_all.deb .

echo "======================="
echo "deb replace"
echo "======================"
sudo cp post* ./icm-agent_0.1RC-0ubuntu1_all/DEBIAN/
sudo rm icm-agent_0.1RC-0ubuntu1_all.deb
sudo dpkg -b icm-agent_0.1RC-0ubuntu1_all icm-agent_0.1RC-0ubuntu1_all.deb

echo "finish!"
