"""
Speech Synthesis Module for Flask Web Application

This module handles text-to-speech functionality for the Sign Language
Recognition web application. It's designed to work in a web environment
with proper threading and error handling.
"""

import pyttsx3
import threading
import time
import logging
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class SpeechSynthesis:
    def __init__(self):
        """Initialize the Speech Synthesis system"""
        self.engine = None
        self.speech_queue = Queue()
        self.is_speaking = False
        self.speech_thread = None
        self.stop_flag = threading.Event()
        
        # Initialize TTS engine
        self.initialize_engine()
        
        # Start speech worker thread
        self.start_speech_worker()
    
    def initialize_engine(self):
        """Initialize the pyttsx3 TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set speech properties
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Get available voices and set default
            try:
                voices = self.engine.getProperty('voices')
                if voices and len(voices) > 0:
                    # Use first available voice (usually default system voice)
                    first_voice = voices[0]
                    self.engine.setProperty('voice', first_voice.id)
                    logger.info(f"TTS engine initialized with voice: {first_voice.name}")
                else:
                    logger.warning("No voices available for TTS engine")
            except (TypeError, IndexError, AttributeError):
                logger.warning("Could not set voice for TTS engine")
            
            logger.info("Speech synthesis engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            self.engine = None
    
    def start_speech_worker(self):
        """Start the background thread for speech synthesis"""
        if self.speech_thread is None or not self.speech_thread.is_alive():
            self.stop_flag.clear()
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
            logger.info("Speech worker thread started")
    
    def _speech_worker(self):
        """Background worker thread for processing speech requests"""
        while not self.stop_flag.is_set():
            try:
                # Get speech request from queue (timeout to check stop flag)
                speech_text = self.speech_queue.get(timeout=1.0)
                
                if speech_text and self.engine:
                    self._speak_text(speech_text)
                
                self.speech_queue.task_done()
                
            except Empty:
                # Timeout - continue loop to check stop flag
                continue
            except Exception as e:
                logger.error(f"Error in speech worker: {e}")
                time.sleep(0.1)  # Brief pause before continuing
    
    def _speak_text(self, text):
        """
        Internal method to speak text using pyttsx3
        
        Args:
            text: Text to speak
        """
        try:
            if not self.engine:
                logger.error("TTS engine not available")
                return
            
            self.is_speaking = True
            logger.info(f"Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Clear any previous speech
            self.engine.stop()
            
            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            
            logger.info("Speech synthesis completed")
            
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            # Try to reinitialize engine if there's an error
            self.reinitialize_engine()
        finally:
            self.is_speaking = False
    
    def speak(self, text):
        """
        Add text to speech queue for asynchronous speaking
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if text was queued successfully
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for speech synthesis")
                return False
            
            # Clean and prepare text
            clean_text = self.clean_text(text)
            
            if not clean_text:
                logger.warning("No speakable text after cleaning")
                return False
            
            # Add to speech queue
            self.speech_queue.put(clean_text)
            logger.info(f"Text queued for speech: {clean_text[:30]}{'...' if len(clean_text) > 30 else ''}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error queuing text for speech: {e}")
            return False
    
    def speak_immediately(self, text):
        """
        Speak text immediately, bypassing the queue
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if speech was successful
        """
        try:
            if not text or not text.strip():
                return False
            
            # Stop current speech
            self.stop_current_speech()
            
            # Clean text
            clean_text = self.clean_text(text)
            
            if clean_text:
                # Speak immediately in current thread
                self._speak_text(clean_text)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in immediate speech: {e}")
            return False
    
    def clean_text(self, text):
        """
        Clean and prepare text for speech synthesis
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text ready for speech
        """
        try:
            # Remove extra whitespace
            cleaned = ' '.join(text.split())
            
            # Remove special characters that might cause issues
            cleaned = ''.join(char for char in cleaned if char.isalnum() or char.isspace() or char in '.,!?')
            
            # Ensure reasonable length
            if len(cleaned) > 1000:
                cleaned = cleaned[:1000] + "..."
                logger.warning("Text truncated for speech synthesis")
            
            return cleaned.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return ""
    
    def stop_current_speech(self):
        """Stop any currently playing speech"""
        try:
            if self.engine and self.is_speaking:
                self.engine.stop()
                logger.info("Current speech stopped")
        except Exception as e:
            logger.error(f"Error stopping current speech: {e}")
    
    def clear_speech_queue(self):
        """Clear all pending speech requests"""
        try:
            # Clear the queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except Empty:
                    break
            
            logger.info("Speech queue cleared")
            
        except Exception as e:
            logger.error(f"Error clearing speech queue: {e}")
    
    def reinitialize_engine(self):
        """Reinitialize the TTS engine if there are issues"""
        try:
            logger.info("Reinitializing TTS engine...")
            
            # Stop current engine
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
            
            # Create new engine
            self.engine = None
            time.sleep(0.5)  # Brief pause
            
            self.initialize_engine()
            
        except Exception as e:
            logger.error(f"Error reinitializing TTS engine: {e}")
    
    def set_speech_rate(self, rate):
        """
        Set speech rate
        
        Args:
            rate: Speech rate (words per minute, typically 100-300)
        """
        try:
            if self.engine and 100 <= rate <= 300:
                self.engine.setProperty('rate', rate)
                logger.info(f"Speech rate set to {rate} WPM")
                return True
            else:
                logger.warning(f"Invalid speech rate: {rate}")
                return False
        except Exception as e:
            logger.error(f"Error setting speech rate: {e}")
            return False
    
    def set_speech_volume(self, volume):
        """
        Set speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            if self.engine and 0.0 <= volume <= 1.0:
                self.engine.setProperty('volume', volume)
                logger.info(f"Speech volume set to {volume}")
                return True
            else:
                logger.warning(f"Invalid volume level: {volume}")
                return False
        except Exception as e:
            logger.error(f"Error setting speech volume: {e}")
            return False
    
    def get_available_voices(self):
        """
        Get list of available voices
        
        Returns:
            list: List of available voice information
        """
        try:
            if not self.engine:
                return []
            
            try:
                voices = self.engine.getProperty('voices')
                voice_list = []
                
                if voices:
                    for voice in voices:
                        voice_info = {
                            'id': voice.id,
                            'name': voice.name,
                            'language': getattr(voice, 'languages', ['Unknown'])[0] if hasattr(voice, 'languages') else 'Unknown',
                            'gender': getattr(voice, 'gender', 'Unknown')
                        }
                        voice_list.append(voice_info)
                
                return voice_list
            except (TypeError, AttributeError):
                logger.error("Error getting available voices")
                return []
            
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def set_voice(self, voice_id):
        """
        Set the voice for speech synthesis
        
        Args:
            voice_id: Voice ID to use
            
        Returns:
            bool: True if voice was set successfully
        """
        try:
            if not self.engine:
                return False
            
            try:
                voices = self.engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if voice.id == voice_id:
                            self.engine.setProperty('voice', voice_id)
                            logger.info(f"Voice set to: {voice.name}")
                            return True
            except (TypeError, AttributeError):
                logger.error("Error setting voice")
            
            logger.warning(f"Voice ID not found: {voice_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def is_engine_available(self):
        """
        Check if TTS engine is available and working
        
        Returns:
            bool: True if engine is available
        """
        return self.engine is not None
    
    def get_engine_status(self):
        """
        Get current engine status
        
        Returns:
            dict: Engine status information
        """
        try:
            status = {
                'engine_available': self.is_engine_available(),
                'is_speaking': self.is_speaking,
                'queue_size': self.speech_queue.qsize(),
                'worker_active': self.speech_thread.is_alive() if self.speech_thread else False
            }
            
            if self.engine:
                try:
                    voices = self.engine.getProperty('voices')
                    voice_count = len(voices) if voices else 0
                    status.update({
                        'rate': self.engine.getProperty('rate'),
                        'volume': self.engine.getProperty('volume'),
                        'voice_count': voice_count
                    })
                except (TypeError, AttributeError):
                    status.update({
                        'rate': 'Unknown',
                        'volume': 'Unknown',
                        'voice_count': 0
                    })
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting engine status: {e}")
            return {'engine_available': False, 'error': str(e)}
    
    def shutdown(self):
        """Shutdown the speech synthesis system"""
        try:
            logger.info("Shutting down speech synthesis system...")
            
            # Stop worker thread
            self.stop_flag.set()
            
            # Clear queue
            self.clear_speech_queue()
            
            # Stop current speech
            self.stop_current_speech()
            
            # Wait for worker thread to finish
            if self.speech_thread and self.speech_thread.is_alive():
                self.speech_thread.join(timeout=2.0)
            
            # Cleanup engine
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
                self.engine = None
            
            logger.info("Speech synthesis system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test the speech synthesis system
    print("Testing Speech Synthesis System...")
    
    speech = SpeechSynthesis()
    
    if speech.is_engine_available():
        print("TTS engine is available")
        
        # Test basic speech
        speech.speak("Hello, this is a test of the speech synthesis system.")
        time.sleep(3)
        
        # Test immediate speech
        speech.speak_immediately("This is immediate speech.")
        time.sleep(2)
        
        # Test status
        status = speech.get_engine_status()
        print(f"Engine status: {status}")
        
        # Test available voices
        voices = speech.get_available_voices()
        print(f"Available voices: {len(voices)}")
        for voice in voices[:3]:  # Show first 3 voices
            print(f"  - {voice['name']} ({voice['language']})")
    else:
        print("TTS engine is not available")
    
    # Cleanup
    speech.shutdown()
    print("Test completed")