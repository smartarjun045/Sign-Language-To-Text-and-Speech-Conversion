# Sign Language To Text and Speech Conversion

A Python-based desktop application for real-time American Sign Language (ASL) fingerspelling recognition using computer vision and deep learning.

## 🚀 Features

- **Real-time Hand Detection**: Uses MediaPipe for robust hand tracking
- **CNN-based Recognition**: Trained model for A-Z ASL fingerspelling recognition  
- **Text-to-Speech**: Converts recognized text to speech using pyttsx3
- **Word Suggestions**: Smart autocomplete with dictionary integration
- **User Authentication**: Secure login and registration system
- **Professional GUI**: Modern tkinter interface with user profiles

## 🛠 Technology Stack

- **Python 3.9+**
- **OpenCV** - Image processing and camera capture
- **MediaPipe** - Hand detection and landmark tracking
- **TensorFlow/Keras** - CNN model for gesture classification
- **CVZone** - Hand tracking utilities
- **pyttsx3** - Text-to-speech synthesis
- **tkinter** - GUI framework
- **NumPy** - Numerical operations

## 📋 Requirements

```
opencv-python
numpy
cvzone
mediapipe
tensorflow
keras
pyttsx3
enchant
pillow
```

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
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

4. **Ensure required files exist:**
   - `cnn8grps_rad1_model.h5` - Pre-trained CNN model
   - `white.jpg` - White background image for hand skeleton drawing

## 🎮 Usage

### Main Application (Recommended)
```bash
python final_complete_auth.py
```
- Full-featured application with authentication
- Complete A-Z recognition
- Word suggestions and text-to-speech
- User profile management

### Alternative Versions

#### Original GUI Version
```bash
python final_pred.py
```
- Original version without authentication
- Full recognition capabilities

#### Console Version
```bash  
python prediction_wo_gui.py
```
- Command-line version
- No GUI, text output only

#### Application Launcher
```bash
python run_app.py
```
- Choose between authenticated, original, or console versions

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
├── data_collection_*.py      # Data collection utilities
├── test_*.py                 # Testing utilities
├── cnn8grps_rad1_model.h5    # Pre-trained CNN model
├── white.jpg                 # Background image
├── requirements.txt          # Python dependencies
├── user_data/               # User accounts and sessions
└── users.json              # User database
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

1. **Camera not working:**
   ```bash
   python test_camera.py
   ```

2. **Import errors:**
   ```bash
   python test_imports.py
   ```

3. **Model not found:**
   - Ensure `cnn8grps_rad1_model.h5` is in the root directory
   - Check file permissions

4. **Audio not working:**
   - Verify pyttsx3 installation
   - Check system audio settings

### Performance Tips

- **Good Lighting**: Ensure adequate lighting for camera
- **Plain Background**: Use plain background for better hand detection
- **Camera Position**: Position camera at appropriate distance
- **Hand Visibility**: Keep hand clearly visible in frame

## 📈 Model Performance

- **Training Data**: 180 images per ASL letter
- **Architecture**: Convolutional Neural Network (CNN)
- **Classes**: 26 letters (A-Z) simplified to 8 broader classes
- **Input**: 400x400 pixel hand skeleton images
- **Accuracy**: Optimized for real-time performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MediaPipe team for hand detection technology
- TensorFlow/Keras for deep learning framework
- OpenCV community for computer vision tools
- ASL community for gesture standards

---

**Made with ❤️ for accessibility and communication**