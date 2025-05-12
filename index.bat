@echo off
echo start Kama...
cd /d %~dp0
python index.py
if %errorlevel% neq 0 (
    echo failed, error code: %errorlevel%
    pause
    exit /b %errorlevel%
)
echo Kama is running...
