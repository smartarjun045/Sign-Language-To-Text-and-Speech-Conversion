"""
User Database Module for Sign Language Authentication System
Handles user registration, login, and credential management
"""

import json
import hashlib
import os
from datetime import datetime
import re

class UserDatabase:
    def __init__(self, db_file="users.json"):
        self.db_file = db_file
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.users, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_username(self, username):
        """Validate username (3-20 chars, alphanumeric + underscore)"""
        if len(username) < 3 or len(username) > 20:
            return False
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
    
    def validate_password(self, password):
        """Validate password strength (min 6 chars, at least 1 letter and 1 number)"""
        if len(password) < 6:
            return False
        has_letter = re.search(r'[a-zA-Z]', password)
        has_digit = re.search(r'\d', password)
        return has_letter and has_digit
    
    def register_user(self, username, email, password, full_name=""):
        """Register a new user"""
        # Validation
        if not self.validate_username(username):
            return False, "Username must be 3-20 characters, letters, numbers, and underscores only"
        
        if not self.validate_email(email):
            return False, "Invalid email format"
        
        if not self.validate_password(password):
            return False, "Password must be at least 6 characters with letters and numbers"
        
        # Check if user already exists
        if username in self.users:
            return False, "Username already exists"
        
        if any(user.get('email') == email for user in self.users.values()):
            return False, "Email already registered"
        
        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password': self.hash_password(password),
            'full_name': full_name,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'login_count': 0
        }
        
        self.users[username] = user_data
        
        if self.save_users():
            return True, "User registered successfully"
        else:
            return False, "Error saving user data"
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        if username not in self.users:
            return False, "Username not found"
        
        user = self.users[username]
        if user['password'] != self.hash_password(password):
            return False, "Invalid password"
        
        # Update login info
        self.users[username]['last_login'] = datetime.now().isoformat()
        self.users[username]['login_count'] += 1
        self.save_users()
        
        return True, "Login successful"
    
    def get_user_info(self, username):
        """Get user information"""
        if username in self.users:
            user_info = self.users[username].copy()
            # Don't return password
            del user_info['password']
            return user_info
        return None
    
    def update_user_password(self, username, old_password, new_password):
        """Update user password"""
        if username not in self.users:
            return False, "User not found"
        
        if self.users[username]['password'] != self.hash_password(old_password):
            return False, "Current password is incorrect"
        
        if not self.validate_password(new_password):
            return False, "New password must be at least 6 characters with letters and numbers"
        
        self.users[username]['password'] = self.hash_password(new_password)
        
        if self.save_users():
            return True, "Password updated successfully"
        else:
            return False, "Error updating password"
    
    def delete_user(self, username):
        """Delete a user account"""
        if username in self.users:
            del self.users[username]
            return self.save_users()
        return False
    
    def get_all_users(self):
        """Get list of all usernames (admin function)"""
        return list(self.users.keys())
    
    def user_exists(self, username):
        """Check if user exists"""
        return username in self.users


# Example usage and testing
if __name__ == "__main__":
    # Test the database
    db = UserDatabase()
    
    print("Testing User Database...")
    
    # Test registration
    success, message = db.register_user("testuser", "test@email.com", "test123", "Test User")
    print(f"Registration: {success}, {message}")
    
    # Test login
    success, message = db.authenticate_user("testuser", "test123")
    print(f"Login: {success}, {message}")
    
    # Test invalid login
    success, message = db.authenticate_user("testuser", "wrongpass")
    print(f"Invalid login: {success}, {message}")
    
    # Get user info
    user_info = db.get_user_info("testuser")
    print(f"User info: {user_info}")