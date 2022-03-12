@echo off
IF %1.==. GOTO DoError
GOTO DoRun

:DoError
echo Drag and Drop the path.json file on this script to run it
GOTO DoEnd

:DoRun
cd /d %~dp0
pip3 install -r requirements.txt
py -3 0_download_master_data.py %1
py -3 1_download_site_assets.py %1
py -3 3_render_html.py --clean

:DoEnd
pause
