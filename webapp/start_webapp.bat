@echo off
echo ======================================
echo Sign Language Recognition Web App
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if we're in the webapp directory
if not exist "app.py" (
    echo ERROR: app.py not found
    echo Please run this script from the webapp directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if requirements are installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
)

REM Check for required model files
if not exist "cnn8grps_rad1_model.h5" (
    echo WARNING: Model file 'cnn8grps_rad1_model.h5' not found
    echo Attempting to copy from parent directory...
    if exist "..\cnn8grps_rad1_model.h5" (
        copy "..\cnn8grps_rad1_model.h5" .
        echo Model file copied successfully!
    ) else (
        echo Please copy this file from the main project directory
        echo.
        set /p continue="Continue anyway? (y/n): "
        if /i not "%continue%"=="y" (
            pause
            exit /b 1
        )
    )
)

if not exist "white.jpg" (
    echo WARNING: White background file 'white.jpg' not found
    echo Attempting to copy from parent directory...
    if exist "..\white.jpg" (
        copy "..\white.jpg" .
        echo White background file copied successfully!
    ) else (
        echo Please copy this file from the main project directory
        echo.
        set /p continue="Continue anyway? (y/n): "
        if /i not "%continue%"=="y" (
            pause
            exit /b 1
        )
    )
)

REM Create necessary directories
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images" mkdir static\images
if not exist "templates" mkdir templates
if not exist "instance" mkdir instance

echo.
echo ======================================
echo Starting Flask Web Application...
echo ======================================
echo.
echo Open your browser and go to:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
.venv\Scripts\python.exe app.py

REM Deactivate virtual environment when done
call .venv\Scripts\deactivate.bat

echo.
echo Application stopped.
pause