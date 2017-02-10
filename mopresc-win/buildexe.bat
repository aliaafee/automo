mkdir src
mkdir src\dist
copy /Y ..\mopresc\*.py src\
copy /Y setup.py src\
copy /Y mopresc.ico src\
cd src
C:\Python27\python.exe setup.py py2exe
del dist\wardpresc.exe
ren dist\__main__.exe wardpresc.exe
pause
