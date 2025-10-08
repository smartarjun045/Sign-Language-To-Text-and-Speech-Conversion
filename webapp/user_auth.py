"""
User Authentication Module for Flask Web Application

This module handles user registration, login, and session management
for the Sign Language Recognition web application. It's based on the
authentication system from the original desktop application.
"""

import json
import hashlib
import os
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class UserAuthentication:
    def __init__(self, users_file='users.json'):
        """
        Initialize the User Authentication system
        
        Args:
            users_file: Path to the JSON file storing user data
        """
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    logger.info(f"Loaded {len(users_data)} users from {self.users_file}")
                    return users_data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading users file: {e}")
                return {}
        else:
            logger.info(f"Users file {self.users_file} not found, starting with empty database")
            return {}
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=4)
            logger.info(f"Saved {len(self.users)} users to {self.users_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            return False
    
    def hash_password(self, password):
        """
        Hash password using SHA-256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        """
        Validate email format using regex
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_username(self, username):
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            bool: True if valid username (3-20 chars, alphanumeric + underscore)
        """
        if len(username) < 3 or len(username) > 20:
            return False
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
    
    def validate_password(self, password):
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            bool: True if password meets requirements (min 6 chars, 1 letter, 1 number)
        """
        if len(password) < 6:
            return False
        has_letter = re.search(r'[a-zA-Z]', password)
        has_digit = re.search(r'\d', password)
        return has_letter and has_digit
    
    def register_user(self, username, email, password, full_name=""):
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User's email address
            password: Plain text password
            full_name: User's full name (optional)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Input validation
            if not username or not email or not password:
                return False, "Username, email, and password are required"
            
            # Validate username format
            if not self.validate_username(username):
                return False, "Username must be 3-20 characters, letters, numbers, and underscores only"
            
            # Validate email format
            if not self.validate_email(email):
                return False, "Invalid email format"
            
            # Validate password strength
            if not self.validate_password(password):
                return False, "Password must be at least 6 characters with letters and numbers"
            
            # Check if username already exists
            if username in self.users:
                return False, "Username already exists"
            
            # Check if email already exists
            if any(user.get('email') == email for user in self.users.values()):
                return False, "Email already registered"
            
            # Create user data
            user_data = {
                'username': username,
                'email': email,
                'password': self.hash_password(password),
                'full_name': full_name,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'login_count': 0,
                'session_count': 0,
                'total_recognition_time': 0  # in seconds
            }
            
            # Add user to database
            self.users[username] = user_data
            
            # Save to file
            if self.save_users():
                logger.info(f"New user registered: {username} ({email})")
                return True, "User registered successfully"
            else:
                # Remove user if save failed
                del self.users[username]
                return False, "Error saving user data"
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def authenticate_user(self, username, password):
        """
        Authenticate user login
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            tuple: (success: bool, message: str, user_info: dict or None)
        """
        try:
            # Check if user exists
            if username not in self.users:
                logger.warning(f"Login attempt with non-existent username: {username}")
                return False, "Invalid username or password", None
            
            user = self.users[username]
            
            # Check password
            if user['password'] != self.hash_password(password):
                logger.warning(f"Invalid password attempt for user: {username}")
                return False, "Invalid username or password", None
            
            # Update login information
            self.users[username]['last_login'] = datetime.now().isoformat()
            self.users[username]['login_count'] += 1
            
            # Save updated user data
            self.save_users()
            
            # Return user info (without password)
            user_info = user.copy()
            del user_info['password']
            
            logger.info(f"Successful login for user: {username}")
            return True, "Login successful", user_info
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"Authentication failed: {str(e)}", None
    
    def get_user_info(self, username):
        """
        Get user information (without password)
        
        Args:
            username: Username to get info for
            
        Returns:
            dict: User information or None if not found
        """
        if username in self.users:
            user_info = self.users[username].copy()
            # Remove sensitive information
            if 'password' in user_info:
                del user_info['password']
            return user_info
        return None
    
    def update_user_password(self, username, old_password, new_password):
        """
        Update user password
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if username not in self.users:
                return False, "User not found"
            
            # Verify current password
            if self.users[username]['password'] != self.hash_password(old_password):
                return False, "Current password is incorrect"
            
            # Validate new password
            if not self.validate_password(new_password):
                return False, "New password must be at least 6 characters with letters and numbers"
            
            # Update password
            self.users[username]['password'] = self.hash_password(new_password)
            
            # Save changes
            if self.save_users():
                logger.info(f"Password updated for user: {username}")
                return True, "Password updated successfully"
            else:
                return False, "Error saving password update"
                
        except Exception as e:
            logger.error(f"Password update error: {e}")
            return False, f"Password update failed: {str(e)}"
    
    def change_password(self, username, current_password, new_password):
        """
        Change user password with current password verification
        
        Args:
            username: Username
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if username not in self.users:
                return False, "User not found"
            
            # Verify current password
            if self.users[username]['password'] != self.hash_password(current_password):
                return False, "Current password is incorrect"
            
            # Validate new password
            if not self.validate_password(new_password):
                return False, "New password must be at least 6 characters with letters and numbers"
            
            # Update password
            self.users[username]['password'] = self.hash_password(new_password)
            
            # Save changes
            if self.save_users():
                logger.info(f"Password changed for user: {username}")
                return True, "Password changed successfully"
            else:
                return False, "Error saving password change"
                
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, f"Password change failed: {str(e)}"
    
    def delete_account(self, username, password):
        """
        Delete user account with password verification
        
        Args:
            username: Username to delete
            password: Password for verification
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if username not in self.users:
                return False, "User not found"
            
            # Verify password
            if self.users[username]['password'] != self.hash_password(password):
                return False, "Incorrect password"
            
            # Delete user
            del self.users[username]
            
            # Save changes
            if self.save_users():
                logger.info(f"Account deleted for user: {username}")
                return True, "Account deleted successfully"
            else:
                return False, "Error deleting account"
                
        except Exception as e:
            logger.error(f"Account deletion error: {e}")
            return False, f"Account deletion failed: {str(e)}"

    def update_user_profile(self, username, full_name=None, email=None):
        """
        Update user profile information
        
        Args:
            username: Username
            full_name: New full name (optional)
            email: New email (optional)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if username not in self.users:
                return False, "User not found"
            
            updated_fields = []
            
            # Update full name if provided
            if full_name is not None and full_name.strip():
                self.users[username]['full_name'] = full_name.strip()
                updated_fields.append('full name')
            
            # Update email if provided
            if email is not None and email.strip():
                # Validate email format
                if not self.validate_email(email):
                    return False, "Invalid email format"
                
                # Check if email already exists for another user
                if any(user.get('email') == email and user_username != username 
                       for user_username, user in self.users.items()):
                    return False, "Email already registered to another user"
                
                self.users[username]['email'] = email.strip()
                updated_fields.append('email')
            
            if updated_fields:
                # Save changes
                if self.save_users():
                    logger.info(f"Profile updated for user {username}: {updated_fields}")
                    return True, f"Updated: {', '.join(updated_fields)}"
                else:
                    return False, "Error saving profile updates"
            else:
                return False, "No valid fields provided for update"
                
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return False, f"Profile update failed: {str(e)}"
    
    def delete_user(self, username):
        """
        Delete a user account
        
        Args:
            username: Username to delete
            
        Returns:
            bool: True if successful
        """
        try:
            if username in self.users:
                del self.users[username]
                success = self.save_users()
                if success:
                    logger.info(f"User deleted: {username}")
                return success
            return False
        except Exception as e:
            logger.error(f"User deletion error: {e}")
            return False
    
    def get_user_stats(self, username):
        """
        Get user statistics
        
        Args:
            username: Username
            
        Returns:
            dict: User statistics or None
        """
        if username in self.users:
            user = self.users[username]
            return {
                'login_count': user.get('login_count', 0),
                'session_count': user.get('session_count', 0),
                'total_recognition_time': user.get('total_recognition_time', 0),
                'member_since': user.get('created_at', ''),
                'last_login': user.get('last_login', '')
            }
        return None
    
    def update_session_stats(self, username, session_duration=0):
        """
        Update user session statistics
        
        Args:
            username: Username
            session_duration: Session duration in seconds
        """
        try:
            if username in self.users:
                self.users[username]['session_count'] = self.users[username].get('session_count', 0) + 1
                self.users[username]['total_recognition_time'] = self.users[username].get('total_recognition_time', 0) + session_duration
                self.save_users()
                logger.info(f"Updated session stats for {username}: +{session_duration}s")
        except Exception as e:
            logger.error(f"Error updating session stats: {e}")
    
    def list_all_users(self):
        """
        Get list of all usernames (admin function)
        
        Returns:
            list: List of all usernames
        """
        return list(self.users.keys())
    
    def user_exists(self, username):
        """
        Check if user exists
        
        Args:
            username: Username to check
            
        Returns:
            bool: True if user exists
        """
        return username in self.users
    
    def get_user_count(self):
        """
        Get total number of registered users
        
        Returns:
            int: Number of users
        """
        return len(self.users)


# Example usage and testing
if __name__ == "__main__":
    # Test the authentication system
    auth = UserAuthentication('test_users.json')
    
    print("Testing User Authentication System...")
    
    # Test registration
    success, message = auth.register_user("testuser", "test@example.com", "password123", "Test User")
    print(f"Registration: {success} - {message}")
    
    # Test login
    success, message, user_info = auth.authenticate_user("testuser", "password123")
    print(f"Login: {success} - {message}")
    if user_info:
        print(f"User info: {user_info}")
    
    # Test invalid login
    success, message, user_info = auth.authenticate_user("testuser", "wrongpassword")
    print(f"Invalid login: {success} - {message}")
    
    # Test user stats
    stats = auth.get_user_stats("testuser")
    print(f"User stats: {stats}")
    
    print(f"Total users: {auth.get_user_count()}")
    
    # Clean up test file
    if os.path.exists('test_users.json'):
        os.remove('test_users.json')