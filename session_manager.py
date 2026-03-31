"""
Session Manager and Authentication Controller for Sign Language Application
Handles user sessions, authentication flow, and integration with main app
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os
from user_database import UserDatabase
from auth_gui import AuthenticationGUI

class SessionManager:
    def __init__(self):
        self.current_user = None
        self.login_time = None
        self.session_file = "current_session.json"
        self.session_timeout = 24  # hours
        
    def start_session(self, username):
        """Start a new user session"""
        self.current_user = username
        self.login_time = datetime.now()
        
        session_data = {
            'username': username,
            'login_time': self.login_time.isoformat(),
            'last_activity': self.login_time.isoformat()
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def update_activity(self):
        """Update last activity time"""
        if self.current_user:
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                session_data['last_activity'] = datetime.now().isoformat()
                
                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f)
            except Exception as e:
                print(f"Error updating activity: {e}")
    
    def load_session(self):
        """Load existing session if valid"""
        if not os.path.exists(self.session_file):
            return False
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            login_time = datetime.fromisoformat(session_data['login_time'])
            last_activity = datetime.fromisoformat(session_data['last_activity'])
            
            # Check if session has expired
            if datetime.now() - last_activity > timedelta(hours=self.session_timeout):
                self.end_session()
                return False
            
            self.current_user = session_data['username']
            self.login_time = login_time
            return True
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def end_session(self):
        """End current session"""
        self.current_user = None
        self.login_time = None
        
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except Exception as e:
                print(f"Error removing session file: {e}")
    
    def is_logged_in(self):
        """Check if user is currently logged in"""
        return self.current_user is not None
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user
    
    def get_session_duration(self):
        """Get current session duration"""
        if self.login_time:
            return datetime.now() - self.login_time
        return None


class AuthenticationController:
    def __init__(self, main_app_class):
        self.main_app_class = main_app_class
        self.session_manager = SessionManager()
        self.db = UserDatabase()
        self.main_app_instance = None
        
    def start_authentication_flow(self):
        """Start the authentication process"""
        # Check for existing valid session
        if self.session_manager.load_session():
            username = self.session_manager.get_current_user()
            print(f"Found valid session for user: {username}")
            self.start_main_application(username)
            return
        
        # Show authentication GUI
        auth_gui = AuthenticationGUI(self.on_login_success)
        auth_gui.run()
    
    def on_login_success(self, username):
        """Called when user successfully logs in"""
        print(f"Login successful for user: {username}")
        
        # Start session
        self.session_manager.start_session(username)
        
        # Start main application
        self.start_main_application(username)
    
    def start_main_application(self, username):
        """Start the main Sign Language application"""
        try:
            # Create and start the main application
            self.main_app_instance = self.main_app_class(
                session_manager=self.session_manager,
                auth_controller=self
            )
            
            # Add user info to the main app
            user_info = self.db.get_user_info(username)
            if user_info:
                self.main_app_instance.set_user_info(user_info)
            
            # Start the main application loop
            self.main_app_instance.root.mainloop()
            
        except Exception as e:
            print(f"Error starting main application: {e}")
            messagebox.showerror("Error", f"Failed to start main application: {e}")
    
    def logout(self):
        """Logout current user and restart authentication"""
        if self.main_app_instance:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Logout", 
                "Are you sure you want to logout?"
            )
            
            if result:
                try:
                    # End session
                    self.session_manager.end_session()
                    
                    # Close main application
                    if self.main_app_instance.root:
                        self.main_app_instance.root.destroy()
                    
                    # Reset main app instance
                    self.main_app_instance = None
                    
                    # Restart authentication flow
                    print("Restarting authentication flow...")
                    self.start_authentication_flow()
                    
                except Exception as e:
                    print(f"Error during logout: {e}")
                    messagebox.showerror("Error", f"Logout failed: {e}")
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.session_manager.get_current_user()
    
    def get_user_info(self, username=None):
        """Get user information"""
        if username is None:
            username = self.session_manager.get_current_user()
        
        if username:
            return self.db.get_user_info(username)
        return None


class UserProfileDialog:
    def __init__(self, parent, auth_controller):
        self.parent = parent
        self.auth_controller = auth_controller
        self.dialog = None
        
    def show_profile(self):
        """Show user profile dialog"""
        user_info = self.auth_controller.get_user_info()
        if not user_info:
            messagebox.showerror("Error", "No user information available")
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("User Profile")
        self.dialog.geometry("400x500")
        self.dialog.configure(bg="#f0f0f0")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.center_dialog()
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Profile content
        self.create_profile_content(user_info)
    
    def center_dialog(self):
        """Center the dialog on parent window"""
        if self.dialog is None:
            return
            
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def create_profile_content(self, user_info):
        """Create profile dialog content"""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="User Profile",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(20, 30))
        
        # Profile frame
        profile_frame = tk.Frame(self.dialog, bg="#ffffff", relief="raised", bd=2)
        profile_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        content_frame = tk.Frame(profile_frame, bg="#ffffff")
        content_frame.pack(padx=30, pady=30, fill="both", expand=True)
        
        # User information
        info_items = [
            ("Full Name:", user_info.get('full_name', 'Not provided')),
            ("Username:", user_info.get('username', '')),
            ("Email:", user_info.get('email', '')),
            ("Member Since:", self.format_date(user_info.get('created_at', ''))),
            ("Last Login:", self.format_date(user_info.get('last_login', ''))),
            ("Login Count:", str(user_info.get('login_count', 0)))
        ]
        
        for label, value in info_items:
            row_frame = tk.Frame(content_frame, bg="#ffffff")
            row_frame.pack(fill="x", pady=8)
            
            tk.Label(
                row_frame,
                text=label,
                font=("Arial", 11, "bold"),
                bg="#ffffff",
                fg="#2c3e50",
                width=15,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                row_frame,
                text=value,
                font=("Arial", 11),
                bg="#ffffff",
                fg="#34495e",
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
        
        # Session info
        session_duration = self.auth_controller.session_manager.get_session_duration()
        if session_duration:
            hours = int(session_duration.total_seconds() // 3600)
            minutes = int((session_duration.total_seconds() % 3600) // 60)
            session_text = f"{hours}h {minutes}m"
            
            row_frame = tk.Frame(content_frame, bg="#ffffff")
            row_frame.pack(fill="x", pady=8)
            
            tk.Label(
                row_frame,
                text="Session Time:",
                font=("Arial", 11, "bold"),
                bg="#ffffff",
                fg="#2c3e50",
                width=15,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                row_frame,
                text=session_text,
                font=("Arial", 11),
                bg="#ffffff",
                fg="#34495e",
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(pady=(30, 0))
        
        # Change Password button
        change_pass_btn = tk.Button(
            button_frame,
            text="Change Password",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            width=15,
            command=self.show_change_password,
            cursor="hand2"
        )
        change_pass_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            width=15,
            command=lambda: self.dialog.destroy() if self.dialog else None,
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=5)
    
    def format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return "Never"
        
        try:
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.strftime("%Y-%m-%d %H:%M")
        except:
            return date_string
    
    def show_change_password(self):
        """Show change password dialog"""
        if self.dialog is None:
            return
            
        pass_dialog = tk.Toplevel(self.dialog)
        pass_dialog.title("Change Password")
        pass_dialog.geometry("300x250")
        pass_dialog.configure(bg="#f0f0f0")
        pass_dialog.resizable(False, False)
        
        # Make modal
        pass_dialog.transient(self.dialog)
        pass_dialog.grab_set()
        
        # Center on profile dialog
        x = self.dialog.winfo_rootx() + 50
        y = self.dialog.winfo_rooty() + 50
        pass_dialog.geometry(f"300x250+{x}+{y}")
        
        # Form
        form_frame = tk.Frame(pass_dialog, bg="#ffffff", relief="raised", bd=2)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        content_frame = tk.Frame(form_frame, bg="#ffffff")
        content_frame.pack(padx=20, pady=20)
        
        # Current password
        tk.Label(content_frame, text="Current Password:", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
        current_pass = tk.Entry(content_frame, font=("Arial", 10), width=25, show="*")
        current_pass.pack(pady=(5, 15))
        
        # New password
        tk.Label(content_frame, text="New Password:", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
        new_pass = tk.Entry(content_frame, font=("Arial", 10), width=25, show="*")
        new_pass.pack(pady=(5, 15))
        
        # Confirm new password
        tk.Label(content_frame, text="Confirm New Password:", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w")
        confirm_pass = tk.Entry(content_frame, font=("Arial", 10), width=25, show="*")
        confirm_pass.pack(pady=(5, 20))
        
        def change_password():
            current = current_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            
            if not all([current, new, confirm]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords don't match")
                return
            
            username = self.auth_controller.get_current_user()
            success, message = self.auth_controller.db.update_user_password(username, current, new)
            
            if success:
                messagebox.showinfo("Success", "Password changed successfully")
                pass_dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack()
        
        tk.Button(
            button_frame,
            text="Change",
            font=("Arial", 10),
            bg="#2ecc71",
            fg="white",
            width=10,
            command=change_password
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            width=10,
            command=pass_dialog.destroy
        ).pack(side="right", padx=5)
        
        current_pass.focus()


# Testing
if __name__ == "__main__":
    # Mock main application class for testing
    class MockMainApp:
        def __init__(self, session_manager=None, auth_controller=None):
            self.session_manager = session_manager
            self.auth_controller = auth_controller
            self.root = tk.Tk()
            self.root.title("Mock Main App")
            self.root.geometry("400x300")
            
            tk.Label(self.root, text="Main Application Running", font=("Arial", 16)).pack(pady=50)
            
            if auth_controller:
                logout_btn = tk.Button(
                    self.root,
                    text="Logout",
                    command=auth_controller.logout
                )
                logout_btn.pack(pady=10)
        
        def set_user_info(self, user_info):
            print(f"User info set: {user_info}")
    
    # Test the authentication flow
    auth_controller = AuthenticationController(MockMainApp)
    auth_controller.start_authentication_flow()