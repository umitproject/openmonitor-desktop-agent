#!/bin/sh -e

echo
echo "##############################################"
echo "# Open Monitor Desktop Agent Source Packages #"
echo "##############################################"
echo

old_pwd=`pwd`
script_dir=`pwd`/$0
script_dir=`dirname $script_dir`
cd $script_dir/..

#echo "Removing some unused files..."
#bash install_scripts/utils/remove_unused_files.sh

echo "Starting setup.py..."
python setup.py sdist --formats=gztar,zip,bztar

rm MANIFEST

cd $old_pwd

echo
echo "#########################################"
echo "# Finished - All Packages were created  #"
echo "#########################################"
echo
