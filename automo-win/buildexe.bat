mkdir src
mkdir src\dist
copy /Y ..\automo\*.py src\
copy /Y setup.py src\
copy /Y ..\images\src\icon_pack.ico src\automo.ico
cd src
C:\Python27\python.exe setup.py py2exe
del dist\automo.exe
ren dist\__main__.exe automo.exe

mkdir final
mkdir final\bin
copy /Y dist final\bin
ren final\dist bin

mkdir src-launcher
copy automo.ico src-launcher\
copy ..\launcher.py src-launcher\
copy ..\setup-launcher.py src-launcher\

cd src-launcher
C:\Python27\python.exe setup-launcher.py py2exe
copy dist\launcher.exe ..\final
del ..\final\automo.exe
ren ..\final\launcher.exe automo.exe


pause
