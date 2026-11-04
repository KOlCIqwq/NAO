@echo off
setlocal
set "SDK_ROOT=C:\Program Files (x86)\Softbank Robotics\Choregraphe Suite 2.8"
set "PYTHONHOME=%SDK_ROOT%\lib\python2.7"
set "PYTHONPATH=%SDK_ROOT%\lib"
set "PATH=%SDK_ROOT%\bin;%PATH%"
"%SDK_ROOT%\bin\python.exe" -u %*
endlocal
