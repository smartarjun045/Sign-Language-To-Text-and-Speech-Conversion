/**
 * Main Application JavaScript for Sign Language Recognition Web App
 * Handles camera controls, recognition management, UI interactions, and real-time updates
 */

class SignLanguageApp {
    constructor() {
        this.isInitialized = false;
        this.camera = {
            active: false,
            stream: null
        };
        this.recognition = {
            active: false,
            results: {
                current_character: '',
                sentence: '',
                word_suggestions: [],
                confidence: 0.0,
                hand_detected: false
            }
        };
        this.ui = {
            videoFeed: null,
            videoPlaceholder: null,
            currentCharacter: null,
            recognizedText: null,
            suggestionButtons: [],
            statusElements: {}
        };
        
        this.updateInterval = null;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    initialize() {
        console.log('Initializing Sign Language Recognition App...');
        
        // Initialize UI elements
        this.initializeUIElements();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize components
        this.initializeComponents();
        
        // Start status updates
        this.startStatusUpdates();
        
        this.isInitialized = true;
        console.log('App initialization complete');
    }

    initializeUIElements() {
        // Video elements
        this.ui.videoFeed = document.getElementById('videoFeed');
        this.ui.videoPlaceholder = document.getElementById('videoPlaceholder');
        
        // Text elements
        this.ui.currentCharacter = document.getElementById('currentCharacter');
        this.ui.recognizedText = document.getElementById('recognizedText');
        
        // Suggestion buttons
        for (let i = 1; i <= 4; i++) {
            const btn = document.getElementById(`suggestion${i}`);
            if (btn) {
                this.ui.suggestionButtons.push(btn);
            }
        }
        
        // Status elements
        this.ui.statusElements = {
            camera: {
                text: document.getElementById('cameraStatus'),
                light: document.getElementById('cameraStatusLight')
            },
            recognition: {
                text: document.getElementById('recognitionStatus'),
                light: document.getElementById('recognitionStatusLight')
            }
        };
        
        // Control buttons
        this.ui.buttons = {
            startCamera: document.getElementById('startCameraBtn'),
            stopCamera: document.getElementById('stopCameraBtn'),
            startRecognition: document.getElementById('startRecognitionBtn'),
            stopRecognition: document.getElementById('stopRecognitionBtn'),
            speak: document.getElementById('speakBtn'),
            clear: document.getElementById('clearBtn'),
            profile: document.getElementById('profileBtn'),
            help: document.getElementById('helpBtn')
        };
    }

    setupEventListeners() {
        // Camera controls
        if (this.ui.buttons.startCamera) {
            this.ui.buttons.startCamera.addEventListener('click', () => this.startCamera());
        }
        if (this.ui.buttons.stopCamera) {
            this.ui.buttons.stopCamera.addEventListener('click', () => this.stopCamera());
        }
        
        // Recognition controls
        if (this.ui.buttons.startRecognition) {
            this.ui.buttons.startRecognition.addEventListener('click', () => this.startRecognition());
        }
        if (this.ui.buttons.stopRecognition) {
            this.ui.buttons.stopRecognition.addEventListener('click', () => this.stopRecognition());
        }
        
        // Text controls
        if (this.ui.buttons.speak) {
            this.ui.buttons.speak.addEventListener('click', () => this.speakText());
        }
        if (this.ui.buttons.clear) {
            this.ui.buttons.clear.addEventListener('click', () => this.clearText());
        }
        
        // UI controls
        if (this.ui.buttons.profile) {
            this.ui.buttons.profile.addEventListener('click', () => this.showProfile());
        }
        if (this.ui.buttons.help) {
            this.ui.buttons.help.addEventListener('click', () => this.showHelp());
        }
        
        // Text area changes
        if (this.ui.recognizedText) {
            this.ui.recognizedText.addEventListener('input', () => this.updateTextStats());
        }
        
        // Suggestion button clicks
        this.ui.suggestionButtons.forEach((btn, index) => {
            btn.addEventListener('click', () => this.applySuggestion(index));
        });
        
        // Modal and overlay controls
        this.setupModalControls();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }

    setupModalControls() {
        // Help panel
        const helpPanel = document.getElementById('helpPanel');
        const closeHelpBtn = document.getElementById('closeHelpBtn');
        
        if (closeHelpBtn) {
            closeHelpBtn.addEventListener('click', () => this.hideHelp());
        }
        
        if (helpPanel) {
            helpPanel.addEventListener('click', (e) => {
                if (e.target === helpPanel) {
                    this.hideHelp();
                }
            });
        }
        
        // Profile modal
        const profileModal = document.getElementById('profileModal');
        const closeProfileBtn = document.getElementById('closeProfileBtn');
        
        if (closeProfileBtn) {
            closeProfileBtn.addEventListener('click', () => this.hideProfile());
        }
        
        if (profileModal) {
            profileModal.addEventListener('click', (e) => {
                if (e.target === profileModal) {
                    this.hideProfile();
                }
            });
        }
        
        // Error message close
        const closeErrorBtn = document.getElementById('closeErrorBtn');
        if (closeErrorBtn) {
            closeErrorBtn.addEventListener('click', () => this.hideError());
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + key combinations
            if (e.ctrlKey || e.metaKey) {
                switch (e.key.toLowerCase()) {
                    case 'enter':
                        e.preventDefault();
                        if (!this.camera.active) {
                            this.startCamera();
                        } else if (!this.recognition.active) {
                            this.startRecognition();
                        }
                        break;
                    case 's':
                        e.preventDefault();
                        this.speakText();
                        break;
                    case 'k':
                        e.preventDefault();
                        this.clearText();
                        break;
                }
            }
            
            // Function keys
            switch (e.key) {
                case 'F1':
                    e.preventDefault();
                    this.showHelp();
                    break;
                case 'Escape':
                    this.hideAllModals();
                    break;
            }
        });
    }

