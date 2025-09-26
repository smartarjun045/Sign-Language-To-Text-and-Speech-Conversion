"""
Authentication GUI Components for Sign Language Application
Includes Login and Registration Pages
"""

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
from user_database import UserDatabase

class AuthenticationGUI:
    def __init__(self, on_login_success_callback=None):
        self.root = tk.Tk()
        self.root.title("Sign Language Authentication")
        self.root.geometry("850x750")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)  # Allow resizing to help with layout
        
        # Set minimum window size
        self.root.minsize(800, 700)
        
        # Center the window
        self.center_window()
        
        # Initialize database
        self.db = UserDatabase()
        
        # Callback function when login is successful
        self.on_login_success = on_login_success_callback
        
        # Current user session
        self.current_user = None
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Show welcome screen initially
        self.show_welcome_screen()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Show welcome screen with login/register options"""
        self.clear_frame()
        
        # Title
        title_label = tk.Label(
            self.main_frame, 
            text="Sign Language To Text & Speech",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(50, 10))
        
        subtitle_label = tk.Label(
            self.main_frame,
            text="Authentication System",
            font=("Arial", 16),
            bg="#f0f0f0",
            fg="#34495e"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Welcome message
        welcome_text = tk.Label(
            self.main_frame,
            text="Welcome! Please login or create a new account to access\nthe Sign Language Recognition System",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#2c3e50",
            justify="center"
        )
        welcome_text.pack(pady=(0, 40))
        
        # Button frame
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        # Login button
        login_btn = tk.Button(
            button_frame,
            text="Login",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2,
            command=self.show_login_screen,
            cursor="hand2"
        )
        login_btn.pack(side="left", padx=10)
        
        # Register button
        register_btn = tk.Button(
            button_frame,
            text="Register",
            font=("Arial", 14, "bold"),
            bg="#2ecc71",
            fg="white",
            width=15,
            height=2,
            command=self.show_register_screen,
            cursor="hand2"
        )
        register_btn.pack(side="right", padx=10)
        
        # Footer
        footer_label = tk.Label(
            self.main_frame,
            text="© 2024 Sign Language Recognition System",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        footer_label.pack(side="bottom", pady=20)
    
    def show_login_screen(self):
        """Show login form with improved layout"""
        self.clear_frame()
        
        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="← Back",
            font=("Arial", 10),
            bg="#ecf0f1",
            command=self.show_welcome_screen,
            cursor="hand2"
        )
        back_btn.pack(anchor="nw", pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="Login to Your Account",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(30, 40))
        
        # Login form frame with better sizing
        form_frame = tk.Frame(self.main_frame, bg="#ffffff", relief="raised", bd=2)
        form_frame.pack(pady=20, padx=100, fill="both", expand=True)
        
        # Form content with proper spacing
        content_frame = tk.Frame(form_frame, bg="#ffffff")
        content_frame.pack(padx=40, pady=40, fill="both", expand=True)
        
        # Username field with better spacing
        username_label = tk.Label(content_frame, text="Username:", font=("Arial", 14, "bold"), bg="#ffffff", fg="#2c3e50")
        username_label.pack(anchor="w", pady=(0, 8))
        
        self.login_username = tk.Entry(
            content_frame, 
            font=("Arial", 14), 
            width=25, 
            relief="solid", 
            bd=2,
            bg="#f8f9fa"
        )
        self.login_username.pack(pady=(0, 25), ipady=10, fill="x")
        
        # Password field with better spacing
        password_label = tk.Label(content_frame, text="Password:", font=("Arial", 14, "bold"), bg="#ffffff", fg="#2c3e50")
        password_label.pack(anchor="w", pady=(0, 8))
        
        self.login_password = tk.Entry(
            content_frame, 
            font=("Arial", 14), 
            width=25, 
            show="*", 
            relief="solid", 
            bd=2,
            bg="#f8f9fa"
        )
        self.login_password.pack(pady=(0, 35), ipady=10, fill="x")
        
        # Login button with better styling
        login_btn = tk.Button(
            content_frame,
            text="LOGIN",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            width=20,
            height=2,
            command=self.handle_login,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        login_btn.pack(pady=20)
        
        # Register link
        register_link = tk.Label(
            content_frame,
            text="Don't have an account? Register here",
            font=("Arial", 12, "underline"),
            bg="#ffffff",
            fg="#3498db",
            cursor="hand2"
        )
        register_link.pack(pady=(25, 0))
        register_link.bind("<Button-1>", lambda e: self.show_register_screen())
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.handle_login())
        
        # Focus on username field
        self.login_username.focus()
    
    def show_register_screen(self):
        """Show registration form with improved layout"""
        self.clear_frame()
        
        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="← Back",
            font=("Arial", 10),
            bg="#ecf0f1",
            command=self.show_welcome_screen,
            cursor="hand2"
        )
        back_btn.pack(anchor="nw", pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="Create New Account",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(10, 30))
        
        # Registration form frame with scrollbar
        form_frame = tk.Frame(self.main_frame, bg="#ffffff", relief="raised", bd=2)
        form_frame.pack(pady=10, padx=80, fill="both", expand=True)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(form_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=30)
        scrollbar.pack(side="right", fill="y")
        
        # Use scrollable_frame as content_frame
        content_frame = scrollable_frame
        
        # Form fields with consistent styling
        field_style = {
            'font': ('Arial', 12),
            'width': 30,
            'relief': 'solid',
            'bd': 2,
            'bg': '#f8f9fa'
        }
        
        label_style = {
            'font': ('Arial', 12, 'bold'),
            'bg': '#ffffff',
            'fg': '#2c3e50'
        }
        
        # Full name field
        tk.Label(content_frame, text="Full Name:", **label_style).pack(anchor="w", pady=(10, 5))
        self.reg_fullname = tk.Entry(content_frame, **field_style)
        self.reg_fullname.pack(pady=(0, 15), ipady=8, fill="x")
        
        # Username field
        tk.Label(content_frame, text="Username:", **label_style).pack(anchor="w", pady=(0, 5))
        self.reg_username = tk.Entry(content_frame, **field_style)
        self.reg_username.pack(pady=(0, 15), ipady=8, fill="x")
        
        # Email field
        tk.Label(content_frame, text="Email Address:", **label_style).pack(anchor="w", pady=(0, 5))
        self.reg_email = tk.Entry(content_frame, **field_style)
        self.reg_email.pack(pady=(0, 15), ipady=8, fill="x")
        
        # Password field
        tk.Label(content_frame, text="Password:", **label_style).pack(anchor="w", pady=(0, 5))
        password_field_style = field_style.copy()
        password_field_style['show'] = '*'
        self.reg_password = tk.Entry(content_frame, **password_field_style)
        self.reg_password.pack(pady=(0, 15), ipady=8, fill="x")
        
        # Confirm password field
        tk.Label(content_frame, text="Confirm Password:", **label_style).pack(anchor="w", pady=(0, 5))
        self.reg_confirm_password = tk.Entry(content_frame, **password_field_style)
        self.reg_confirm_password.pack(pady=(0, 15), ipady=8, fill="x")
        
        # Password requirements
        req_label = tk.Label(
            content_frame,
            text="Password must be at least 6 characters with letters and numbers",
            font=("Arial", 10),
            bg="#ffffff",
            fg="#7f8c8d"
        )
        req_label.pack(pady=(0, 20))
        
        # Register button - make it more prominent
        register_btn = tk.Button(
            content_frame,
            text="CREATE ACCOUNT",
            font=("Arial", 14, "bold"),
            bg="#2ecc71",
            fg="white",
            width=25,
            height=2,
            command=self.handle_register,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        register_btn.pack(pady=20)
        
        # Login link
        login_link = tk.Label(
            content_frame,
            text="Already have an account? Login here",
            font=("Arial", 12, "underline"),
            bg="#ffffff",
            fg="#3498db",
            cursor="hand2"
        )
        login_link.pack(pady=(15, 25))
        login_link.bind("<Button-1>", lambda e: self.show_login_screen())
        
        # Bind Enter key to register
        self.root.bind('<Return>', lambda e: self.handle_register())
        
        # Focus on full name field
        self.reg_fullname.focus()
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        success, message = self.db.authenticate_user(username, password)
        
        if success:
            self.current_user = username
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            
            # Call the success callback if provided
            if self.on_login_success:
                self.root.destroy()  # Close auth window
                self.on_login_success(username)
            else:
                # For testing, show a success screen
                self.show_success_screen(username)
        else:
            messagebox.showerror("Login Failed", message)
            self.login_password.delete(0, tk.END)  # Clear password field
    
    def handle_register(self):
        """Handle registration attempt"""
        full_name = self.reg_fullname.get().strip()
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        confirm_password = self.reg_confirm_password.get()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        success, message = self.db.register_user(username, email, password, full_name)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.show_login_screen()
        else:
            messagebox.showerror("Registration Failed", message)
    
    def show_success_screen(self, username):
        """Show success screen after login (for testing)"""
        self.clear_frame()
        
        # Success message
        success_label = tk.Label(
            self.main_frame,
            text=f"Welcome, {username}!",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#27ae60"
        )
        success_label.pack(pady=(100, 20))
        
        message_label = tk.Label(
            self.main_frame,
            text="Login successful! The Sign Language Recognition System will now start.",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        message_label.pack(pady=20)
        
        # Continue button
        continue_btn = tk.Button(
            self.main_frame,
            text="Continue to Application",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=25,
            height=2,
            command=self.root.destroy,
            cursor="hand2"
        )
        continue_btn.pack(pady=30)
        
        # Auto close after 3 seconds
        self.root.after(3000, self.root.destroy)
    
    def run(self):
        """Start the authentication GUI"""
        self.root.mainloop()
        return self.current_user


# Standalone testing
if __name__ == "__main__":
    def test_callback(username):
        print(f"Login successful for user: {username}")
    
    auth_gui = AuthenticationGUI(test_callback)
    user = auth_gui.run()
    print(f"Authenticated user: {user}")