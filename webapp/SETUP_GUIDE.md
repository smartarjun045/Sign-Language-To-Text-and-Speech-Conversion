# Sign Language Recognition Web Application

## Overview

This Flask web application provides a modern, user-friendly interface for real-time American Sign Language (ASL) fingerspelling recognition. It converts the original desktop application into a web-based platform accessible through any modern web browser.

## Features

### 🌟 Core Functionality
- **Real-time Camera Recognition**: Live webcam feed with hand gesture detection
- **A-Z ASL Fingerspelling**: Complete American Sign Language alphabet recognition
- **Text-to-Speech**: Convert recognized text to speech using browser APIs
- **Smart Word Suggestions**: Dictionary-based autocomplete and word suggestions
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🔧 Technical Features
- **Flask Backend**: Robust Python web framework with modular architecture
- **Real-time Video Streaming**: Efficient video processing and streaming
- **CNN-based Recognition**: Pre-trained deep learning model for gesture classification
- **Session Management**: Secure user sessions with proper authentication
- **REST API**: Clean API endpoints for frontend-backend communication
- **Modern UI**: Responsive design with intuitive user interface

## Project Structure

```
webapp/
├── app.py                      # Main Flask application
├── sign_language_recognizer.py # Core recognition logic
├── user_auth.py               # User authentication module
├── speech_synthesis.py        # Text-to-speech functionality
├── requirements.txt           # Python dependencies
├── README.md                 # This documentation
│
├── templates/                 # HTML templates
│   ├── index.html            # Main application page
│   ├── login.html            # User login page
│   ├── register.html         # User registration page
│   └── error.html            # Error page template
│
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── js/
│   │   ├── app.js            # Main application JavaScript
│   │   └── auth.js           # Authentication JavaScript
│   └── images/               # Image assets (if any)
│
└── instance/                  # Instance-specific files
    ├── users.json            # User database (created automatically)
    └── flask_session/        # Session data (created automatically)
```

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher (3.9-3.10 recommended)
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Webcam**: Required for gesture recognition
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space

### Required Files from Original Project
Before running the web application, ensure you have these files from the original desktop application:

1. **`cnn8grps_rad1_model.h5`** - Pre-trained CNN model (~13.5MB)
2. **`white.jpg`** - White background image for hand skeleton drawing

Copy these files to the webapp directory:
```bash
cp ../cnn8grps_rad1_model.h5 ./
cp ../white.jpg ./
```

## Installation Guide

### Step 1: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd Sign-Language-To-Text-and-Speech-Conversion/webapp

# Or extract the provided files to the webapp directory
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter issues, try upgrading pip first:
pip install --upgrade pip
```

### Step 4: Install System Dependencies

#### Windows
- Most dependencies work out of the box
- For dictionary functionality, ensure Windows Language Packs are installed

#### macOS
```bash
# Install required system libraries
brew install enchant
brew install portaudio  # For audio functionality
```

#### Ubuntu/Debian
```bash
# Install required system libraries
sudo apt-get update
sudo apt-get install libenchant-2-2
sudo apt-get install portaudio19-dev
sudo apt-get install espeak espeak-data  # For text-to-speech
```

#### CentOS/RHEL/Fedora
```bash
# Install required system libraries
sudo yum install enchant2
sudo yum install portaudio-devel
sudo dnf install espeak  # For text-to-speech
```

### Step 5: Verify Installation
```bash
# Test the installation
python -c "import cv2, tensorflow, flask, enchant; print('All dependencies installed successfully!')"
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the webapp directory for custom configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Server Configuration
HOST=127.0.0.1
PORT=5000

# Security Settings
SESSION_TIMEOUT=24  # hours
MAX_LOGIN_ATTEMPTS=5

# Model Configuration
MODEL_PATH=cnn8grps_rad1_model.h5
WHITE_BG_PATH=white.jpg

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Application Settings
You can modify settings in `app.py`:

```python
# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Recognition settings
UPDATE_INTERVAL = 2  # seconds
CONFIDENCE_THRESHOLD = 0.5

# Session settings
SESSION_TIMEOUT = 24  # hours
```

## Running the Application

### Development Mode
```bash
# Make sure virtual environment is activated
# Navigate to webapp directory
cd webapp

# Run the Flask application
python app.py

# The application will be available at:
# http://localhost:5000
```

### Production Mode (Optional)
For production deployment, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Usage Instructions

### 1. Initial Setup
1. Open your web browser and navigate to `http://localhost:5000`
2. Click "Register" to create a new account
3. Fill in the registration form with your details
4. After successful registration, log in with your credentials

### 2. Using the Recognition System
1. **Start Camera**: Click the "Start Camera" button to activate your webcam
2. **Start Recognition**: Once the camera is active, click "Start Recognition"
3. **Position Your Hand**: Place your hand clearly in the camera view
4. **Make Gestures**: Perform ASL fingerspelling gestures (A-Z)
5. **View Results**: 
   - Current character appears in the character display
   - Complete text builds up in the text area
   - Word suggestions appear below the text

### 3. Using Text Features
- **Speak Text**: Click "Speak Text" to hear the recognized text
- **Clear Text**: Click "Clear Text" to reset the text area
- **Word Suggestions**: Click on any suggested word to replace the current word
- **Manual Editing**: You can manually edit text in the text area

