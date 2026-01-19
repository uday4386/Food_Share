@echo off
echo ========================================
echo Database Data Extraction Commands
echo ========================================
echo.
echo 1. View All Users
echo 2. View All Donations
echo 3. View All Requests
echo 4. Export All Data to CSV
echo 5. Show Statistics
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    python quick_export.py view_users
    pause
    goto :start
)

if "%choice%"=="2" (
    python quick_export.py view_donations
    pause
    goto :start
)

if "%choice%"=="3" (
    python quick_export.py view_requests
    pause
    goto :start
)

if "%choice%"=="4" (
    python export_data.py
    pause
    goto :start
)

if "%choice%"=="5" (
    python quick_export.py stats
    pause
    goto :start
)

if "%choice%"=="6" (
    exit
)

echo Invalid choice!
pause

