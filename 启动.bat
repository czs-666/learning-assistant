@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Load .env and start server
set PYTHON=C:\Python314\pythonw.exe

:: Install deps if needed (silent)
"%PYTHON:pythonw=python%" -m pip install python-dotenv flask pypdf python-docx -q 2>nul

:: Start server silently in background (pythonw = no console window)
start "" /B "%PYTHON%" -c "import os; os.chdir(r'%~dp0'); from dotenv import load_dotenv; load_dotenv(); from app import app; app.run(host='0.0.0.0', port=5000)"

:: Wait for server to be ready
echo 正在启动学习助手...
:waitloop
timeout /t 1 /nobreak >nul
curl.exe -s http://127.0.0.1:5000 >nul 2>&1
if errorlevel 1 goto waitloop

:: Open browser
start http://localhost:5000
echo 已打开学习助手！
