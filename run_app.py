"""
Application Launcher for Sign Language Recognition System
Choose between different versions of the application
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


class ApplicationLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sign Language Recognition - Application Launcher")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="Sign Language Recognition System", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            self.root,
            text="Choose your preferred application version:",
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666666'
        )
        subtitle_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Authenticated Version Button
        auth_btn = tk.Button(
            button_frame,
            text="Launch Authenticated Version",
            command=self.launch_authenticated_app,
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        auth_btn.pack(pady=10, fill='x')
        
        # Original Version Button
        original_btn = tk.Button(
            button_frame,
            text="Launch Original Version",
            command=self.launch_original_app,
            font=("Arial", 12),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        original_btn.pack(pady=10, fill='x')
        
        # Console Version Button
        console_btn = tk.Button(
            button_frame,
            text="Launch Console Version",
            command=self.launch_console_app,
            font=("Arial", 12),
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        console_btn.pack(pady=10, fill='x')
        
        # Web Services Button
        web_btn = tk.Button(
            button_frame,
            text="Start Web Services",
            command=self.launch_web_services,
            font=("Arial", 12),
            bg='#9C27B0',
            fg='white',
            padx=20,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        web_btn.pack(pady=10, fill='x')
        
        # Info text
        info_label = tk.Label(
            self.root,
            text="Authenticated Version: Login required, user management\nOriginal Version: Direct access to recognition\nConsole Version: Command line interface\nWeb Services: Start backend and frontend services",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#888888',
            justify='left'
        )
        info_label.pack(pady=20)
        
        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 10),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5
        )
        exit_btn.pack(pady=10)
    
    def launch_authenticated_app(self):
        """Launch the authenticated version with user management"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'final_complete_auth.py')
            if os.path.exists(script_path):
                subprocess.Popen([sys.executable, script_path])
                messagebox.showinfo("Success", "Authenticated application launched!")
                self.root.quit()
            else:
                messagebox.showerror("Error", "Authenticated app script not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch authenticated app: {str(e)}")
    
    def launch_original_app(self):
        """Launch the original version without authentication"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'final_pred.py')
            if os.path.exists(script_path):
                subprocess.Popen([sys.executable, script_path])
                messagebox.showinfo("Success", "Original application launched!")
                self.root.quit()
            else:
                messagebox.showerror("Error", "Original app script not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch original app: {str(e)}")
    
    def launch_console_app(self):
        """Launch the console version without GUI"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'prediction_wo_gui.py')
            if os.path.exists(script_path):
                subprocess.Popen([sys.executable, script_path])
                messagebox.showinfo("Success", "Console application launched!")
                self.root.quit()
            else:
                messagebox.showerror("Error", "Console app script not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch console app: {str(e)}")
    
    def launch_web_services(self):
        """Start the web services (backend and frontend)"""
        try:
            web_script = os.path.join(os.path.dirname(__file__), 'web-app', 'start-all-services.bat')
            if os.path.exists(web_script):
                subprocess.Popen(web_script, shell=True)
                messagebox.showinfo("Success", "Web services are starting!\nCheck the opened windows for status.")
                self.root.quit()
            else:
                messagebox.showerror("Error", "Web services script not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start web services: {str(e)}")
    
    def run(self):
        """Start the application launcher"""
        self.root.mainloop()


if __name__ == "__main__":
    launcher = ApplicationLauncher()
    launcher.run()