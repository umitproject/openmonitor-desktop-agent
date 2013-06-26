@echo off

echo ########################################
echo # OpenMonior Desktop Agent for Windows #
echo ########################################
echo .

echo Setting installation variables...
set PythonEXE=C:\Python27\python.exe
set UmitOrig=.
set UmitDir=C:\ICMTemp
set DistDir=%UmitDir%\dist
set GTKDir=C:\Python27\Lib\site-packages\gtk-2.0\runtime
set WinInstallDir=%UmitDir%\install_scripts\windows
set Output=%UmitDir%\win_install.log
set MakeNSIS="C:\Program Files\NSIS\makensis.exe"
set UtilsDir=%UmitDir%\install_scripts\utils

echo [1] Writing output to %Output%
rd %Output% /S /Q

echo [0] Removing old compilation...
rd %UmitDir% /S /Q

echo ########################
echo # New Build ExE Process#
echo ########################
echo .

echo [1] Creating a temp directory for compilation...
mkdir %UmitDir%
mkdir %DistDir%
mkdir %WinInstallDir%

echo [2] Copying trunk to the temp dir...
xcopy %UmitOrig%\*.* %UmitDir% /E /S /C /Y /V /I >> %Output%
xcopy %UmitOrig%\deps\icm-common\umit\*.* %UmitDir%\umit /E /S /C /Y /V /I >> %Output%
xcopy %UmitOrig%\deps\umit-common\umit\*.* %UmitDir%\umit /E /S /C /Y /V /I >> %Output%
mkdir %UmitDir%\higwidgets
xcopy %UmitOrig%\deps\higwidgets\*.* %UmitDir%\higwidgets /E /S /C /Y /V /I >> %Output%
xcopy %UmitOrig%\install_scripts\windows\setup.nsi %UmitDir% /E /S /C /Y /V /I >> %Output%

echo [3] Creating dist and dist\share directories...
mkdir %DistDir%\share
mkdir %DistDir%\share\gtk-2.0
mkdir %DistDir%\share\themes
mkdir %DistDir%\share\themes\Default
mkdir %DistDir%\share\themes\MS-Windows

echo [4] Copying GTK's share to dist directory...
xcopy %GTKDir%\share\gtk-2.0\*.* %DistDir%\share\gtk-2.0\ /S >> %Output%
xcopy %GTKDir%\share\themes\Default\*.* %DistDir%\share\themes\Default /S /Y >> %Output%
xcopy %GTKDir%\share\themes\MS-Windows\*.* %DistDir%\share\themes\MS-Windows /S /Y >> %Output%
xcopy %GTKDir%\bin\*.dll %DistDir% /Y /S >> %Output%

echo [5] Copying setup.py...
xcopy %UmitOrig%\install_scripts\windows\setup.py %UmitDir% /Y

echo [6] Compiling Umit using py2exe...
cd %UmitDir%
%PythonEXE% -OO setup.py py2exe

echo #######################
echo # New Package Process#
echo #######################
echo .

echo [7] Copying some more GTK files to dist directory...
rem xcopy %GTKDir%\lib %DistDir%\lib /S /I >> %Output%
rem xcopy %GTKDir%\etc %DistDir%\etc /S /I >> %Output%

echo [8] Removing the build directory...
rd %UmitDir%\build /s /q >> %Output%

echo [9] Copying conf and share into dist folder
mkdir %UmitDir%\dist\icmagent
mkdir %UmitDir%\dist\icmagent\conf
mkdir %UmitDir%\dist\icmagent\share
xcopy %UmitOrig%\conf %DistDir%\icmagent\conf /S /Y /E >> %Output%
xcopy %UmitOrig%\share %DistDir%\icmagent\share /S /Y /E >> %Output%

echo .
echo Creating installer...
%MakeNSIS% /P5 /V4 /NOCD %WinInstallDir%\setup.nsi

cd %UmitOrig%
echo Done!

pause
pause