### 4. Tips for Better Recognition
- **Lighting**: Ensure good lighting on your hand
- **Background**: Use a plain background when possible
- **Hand Position**: Keep your entire hand visible in the camera frame
- **Gesture Duration**: Hold each gesture steady for 1-2 seconds
- **Distance**: Maintain consistent distance from the camera

## API Documentation

The application provides REST API endpoints for programmatic access:

### Authentication Endpoints

#### POST /login
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### POST /register
```json
{
  "username": "new_username",
  "email": "email@example.com",
  "password": "secure_password",
  "full_name": "Your Full Name"
}
```

### Camera Control Endpoints

#### POST /api/camera/start
Start the camera feed

#### POST /api/camera/stop
Stop the camera feed

### Recognition Control Endpoints

#### POST /api/recognition/start
Start gesture recognition

#### POST /api/recognition/stop
Stop gesture recognition

#### GET /api/recognition/status
Get current recognition status and results

### Text Processing Endpoints

#### POST /api/text/speak
```json
{
  "text": "Text to speak"
}
```

#### POST /api/text/clear
Clear recognized text

#### POST /api/text/suggest
```json
{
  "suggestion": "suggested_word"
}
```

### Video Stream Endpoint

#### GET /video_feed
Returns live video stream with hand detection overlay

## Troubleshooting

### Common Issues and Solutions

#### 1. Camera Not Working
**Problem**: Camera fails to start or shows black screen
**Solutions**:
- Check camera permissions in browser settings
- Ensure no other applications are using the camera
- Try refreshing the page
- Check if camera drivers are installed

#### 2. Model Loading Errors
**Problem**: "Model file not found" or TensorFlow errors
**Solutions**:
- Verify `cnn8grps_rad1_model.h5` is in the webapp directory
- Check file permissions
- Ensure TensorFlow is properly installed
- Try downloading the model file again

#### 3. Recognition Not Working
**Problem**: Hand detected but no character recognition
**Solutions**:
- Ensure good lighting conditions
- Check hand positioning in camera frame
- Verify model file is not corrupted
- Try restarting recognition

#### 4. Speech Synthesis Issues
**Problem**: Text-to-speech not working
**Solutions**:
- Check browser audio permissions
- Verify system audio settings
- Ensure pyttsx3 is properly installed
- Try different browsers

#### 5. Installation Problems
**Problem**: Package installation failures
**Solutions**:
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install packages individually if bulk install fails
pip install Flask
pip install opencv-python
pip install tensorflow
# ... etc

# For Windows users with Visual C++ issues:
pip install --upgrade setuptools
# Install Microsoft Visual C++ Redistributable
```

#### 6. Performance Issues
**Problem**: Slow recognition or high CPU usage
**Solutions**:
- Reduce camera resolution in app.py
- Increase recognition update interval
- Close other resource-intensive applications
- Consider using GPU acceleration if available

#### 7. Browser Compatibility
**Problem**: Features not working in certain browsers
**Solutions**:
- Use Chrome, Firefox, or Edge (latest versions)
- Enable camera and microphone permissions
- Check if WebRTC is supported
- Clear browser cache and cookies

### Debug Mode
Enable debug mode for detailed error information:

```python
# In app.py, set:
app.run(debug=True)
```

### Logging
Check application logs for detailed error information:
- Console output during development
- Log files if configured in production

## Security Considerations

### Authentication Security
- Passwords are hashed using SHA-256
- Sessions use secure tokens
- User input is validated and sanitized

### Web Security
- CSRF protection enabled
- Secure session cookies
- Input validation on all endpoints

### Privacy
- Video streams are processed locally
- No video data is stored permanently
- User data is stored locally in JSON format

## Performance Optimization

### For Better Performance
1. **Hardware Acceleration**: Use GPU-enabled TensorFlow if available
2. **Camera Settings**: Adjust resolution and FPS based on hardware
3. **Model Optimization**: Consider model quantization for faster inference
4. **Caching**: Enable browser caching for static assets

### Resource Usage
- **Memory**: ~2-4GB RAM during operation
- **CPU**: Moderate usage for video processing
- **Storage**: ~500MB for dependencies + model file

## Development Guide

### Adding New Features
1. **Backend**: Add routes in `app.py`
2. **Frontend**: Update HTML templates and JavaScript
3. **Recognition**: Modify `sign_language_recognizer.py`
4. **Authentication**: Update `user_auth.py`

### Code Structure
- **Modular Design**: Separate concerns into different modules
- **Error Handling**: Comprehensive try-catch blocks
- **Logging**: Detailed logging for debugging
- **Documentation**: Inline comments and docstrings

### Testing
```bash
# Install testing dependencies
pip install pytest pytest-flask

# Run tests (if test files are created)
pytest tests/
```

## Deployment

### Local Network Access
To access from other devices on your network:
```python
# In app.py, change:
app.run(host='0.0.0.0', port=5000)
```

### Production Deployment
For production environments:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx, Apache)
3. Use environment variables for configuration
4. Implement proper logging and monitoring
5. Set up SSL/HTTPS

## Support and Contributions

### Getting Help
- Check this documentation first
- Review error messages and logs
- Search for similar issues online
- Contact the development team

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Reporting Issues
Please include:
- Operating system and version
- Python version
- Browser and version
- Error messages and logs
- Steps to reproduce the issue

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Original desktop application developers
- MediaPipe team for hand detection technology
- TensorFlow team for machine learning framework
- Flask community for web framework
- ASL community for gesture standards

---

**Made with ❤️ for accessibility and inclusive communication**