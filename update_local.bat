@echo off
IF %1.==. GOTO DoError
GOTO DoRun

:DoError
echo Drag and Drop the path.json file on this script to run it
GOTO DoEnd

:DoRun
cd /d %~dp0
python3.10 -m pip install -r requirements.txt
python3.10 0_download_master_data.py %1
python3.10 1_download_site_assets.py %1
python3.10 3_render_html.py --clean

:DoEnd
pause
