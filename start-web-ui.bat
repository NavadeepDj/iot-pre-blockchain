@echo off
REM Quick Start Script for IoT PRE Blockchain Web UI
REM This script helps you start all required services

echo ========================================
echo  IoT PRE Blockchain System - Quick Start
echo ========================================
echo.

echo This will open 4 terminal windows:
echo   1. Anvil Blockchain
echo   2. IPFS Daemon  
echo   3. Flask API Server
echo   4. Web Browser
echo.
echo Make sure you have:
echo   - Installed all dependencies
echo   - Deployed the smart contract
echo   - Configured .env file
echo.
pause

echo.
echo [1/4] Starting Anvil Blockchain...
start "Anvil Blockchain" cmd /k "cd blockchain && anvil"
timeout /t 3 /nobreak >nul

echo [2/4] Starting IPFS Daemon...
start "IPFS Daemon" cmd /k "ipfs daemon"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Flask API Server...
start "Flask API" cmd /k "cd python-backend && .\\venv\\Scripts\\activate && python app.py"
timeout /t 5 /nobreak >nul

echo [4/4] Opening Web UI...
start "" "http://localhost:8080"
cd web-ui
start "Web Server" cmd /k "python -m http.server 8080"

echo.
echo ========================================
echo  All services started!
echo ========================================
echo.
echo  Anvil:     http://localhost:8545
echo  IPFS:      http://localhost:5001
echo  API:       http://localhost:5000
echo  Web UI:    http://localhost:8080
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq Anvil Blockchain*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq IPFS Daemon*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Flask API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Web Server*" /F >nul 2>&1

echo All services stopped.
pause
