cd ..

pyinstaller --noconfirm --log-level=WARN ^
    --distpath automo-win\dist ^
    --workpath automo-win\build ^
    --specpath automo-win\ ^
    --name automo ^
    --windowed ^
    --icon images\src\icon_pack.ico ^
    automo-gui.py

pyinstaller --noconfirm --log-level=WARN ^
    --distpath automo-win\dist ^
    --workpath automo-win\build ^
    --onefile ^
    --specpath automo-win\ ^
    --name automo-cli ^
    --icon images\src\icon_pack.ico ^
    automo-cli.py

pause