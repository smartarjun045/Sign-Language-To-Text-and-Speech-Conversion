"""
Sign Language Recognizer Module

This module contains the core logic for real-time American Sign Language 
fingerspelling recognition. It's extracted and refactored from the original
desktop application to work with the Flask web application.

Key Features:
- Real-time hand detection using MediaPipe
- CNN-based gesture classification
- A-Z ASL fingerspelling recognition
- Word completion and suggestions
- Hand skeleton visualization
"""

import cv2
import numpy as np
import math
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import enchant
import os
import logging

logger = logging.getLogger(__name__)

class SignLanguageRecognizer:
    def __init__(self, model_path='cnn8grps_rad1_model.h5', white_bg_path='white.jpg'):
        """
        Initialize the Sign Language Recognizer
        
        Args:
            model_path: Path to the trained CNN model
            white_bg_path: Path to white background image for hand skeleton
        """
        self.model_path = model_path
        self.white_bg_path = white_bg_path
        
        # Initialize hand detectors
        self.hd = HandDetector(maxHands=1)
        self.hd2 = HandDetector(maxHands=1)
        
        # Load CNN model
        self.model = None
        self.load_model()
        
        # Initialize dictionary for word suggestions
        try:
            self.dictionary = enchant.Dict("en-US")
        except Exception as e:
            logger.warning(f"Could not load dictionary: {e}")
            self.dictionary = None
        
        # Recognition state variables
        self.reset_recognition_state()
        
        # Constants
        self.offset = 29
        
    def load_model(self):
        """Load the pre-trained CNN model"""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                logger.info(f"Model loaded successfully from {self.model_path}")
            else:
                # Try to find model in parent directory
                parent_model_path = os.path.join('..', self.model_path)
                if os.path.exists(parent_model_path):
                    self.model = load_model(parent_model_path)
                    logger.info(f"Model loaded from parent directory: {parent_model_path}")
                else:
                    raise FileNotFoundError(f"Model file not found: {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def reset_recognition_state(self):
        """Reset all recognition state variables"""
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        self.space_flag = False
        self.next_flag = True
        self.prev_char = ""
        self.count = -1
        self.ten_prev_char = [" "] * 10
        
        # Initialize character counters
        for i in ascii_uppercase:
            self.ct[i] = 0
            
        # Text accumulation
        self.recognized_text = ""
        self.current_word = ""
        self.current_symbol = "-"
        
        # Word suggestions
        self.word_suggestions = [" ", " ", " ", " "]
        
        logger.info("Recognition state reset")
    
    def distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def draw_hand_skeleton(self, white_bg, landmarks, bbox):
        """
        Draw hand skeleton on white background
        
        Args:
            white_bg: White background image
            landmarks: Hand landmarks from MediaPipe
            bbox: Bounding box [x, y, w, h]
            
        Returns:
            Image with hand skeleton drawn
        """
        x, y, w, h = bbox
        os_x = ((400 - w) // 2) - 15
        os_y = ((400 - h) // 2) - 15
        
        # Draw finger connections
        connections = [
            (0, 4), (5, 8), (9, 12), (13, 16), (17, 20),  # Finger lines
            (5, 9), (9, 13), (13, 17), (0, 5), (0, 17)    # Palm connections
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start_point = (landmarks[start_idx][0] + os_x, landmarks[start_idx][1] + os_y)
                end_point = (landmarks[end_idx][0] + os_x, landmarks[end_idx][1] + os_y)
                cv2.line(white_bg, start_point, end_point, (0, 255, 0), 3)
        
        # Draw landmark points
        for point in landmarks:
            cv2.circle(white_bg, (point[0] + os_x, point[1] + os_y), 2, (0, 0, 255), 1)
            
        return white_bg
    
    def predict_gesture(self, hand_image, landmarks):
        """
        Predict ASL gesture from hand image and landmarks
        
        Args:
            hand_image: Processed hand image (400x400)
            landmarks: Hand landmarks
            
        Returns:
            Predicted character/gesture
        """
        if self.model is None:
            return 'MODEL_ERROR'
            
        try:
            # Prepare image for model prediction
            input_image = hand_image.reshape(1, 400, 400, 3)
            
            # Get model predictions
            prob = np.array(self.model.predict(input_image)[0], dtype='float32')
            ch1 = np.argmax(prob, axis=0)
            prob[ch1] = 0
            ch2 = np.argmax(prob, axis=0)
            prob[ch2] = 0
            ch3 = np.argmax(prob, axis=0)
            prob[ch3] = 0
            
            pl = [ch1, ch2]
            
            # Apply complex gesture recognition logic (from original)
            predicted_char = self._apply_gesture_rules(ch1, ch2, landmarks)
            
            return predicted_char
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 'PRED_ERROR'
    
    def _apply_gesture_rules(self, ch1, ch2, landmarks):
        """
        Apply the complex gesture recognition rules from the original system
        This is the exact logic from the original predict() method
        """
        pts = landmarks  # For compatibility with original code
        if not isinstance(pts, (list, tuple)) or len(pts) < 21:
            return "-"
        ch1 = int(ch1)
        ch2 = int(ch2)

        # 8-group remapping rules ported from the original predictor.
        pl = [ch1, ch2]

        l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
             [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
             [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
        if pl in l and (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 0

        l = [[2, 2], [2, 1]]
        if pl in l and pts[5][0] < pts[4][0]:
            ch1 = 0

        l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if (pts[0][0] > pts[8][0] and pts[0][0] > pts[4][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and pts[5][0] > pts[4][0]:
                ch1 = 2

        l = [[6, 0], [6, 6], [6, 2]]
        pl = [ch1, ch2]
        if pl in l and self.distance(pts[8], pts[16]) < 52:
            ch1 = 2

        l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if pts[6][1] > pts[8][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
                ch1 = 3

        l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
        pl = [ch1, ch2]
        if pl in l and pts[4][0] > pts[0][0]:
            ch1 = 3

        l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
        pl = [ch1, ch2]
        if pl in l and pts[2][1] + 15 < pts[16][1]:
            ch1 = 3

        l = [[6, 4], [6, 1], [6, 2]]
        pl = [ch1, ch2]
        if pl in l and self.distance(pts[4], pts[11]) > 55:
            ch1 = 4

        l = [[1, 4], [1, 6], [1, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.distance(pts[4], pts[11]) > 50) and (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                ch1 = 4

        l = [[3, 6], [3, 4]]
        pl = [ch1, ch2]
        if pl in l and pts[4][0] < pts[0][0]:
            ch1 = 4

        l = [[2, 2], [2, 5], [2, 4]]
        pl = [ch1, ch2]
        if pl in l and pts[1][0] < pts[12][0]:
            ch1 = 4

        l = [[3, 6], [3, 5], [3, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] > pts[10][1]:
                ch1 = 5

        l = [[3, 2], [3, 1], [3, 6]]
        pl = [ch1, ch2]
        if pl in l and (pts[4][1] + 17 > pts[8][1] and pts[4][1] + 17 > pts[12][1] and pts[4][1] + 17 > pts[16][1] and pts[4][1] + 17 > pts[20][1]):
            ch1 = 5

        l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
        pl = [ch1, ch2]
        if pl in l and pts[4][0] > pts[0][0]:
            ch1 = 5

        l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
        pl = [ch1, ch2]
        if pl in l and (pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]):
            ch1 = 5

        l = [[5, 7], [5, 2], [5, 6]]
        pl = [ch1, ch2]
        if pl in l and pts[3][0] < pts[0][0]:
            ch1 = 7

        l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
        pl = [ch1, ch2]
        if pl in l and pts[6][1] < pts[8][1]:
            ch1 = 7

        l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
        pl = [ch1, ch2]
        if pl in l and pts[18][1] > pts[20][1]:
            ch1 = 7

        l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
        pl = [ch1, ch2]
        if pl in l and pts[5][0] > pts[16][0]:
            ch1 = 6

        l = [[7, 2]]
        pl = [ch1, ch2]
        if pl in l and pts[18][1] < pts[20][1]:
            ch1 = 6

        l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
        pl = [ch1, ch2]
        if pl in l and self.distance(pts[8], pts[16]) > 50:
            ch1 = 6

        l = [[4, 6], [4, 2], [4, 1], [4, 4]]
        pl = [ch1, ch2]
        if pl in l and self.distance(pts[4], pts[11]) < 60:
            ch1 = 6

        l = [[1, 4], [1, 6], [1, 0], [1, 2]]
        pl = [ch1, ch2]
        if pl in l and (pts[5][0] - pts[4][0] - 15 > 0):
            ch1 = 6

        l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0], [6, 3], [6, 4], [7, 5], [7, 2]]
        pl = [ch1, ch2]
        if pl in l and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

        l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                ch1 = 1

        l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
        pl = [ch1, ch2]
        if pl in l and (pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

        l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[4][1] > pts[14][1]):
                ch1 = 1

        l = [[4, 1], [4, 2], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.distance(pts[4], pts[11]) < 50) and (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                ch1 = 1

        l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[14][1] < pts[4][1]):
                ch1 = 1

        l = [[6, 6], [6, 4], [6, 1], [6, 2]]
        pl = [ch1, ch2]
        if pl in l and (pts[5][0] - pts[4][0] - 15 < 0):
            ch1 = 1

        l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
                ch1 = 1

        l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if (pts[4][0] < pts[5][0] + 15) and (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
                ch1 = 7

        l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if ((pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] > pts[14][1]):
                ch1 = 1

        l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
        pl = [ch1, ch2]
        fg = 13
        if pl in l:
            left_cluster = (pts[0][0] + fg < pts[8][0] and pts[0][0] + fg < pts[12][0] and pts[0][0] + fg < pts[16][0] and pts[0][0] + fg < pts[20][0])
            right_cluster = (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0])
            if (not left_cluster) and (not right_cluster) and self.distance(pts[4], pts[11]) < 50:
                ch1 = 1

        l = [[5, 0], [5, 5], [0, 1]]
        pl = [ch1, ch2]
        if pl in l and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1]):
            ch1 = 1

        # Subgroup mapping
        predicted_char = "-"
        if ch1 == 0:
            predicted_char = 'S'
            if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
                predicted_char = 'A'
            if pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
                predicted_char = 'T'
            if pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
                predicted_char = 'E'
            if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
                predicted_char = 'M'
            if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
                predicted_char = 'N'

        elif ch1 == 2:
            predicted_char = 'C' if self.distance(pts[12], pts[4]) > 42 else 'O'
        elif ch1 == 3:
            predicted_char = 'G' if self.distance(pts[8], pts[12]) > 72 else 'H'
        elif ch1 == 4:
            predicted_char = 'L'
        elif ch1 == 5:
            if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
                predicted_char = 'Z' if pts[8][1] < pts[5][1] else 'Q'
            else:
                predicted_char = 'P'
        elif ch1 == 6:
            predicted_char = 'X'
        elif ch1 == 7:
            predicted_char = 'Y' if self.distance(pts[8], pts[4]) > 42 else 'J'
        elif ch1 == 1:
            if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]:
                predicted_char = 'B'
            if pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]:
                predicted_char = 'D'
            if pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]:
                predicted_char = 'F'
            if pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]:
                predicted_char = 'I'
            if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]:
                predicted_char = 'W'
            if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
                predicted_char = 'K'
            if ((self.distance(pts[8], pts[12]) - self.distance(pts[6], pts[10])) < 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                predicted_char = 'U'
            if ((self.distance(pts[8], pts[12]) - self.distance(pts[6], pts[10])) >= 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
                predicted_char = 'V'
            if (pts[8][0] > pts[12][0]) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                predicted_char = 'R'

        if predicted_char in ['B', 'E', 'S', 'X', 'Y']:
            if pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]:
                predicted_char = ' '

        if predicted_char in ['E', 'Y', 'B'] and pts[4][0] < pts[5][0]:
            predicted_char = 'next'

        if predicted_char in ['next', 'B', 'C', 'H', 'F']:
            if (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and pts[4][1] < pts[8][1] and pts[4][1] < pts[12][1] and pts[4][1] < pts[16][1] and pts[4][1] < pts[20][1]:
                predicted_char = 'Backspace'

        return predicted_char
    
    def update_text_with_character(self, character):
        """
        Update recognized text with new character using original logic
        
        Args:
            character: Recognized character or special command
        """
        if not isinstance(character, str) or character == "":
            return

        # Handle "next" gesture for character confirmation
        if character == "next" and self.prev_char != "next":
            if self.ten_prev_char[(self.count-2) % 10] != "next":
                if self.ten_prev_char[(self.count-2) % 10] == "Backspace":
                    if len(self.recognized_text) > 0:
                        self.recognized_text = self.recognized_text[:-1]
                else:
                    if self.ten_prev_char[(self.count-2) % 10] not in ["Backspace", " ", "next"]:
                        self.recognized_text += self.ten_prev_char[(self.count-2) % 10]
            else:
                if self.ten_prev_char[self.count % 10] not in ["Backspace", " ", "next"]:
                    self.recognized_text += self.ten_prev_char[self.count % 10]
        
        # Handle space
        elif character == " " and self.prev_char != " ":
            self.recognized_text += " "
        
        # Handle backspace
        elif character == "Backspace" and self.prev_char != "Backspace":
            if len(self.recognized_text) > 0:
                self.recognized_text = self.recognized_text[:-1]
        
        # Update tracking variables
        self.prev_char = character
        self.current_symbol = character
        self.count += 1
        self.ten_prev_char[self.count % 10] = character
        
        # Update word suggestions
        self.update_word_suggestions()
    
    def update_word_suggestions(self):
        """Update word suggestions based on current text"""
        if not self.dictionary:
            self.word_suggestions = [" ", " ", " ", " "]
            return
            
        try:
            if len(self.recognized_text.strip()) != 0:
                # Get current word
                last_space = self.recognized_text.rfind(" ")
                current_word = self.recognized_text[last_space + 1:]
                self.current_word = current_word
                
                if len(current_word.strip()) != 0:
                    # Get dictionary suggestions
                    suggestions = self.dictionary.suggest(current_word)
                    
                    # Fill suggestion array
                    for i in range(4):
                        if i < len(suggestions):
                            self.word_suggestions[i] = suggestions[i]
                        else:
                            self.word_suggestions[i] = " "
                else:
                    self.word_suggestions = [" ", " ", " ", " "]
            else:
                self.word_suggestions = [" ", " ", " ", " "]
                
        except Exception as e:
            logger.error(f"Error updating word suggestions: {e}")
            self.word_suggestions = [" ", " ", " ", " "]
    
    def apply_word_suggestion(self, suggestion):
        """
        Apply a word suggestion to replace the current word
        
        Args:
            suggestion: The suggested word to apply
            
        Returns:
            Updated sentence text
        """
        try:
            last_space = self.recognized_text.rfind(" ")
            if last_space >= 0:
                self.recognized_text = self.recognized_text[:last_space + 1] + suggestion.upper()
            else:
                self.recognized_text = suggestion.upper()
            
            self.update_word_suggestions()
            return self.recognized_text
            
        except Exception as e:
            logger.error(f"Error applying suggestion: {e}")
            return self.recognized_text
    
    def clear_text(self):
        """Clear all recognized text and reset state"""
        self.recognized_text = ""
        self.current_word = ""
        self.word_suggestions = [" ", " ", " ", " "]
        self.reset_recognition_state()
    
    def process_frame(self, frame):
        """
        Process a video frame for hand detection and recognition
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            tuple: (processed_frame, recognition_results)
        """
        try:
            # Detect hands in frame
            hands_result = self.hd.findHands(frame, draw=False, flipType=True)

            # cvzone return shape differs across versions:
            # - older/newer variants can return only allHands (list)
            # - some variants return (allHands, image)
            if isinstance(hands_result, tuple):
                all_hands = hands_result[0] if len(hands_result) > 0 else []
            else:
                all_hands = hands_result if isinstance(hands_result, list) else []

            frame_copy = np.array(frame)
            
            # Initialize results
            results = {
                'current_character': self.current_symbol,
                'sentence': self.recognized_text,
                'word_suggestions': self.word_suggestions,
                'confidence': 0.0,
                'hand_detected': False
            }
            
            if all_hands:  # Hand detected
                results['hand_detected'] = True
                hand_info = all_hands[0]
                x, y, w, h = hand_info['bbox']
                landmarks_full = hand_info.get('lmList', [])

                if not isinstance(landmarks_full, (list, tuple)) or len(landmarks_full) < 21:
                    return frame, results
                
                # Extract hand region with offset
                hand_region = frame_copy[
                    max(0, y - self.offset):y + h + self.offset,
                    max(0, x - self.offset):x + w + self.offset
                ]
                
                if hand_region.size > 0:
                    # Load white background for skeleton drawing
                    try:
                        white_bg_path = self.white_bg_path
                        if not os.path.exists(white_bg_path):
                            white_bg_path = os.path.join('..', self.white_bg_path)
                        
                        if os.path.exists(white_bg_path):
                            white = cv2.imread(white_bg_path)
                        else:
                            # Create white background if file not found
                            white = np.ones((400, 400, 3), dtype=np.uint8) * 255
                    except:
                        white = np.ones((400, 400, 3), dtype=np.uint8) * 255

                    # Use the primary detector's landmarks directly.
                    # Convert absolute frame coordinates into bbox-relative coordinates
                    # so the downstream skeleton logic matches the trained pipeline.
                    landmarks = []
                    for lm in landmarks_full:
                        if not isinstance(lm, (list, tuple)) or len(lm) < 2:
                            continue
                        landmarks.append([
                            max(0, int(lm[0] - x)),
                            max(0, int(lm[1] - y)),
                            lm[2] if len(lm) > 2 else 0
                        ])

                    if len(landmarks) < 21:
                        return frame, results

                    # Draw hand skeleton
                    skeleton_image = self.draw_hand_skeleton(white, landmarks, [0, 0, w, h])

                    # Predict gesture
                    predicted_char = self.predict_gesture(skeleton_image, landmarks)

                    # Update text with prediction
                    self.update_text_with_character(predicted_char)

                    # Update results
                    results.update({
                        'current_character': self.current_symbol,
                        'sentence': self.recognized_text,
                        'word_suggestions': self.word_suggestions,
                        'confidence': 0.85  # Placeholder confidence
                    })

                    # Draw bounding box and label on frame
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Detected: {self.current_symbol}",
                               (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add text overlay to frame
            if self.recognized_text:
                cv2.putText(frame, f"Text: {self.recognized_text}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            cv2.putText(frame, f"Character: {self.current_symbol}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            return frame, results
            
        except Exception as e:
            logger.exception(f"Error processing frame: {e}")
            results = {
                'current_character': 'ERROR',
                'sentence': self.recognized_text,
                'word_suggestions': self.word_suggestions,
                'confidence': 0.0,
                'hand_detected': False
            }
            return frame, results


# Example usage and testing
if __name__ == "__main__":
    # Test the recognizer
    recognizer = SignLanguageRecognizer()
    print("Sign Language Recognizer initialized successfully")
    
    # Test with dummy frame
    import cv2
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    processed_frame, results = recognizer.process_frame(test_frame)
    print(f"Test results: {results}")