@echo off
echo ======================================
echo SQLite3 Installation Script
echo ======================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Running PowerShell installation script...
    powershell.exe -ExecutionPolicy Bypass -File install_sqlite3.ps1
) else (
    echo PowerShell not found. Please download manually.
    echo.
    echo Manual Installation:
    echo 1. Visit: https://www.sqlite.org/download.html
    echo 2. Download "sqlite-tools-win-x64-XXXXX.zip"
    echo 3. Extract sqlite3.exe to your project folder
    echo.
)

pause

