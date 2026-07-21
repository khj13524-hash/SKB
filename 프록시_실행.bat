@echo off
cd /d "%~dp0"
echo 프록시 서버를 시작합니다... (이 창을 닫으면 서버가 꺼집니다)
python proxy.py
pause
