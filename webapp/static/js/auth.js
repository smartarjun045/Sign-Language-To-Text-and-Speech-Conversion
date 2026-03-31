/**
 * Authentication JavaScript for Sign Language Recognition Web App
 * Handles login and registration forms with validation and API communication
 */

class AuthenticationManager {
    constructor() {
        this.isSubmitting = false;
        this.init();
    }

    init() {
        // Initialize form handlers
        this.initLoginForm();
        this.initRegisterForm();
        
        // Setup validation
        this.setupValidation();
        
        // Handle page transitions
        this.handlePageLoad();
    }

    initLoginForm() {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
            
            // Handle Enter key
            const inputs = loginForm.querySelectorAll('input');
            inputs.forEach(input => {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.handleLogin(e);
                    }
                });
            });
        }
    }

    initRegisterForm() {
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
            
            // Real-time password validation
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password && confirmPassword) {
                confirmPassword.addEventListener('input', () => {
                    this.validatePasswordMatch();
                });
                
                password.addEventListener('input', () => {
                    this.validatePasswordStrength();
                    this.validatePasswordMatch();
                });
            }
            
            // Username validation
            const username = document.getElementById('username');
            if (username) {
                username.addEventListener('input', () => {
                    this.validateUsername();
                });
            }
            
            // Email validation
            const email = document.getElementById('email');
            if (email) {
                email.addEventListener('input', () => {
                    this.validateEmail();
                });
            }
        }
    }

    setupValidation() {
        // Add validation styling
        const style = document.createElement('style');
        style.textContent = `
            .form-group input.valid {
                border-color: var(--success-color);
                background-color: #f8fff9;
            }
            
            .form-group input.invalid {
                border-color: var(--accent-color);
                background-color: #fff8f8;
            }
            
            .validation-message {
                margin-top: 0.25rem;
                font-size: 0.8rem;
                transition: all 0.3s ease;
            }
            
            .validation-message.success {
                color: var(--success-color);
            }
            
            .validation-message.error {
                color: var(--accent-color);
            }
        `;
        document.head.appendChild(style);
    }

    async handleLogin(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        this.isSubmitting = true;

        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const username = form.querySelector('#username').value.trim();
        const password = form.querySelector('#password').value;

        // Validate inputs
        if (!username || !password) {
            this.showMessage('Please enter both username and password', 'error');
            this.isSubmitting = false;
            return;
        }

        // Update UI
        this.setButtonLoading(submitBtn, true);
        this.clearMessage();

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Login successful! Redirecting...', 'success');
                
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = data.redirect || '/';
                }, 1000);
            } else {
                this.showMessage(data.message || 'Login failed', 'error');
                // Clear password field
                form.querySelector('#password').value = '';
                form.querySelector('#password').focus();
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('Network error. Please try again.', 'error');
        } finally {
            this.setButtonLoading(submitBtn, false);
            this.isSubmitting = false;
        }
    }

    async handleRegister(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        this.isSubmitting = true;

        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Get form data
        const formData = {
            full_name: form.querySelector('#full_name').value.trim(),
            username: form.querySelector('#username').value.trim(),
            email: form.querySelector('#email').value.trim(),
            password: form.querySelector('#password').value,
            confirm_password: form.querySelector('#confirm_password').value
        };

        // Validate form
        if (!this.validateRegistrationForm(formData)) {
            this.isSubmitting = false;
            return;
        }

        // Update UI
        this.setButtonLoading(submitBtn, true);
        this.clearMessage();

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Registration successful! Redirecting to login...', 'success');
                
                // Redirect to login page
                setTimeout(() => {
                    window.location.href = data.redirect || '/login';
                }, 2000);
            } else {
                this.showMessage(data.message || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Network error. Please try again.', 'error');
        } finally {
            this.setButtonLoading(submitBtn, false);
            this.isSubmitting = false;
        }
    }

    validateRegistrationForm(data) {
        let isValid = true;

        // Required fields
        if (!data.username || !data.email || !data.password || !data.confirm_password) {
            this.showMessage('Please fill in all required fields', 'error');
            isValid = false;
        }

        // Username validation
        if (!this.isValidUsername(data.username)) {
            this.showMessage('Username must be 3-20 characters, letters, numbers, and underscores only', 'error');
            isValid = false;
        }

        // Email validation
        if (!this.isValidEmail(data.email)) {
            this.showMessage('Please enter a valid email address', 'error');
            isValid = false;
        }

        // Password validation
        if (!this.isValidPassword(data.password)) {
            this.showMessage('Password must be at least 6 characters with letters and numbers', 'error');
            isValid = false;
        }

        // Password confirmation
        if (data.password !== data.confirm_password) {
            this.showMessage('Passwords do not match', 'error');
            isValid = false;
        }

        return isValid;
    }

    validateUsername() {
        const username = document.getElementById('username');
        if (!username) return;

        const value = username.value.trim();
        const isValid = this.isValidUsername(value);
        
        this.setFieldValidation(username, isValid, 
            isValid ? 'Username is valid' : 'Username must be 3-20 characters, letters, numbers, and underscores only');
    }

    validateEmail() {
        const email = document.getElementById('email');
        if (!email) return;

        const value = email.value.trim();
        const isValid = this.isValidEmail(value);
        
        this.setFieldValidation(email, isValid, 
            isValid ? 'Email is valid' : 'Please enter a valid email address');
    }

    validatePasswordStrength() {
        const password = document.getElementById('password');
        if (!password) return;

        const value = password.value;
        const isValid = this.isValidPassword(value);
        
        this.setFieldValidation(password, isValid, 
            isValid ? 'Password meets requirements' : 'Password must be at least 6 characters with letters and numbers');
    }

    validatePasswordMatch() {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        
        if (!password || !confirmPassword) return;

        const match = password.value === confirmPassword.value;
        const hasValue = confirmPassword.value.length > 0;
        
        if (hasValue) {
            this.setFieldValidation(confirmPassword, match, 
                match ? 'Passwords match' : 'Passwords do not match');
        } else {
            this.clearFieldValidation(confirmPassword);
        }
    }

    isValidUsername(username) {
        return username && username.length >= 3 && username.length <= 20 && /^[a-zA-Z0-9_]+$/.test(username);
    }

    isValidEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return email && emailRegex.test(email);
    }

    isValidPassword(password) {
        return password && password.length >= 6 && /[a-zA-Z]/.test(password) && /\d/.test(password);
    }

    setFieldValidation(field, isValid, message) {
        // Update field appearance
        field.classList.remove('valid', 'invalid');
        field.classList.add(isValid ? 'valid' : 'invalid');
        
        // Update validation message
        let validationMsg = field.parentNode.querySelector('.validation-message');
        if (!validationMsg) {
            validationMsg = document.createElement('div');
            validationMsg.className = 'validation-message';
            field.parentNode.appendChild(validationMsg);
        }
        
        validationMsg.textContent = message;
        validationMsg.classList.remove('success', 'error');
        validationMsg.classList.add(isValid ? 'success' : 'error');
    }

    clearFieldValidation(field) {
        field.classList.remove('valid', 'invalid');
        const validationMsg = field.parentNode.querySelector('.validation-message');
        if (validationMsg) {
            validationMsg.remove();
        }
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        } else {
            button.disabled = false;
            // Restore original text
            if (button.id === 'loginForm' || button.closest('#loginForm')) {
                button.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
            } else {
                button.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
            }
        }
    }

    showMessage(message, type) {
        let messageEl = document.getElementById('message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'message';
            messageEl.className = 'message';
            
            // Insert after the form
            const form = document.querySelector('.auth-form');
            if (form) {
                form.parentNode.insertBefore(messageEl, form.nextSibling);
            }
        }

        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.classList.remove('hidden');

        // Auto-hide after 5 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                this.clearMessage();
            }, 5000);
        }
    }

    clearMessage() {
        const messageEl = document.getElementById('message');
        if (messageEl) {
            messageEl.classList.add('hidden');
        }
    }

    handlePageLoad() {
        // Add entrance animations
        const authCard = document.querySelector('.auth-card');
        const authInfo = document.querySelector('.auth-info');
        
        if (authCard) {
            authCard.style.opacity = '0';
            authCard.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                authCard.style.transition = 'all 0.6s ease';
                authCard.style.opacity = '1';
                authCard.style.transform = 'translateX(0)';
            }, 100);
        }
        
        if (authInfo) {
            authInfo.style.opacity = '0';
            authInfo.style.transform = 'translateX(20px)';
            
            setTimeout(() => {
                authInfo.style.transition = 'all 0.6s ease';
                authInfo.style.opacity = '1';
                authInfo.style.transform = 'translateX(0)';
            }, 200);
        }
        
        // Focus on first input
        const firstInput = document.querySelector('.auth-form input');
        if (firstInput) {
            setTimeout(() => {
                firstInput.focus();
            }, 300);
        }
    }
}

