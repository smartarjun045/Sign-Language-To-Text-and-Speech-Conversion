# Importing Libraries
import numpy as np
import math
import cv2
import os, sys
import traceback
import pyttsx3
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import enchant
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk

# Authentication imports
from session_manager import AuthenticationController, SessionManager, UserProfileDialog

# Initialize components
ddd = enchant.Dict("en-US")
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)
offset = 29

os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"

class AuthenticatedApplication:
    def __init__(self, session_manager=None, auth_controller=None):
        # Authentication components
        self.session_manager = session_manager
        self.auth_controller = auth_controller
        self.user_info = None
        
        # Initialize video capture and model (same as original)
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.model = load_model('cnn8grps_rad1_model.h5')
        
        # Text-to-speech setup
        self.speak_engine = pyttsx3.init()
        self.speak_engine.setProperty("rate", 100)
        voices = self.speak_engine.getProperty("voices")
        if voices and len(voices) > 0:
            self.speak_engine.setProperty("voice", voices[0].id)

        # Initialize recognition variables (same as original)
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        self.space_flag = False
        self.next_flag = True
        self.prev_char = ""
        self.count = -1
        self.ten_prev_char = []
        for i in range(10):
            self.ten_prev_char.append(" ")

        for i in ascii_uppercase:
            self.ct[i] = 0
        print("Loaded model from disk")

        # Initialize GUI with authentication features
        self.setup_gui()
        
        # Initialize text variables (modified for continuous spelling)
        self.str = ""
        self.ccc = 0
        self.word = ""
        self.current_symbol = "C"
        self.photo = "Empty"
        self.word1 = " "
        self.word2 = " "
        self.word3 = " "
        self.word4 = " "

        # Start video processing
        self.video_loop()

    def setup_gui(self):
        """Setup GUI with authentication enhancements"""
        self.root = tk.Tk()
        self.root.title("Sign Language To Text Conversion - Authenticated")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("1400x750")
        self.root.configure(bg="#f8f9fa")

        # Create menu bar with authentication features
        self.create_menu_bar()
        
        # Create header with user info
        self.create_header()

        # Main video panel (same position as original)
        self.panel = tk.Label(self.root, bg="black", relief="solid", bd=2)
        self.panel.place(x=100, y=80, width=480, height=640)

        # Hand skeleton display panel
        self.panel2 = tk.Label(self.root, bg="white", relief="solid", bd=2)
        self.panel2.place(x=700, y=150, width=400, height=400)

        # Current Symbol display
        self.panel3 = tk.Label(self.root, bg="white", relief="solid", bd=1)
        self.panel3.place(x=250, y=625)

        self.T1 = tk.Label(self.root, bg="#f8f9fa")
        self.T1.place(x=100, y=620)
        self.T1.config(text="Character:", font=("Arial", 16, "bold"), fg="#2c3e50")

        # Sentence display
        self.panel5 = tk.Label(self.root, bg="white", relief="solid", bd=1, anchor="w", justify="left")
        self.panel5.place(x=250, y=670, width=900, height=30)

        self.T3 = tk.Label(self.root, bg="#f8f9fa")
        self.T3.place(x=100, y=670)
        self.T3.config(text="Sentence:", font=("Arial", 16, "bold"), fg="#2c3e50")

        # Suggestions
        self.T4 = tk.Label(self.root, bg="#f8f9fa")
        self.T4.place(x=100, y=710)
        self.T4.config(text="Suggestions:", fg="#e74c3c", font=("Arial", 14, "bold"))

        # Suggestion buttons (same as original)
        self.b1 = tk.Button(self.root, relief="solid", bd=1, bg="#ecf0f1", cursor="hand2")
        self.b1.place(x=250, y=710, width=150, height=25)

        self.b2 = tk.Button(self.root, relief="solid", bd=1, bg="#ecf0f1", cursor="hand2")
        self.b2.place(x=410, y=710, width=150, height=25)

        self.b3 = tk.Button(self.root, relief="solid", bd=1, bg="#ecf0f1", cursor="hand2")
        self.b3.place(x=570, y=710, width=150, height=25)

        self.b4 = tk.Button(self.root, relief="solid", bd=1, bg="#ecf0f1", cursor="hand2")
        self.b4.place(x=730, y=710, width=150, height=25)

        # Control buttons
        self.speak = tk.Button(self.root, relief="solid", bd=1, cursor="hand2")
        self.speak.place(x=1200, y=670, width=80, height=30)
        self.speak.config(text="Speak", font=("Arial", 12, "bold"), bg="#3498db", fg="white", command=self.speak_fun)

        self.clear = tk.Button(self.root, relief="solid", bd=1, cursor="hand2")
        self.clear.place(x=1290, y=670, width=80, height=30)
        self.clear.config(text="Clear", font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", command=self.clear_fun)

        # Info panel
        self.create_info_panel()

    def create_menu_bar(self):
        """Create menu bar with user options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # User menu
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="User", menu=user_menu)
        user_menu.add_command(label="Profile", command=self.show_user_profile)
        user_menu.add_separator()
        user_menu.add_command(label="Logout", command=self.logout)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

    def create_header(self):
        """Create header with title and user info"""
        header_frame = tk.Frame(self.root, bg="#34495e", height=60)
        header_frame.place(x=0, y=0, width=1400, height=60)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Sign Language To Text & Speech Conversion",
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg="white"
        )
        title_label.place(x=20, y=15)

        # User info
        if self.session_manager and self.session_manager.get_current_user():
            username = self.session_manager.get_current_user()
            user_label = tk.Label(
                header_frame,
                text=f"Welcome, {username}",
                font=("Arial", 12),
                bg="#34495e",
                fg="#ecf0f1"
            )
            user_label.place(x=1200, y=20)

    def create_info_panel(self):
        """Create information panel"""
        info_frame = tk.Frame(self.root, bg="white", relief="solid", bd=2)
        info_frame.place(x=1120, y=150, width=250, height=400)
        
        tk.Label(
            info_frame,
            text="Hand Detection Status",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        self.info_text = tk.Text(
            info_frame,
            font=("Arial", 9),
            bg="#f8f9fa",
            fg="#2c3e50",
            height=20,
            width=30,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.info_text.pack(padx=10, pady=5, fill="both", expand=True)

    def update_info_text(self, message):
        """Update the info panel text"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, message)
        self.info_text.config(state=tk.DISABLED)

    def set_user_info(self, user_info):
        """Set user information from authentication"""
        self.user_info = user_info
        print(f"User info loaded for: {user_info.get('username', 'Unknown')}")

    # Authentication helper methods
    def show_user_profile(self):
        """Show user profile dialog"""
        if self.session_manager:
            current_user = self.session_manager.get_current_user()
            messagebox.showinfo("User Profile", f"Logged in as: {current_user}")
        
    def logout(self):
        """Logout user and return to authentication"""
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            if self.session_manager:
                self.session_manager.logout()
            self.destructor()
    
    def show_help(self):
        """Show help information"""
        help_text = """
        How to Use Sign Language Recognition:
        
        1. Position your hand in front of the camera
        2. Make ASL fingerspelling gestures
        3. The system will recognize and display letters
        4. Use suggestion buttons for word completion
        5. Use Speak button for text-to-speech
        6. Use Clear button to reset text
        
        Supported Gestures: A-Z American Sign Language
        """
        messagebox.showinfo("How to Use", help_text)
    
    def show_about(self):
        """Show about information"""
        about_text = """
        Sign Language To Text & Speech Conversion
        
        Version: 2.0 (Authenticated)
        
        This application uses computer vision and machine learning
        to recognize American Sign Language fingerspelling and
        convert it to text and speech.
        
        Features:
        - Real-time hand tracking
        - CNN-based gesture recognition
        - Word suggestions and autocomplete
        - Text-to-speech synthesis
        - User authentication and sessions
        """
        messagebox.showinfo("About", about_text)

    # === COMPLETE ORIGINAL VIDEO PROCESSING AND PREDICTION CODE ===
    
    def video_loop(self):
        """Original video loop from final_pred.py - EXACT COPY"""
        try:
            # Update session activity
            if self.session_manager:
                self.session_manager.update_activity()
                
            ok, frame = self.vs.read()
            cv2image = cv2.flip(frame, 1)
            if cv2image is not None:
                hands = hd.findHands(cv2image, draw=False, flipType=True)
                cv2image_copy = np.array(cv2image)
                cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
                self.current_image = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=self.current_image)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)

                if hands[0]:
                    hand = hands[0]
                    map = hand[0]
                    x, y, w, h = map['bbox']
                    image = cv2image_copy[y - offset:y + h + offset, x - offset:x + w + offset]

                    white = cv2.imread("white.jpg")
                    if image.size > 0:
                        handz = hd2.findHands(image, draw=False, flipType=True)
                        self.ccc += 1
                        if handz[0]:
                            hand = handz[0]
                            handmap = hand[0]
                            self.pts = handmap['lmList']

                            os = ((400 - w) // 2) - 15
                            os1 = ((400 - h) // 2) - 15
                            
                            # Draw hand skeleton (exact same as original)
                            for t in range(0, 4, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(5, 8, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(9, 12, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(13, 16, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(17, 20, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (self.pts[5][0] + os, self.pts[5][1] + os1), (self.pts[9][0] + os, self.pts[9][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (self.pts[9][0] + os, self.pts[9][1] + os1), (self.pts[13][0] + os, self.pts[13][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (self.pts[13][0] + os, self.pts[13][1] + os1), (self.pts[17][0] + os, self.pts[17][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1), (self.pts[5][0] + os, self.pts[5][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1), (self.pts[17][0] + os, self.pts[17][1] + os1), (0, 255, 0), 3)

                            for i in range(21):
                                cv2.circle(white, (self.pts[i][0] + os, self.pts[i][1] + os1), 2, (0, 0, 255), 1)

                            res = white
                            print(f"DEBUG: Calling predict function with image shape: {res.shape}")
                            self.predict(res)
                            print(f"DEBUG: Prediction completed. Current symbol: {self.current_symbol}, Sentence: '{self.str.strip()}'")

                            self.current_image2 = Image.fromarray(res)
                            imgtk = ImageTk.PhotoImage(image=self.current_image2)
                            self.panel2.imgtk = imgtk
                            self.panel2.config(image=imgtk)

                            self.panel3.config(text=self.current_symbol, font=("Arial", 16, "bold"))

                            # Update suggestion buttons
                            self.b1.config(text=self.word1, font=("Arial", 10), wraplength=140, command=self.action1)
                            self.b2.config(text=self.word2, font=("Arial", 10), wraplength=140, command=self.action2)
                            self.b3.config(text=self.word3, font=("Arial", 10), wraplength=140, command=self.action3)
                            self.b4.config(text=self.word4, font=("Arial", 10), wraplength=140, command=self.action4)
                            
                            # Update info panel
                            detection_info = f"Hand detected!\n\nCharacter: {self.current_symbol}\n\nSentence: {self.str.strip()}\n\nWord: {self.word.strip()}"
                            self.update_info_text(detection_info)
                else:
                    self.update_info_text("No hand detected.\\nPosition your hand in camera view.")

                self.panel5.config(text=self.str, font=("Arial", 14))
        except Exception as e:
            print(f"Error in video loop: {e}")
            traceback.print_exc()
        finally:
            self.root.after(1, self.video_loop)

    def distance(self, x, y):
        """Calculate distance between two points - EXACT FROM ORIGINAL"""
        return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

    def action1(self):
        """Word suggestion action 1 - EXACT FROM ORIGINAL"""
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word1.upper()

    def action2(self):
        """Word suggestion action 2 - EXACT FROM ORIGINAL"""
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word2.upper()

    def action3(self):
        """Word suggestion action 3 - EXACT FROM ORIGINAL"""
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word3.upper()

    def action4(self):
        """Word suggestion action 4 - EXACT FROM ORIGINAL"""
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word4.upper()

    def speak_fun(self):
        """Text-to-speech function with improved reliability and threading"""
        import threading
        
        def speak_thread():
            try:
                # Check if there's text to speak
                text_to_speak = self.str.strip()
                if not text_to_speak:
                    print("No text to speak")
                    return
                
                print(f"Speaking: '{text_to_speak}'")
                
                # Disable speak button during speech
                self.speak.config(state='disabled', text='Speaking...')
                
                # Stop any ongoing speech
                try:
                    self.speak_engine.stop()
                except:
                    pass
                
                # Clear the speech queue and speak
                self.speak_engine.say(text_to_speak)
                self.speak_engine.runAndWait()
                
                print("Speech completed")
                
            except Exception as e:
                print(f"Speech error: {e}")
                # Try to reinitialize the speech engine
                try:
                    self.speak_engine = pyttsx3.init()
                    self.speak_engine.setProperty("rate", 100)
                    voices = self.speak_engine.getProperty("voices")
                    if voices and hasattr(voices, '__len__') and len(voices) > 0:
                        self.speak_engine.setProperty("voice", voices[0].id)
                    # Try speaking again
                    self.speak_engine.say(text_to_speak)
                    self.speak_engine.runAndWait()
                    print("Speech completed after reinit")
                except Exception as e2:
                    print(f"Failed to reinitialize speech engine: {e2}")
            finally:
                # Re-enable speak button
                try:
                    self.speak.config(state='normal', text='Speak')
                except:
                    pass
        
        # Run speech in separate thread to prevent UI freezing
        speech_thread = threading.Thread(target=speak_thread, daemon=True)
        speech_thread.start()

    def clear_fun(self):
        """Clear function - Modified for continuous spelling"""
        self.str = ""
        self.word1 = " "
        self.word2 = " "
        self.word3 = " "
        self.word4 = " "

    def predict(self, test_image):
        """Complete prediction method from original final_pred.py - EXACT COPY"""
        white = test_image
        white = white.reshape(1, 400, 400, 3)
        prob = np.array(self.model.predict(white)[0], dtype='float32')
        ch1 = np.argmax(prob, axis=0)
        prob[ch1] = 0
        ch2 = np.argmax(prob, axis=0)
        prob[ch2] = 0
        ch3 = np.argmax(prob, axis=0)
        prob[ch3] = 0

        pl = [ch1, ch2]

        # Complete prediction logic from original - copied exactly
        # condition for [Aemnst]
        l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5], [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6], [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
        if pl in l:
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 0

        # condition for [o][s]
        l = [[2, 2], [2, 1]]
        if pl in l:
            if (self.pts[5][0] < self.pts[4][0]):
                ch1 = 0
                print("+++++++++++++++++++")

        # condition for [c0][aemnst]
        l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[0][0] > self.pts[8][0] and self.pts[0][0] > self.pts[4][0] and self.pts[0][0] > self.pts[12][0] and self.pts[0][0] > self.pts[16][0] and self.pts[0][0] > self.pts[20][0]) and self.pts[5][0] > self.pts[4][0]:
                ch1 = 2

        # condition for [c0][aemnst]
        l = [[6, 0], [6, 6], [6, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[8], self.pts[16]) < 52:
                ch1 = 2

        # All remaining prediction logic follows - implemented exactly as original
        # condition for [gh][bdfikruvw]
        l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[6][1] > self.pts[8][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1] and self.pts[0][0] < self.pts[8][0] and self.pts[0][0] < self.pts[12][0] and self.pts[0][0] < self.pts[16][0] and self.pts[0][0] < self.pts[20][0]:
                ch1 = 3

        # con for [gh][l]
        l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[4][0] > self.pts[0][0]:
                ch1 = 3

        # con for [gh][pqz]
        l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[2][1] + 15 < self.pts[16][1]:
                ch1 = 3

        # con for [l][x]
        l = [[6, 4], [6, 1], [6, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[4], self.pts[11]) > 55:
                ch1 = 4

        # con for [l][d]
        l = [[1, 4], [1, 6], [1, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.distance(self.pts[4], self.pts[11]) > 50) and (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 4

        # con for [l][gh]
        l = [[3, 6], [3, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[4][0] < self.pts[0][0]):
                ch1 = 4

        # con for [l][c0]
        l = [[2, 2], [2, 5], [2, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[1][0] < self.pts[12][0]):
                ch1 = 4

        # con for [gh][z]
        l = [[3, 6], [3, 5], [3, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and self.pts[4][1] > self.pts[10][1]:
                ch1 = 5

        # con for [gh][pq]
        l = [[3, 2], [3, 1], [3, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[4][1] + 17 > self.pts[8][1] and self.pts[4][1] + 17 > self.pts[12][1] and self.pts[4][1] + 17 > self.pts[16][1] and self.pts[4][1] + 17 > self.pts[20][1]:
                ch1 = 5

        # con for [l][pqz]
        l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[4][0] > self.pts[0][0]:
                ch1 = 5

        # con for [pqz][aemnst]
        l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[0][0] < self.pts[8][0] and self.pts[0][0] < self.pts[12][0] and self.pts[0][0] < self.pts[16][0] and self.pts[0][0] < self.pts[20][0]:
                ch1 = 5

        # con for [pqz][yj]
        l = [[5, 7], [5, 2], [5, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[3][0] < self.pts[0][0]:
                ch1 = 7

        # con for [l][yj]
        l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[6][1] < self.pts[8][1]:
                ch1 = 7

        # con for [x][yj]
        l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[18][1] > self.pts[20][1]:
                ch1 = 7

        # condition for [x][aemnst]
        l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[5][0] > self.pts[16][0]:
                ch1 = 6

        # condition for [yj][x]
        l = [[7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[18][1] < self.pts[20][1] and self.pts[8][1] < self.pts[10][1]:
                ch1 = 6

        # condition for [c0][x]
        l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[8], self.pts[16]) > 50:
                ch1 = 6

        # con for [l][x]
        l = [[4, 6], [4, 2], [4, 1], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[4], self.pts[11]) < 60:
                ch1 = 6

        # con for [x][d]
        l = [[1, 4], [1, 6], [1, 0], [1, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[5][0] - self.pts[4][0] - 15 > 0:
                ch1 = 6

        # con for [b][pqz]
        l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0], [6, 3], [6, 4], [7, 5], [7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 1

        # con for [f][pqz]
        l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 1

        l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 1

        # con for [d][pqz]
        l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and (self.pts[2][0] < self.pts[0][0]) and self.pts[4][1] > self.pts[14][1]):
                ch1 = 1

        l = [[4, 1], [4, 2], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.distance(self.pts[4], self.pts[11]) < 50) and (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 1

        l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and (self.pts[2][0] < self.pts[0][0]) and self.pts[14][1] < self.pts[4][1]):
                ch1 = 1

        l = [[6, 6], [6, 4], [6, 1], [6, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[5][0] - self.pts[4][0] - 15 < 0:
                ch1 = 1

        # con for [i][pqz]
        l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] > self.pts[20][1])):
                ch1 = 1

        # con for [yj][bfdi]
        l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[4][0] < self.pts[5][0] + 15) and ((self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] > self.pts[20][1])):
                ch1 = 7

        # con for [uvr]
        l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1])) and self.pts[4][1] > self.pts[14][1]:
                ch1 = 1

        # con for [w]
        fg = 13
        l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if not (self.pts[0][0] + fg < self.pts[8][0] and self.pts[0][0] + fg < self.pts[12][0] and self.pts[0][0] + fg < self.pts[16][0] and self.pts[0][0] + fg < self.pts[20][0]) and not (self.pts[0][0] > self.pts[8][0] and self.pts[0][0] > self.pts[12][0] and self.pts[0][0] > self.pts[16][0] and self.pts[0][0] > self.pts[20][0]) and self.distance(self.pts[4], self.pts[11]) < 50:
                ch1 = 1

        l = [[5, 0], [5, 5], [0, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1]:
                ch1 = 1
        # Final character assignment
        if ch1 == 0:
            ch1 = 'S'
            if self.pts[4][0] < self.pts[6][0] and self.pts[4][0] < self.pts[10][0] and self.pts[4][0] < self.pts[14][0] and self.pts[4][0] < self.pts[18][0]:
                ch1 = 'A'
            if self.pts[4][0] > self.pts[6][0] and self.pts[4][0] < self.pts[10][0] and self.pts[4][0] < self.pts[14][0] and self.pts[4][0] < self.pts[18][0] and self.pts[4][1] < self.pts[14][1] and self.pts[4][1] < self.pts[18][1]:
                ch1 = 'T'
            if self.pts[4][1] > self.pts[8][1] and self.pts[4][1] > self.pts[12][1] and self.pts[4][1] > self.pts[16][1] and self.pts[4][1] > self.pts[20][1]:
                ch1 = 'E'
            if self.pts[4][0] > self.pts[6][0] and self.pts[4][0] > self.pts[10][0] and self.pts[4][0] > self.pts[14][0] and self.pts[4][1] < self.pts[18][1]:
                ch1 = 'M'
            if self.pts[4][0] > self.pts[6][0] and self.pts[4][0] > self.pts[10][0] and self.pts[4][1] < self.pts[18][1] and self.pts[4][1] < self.pts[14][1]:
                ch1 = 'N'

        if ch1 == 2:
            if self.distance(self.pts[12], self.pts[4]) > 42:
                ch1 = 'C'
            else:
                ch1 = 'O'

        if ch1 == 3:
            if (self.distance(self.pts[8], self.pts[12])) > 72:
                ch1 = 'G'
            else:
                ch1 = 'H'

        if ch1 == 7:
            if self.distance(self.pts[8], self.pts[4]) > 42:
                ch1 = 'Y'
            else:
                ch1 = 'J'

        if ch1 == 4:
            ch1 = 'L'

        if ch1 == 6:
            ch1 = 'X'

        if ch1 == 5:
            if self.pts[4][0] > self.pts[12][0] and self.pts[4][0] > self.pts[16][0] and self.pts[4][0] > self.pts[20][0]:
                if self.pts[8][1] < self.pts[5][1]:
                    ch1 = 'Z'
                else:
                    ch1 = 'Q'
            else:
                ch1 = 'P'

        if ch1 == 1:
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 'B'
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 'D'
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 'F'
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 'I'
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 'W'
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and self.pts[4][1] < self.pts[9][1]:
                ch1 = 'K'
            if ((self.distance(self.pts[8], self.pts[12]) - self.distance(self.pts[6], self.pts[10])) < 8) and (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 'U'
            if ((self.distance(self.pts[8], self.pts[12]) - self.distance(self.pts[6], self.pts[10])) >= 8) and (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and (self.pts[4][1] > self.pts[9][1]):
                ch1 = 'V'
            if (self.pts[8][0] > self.pts[12][0]) and (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 'R'

        # Handle special gesture recognition
        if ch1 == 1 or ch1 =='E' or ch1 =='S' or ch1 =='X' or ch1 =='Y' or ch1 =='B':
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1=" "

        # Handle 'next' gesture for character confirmation
        if ch1 == 'E' or ch1=='Y' or ch1=='B':
            if (self.pts[4][0] < self.pts[5][0]) and (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1="next"

        # Character accumulation logic - Fixed to spell words without spaces
        if ch1=="next" and self.prev_char!="next":
            if self.ten_prev_char[(self.count-2)%10]!="next":
                if self.ten_prev_char[(self.count-2)%10]=="Backspace":
                    if len(self.str) > 1:
                        self.str=self.str[0:-1]
                else:
                    if self.ten_prev_char[(self.count - 2) % 10] not in ["Backspace", " ", "next"]:
                        # Add character directly without space for continuous word spelling
                        self.str = self.str.rstrip() + self.ten_prev_char[(self.count-2)%10]
            else:
                if self.ten_prev_char[(self.count - 0) % 10] not in ["Backspace", " ", "next"]:
                    # Add character directly without space for continuous word spelling
                    self.str = self.str.rstrip() + self.ten_prev_char[(self.count - 0) % 10]

        # Handle backspace 
        if ch1=="Backspace" and self.prev_char!="Backspace":
            if len(self.str) > 0:
                self.str = self.str[0:-1]

        # Handle space - Modified to add spaces between words
        if ch1==" " and self.prev_char!=" ":
            self.str = self.str + " "
        
        # Add space for specific gestures to separate words
        if ch1 in ["S", "T"] and self.prev_char not in ["S", "T", " "]:
            if len(self.str) > 0 and not self.str.endswith(" "):
                self.str = self.str + " "

        # Update tracking variables
        self.prev_char=ch1
        self.current_symbol=ch1
        self.count += 1
        self.ten_prev_char[self.count%10]=ch1

        # Debug output with more details
        print(f"PREDICT DEBUG: Detected: {ch1}, Prev: {self.prev_char}, Sentence: '{self.str}', Count: {self.count}")
        print(f"PREDICT DEBUG: ten_prev_char: {self.ten_prev_char}")
        
        # Word suggestion logic with debugging
        if len(self.str.strip())!=0:
            st=self.str.rfind(" ")
            ed=len(self.str)
            word=self.str[st+1:ed]
            self.word=word
            print(f"WORD DEBUG: Current word: '{word}', str: '{self.str}'")
            if len(word.strip())!=0:
                ddd.check(word)
                lenn = len(ddd.suggest(word))
                print(f"WORD DEBUG: Dictionary suggestions count: {lenn}")
                if lenn >= 4:
                    self.word4 = ddd.suggest(word)[3]
                if lenn >= 3:
                    self.word3 = ddd.suggest(word)[2]
                if lenn >= 2:
                    self.word2 = ddd.suggest(word)[1]
                if lenn >= 1:
                    self.word1 = ddd.suggest(word)[0]
                print(f"WORD DEBUG: Suggestions: [{self.word1}] [{self.word2}] [{self.word3}] [{self.word4}]")
            else:
                self.word1 = " "
                self.word2 = " "
                self.word3 = " "
                self.word4 = " "
                print("WORD DEBUG: No word to suggest for, cleared suggestions")
        else:
            print("WORD DEBUG: Empty sentence, no word suggestions")

    def destructor(self):
        """Destructor method - EXACT FROM ORIGINAL"""
        print(self.ten_prev_char)
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()


# Authentication entry point
def start_authenticated_application():
    """Start the authenticated application"""
    try:
        # Initialize authentication components
        session_manager = SessionManager()
        auth_controller = AuthenticationController(session_manager)
        
        # Define callback for successful authentication
        def on_auth_success(username):
            print(f"Authentication successful for user: {username}")
            # Start the main authenticated application
            app = AuthenticatedApplication(session_manager, auth_controller)
            app.set_user_info({'username': username})
            app.root.mainloop()
        
        # Show authentication GUI
        from auth_gui import AuthenticationGUI
        auth_gui = AuthenticationGUI(on_auth_success)
        auth_gui.root.mainloop()
            
    except Exception as e:
        print(f"Error starting authenticated application: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting Authenticated Sign Language Application...")
    start_authenticated_application()