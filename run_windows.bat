@echo off

REM Order Barcode Management System One-Click Run Script
REM Double-click this file on Windows to run

cls
echo =============================================================
echo Order Barcode Management System
echo =============================================================
echo
echo Starting system...
echo Please wait...
echo
echo [INFO] System will auto open browser at:
echo http://127.0.0.1:888
echo
echo [INFO] Features:
echo   - Order Management: Create, edit, delete orders
echo   - Barcode Generation: Auto-generate unique barcodes
echo   - Barcode Scanning: Support scanner and manual input
echo   - Scan Records: View all scan history
echo   - Reports: Generate order statistics
echo
echo [WARNING] Notes:
echo   - First run may need to install dependencies
echo   - Ensure port 888 is not in use
echo   - Press Ctrl+C to stop server
echo =============================================================
echo


REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.11 and add to PATH
    pause
    exit /b 1
)

REM Check dependencies
pip list | findstr "Flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install flask flask-cors python-barcode Pillow==9.5.0
    if %errorlevel% neq 0 (
        echo [ERROR] Dependencies installation failed
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    echo
)

REM Run system
echo [INFO] Starting server...
echo
python start.py

pause
