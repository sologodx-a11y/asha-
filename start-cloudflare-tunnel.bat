@echo off
echo Starting ASHA Beauty Salon - Flask App + Cloudflare Tunnel
echo ==========================================================
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: cloudflared is not installed or not in PATH
    echo Please install Cloudflare Tunnel from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first.
    echo.
    pause
    exit /b 1
)

REM Start Flask app in background
echo [1/2] Starting Flask app on localhost:5000...
start "ASHA Flask App" cmd /k "cd /d %~dp0 && python app.py"

REM Wait for Flask to start
echo Waiting for Flask app to start...
timeout /t 5 /nobreak >nul

REM Check if Flask is running
echo Checking if Flask app started successfully...
curl -s http://localhost:5000 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Flask app may not have started properly
    echo Continuing with tunnel setup anyway...
    echo.
)

REM Start Cloudflare tunnel
echo [2/2] Starting Cloudflare tunnel...
echo This will create a temporary public URL for your localhost:5000
echo.
echo ==========================================================
echo IMPORTANT: Keep BOTH windows open!
echo - Flask App window (separate window)
echo - This Cloudflare Tunnel window
echo ==========================================================
echo.
echo Copy the URL below and share it with others:
echo.
cloudflared tunnel --url http://localhost:5000

pause
