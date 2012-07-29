#!/bin/sh


echo "########################################"
echo "Open Monitor Desktop Agent Alpha"
echo "Dependencies installed in your system:"
echo ""

python -V > /dev/null 2> /dev/null
if [ $? -eq 127 ]; then
   echo "Python Failed!";
   exit;
else
   python -V;
fi

sqlite3 -version > /dev/null 2> /dev/null
if [ $? -eq 127 ]; then
	echo "SQLite3 Failed"
	exit;
else
	python -c "import sqlite3; print 'sqlite3 version: %s' % sqlite3.version";
fi

python -c "import gtk" > /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
   echo "GTK Failed!";
   exit;
else
   python -c "import gtk; print 'GTK version: %d.%d.%d' % gtk.gtk_version";
fi 

python -c "import pygtk" > /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
   echo "PyGTK Failed!";
   exit;
else
   python -c "import gtk; print 'PyGTK version: %d.%d.%d' % gtk.pygtk_version";
fi 

python -c "import zope.interface" > /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	echo "zope.interface Failed";
	exit;
else
	echo "zope.interface"
fi

python -c "import twisted" > /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	echo "Twisted Failed";
	exit;
else
	python -c "import twisted; print 'Twisted version: %s' % twisted.version.base()";
fi

python -c "import OpenSSL"
if [ $? -eq 1 ]; then
	echo "Python-OpenSSL Failed";
	exit;
else
	python -c "import OpenSSL; print 'Python-OpenSSL version: %s' % OpenSSL.version.__version__";
fi

python -c "import Crypto"
if [ $? -eq 1 ]; then
	echo "Python-Crypto Failed";
	exit;
else
	python -c "import Crypto; print 'Python-Crypto version: %d.%d.%d-%s-%d' % Crypto.version_info";
fi

python -c "import pygtk_chart"
if [ $? -eq 1 ]; then
	echo "Python-gtkChart Failed";
	exit;
else
	python -c "import pygtk_chart; print 'Python-gtkChart version: %s' % pygtk_chart.__version__";
fi	

python -c "import google.protobuf"
if [ $? -eq 1 ]; then
	echo "Google Protocol Buffer Failed";
	exit;
else
	python -c "import google.protobuf; print google.protobuf.__name__";
fi	

echo "########################################"
echo ""
echo "########################################"
echo "Everything seens to work!"
echo "Check the following needed versions:"
echo "    * Python 2.7 or greater"
echo "    * GTK 2.6 or greater"
echo "    * PyGTK 2.24 or greater"
echo "    * SQLite3 2.6.0 or greater"
echo "    * zope.interface 3.6.3 or greater"
echo "    * Python-OpenSSL 0.12 or greater"
echo "    * Python-Crypto 2.1.0 or greater"
echo "    * Python-gtkChart Beta or greater"
echo "    * Google Protocol Buffer 2.4.1 or greater"
echo ""
echo "If all the versions above are in agreement, you're ok to run OpenMonitor Desktop Agent now."
echo "########################################"
echo ""