    initializeComponents() {
        // Initialize text stats
        this.updateTextStats();
        
        // Check initial status
        this.checkStatus();
        
        // Setup video feed error handling
        if (this.ui.videoFeed) {
            this.ui.videoFeed.addEventListener('error', () => {
                this.showError('Video feed error. Please refresh the page.');
            });
        }
        
        // Initialize speech synthesis
        this.initializeSpeechSynthesis();
        
        // Ensure buttons have correct initial state
        this.initializeButtonStates();
    }

    initializeButtonStates() {
        // Ensure all buttons have correct initial content
        if (this.ui.buttons.speak) {
            this.ui.buttons.speak.innerHTML = '<i class="fas fa-play-circle"></i> Speak Text';
            this.ui.buttons.speak.disabled = false;
        }
        
        if (this.ui.buttons.clear) {
            this.ui.buttons.clear.innerHTML = '<i class="fas fa-trash"></i> Clear Text';
            this.ui.buttons.clear.disabled = false;
        }
    }

    initializeSpeechSynthesis() {
        // Initialize browser speech synthesis
        if ('speechSynthesis' in window) {
            // Load voices
            const loadVoices = () => {
                const voices = window.speechSynthesis.getVoices();
                console.log(`Found ${voices.length} speech synthesis voices`);
                
                // Log available English voices
                const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
                if (englishVoices.length > 0) {
                    console.log('Available English voices:', englishVoices.map(v => v.name));
                } else {
                    console.warn('No English voices found for speech synthesis');
                }
            };
            
            // Load voices when available
            if (window.speechSynthesis.getVoices().length > 0) {
                loadVoices();
            } else {
                window.speechSynthesis.addEventListener('voiceschanged', loadVoices);
            }
        } else {
            console.warn('Speech synthesis not supported in this browser');
        }
    }

    // Camera Control Methods
    async startCamera() {
        if (this.camera.active) return;
        
        this.showLoading('Starting camera...');
        
        try {
            const response = await this.apiCall('/api/camera/start', 'POST');
            
            if (response.success) {
                this.camera.active = true;
                this.updateCameraUI();
                this.startVideoFeed();
                this.showSuccess('Camera started successfully');
            } else {
                this.showError(response.message || 'Failed to start camera');
            }
        } catch (error) {
            console.error('Camera start error:', error);
            this.showError('Failed to start camera. Please check permissions.');
        } finally {
            this.hideLoading();
        }
    }

