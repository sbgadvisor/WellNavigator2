"""
Voice input module for WellNavigator.
Handles audio recording, transcription, and listening mode functionality.
"""

import os
import io
import time
import base64
from typing import Optional, Dict, List, Any
import streamlit as st

try:
    import openai
except ImportError:
    openai = None


class VoiceTranscriber:
    """Handles audio transcription using OpenAI Whisper."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client for transcription."""
        if openai is None:
            print("❌ OpenAI library not available")
            return
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found")
            return
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            print(f"❌ Error initializing OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if transcription is available."""
        return self.client is not None
    
    def transcribe_audio(self, audio_data: bytes, filename: str = "audio.webm") -> Optional[str]:
        """
        Transcribe audio data using OpenAI Whisper.
        
        Args:
            audio_data: Raw audio data bytes
            filename: Audio filename (used for format detection)
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            # Create audio file object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename
            
            # Transcribe using OpenAI Whisper
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"  # Optional: specify language for better accuracy
            )
            
            return transcript.text.strip()
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None


class ListeningModeDemo:
    """Demo listening mode with live notes and coach suggestions."""
    
    def __init__(self):
        self.session_key = "listening_mode_data"
        self._initialize_session_data()
    
    def _initialize_session_data(self):
        """Initialize session data for listening mode."""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                "live_notes": [],
                "coach_suggestions": [],
                "session_start_time": time.time(),
                "total_messages": 0
            }
    
    def add_user_message(self, message: str):
        """Add user message to live notes."""
        if not message.strip():
            return
        
        timestamp = time.strftime("%H:%M:%S")
        note = {
            "timestamp": timestamp,
            "content": message,
            "type": "user_message"
        }
        
        st.session_state[self.session_key]["live_notes"].append(note)
        st.session_state[self.session_key]["total_messages"] += 1
        
        # Generate coach suggestions based on message content
        self._generate_coach_suggestions(message)
    
    def _generate_coach_suggestions(self, message: str):
        """Generate coach suggestions based on message content."""
        suggestions = []
        message_lower = message.lower()
        
        # Health condition detection
        if any(term in message_lower for term in ['diabetes', 'blood sugar', 'insulin']):
            suggestions.append({
                "title": "Diabetes Management",
                "content": "Consider asking about blood sugar monitoring, medication adherence, and lifestyle modifications.",
                "icon": "🩺",
                "priority": "high"
            })
        
        if any(term in message_lower for term in ['blood pressure', 'hypertension', 'high bp']):
            suggestions.append({
                "title": "Blood Pressure Control",
                "content": "Discuss lifestyle changes, medication timing, and home monitoring techniques.",
                "icon": "❤️",
                "priority": "high"
            })
        
        # Appointment preparation
        if any(term in message_lower for term in ['doctor', 'appointment', 'visit', 'see']):
            suggestions.append({
                "title": "Appointment Preparation",
                "content": "Prepare questions, bring medication list, and consider bringing a support person.",
                "icon": "📅",
                "priority": "medium"
            })
        
        # Medication concerns
        if any(term in message_lower for term in ['medication', 'medicine', 'drug', 'side effect']):
            suggestions.append({
                "title": "Medication Review",
                "content": "Discuss effectiveness, side effects, interactions, and adherence strategies.",
                "icon": "💊",
                "priority": "high"
            })
        
        # Test results
        if any(term in message_lower for term in ['test', 'result', 'lab', 'blood work']):
            suggestions.append({
                "title": "Test Results Discussion",
                "content": "Ask for explanations in plain language, understand normal ranges, and clarify next steps.",
                "icon": "🔬",
                "priority": "medium"
            })
        
        # Lifestyle factors
        if any(term in message_lower for term in ['diet', 'exercise', 'sleep', 'stress']):
            suggestions.append({
                "title": "Lifestyle Optimization",
                "content": "Focus on sustainable changes, gradual improvements, and realistic goal setting.",
                "icon": "🌱",
                "priority": "medium"
            })
        
        # Insurance/cost concerns
        if any(term in message_lower for term in ['insurance', 'cost', 'bill', 'afford', 'expensive']):
            suggestions.append({
                "title": "Financial Resources",
                "content": "Explore insurance benefits, patient assistance programs, and generic alternatives.",
                "icon": "💰",
                "priority": "medium"
            })
        
        # Add unique suggestions to session data
        for suggestion in suggestions:
            if suggestion not in st.session_state[self.session_key]["coach_suggestions"]:
                st.session_state[self.session_key]["coach_suggestions"].append(suggestion)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get listening mode session statistics."""
        data = st.session_state[self.session_key]
        session_duration = time.time() - data["session_start_time"]
        
        return {
            "duration_minutes": round(session_duration / 60, 1),
            "total_messages": data["total_messages"],
            "notes_count": len(data["live_notes"]),
            "suggestions_count": len(data["coach_suggestions"])
        }
    
    def clear_session(self):
        """Clear listening mode session data."""
        st.session_state[self.session_key] = {
            "live_notes": [],
            "coach_suggestions": [],
            "session_start_time": time.time(),
            "total_messages": 0
        }


# Global instances
_transcriber = None
_listening_mode = None

def get_transcriber() -> VoiceTranscriber:
    """Get or create global transcriber instance."""
    global _transcriber
    if _transcriber is None:
        _transcriber = VoiceTranscriber()
    return _transcriber

def get_listening_mode() -> ListeningModeDemo:
    """Get or create global listening mode instance."""
    global _listening_mode
    if _listening_mode is None:
        _listening_mode = ListeningModeDemo()
    return _listening_mode

def is_voice_available() -> bool:
    """Check if voice transcription is available."""
    transcriber = get_transcriber()
    return transcriber.is_available()

def transcribe_audio_file(audio_data: bytes, filename: str = "audio.webm") -> Optional[str]:
    """Convenience function for audio transcription."""
    transcriber = get_transcriber()
    return transcriber.transcribe_audio(audio_data, filename)

def add_to_listening_mode(message: str):
    """Add message to listening mode live notes."""
    listening_mode = get_listening_mode()
    listening_mode.add_user_message(message)
