OpenMonitor Desktop Agent - Install Instructions
============================================================

OpenMonitor Desktop Agent runs in Windows, Linux and Ubuntu.


Windows
----------------------------------------------------------

1. Download Python 2.7
2. Download pip: https://pypi.python.org/pypi/pip#downloads
3. PyCrypto: http://www.voidspace.org.uk/python/modules.shtml#pycrypto - Download and install it
4. Twisted: http://twistedmatrix.com/trac/wiki/Downloads - Download and Install it
5. PyOpenSSL: https://pypi.python.org/pypi/pyOpenSSL - Download and Install it
6. Extract pip and install with python setup.py install
7. Download OpenMonitor Desktop Agent: https://dl.dropbox.com/u/2859837/openmonitor-desktop-agent.zip
8. Unzip openmonitor-desktop-agent.zip
9. cd openmonitor-desktop-agent
10. C:\Python27\Scripts\pip.exe install -r requirements.txt
11. python bin/icm-agent
12. You need to be registered at www.openmonitor.org
13. You login with your credentials and your Agent will be sent information to the Aggregator. You're contribution to a better world!




Linux
---------------------------------------------------------

1. Download Python 2.7. For instance, in Ubuntu you do: sudo apt-get install python2.7
2. Install python pip. In Ubuntu you do: sudo apt-get install python-pip
3. Download OpenMonitor Desktop Agent: https://dl.dropbox.com/u/2859837/openmonitor-desktop-agent.zip 
4. unzip openmonitor-desktop-agent.zip
5. cd openmonitor-desktop-agent
6. pip install -r requirements.txt
7. python bin/icm-agent
8. You need to be registered at www.openmonitor.org
9. You login with your credentials and your Agent will be sent information to the Aggregator. You're contribution to a better world!

Mac OS
----------------------------------------------------------
0. You need XCode and development tools installed
1. Download Python 2.7. It is installed by default on Mac OS, check it. Probably you can skip.
2. Download OpenMonitor Desktop Agent: https://dl.dropbox.com/u/2859837/openmonitor-desktop-agent.zip
3. Unzip openmonitor-desktop-agent.zip
4. cd openmonitor-desktop-agent
4. pip install -r requirements.txt && pip install Twisted
6. python bin/icm-agent
7. You need to be registered at www.openmonitor.org
8. You login with your credentials and your Agent will be sent information to the Aggregator. You're contribution to a better world!



Any problems contact
---------------------------------- 

"umit devel" <umit-devel@lists.sourceforge.net>
Subscribe at https://lists.sourceforge.net/lists/listinfo/umit-devel


