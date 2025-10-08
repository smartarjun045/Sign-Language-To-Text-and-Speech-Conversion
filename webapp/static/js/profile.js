// Profile page JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Modal elements
    const editModal = document.getElementById('editModal');
    const passwordModal = document.getElementById('passwordModal');
    const deleteModal = document.getElementById('deleteModal');
    
    // Button elements
    const editProfileBtn = document.getElementById('editProfileBtn');
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    
    // Close buttons
    const closeButtons = document.querySelectorAll('.close');
    
    // Form elements
    const editForm = document.getElementById('editForm');
    const passwordForm = document.getElementById('passwordForm');
    const deleteForm = document.getElementById('deleteForm');

    // Open modals
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            editModal.style.display = 'block';
        });
    }

    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', function() {
            passwordModal.style.display = 'block';
        });
    }

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function() {
            deleteModal.style.display = 'block';
        });
    }

    // Close modals
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            modal.style.display = 'none';
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });

    // Handle edit profile form submission
    if (editForm) {
        editForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/update_profile', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Profile updated successfully!', 'success');
                    editModal.style.display = 'none';
                    // Refresh the page to show updated information
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showMessage(result.message || 'Failed to update profile', 'error');
                }
            } catch (error) {
                showMessage('An error occurred while updating profile', 'error');
            }
        });
    }

    // Handle password change form submission
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Validate password confirmation
            if (data.new_password !== data.confirm_password) {
                showMessage('New passwords do not match', 'error');
                return;
            }
            
            try {
                const response = await fetch('/change_password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        current_password: data.current_password,
                        new_password: data.new_password
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Password changed successfully!', 'success');
                    passwordModal.style.display = 'none';
                    this.reset();
                } else {
                    showMessage(result.message || 'Failed to change password', 'error');
                }
            } catch (error) {
                showMessage('An error occurred while changing password', 'error');
            }
        });
    }

    // Handle account deletion form submission
    if (deleteForm) {
        deleteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const password = formData.get('password');
            
            try {
                const response = await fetch('/delete_account', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ password: password })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Account deleted successfully. Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                } else {
                    showMessage(result.message || 'Failed to delete account', 'error');
                }
            } catch (error) {
                showMessage('An error occurred while deleting account', 'error');
            }
        });
    }

    // Utility function to show messages
    function showMessage(message, type) {
        // Remove existing messages
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Create new message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Style the message
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
            ${type === 'success' ? 'background-color: #4CAF50;' : 'background-color: #f44336;'}
        `;
        
        // Add to page
        document.body.appendChild(messageDiv);
        
        // Fade in
        setTimeout(() => {
            messageDiv.style.opacity = '1';
        }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }
});