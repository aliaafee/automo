mkdir src
mkdir src\automo
mkdir src\dist
xcopy /Y /E ..\automo\*.py src\automo\
copy /Y ..\automo.py src\
copy /Y setup.py src\
copy /Y ..\images\src\icon_pack.ico src\automo.ico
cd src
C:\Python27\python.exe setup.py py2exe

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

cd ..\..

mkdir ..\dist
mkdir ..\dist\win
mkdir ..\dist\win\automo

xcopy /Y /S src\final\* ..\dist\win\automo


pause