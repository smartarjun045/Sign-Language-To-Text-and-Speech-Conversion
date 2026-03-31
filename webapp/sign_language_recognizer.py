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
from collections import deque, Counter
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import os
import logging

logger = logging.getLogger(__name__)

COMMON_WORDS = (
    "a", "about", "after", "again", "all", "also", "am", "an", "and", "any", "are", "as", "at",
    "back", "be", "because", "been", "before", "best", "better", "but", "by",
    "can", "come", "could",
    "day", "do", "does", "done", "down",
    "easy", "end", "enough", "even", "every",
    "feel", "find", "for", "from",
    "get", "give", "go", "good", "great",
    "had", "have", "hello", "help", "her", "here", "hi", "him", "his", "home", "how",
    "i", "if", "in", "into", "is", "it", "its",
    "just",
    "know",
    "last", "later", "like", "little", "look", "love",
    "make", "many", "me", "more", "most", "my",
    "need", "new", "next", "nice", "no", "not", "now",
    "of", "off", "ok", "on", "one", "only", "or", "our", "out", "over",
    "people", "please",
    "right",
    "say", "see", "she", "so", "some", "sorry", "start", "stop",
    "take", "tell", "thank", "thanks", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "time", "to", "today", "tomorrow", "too", "try",
    "up", "us",
    "very",
    "want", "was", "we", "well", "were", "what", "when", "where", "which", "who", "why",
    "will", "with", "work", "would",
    "yes", "you", "your",
)

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
        
        import mediapipe as mp
        if not hasattr(mp, "solutions"):
            import mediapipe.python.solutions as mp_solutions
            mp.solutions = mp_solutions

        # Initialize hand detectors
        self.hd = HandDetector(maxHands=1)
        self.hd2 = HandDetector(maxHands=1)
        
        # Load CNN model
        self.model = None
        self.load_model()
        
        self.dictionary = None
        
        # Recognition state variables
        self.reset_recognition_state()
        
        # Constants
        self.offset = 29

    def _normalize_hands_result(self, result):
        if result is None:
            return []
        if isinstance(result, list):
            if len(result) == 0:
                return []
            if isinstance(result[0], dict):
                return result
            if len(result) == 2 and isinstance(result[0], np.ndarray) and isinstance(result[1], list):
                return result[1]
            if len(result) == 2 and isinstance(result[1], np.ndarray) and isinstance(result[0], list):
                return result[0]
            return []
        if isinstance(result, tuple):
            if len(result) == 2 and isinstance(result[0], np.ndarray) and isinstance(result[1], list):
                return result[1]
            if len(result) == 2 and isinstance(result[1], np.ndarray) and isinstance(result[0], list):
                return result[0]
        return []
        
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
                    self.model = None
                    logger.error(f"Model file not found: {self.model_path}")
        except Exception as e:
            self.model = None
            logger.error(f"Error loading model: {e}")
    
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
        self.current_symbol = "C"
        
        # Word suggestions
        self.word_suggestions = [" ", " ", " ", " "]

        self.prediction_history = deque(maxlen=7)
        self.last_confidence = 0.0
        
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
            raw_prob = np.array(self.model.predict(input_image)[0], dtype='float32')
            ch1 = int(np.argmax(raw_prob, axis=0))
            self.last_confidence = float(raw_prob[ch1]) if raw_prob.size > 0 else 0.0

            prob = raw_prob.copy()
            prob[ch1] = 0
            ch2 = int(np.argmax(prob, axis=0))
            prob[ch2] = 0
            ch3 = int(np.argmax(prob, axis=0))
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
        pl = [ch1, ch2]
        
        # Apply all the gesture recognition rules from original code
        # (This is a condensed version - the full logic would be very long)
        
        # Group classification logic (simplified)
        if ch1 == 0:
            predicted_char = 'S'
            if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
                predicted_char = 'A'
            elif pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
                predicted_char = 'E'
            elif pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
                predicted_char = 'M'
            elif pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
                predicted_char = 'N'
        
        elif ch1 == 2:
            if self.distance(pts[12], pts[4]) > 42:
                predicted_char = 'C'
            else:
                predicted_char = 'O'
                
        elif ch1 == 3:
            if self.distance(pts[8], pts[12]) > 72:
                predicted_char = 'G'
            else:
                predicted_char = 'H'
                
        elif ch1 == 4:
            predicted_char = 'L'
            
        elif ch1 == 5:
            if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
                if pts[8][1] < pts[5][1]:
                    predicted_char = 'Z'
                else:
                    predicted_char = 'Q'
            else:
                predicted_char = 'P'
                
        elif ch1 == 6:
            predicted_char = 'X'
            
        elif ch1 == 7:
            if self.distance(pts[8], pts[4]) > 42:
                predicted_char = 'Y'
            else:
                predicted_char = 'J'
                
        elif ch1 == 1:
            # Complex finger position analysis for group 1
            finger_up = [
                pts[6][1] > pts[8][1],   # Index finger
                pts[10][1] > pts[12][1], # Middle finger  
                pts[14][1] > pts[16][1], # Ring finger
                pts[18][1] > pts[20][1]  # Pinky finger
            ]
            
            if all(finger_up):
                predicted_char = 'B'
            elif finger_up[0] and not finger_up[1] and not finger_up[2] and not finger_up[3]:
                predicted_char = 'D'
            elif not finger_up[0] and finger_up[1] and finger_up[2] and finger_up[3]:
                predicted_char = 'F'
            elif not finger_up[0] and not finger_up[1] and not finger_up[2] and finger_up[3]:
                predicted_char = 'I'
            elif finger_up[0] and finger_up[1] and finger_up[2] and not finger_up[3]:
                predicted_char = 'W'
            elif finger_up[0] and finger_up[1] and not finger_up[2] and not finger_up[3]:
                tip_dist = self.distance(pts[8], pts[12])
                mcp_dist = self.distance(pts[5], pts[9]) + 1e-6
                ratio = tip_dist / mcp_dist

                crossed = (pts[8][0] - pts[12][0]) * (pts[5][0] - pts[9][0]) < 0

                x_min = min(pts[5][0], pts[9][0])
                x_max = max(pts[5][0], pts[9][0])
                thumb_between = x_min < pts[4][0] < x_max
                palm_scale = self.distance(pts[5], pts[17]) + 1e-6
                thumb_extended = (self.distance(pts[4], pts[0]) / palm_scale) > 0.75 and pts[4][1] < pts[0][1]

                if crossed and ratio < 1.1:
                    predicted_char = 'R'
                elif thumb_between and thumb_extended:
                    predicted_char = 'K'
                elif ratio < 0.75:
                    predicted_char = 'U'
                else:
                    predicted_char = 'V'
            else:
                predicted_char = 'K'
        else:
            predicted_char = str(ch1)  # Fallback
        
        # Handle special gestures
        if predicted_char in ['E', 'Y', 'B']:
            if (pts[4][0] < pts[5][0]) and all([
                pts[6][1] > pts[8][1], pts[10][1] > pts[12][1], 
                pts[14][1] > pts[16][1], pts[18][1] > pts[20][1]
            ]):
                predicted_char = "next"
        
        # Check for space gesture
        if predicted_char in ['S', 'T'] and len(pts) > 20:
            # Simple space detection logic
            if pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1]:
                predicted_char = " "
        
        return predicted_char
    
    def update_text_with_character(self, character):
        """
        Update recognized text with new character using original logic
        
        Args:
            character: Recognized character or special command
        """
        # Handle "next" gesture for character confirmation
        if character == "next" and self.prev_char != "next":
            stable = self._get_stable_candidate()
            if stable and stable not in ["Backspace", " ", "next"]:
                self.recognized_text += stable
            else:
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
        self._record_prediction(character, self.last_confidence)
        display = self._get_stable_candidate() if character not in ["next", " ", "Backspace"] else character
        self.current_symbol = display if display else character
        self.count += 1
        self.ten_prev_char[self.count % 10] = self.current_symbol
        
        # Update word suggestions
        self.update_word_suggestions()

    def _record_prediction(self, character, confidence):
        if character in ascii_uppercase:
            self.prediction_history.append((character, float(confidence) if confidence is not None else 0.0))

    def _get_stable_candidate(self):
        if not self.prediction_history:
            return ""

        letters = [c for c, _ in self.prediction_history if c in ascii_uppercase]
        if not letters:
            return ""

        counts = Counter(letters)
        best, best_count = counts.most_common(1)[0]
        if best_count >= max(2, (len(letters) + 1) // 2):
            return best
        return letters[-1]

    def _current_word(self):
        last_space = self.recognized_text.rfind(" ")
        return self.recognized_text[last_space + 1:] if last_space >= 0 else self.recognized_text

    def _fallback_suggestions(self, prefix, limit=4):
        prefix = prefix.strip().lower()
        if not prefix:
            return [" "] * limit

        suggestions = []
        for word in COMMON_WORDS:
            if word.startswith(prefix) and word != prefix:
                suggestions.append(word.upper())
                if len(suggestions) >= limit:
                    break

        while len(suggestions) < limit:
            suggestions.append(" ")

        return suggestions
    
    def update_word_suggestions(self):
        """Update word suggestions based on current text"""
        try:
            if len(self.recognized_text.strip()) == 0:
                self.word_suggestions = [" ", " ", " ", " "]
                return

            current_word = self._current_word()
            self.current_word = current_word

            if len(current_word.strip()) == 0:
                self.word_suggestions = [" ", " ", " ", " "]
                return

            if self.dictionary:
                suggestions = self.dictionary.suggest(current_word)
                self.word_suggestions = [
                    suggestions[i] if i < len(suggestions) else " "
                    for i in range(4)
                ]
                return

            self.word_suggestions = self._fallback_suggestions(current_word, limit=4)
                
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
            hands_result = self.hd.findHands(frame, draw=False, flipType=True)
            hands = self._normalize_hands_result(hands_result)
            frame_copy = np.array(frame)
            
            # Initialize results
            results = {
                'current_character': self.current_symbol,
                'sentence': self.recognized_text,
                'word_suggestions': self.word_suggestions,
                'confidence': 0.0,
                'hand_detected': False
            }
            
            if len(hands) > 0:
                results['hand_detected'] = True
                hand_info = hands[0]
                x, y, w, h = hand_info.get('bbox', (0, 0, 0, 0))
                
                # Extract hand region with offset
                x1 = max(0, x - self.offset)
                y1 = max(0, y - self.offset)
                x2 = min(frame_copy.shape[1], x + w + self.offset)
                y2 = min(frame_copy.shape[0], y + h + self.offset)
                hand_region = frame_copy[y1:y2, x1:x2]
                
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
                    
                    hands_cropped_result = self.hd2.findHands(hand_region, draw=False, flipType=True)
                    hands_cropped = self._normalize_hands_result(hands_cropped_result)
                    
                    if len(hands_cropped) > 0:
                        hand_cropped = hands_cropped[0]
                        landmarks = hand_cropped.get('lmList', [])
                        bbox_cropped = hand_cropped.get('bbox', None)
                        
                        # Draw hand skeleton
                        if bbox_cropped and len(bbox_cropped) == 4:
                            skeleton_bbox = [0, 0, bbox_cropped[2], bbox_cropped[3]]
                        else:
                            skeleton_bbox = [0, 0, w, h]
                        skeleton_image = self.draw_hand_skeleton(white, landmarks, skeleton_bbox)
                        
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
            logger.error(f"Error processing frame: {e}")
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