    async stopCamera() {
        if (!this.camera.active) return;
        
        try {
            const response = await this.apiCall('/api/camera/stop', 'POST');
            
            if (response.success) {
                this.camera.active = false;
                this.recognition.active = false;
                this.updateCameraUI();
                this.updateRecognitionUI();
                this.stopVideoFeed();
                this.showSuccess('Camera stopped');
            } else {
                this.showError(response.message || 'Failed to stop camera');
            }
        } catch (error) {
            console.error('Camera stop error:', error);
            this.showError('Failed to stop camera');
        }
    }

    startVideoFeed() {
        if (this.ui.videoFeed && this.ui.videoPlaceholder) {
            this.ui.videoFeed.src = '/video_feed?' + new Date().getTime();
            this.ui.videoFeed.style.display = 'block';
            this.ui.videoPlaceholder.style.display = 'none';
        }
    }

    stopVideoFeed() {
        if (this.ui.videoFeed && this.ui.videoPlaceholder) {
            this.ui.videoFeed.src = '';
            this.ui.videoFeed.style.display = 'none';
            this.ui.videoPlaceholder.style.display = 'flex';
        }
    }

    // Recognition Control Methods
    async startRecognition() {
        if (!this.camera.active) {
            this.showError('Please start the camera first');
            return;
        }
        
        if (this.recognition.active) return;
        
        try {
            const response = await this.apiCall('/api/recognition/start', 'POST');
            
            if (response.success) {
                this.recognition.active = true;
                this.updateRecognitionUI();
                this.showSuccess('Recognition started');
            } else {
                this.showError(response.message || 'Failed to start recognition');
            }
        } catch (error) {
            console.error('Recognition start error:', error);
            this.showError('Failed to start recognition');
        }
    }

    async stopRecognition() {
        if (!this.recognition.active) return;
        
        try {
            const response = await this.apiCall('/api/recognition/stop', 'POST');
            
            if (response.success) {
                this.recognition.active = false;
                this.updateRecognitionUI();
                this.showSuccess('Recognition stopped');
            } else {
                this.showError(response.message || 'Failed to stop recognition');
            }
        } catch (error) {
            console.error('Recognition stop error:', error);
            this.showError('Failed to stop recognition');
        }
    }

    // Text Control Methods
    async speakText() {
        const text = this.ui.recognizedText?.textContent || this.ui.recognizedText?.innerText || '';
        
        if (!text.trim()) {
            this.showError('No text to speak');
            return;
        }
        
        try {
            this.setButtonLoading(this.ui.buttons.speak, true, 'Speaking...');
            
            const response = await this.apiCall('/api/text/speak', 'POST', {
                text: text.trim()
            });
            
            if (response.success) {
                if (response.use_client_speech) {
                    // Use browser's speech synthesis as fallback
                    await this.speakWithBrowser(response.text || text.trim());
                    this.showSuccess('Text spoken successfully');
                } else {
                    this.showSuccess('Text spoken successfully');
                }
            } else {
                // Fallback to browser speech synthesis
                await this.speakWithBrowser(text.trim());
                this.showSuccess('Text spoken successfully');
            }
        } catch (error) {
            console.error('Speech error:', error);
            // Always fallback to browser speech synthesis
            try {
                await this.speakWithBrowser(text.trim());
                this.showSuccess('Text spoken successfully');
            } catch (fallbackError) {
                this.showError('Speech synthesis failed');
            }
        } finally {
            // Always restore button state
            this.setButtonLoading(this.ui.buttons.speak, false);
        }
    }

