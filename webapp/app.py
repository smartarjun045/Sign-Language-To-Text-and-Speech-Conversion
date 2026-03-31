"""
Flask Web Application for Sign Language to Text and Speech Conversion

This is a web-based version of the desktop Sign Language Recognition System.
It provides real-time hand gesture recognition through webcam, converts 
recognized gestures to text, and offers text-to-speech functionality.

Features:
- Real-time camera feed with hand detection
- ASL fingerspelling recognition (A-Z)
- Word suggestions and autocomplete
- Text-to-speech synthesis
- User authentication and sessions
- Responsive web interface

Author: Sign Language Recognition System
"""

from flask import Flask, render_template, request, jsonify, session, Response, redirect, url_for
from flask_session import Session
import cv2
import numpy as np
import base64
import json
import os
from datetime import datetime, timedelta
import logging
import threading
import time

# Import our custom modules
from sign_language_recognizer import SignLanguageRecognizer
from user_auth import UserAuthentication
from speech_synthesis import SpeechSynthesis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'slr:'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize Flask-Session
Session(app)

# Initialize components
recognizer = SignLanguageRecognizer()
user_auth = UserAuthentication()
try:
    speech_synthesis = SpeechSynthesis()
    logger.info("Speech synthesis initialized successfully")
except Exception as e:
    logger.error(f"Speech synthesis initialization failed: {e}")
    speech_synthesis = None
    logger.info("Will use client-side speech synthesis as fallback")

# Global variables for camera and recognition state
camera = None
camera_active = False
recognition_active = False
current_frame = None
recognition_results = {
    'current_character': '',
    'sentence': '',
    'word_suggestions': [],
    'confidence': 0.0
}

def get_camera():
    """Initialize and return camera object"""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
    return camera

def release_camera():
    """Release camera resources"""
    global camera, camera_active
    if camera is not None:
        camera.release()
        camera = None
    camera_active = False

@app.route('/')
def index():
    """Main application page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_info = user_auth.get_user_info(session['user_id'])
    return render_template('index.html', user=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'})
        
        success, message, user_info = user_auth.authenticate_user(username, password)
        
        if success:
            session['user_id'] = username
            session['login_time'] = datetime.now().isoformat()
            session.permanent = True
            
            logger.info(f"User {username} logged in successfully")
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'redirect': url_for('index')
            })
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({'success': False, 'message': message})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        success, message = user_auth.register_user(username, email, password, full_name)
        
        if success:
            logger.info(f"New user registered: {username}")
            return jsonify({
                'success': True, 
                'message': 'Registration successful! Please log in.',
                'redirect': url_for('login')
            })
        else:
            return jsonify({'success': False, 'message': message})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    if 'user_id' in session:
        logger.info(f"User {session['user_id']} logged out")
        session.clear()
    
    release_camera()
    return redirect(url_for('login'))

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """Start camera feed"""
    global camera_active
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        camera = get_camera()
        if camera.isOpened():
            camera_active = True
            logger.info(f"Camera started for user {session['user_id']}")
            return jsonify({'success': True, 'message': 'Camera started'})
        else:
            return jsonify({'success': False, 'message': 'Cannot access camera'})
    except Exception as e:
        logger.error(f"Error starting camera: {str(e)}")
        return jsonify({'success': False, 'message': f'Camera error: {str(e)}'})

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera feed"""
    global camera_active
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    camera_active = False
    logger.info(f"Camera stopped for user {session['user_id']}")
    return jsonify({'success': True, 'message': 'Camera stopped'})

@app.route('/api/recognition/start', methods=['POST'])
def start_recognition():
    """Start sign language recognition"""
    global recognition_active
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if not camera_active:
        return jsonify({'success': False, 'message': 'Camera not active'})
    
    recognition_active = True
    logger.info(f"Recognition started for user {session['user_id']}")
    return jsonify({'success': True, 'message': 'Recognition started'})

@app.route('/api/recognition/stop', methods=['POST'])
def stop_recognition():
    """Stop sign language recognition"""
    global recognition_active
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    recognition_active = False
    logger.info(f"Recognition stopped for user {session['user_id']}")
    return jsonify({'success': True, 'message': 'Recognition stopped'})

