# Sign Language To Text and Speech Conversion

A Python-based desktop application for real-time American Sign Language (ASL) fingerspelling recognition using computer vision and deep learning.

## 🚀 Features

- **Real-time Hand Detection**: Uses MediaPipe for robust hand tracking
- **CNN-based Recognition**: Pre-trained model for A-Z ASL fingerspelling recognition  
- **Text-to-Speech**: Converts recognized text to speech using pyttsx3
- **Word Suggestions**: Smart autocomplete with dictionary integration
- **User Authentication**: Secure login and registration system with session management
- **Professional GUI**: Modern tkinter interface with user profiles
- **Multiple Application Modes**: Choose from authenticated, original, or console versions

## 🛠 Technology Stack

- **Python 3.9+**
- **OpenCV** - Image processing and camera capture
- **MediaPipe** - Hand detection and landmark tracking
- **TensorFlow/Keras** - CNN model for gesture classification
- **CVZone** - Hand tracking utilities
- **pyttsx3** - Text-to-speech synthesis
- **tkinter** - GUI framework
- **NumPy** - Numerical operations
- **PyEnchant** - Dictionary and word suggestions

## 📋 Requirements

See `requirements.txt` for exact versions:

```
opencv-python>=4.5.0
tensorflow>=2.8.0
cvzone>=1.5.0
pyttsx3>=2.90
pyenchant>=3.2.0
numpy>=1.21.0
Pillow>=8.3.0
tk>=0.1.0
```

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/smartarjun045/Sign-Language-To-Text-and-Speech-Conversion.git
   cd Sign-Language-To-Text-and-Speech-Conversion
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Required files (included in repository):**
   - `cnn8grps_rad1_model.h5` - Pre-trained CNN model
   - `white.jpg` - White background image for hand skeleton drawing
   - `AtoZ_3.1/` - Training dataset (A-Z folders with ~180 images each)

## 🎮 Usage

### Quick Start (Windows)
```bash
start.bat
```
- Double-click `start.bat` to launch the application launcher

### Main Application (Recommended)
```bash
python final_complete_auth.py
```
- Full-featured application with user authentication
- Complete A-Z ASL recognition
- Word suggestions and text-to-speech
- User profile and session management

### Alternative Versions

#### Application Launcher
```bash
python run_app.py
```
- Interactive menu to choose between different application modes

#### Original GUI Version
```bash
python final_pred.py
```
- Original version without authentication system
- Full recognition capabilities with GUI

#### Console Version
```bash  
python prediction_wo_gui.py
```
- Command-line version for testing
- Text output only, no GUI

## 🎯 How It Works

1. **Camera Capture**: Captures real-time video from webcam
2. **Hand Detection**: MediaPipe detects hand landmarks (21 key points)
3. **Preprocessing**: Draws hand skeleton on white background for normalization
4. **Classification**: CNN model predicts ASL letter from hand pose
5. **Text Building**: Accumulates characters with gesture confirmation
6. **Speech Output**: Converts recognized text to speech

## 🖐 Gesture Recognition

- **A-Z Letters**: All 26 ASL fingerspelling gestures
- **Special Gestures**:
  - `Space`: Add space between words
  - `Next`: Confirm current character 
  - `Backspace`: Delete last character

## 📁 Project Structure

```
├── final_complete_auth.py      # Main authenticated application
├── final_pred.py              # Original GUI application  
├── prediction_wo_gui.py       # Console application
├── run_app.py                # Application launcher
├── auth_gui.py               # Authentication GUI components
├── session_manager.py        # User session management
├── user_database.py          # User data management
├── start.bat                 # Windows batch file launcher
├── cnn8grps_rad1_model.h5    # Pre-trained CNN model (13.5MB)
├── white.jpg                 # White background image
├── requirements.txt          # Python dependencies
├── users.json               # User database
├── current_session.json     # Current user session
├── AtoZ_3.1/               # Training dataset
│   ├── A/                  # ~180 images for letter A
│   ├── B/                  # ~180 images for letter B
│   └── ...                 # ... (A-Z folders)
└── .gitignore              # Git ignore file
```

## 🔐 Authentication System

- **User Registration**: Create new accounts with validation
- **Secure Login**: SHA-256 password hashing
- **Session Management**: Automatic session handling
- **User Profiles**: Profile management and preferences

## 🎨 GUI Features

- **Modern Interface**: Professional tkinter design
- **Real-time Video**: Live camera feed display
- **Hand Skeleton**: Visual hand landmark overlay
- **Character Display**: Current recognized character
- **Sentence Building**: Accumulated text display  
- **Word Suggestions**: Dictionary-based autocomplete
- **Control Buttons**: Speak, Clear, and settings

## 🔧 Troubleshooting

### Common Issues

1. **Model not found:**
   - Ensure `cnn8grps_rad1_model.h5` is in the root directory
   - File should be ~13.5MB in size

2. **Camera not working:**
   - Check camera permissions
   - Ensure no other applications are using the camera

3. **Import errors:**
   - Verify all requirements are installed: `pip install -r requirements.txt`
   - Check Python version (3.9+ recommended)

4. **Audio not working:**
   - Verify pyttsx3 installation
   - Check system audio settings
   - Try running: `python -c "import pyttsx3; pyttsx3.speak('test')"`

### Performance Tips

- **Good Lighting**: Ensure adequate lighting for camera
- **Plain Background**: Use plain background for better hand detection
- **Camera Position**: Position camera at appropriate distance (arm's length)
- **Hand Visibility**: Keep entire hand clearly visible in frame
- **Stable Position**: Minimize hand movement during recognition

## 📈 Model Performance

- **Training Data**: ~180 images per ASL letter (4,680+ total images)
- **Dataset**: Complete A-Z ASL fingerspelling alphabet
- **Architecture**: Convolutional Neural Network (CNN)
- **Model Size**: 13.5MB (`cnn8grps_rad1_model.h5`)
- **Input**: Hand skeleton images on white background
- **Performance**: Optimized for real-time recognition
- **Classes**: Originally 26 letters, grouped into 8 broader classes for better accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make changes and test thoroughly
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **MediaPipe** team for robust hand detection technology
- **TensorFlow/Keras** for deep learning framework
- **OpenCV** community for computer vision tools
- **ASL Community** for gesture standards and accessibility advocacy
- **Python Community** for excellent libraries and documentation

## 📧 Contact

**Developer**: smartarjun045  
**GitHub**: [@smartarjun045](https://github.com/smartarjun045)  
**Repository**: [Sign-Language-To-Text-and-Speech-Conversion](https://github.com/smartarjun045/Sign-Language-To-Text-and-Speech-Conversion)

---

**Made with ❤️ for accessibility and inclusive communication**