    speakWithBrowser(text) {
        // Use browser's built-in speech synthesis
        return new Promise((resolve, reject) => {
            try {
                // Check if browser supports speech synthesis
                if (!('speechSynthesis' in window)) {
                    throw new Error('Speech synthesis not supported in this browser');
                }
                
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                // Create speech utterance
                const utterance = new SpeechSynthesisUtterance(text);
                
                // Configure speech settings
                utterance.rate = 0.8; // Slightly slower for clarity
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // Set voice if available
                const voices = window.speechSynthesis.getVoices();
                if (voices.length > 0) {
                    // Try to find English voice
                    const englishVoice = voices.find(voice => voice.lang.startsWith('en'));
                    if (englishVoice) {
                        utterance.voice = englishVoice;
                    }
                }
                
                // Add event listeners
                utterance.onstart = () => {
                    console.log('Speech synthesis started');
                };
                
                utterance.onend = () => {
                    console.log('Speech synthesis completed');
                    resolve(true);
                };
                
                utterance.onerror = (event) => {
                    console.error('Speech synthesis error:', event.error);
                    reject(new Error(`Speech synthesis failed: ${event.error}`));
                };
                
                // Speak the text
                window.speechSynthesis.speak(utterance);
                
                // Fallback timeout in case events don't fire
                setTimeout(() => {
                    if (!utterance.onend) {
                        resolve(true);
                    }
                }, Math.max(text.length * 100, 3000)); // Estimate speech duration
                
            } catch (error) {
                console.error('Browser speech synthesis error:', error);
                reject(error);
            }
        });
    }

    async clearText() {
        try {
            const response = await this.apiCall('/api/text/clear', 'POST');
            
            if (response.success) {
                if (this.ui.recognizedText) {
                    this.ui.recognizedText.textContent = '';
                }
                this.updateTextStats();
                this.updateSuggestions([]);
                this.showSuccess('Text cleared');
            } else {
                this.showError(response.message || 'Failed to clear text');
            }
        } catch (error) {
            console.error('Clear text error:', error);
            this.showError('Failed to clear text');
        }
    }

    async applySuggestion(index) {
        const suggestion = this.recognition.results.word_suggestions[index];
        if (!suggestion || suggestion.trim() === '') return;
        
        try {
            const response = await this.apiCall('/api/text/suggest', 'POST', {
                suggestion: suggestion
            });
            
            if (response.success && response.sentence) {
                if (this.ui.recognizedText) {
                    this.ui.recognizedText.textContent = response.sentence;
                }
                this.updateTextStats();
                this.showSuccess(`Applied suggestion: ${suggestion}`);
            } else {
                this.showError('Failed to apply suggestion');
            }
        } catch (error) {
            console.error('Suggestion error:', error);
            this.showError('Failed to apply suggestion');
        }
    }

    // UI Update Methods
    updateCameraUI() {
        // Update button states
        if (this.ui.buttons.startCamera) {
            this.ui.buttons.startCamera.disabled = this.camera.active;
        }
        if (this.ui.buttons.stopCamera) {
            this.ui.buttons.stopCamera.disabled = !this.camera.active;
        }
        if (this.ui.buttons.startRecognition) {
            this.ui.buttons.startRecognition.disabled = !this.camera.active;
        }
        
        // Update status display
        const status = this.ui.statusElements.camera;
        if (status.text && status.light) {
            status.text.textContent = `Camera: ${this.camera.active ? 'On' : 'Off'}`;
            status.light.className = `status-light ${this.camera.active ? 'on' : 'off'}`;
        }
    }

    updateRecognitionUI() {
        // Update button states
        if (this.ui.buttons.startRecognition) {
            this.ui.buttons.startRecognition.disabled = !this.camera.active || this.recognition.active;
        }
        if (this.ui.buttons.stopRecognition) {
            this.ui.buttons.stopRecognition.disabled = !this.recognition.active;
        }
        
        // Update status display
        const status = this.ui.statusElements.recognition;
        if (status.text && status.light) {
            status.text.textContent = `Recognition: ${this.recognition.active ? 'On' : 'Off'}`;
            status.light.className = `status-light ${this.recognition.active ? 'on' : 'off'}`;
        }
    }

    updateRecognitionResults(results) {
        this.recognition.results = { ...this.recognition.results, ...results };
        
        // Update current character
        if (this.ui.currentCharacter && results.current_character !== undefined) {
            this.ui.currentCharacter.textContent = results.current_character || '-';
        }
        
        // Update sentence
        if (this.ui.recognizedText && results.sentence !== undefined) {
            this.ui.recognizedText.textContent = results.sentence;
            this.updateTextStats();
        }
        
        // Update suggestions
        if (results.word_suggestions) {
            this.updateSuggestions(results.word_suggestions);
        }
    }