// Initialize authentication manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AuthenticationManager();
});

// Utility functions for password strength indicator
function addPasswordStrengthIndicator() {
    const passwordField = document.getElementById('password');
    if (!passwordField) return;

    const strengthIndicator = document.createElement('div');
    strengthIndicator.className = 'password-strength';
    strengthIndicator.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill"></div>
        </div>
        <div class="strength-text">Password strength: <span>Weak</span></div>
    `;

    passwordField.parentNode.appendChild(strengthIndicator);

    passwordField.addEventListener('input', () => {
        updatePasswordStrength(passwordField.value, strengthIndicator);
    });
}

function updatePasswordStrength(password, indicator) {
    const strengthFill = indicator.querySelector('.strength-fill');
    const strengthText = indicator.querySelector('.strength-text span');
    
    let strength = 0;
    let strengthLabel = 'Very Weak';
    let color = '#e74c3c';

    if (password.length >= 6) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/\d/.test(password)) strength += 1;
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;

    switch (strength) {
        case 0:
        case 1:
            strengthLabel = 'Very Weak';
            color = '#e74c3c';
            break;
        case 2:
            strengthLabel = 'Weak';
            color = '#f39c12';
            break;
        case 3:
            strengthLabel = 'Fair';
            color = '#f1c40f';
            break;
        case 4:
            strengthLabel = 'Good';
            color = '#2ecc71';
            break;
        case 5:
            strengthLabel = 'Strong';
            color = '#27ae60';
            break;
    }

    strengthFill.style.width = `${(strength / 5) * 100}%`;
    strengthFill.style.backgroundColor = color;
    strengthText.textContent = strengthLabel;
    strengthText.style.color = color;
}

// Add styles for password strength indicator
const strengthStyles = `
    .password-strength {
        margin-top: 0.5rem;
    }
    
    .strength-bar {
        height: 4px;
        background-color: #ecf0f1;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 0.25rem;
    }
    
    .strength-fill {
        height: 100%;
        width: 0%;
        transition: all 0.3s ease;
    }
    
    .strength-text {
        font-size: 0.8rem;
        color: #7f8c8d;
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = strengthStyles;
document.head.appendChild(styleSheet);