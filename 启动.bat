@echo off
chcp 65001 >nul
echo 启动学习助手（智谱 GLM AI）...
echo.

REM 设置 API Key
set GLM_API_KEY=d01dfee8e4ae4876b766bf427be78e37.nxPm1wgk01YlpKjm

REM 启动应用
python app.py

pause
