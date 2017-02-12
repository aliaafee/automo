mkdir src
mkdir src\dist
copy /Y ..\mopresc\*.py src\
copy /Y setup.py src\
copy /Y ..\images\src\icon_pack.ico src\mopresc.ico
cd src
C:\Python27\python.exe setup.py py2exe
del dist\wardpresc.exe
ren dist\__main__.exe wardpresc.exe

mkdir final
mkdir final\bin
copy /Y dist final\bin
ren final\dist bin

mkdir src-launcher
copy ..\mopresc.ico src-launcher\
copy ..\launcher.py src-launcher\
copy ..\setup-launcher.py src-launcher\

cd src-launcher
C:\Python27\python.exe setup-launcher.py py2exe
copy dist\launcher.exe ..\final
del ..\final\wardpresc.exe
ren ..\final\launcher.exe wardpresc.exe


pause