    updateSuggestions(suggestions) {
        const noSuggestions = document.getElementById('noSuggestions');
        
        this.ui.suggestionButtons.forEach((btn, index) => {
            if (suggestions[index] && suggestions[index].trim() !== '' && suggestions[index] !== ' ') {
                btn.textContent = suggestions[index];
                btn.style.display = 'block';
            } else {
                btn.style.display = 'none';
            }
        });
        
        // Show/hide no suggestions message
        const hasVisibleSuggestions = this.ui.suggestionButtons.some(btn => btn.style.display === 'block');
        if (noSuggestions) {
            noSuggestions.style.display = hasVisibleSuggestions ? 'none' : 'flex';
        }
    }

    updateTextStats() {
        const text = this.ui.recognizedText?.textContent || '';
        const charCount = text.length;
        const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
        
        const charCountEl = document.getElementById('charCount');
        const wordCountEl = document.getElementById('wordCount');
        
        if (charCountEl) {
            charCountEl.textContent = `${charCount} character${charCount !== 1 ? 's' : ''}`;
        }
        if (wordCountEl) {
            wordCountEl.textContent = `${wordCount} word${wordCount !== 1 ? 's' : ''}`;
        }
    }

    // Status and Monitoring
    startStatusUpdates() {
        this.updateInterval = setInterval(() => {
            this.checkStatus();
        }, 2000); // Check every 2 seconds
    }

    async checkStatus() {
        try {
            const response = await this.apiCall('/api/recognition/status', 'GET');
            
            if (response.success) {
                this.camera.active = response.camera_active;
                this.recognition.active = response.recognition_active;
                
                this.updateCameraUI();
                this.updateRecognitionUI();
                
                if (response.results) {
                    this.updateRecognitionResults(response.results);
                }
            }
        } catch (error) {
            // Silently handle status check errors
            console.warn('Status check failed:', error);
        }
    }

    // Modal and UI Methods
    showProfile() {
        const modal = document.getElementById('profileModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    hideProfile() {
        const modal = document.getElementById('profileModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    showHelp() {
        const panel = document.getElementById('helpPanel');
        if (panel) {
            panel.classList.remove('hidden');
        }
    }

    hideHelp() {
        const panel = document.getElementById('helpPanel');
        if (panel) {
            panel.classList.add('hidden');
        }
    }

    hideAllModals() {
        this.hideProfile();
        this.hideHelp();
        this.hideError();
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay?.querySelector('p');
        
        if (overlay) {
            if (text) text.textContent = message;
            overlay.classList.remove('hidden');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }

    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        const textEl = document.getElementById('errorText');
        
        if (errorEl && textEl) {
            textEl.textContent = message;
            errorEl.classList.remove('hidden');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
        }
    }

    hideError() {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) {
            errorEl.classList.add('hidden');
        }
    }

    showSuccess(message) {
        const successEl = document.getElementById('successMessage');
        const textEl = document.getElementById('successText');
        
        if (successEl && textEl) {
            textEl.textContent = message;
            successEl.classList.remove('hidden');
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                successEl.classList.add('hidden');
            }, 3000);
        }
    }

    setButtonLoading(button, loading, customText = null) {
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            const originalContent = button.innerHTML;
            button.dataset.originalContent = originalContent;
            
            const loadingText = customText || 'Loading...';
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
        } else {
            button.disabled = false;
            if (button.dataset.originalContent) {
                button.innerHTML = button.dataset.originalContent;
                delete button.dataset.originalContent;
            } else {
                // Fallback: restore default content based on button
                if (button === this.ui.buttons.speak) {
                    button.innerHTML = '<i class="fas fa-play-circle"></i> Speak Text';
                } else if (button === this.ui.buttons.clear) {
                    button.innerHTML = '<i class="fas fa-trash"></i> Clear Text';
                } else {
                    button.innerHTML = button.textContent.replace(/Loading\.\.\.|Speaking\.\.\./g, '').trim();
                }
            }
        }
    }

    // API Communication
    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    // Cleanup
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.stopCamera();
    }
}

// Initialize the application
let app;

document.addEventListener('DOMContentLoaded', () => {
    app = new SignLanguageApp();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (app) {
        app.destroy();
    }
});