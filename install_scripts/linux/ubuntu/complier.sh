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
sudo rm -rf makedeb
sudo mkdir makedeb
sudo dpkg -x icm-agent_0.1RC-0ubuntu1_all.deb ./makedeb
sudo dpkg -e icm-agent_0.1RC-0ubuntu1_all.deb ./makedeb/DEBIAN


echo "======================="
echo "deb replace"
echo "======================"
sudo cp post* ./makedeb/DEBIAN/
sudo rm icm-agent_0.1RC-0ubuntu1_all.deb
sudo dpkg -b makedeb icm-agent_0.1RC-0ubuntu1_all_new.deb

echo "finish!"
