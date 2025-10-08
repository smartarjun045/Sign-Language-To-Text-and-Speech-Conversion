#!/bin/bash

echo "======================================"
echo "Sign Language Recognition Web App"
echo "======================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ from your package manager or https://python.org"
    exit 1
fi

echo -e "${GREEN}Python found:${NC}"
python3 --version

# Check if we're in the webapp directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}ERROR: app.py not found${NC}"
    echo "Please run this script from the webapp directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if requirements are installed
if ! pip show flask &> /dev/null; then
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install requirements${NC}"
        echo "Please check your internet connection and try again"
        exit 1
    fi
fi

# Check for required model files
if [ ! -f "cnn8grps_rad1_model.h5" ]; then
    echo -e "${YELLOW}WARNING: Model file 'cnn8grps_rad1_model.h5' not found${NC}"
    echo "Please copy this file from the main project directory"
    echo
    read -p "Continue anyway? (y/n): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ ! -f "white.jpg" ]; then
    echo -e "${YELLOW}WARNING: White background file 'white.jpg' not found${NC}"
    echo "Please copy this file from the main project directory"
    echo
    read -p "Continue anyway? (y/n): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
mkdir -p static/css static/js static/images templates instance

echo
echo "======================================"
echo "Starting Flask Web Application..."
echo "======================================"
echo
echo -e "${GREEN}Open your browser and go to:${NC}"
echo -e "${GREEN}http://localhost:5000${NC}"
echo
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo

# Start the Flask application
python3 app.py

# Deactivate virtual environment when done
deactivate

echo
echo -e "${GREEN}Application stopped.${NC}"