@app.route('/api/recognition/status')
def recognition_status():
    """Get current recognition results"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    return jsonify({
        'success': True,
        'camera_active': camera_active,
        'recognition_active': recognition_active,
        'results': recognition_results
    })

@app.route('/api/text/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'message': 'No text provided'})
    
    try:
        if speech_synthesis:
            # Use immediate speech instead of queued speech for web interface
            success = speech_synthesis.speak_immediately(text)
            if success:
                logger.info(f"Text-to-speech for user {session['user_id']}: {text[:50]}...")
                return jsonify({'success': True, 'message': 'Speech synthesis completed'})
            else:
                return jsonify({'success': False, 'message': 'Speech synthesis failed'})
        else:
            # Fallback: return text for client-side speech synthesis
            logger.warning("Server-side speech synthesis not available, using client-side fallback")
            return jsonify({
                'success': True, 
                'message': 'Using browser speech synthesis',
                'text': text,
                'use_client_speech': True
            })
    except Exception as e:
        logger.error(f"Speech synthesis error: {str(e)}")
        # Fallback to client-side speech
        return jsonify({
            'success': True, 
            'message': 'Using browser speech synthesis (server fallback)',
            'text': text,
            'use_client_speech': True
        })

@app.route('/api/text/clear', methods=['POST'])
def clear_text():
    """Clear recognized text"""
    global recognition_results
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    recognition_results['sentence'] = ''
    recognition_results['word_suggestions'] = []
    
    # Clear text in recognizer
    recognizer.clear_text()
    
    logger.info(f"Text cleared for user {session['user_id']}")
    return jsonify({'success': True, 'message': 'Text cleared'})

@app.route('/api/text/suggest', methods=['POST'])
def apply_suggestion():
    """Apply word suggestion"""
    global recognition_results
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    suggestion = data.get('suggestion', '').strip()
    
    if not suggestion:
        return jsonify({'success': False, 'message': 'No suggestion provided'})
    
    try:
        # Apply suggestion through recognizer
        new_sentence = recognizer.apply_word_suggestion(suggestion)
        recognition_results['sentence'] = new_sentence
        
        return jsonify({'success': True, 'sentence': new_sentence})
    except Exception as e:
        logger.error(f"Error applying suggestion: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

def generate_video_frames():
    """Generate video frames for streaming"""
    global camera_active, recognition_active, current_frame, recognition_results
    
    camera = get_camera()
    
    while True:
        if not camera_active:
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if not success:
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        current_frame = frame.copy()
        
        # Perform recognition if active
        if recognition_active:
            try:
                # Process frame through recognizer
                processed_frame, results = recognizer.process_frame(frame)
                
                # Update global recognition results
                recognition_results.update(results)
                
                # Use processed frame for display
                frame = processed_frame
                
            except Exception as e:
                logger.error(f"Recognition error: {str(e)}")
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            frame_data = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        
        time.sleep(0.03)  # ~30 FPS

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    if 'user_id' not in session:
        return Response('Unauthorized', status=401)
    
    return Response(
        generate_video_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/profile')
def profile():
    """Profile page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_info = user_auth.get_user_info(session['user_id'])
    if not user_info:
        session.clear()
        return redirect(url_for('login'))
    
    # Add some statistics
    user_info['join_date'] = user_info.get('created_at', 'Unknown')
    user_info['total_sessions'] = user_info.get('total_sessions', 0)
    user_info['words_recognized'] = user_info.get('words_recognized', 0)
    
    return render_template('profile.html', user=user_info)

@app.route('/api/user/profile')
def user_profile():
    """Get user profile information"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    user_info = user_auth.get_user_info(session['user_id'])
    if user_info:
        return jsonify({'success': True, 'user': user_info})
    else:
        return jsonify({'success': False, 'message': 'User not found'})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    
    if not full_name or not email:
        return jsonify({'success': False, 'message': 'Name and email are required'})
    
    try:
        success, message = user_auth.update_user_profile(session['user_id'], full_name, email)
        if success:
            logger.info(f"Profile updated for user {session['user_id']}")
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        else:
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while updating profile'})

@app.route('/change_password', methods=['POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Current and new passwords are required'})
    
    try:
        success, message = user_auth.change_password(session['user_id'], current_password, new_password)
        if success:
            logger.info(f"Password changed for user {session['user_id']}")
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        else:
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while changing password'})

@app.route('/delete_account', methods=['POST'])
def delete_account():
    """Delete user account"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    password = data.get('password', '')
    
    if not password:
        return jsonify({'success': False, 'message': 'Password is required to delete account'})
    
    try:
        success, message = user_auth.delete_account(session['user_id'], password)
        if success:
            logger.info(f"Account deleted for user {session['user_id']}")
            session.clear()
            release_camera()
            return jsonify({'success': True, 'message': 'Account deleted successfully'})
        else:
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting account'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

def cleanup():
    """Cleanup resources on app shutdown"""
    release_camera()
    logger.info("Application cleanup completed")

# Register cleanup function
import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    print("Starting Sign Language Recognition Web Application...")
    print("Access the application at: http://localhost:5000")
    
    # Create required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Run the Flask application
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=False  # Disable reloader to prevent camera issues
    )