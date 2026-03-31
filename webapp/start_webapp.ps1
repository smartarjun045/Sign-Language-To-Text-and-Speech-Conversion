# Sign Language Recognition Web App - PowerShell Startup Script
# Run this script from PowerShell with: .\start_webapp.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Sign Language Recognition Web App" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the webapp directory
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the webapp directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Check if requirements are installed
try {
    pip show flask > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing requirements..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
            Write-Host "Please check your internet connection and try again" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
} catch {
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check for required model files
if (-not (Test-Path "cnn8grps_rad1_model.h5")) {
    Write-Host "WARNING: Model file 'cnn8grps_rad1_model.h5' not found" -ForegroundColor Yellow
    Write-Host "Attempting to copy from parent directory..." -ForegroundColor Yellow
    if (Test-Path "..\cnn8grps_rad1_model.h5") {
        Copy-Item "..\cnn8grps_rad1_model.h5" -Destination "."
        Write-Host "Model file copied successfully!" -ForegroundColor Green
    } else {
        Write-Host "Please copy this file from the main project directory" -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
}

if (-not (Test-Path "white.jpg")) {
    Write-Host "WARNING: White background file 'white.jpg' not found" -ForegroundColor Yellow
    Write-Host "Attempting to copy from parent directory..." -ForegroundColor Yellow
    if (Test-Path "..\white.jpg") {
        Copy-Item "..\white.jpg" -Destination "."
        Write-Host "White background file copied successfully!" -ForegroundColor Green
    } else {
        Write-Host "Please copy this file from the main project directory" -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
}

# Create necessary directories
$directories = @("static\css", "static\js", "static\images", "templates", "instance")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force > $null
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Starting Flask Web Application..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open your browser and go to:" -ForegroundColor Green
Write-Host "http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Flask application
try {
    .venv\Scripts\python.exe app.py
} catch {
    Write-Host ""
    Write-Host "Application stopped with error: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Application stopped." -ForegroundColor Green
}

# Deactivate virtual environment (automatic when script ends)
deactivate 2>$null

Read-Host "Press Enter to exit"