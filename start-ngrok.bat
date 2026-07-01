@echo off
echo Starting ASHA Beauty Salon - Flask App + ngrok Tunnel
echo ======================================================
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ngrok is not installed or not in PATH
    echo Please download ngrok from: https://ngrok.com/download
    echo Extract and add to PATH, or place ngrok.exe in this folder
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

REM Start ngrok tunnel
echo [2/2] Starting ngrok tunnel...
echo This will create a temporary public URL for your localhost:5000
echo.
echo ======================================================
echo IMPORTANT: Keep BOTH windows open!
echo - Flask App window (separate window)
echo - This ngrok Tunnel window
echo ======================================================
echo.
echo Copy the https URL from below and share it with others:
echo.
ngrok http 5000

pause
