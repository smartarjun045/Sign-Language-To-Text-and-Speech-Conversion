# Fix Installation Script for Sign Language Recognition Web App
# This script resolves TensorFlow installation issues on Windows

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Fixing Installation Issues..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean up corrupted virtual environment
Write-Host "Step 1: Cleaning corrupted virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force .venv
    Write-Host "Old virtual environment removed." -ForegroundColor Green
}

# Step 2: Create fresh virtual environment
Write-Host "Step 2: Creating fresh virtual environment..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Write-Host "Please ensure Python 3.11.1 is installed" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Virtual environment created successfully." -ForegroundColor Green

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Step 4: Upgrade pip and tools
Write-Host "Step 4: Upgrading pip and build tools..." -ForegroundColor Yellow
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\pip.exe install --upgrade setuptools wheel

# Step 5: Install core dependencies first
Write-Host "Step 5: Installing core dependencies..." -ForegroundColor Yellow
$corePackages = @(
    "numpy==1.24.3",
    "opencv-python==4.8.0.76",
    "Pillow==9.5.0"
)

foreach ($package in $corePackages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    .venv\Scripts\pip.exe install $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Failed to install $package" -ForegroundColor Yellow
    } else {
        Write-Host "✓ $package installed successfully" -ForegroundColor Green
    }
}

# Step 6: Install TensorFlow with specific strategy
Write-Host "Step 6: Installing TensorFlow (this may take a while)..." -ForegroundColor Yellow
.venv\Scripts\pip.exe install tensorflow==2.12.0 --no-cache-dir
if ($LASTEXITCODE -ne 0) {
    Write-Host "TensorFlow installation failed. Trying alternative approach..." -ForegroundColor Yellow
    .venv\Scripts\pip.exe install tensorflow-cpu==2.12.0 --no-cache-dir
}

# Step 7: Install MediaPipe
Write-Host "Step 7: Installing MediaPipe..." -ForegroundColor Yellow
.venv\Scripts\pip.exe install mediapipe==0.10.3 --no-cache-dir

# Step 8: Install remaining Flask dependencies
Write-Host "Step 8: Installing Flask and web dependencies..." -ForegroundColor Yellow
$webPackages = @(
    "Flask==2.3.3",
    "Flask-Session==0.5.0",
    "Werkzeug==2.3.7"
)

foreach ($package in $webPackages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    .venv\Scripts\pip.exe install $package
}

# Step 9: Install remaining dependencies
Write-Host "Step 9: Installing remaining dependencies..." -ForegroundColor Yellow
$remainingPackages = @(
    "cvzone==1.5.6",
    "pyttsx3==2.90",
    "pyenchant==3.2.2",
    "requests==2.31.0"
)

foreach ($package in $remainingPackages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    .venv\Scripts\pip.exe install $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Failed to install $package" -ForegroundColor Yellow
    }
}

# Step 10: Verify installation
Write-Host "Step 10: Verifying installation..." -ForegroundColor Yellow
$testScript = @"
try:
    import tensorflow as tf
    print(f'TensorFlow version: {tf.__version__}')
    
    import cv2
    print(f'OpenCV version: {cv2.__version__}')
    
    import mediapipe as mp
    print(f'MediaPipe version: {mp.__version__}')
    
    import flask
    print(f'Flask version: {flask.__version__}')
    
    print('✓ All core dependencies installed successfully!')
    
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
"@

$testScript | Out-File -FilePath "test_imports.py" -Encoding UTF8
.venv\Scripts\python.exe test_imports.py
$testResult = $LASTEXITCODE

Remove-Item "test_imports.py" -ErrorAction SilentlyContinue

if ($testResult -eq 0) {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "✓ Installation completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the application with:" -ForegroundColor Cyan
    Write-Host ".\start_webapp.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "✗ Installation completed with errors" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    Write-Host "You may need to install some packages manually." -ForegroundColor Yellow
}

Read-Host "Press Enter to continue"