@echo off
echo Starting POS System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if PyQt5 is installed
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo PyQt5 is not installed. Installing now...
    pip install PyQt5==5.15.9
    if errorlevel 1 (
        echo Failed to install PyQt5
        pause
        exit /b 1
    )
)

REM Run the POS system
python run_pos.py

if errorlevel 1 (
    echo.
    echo Application encountered an error
    pause
)
