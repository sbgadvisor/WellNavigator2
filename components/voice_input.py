"""
Voice input component for Streamlit.
Provides push-to-talk functionality with audio recording and transcription.
"""

import streamlit as st
from typing import Optional, Callable
import base64


def voice_input_component(
    key: str = "voice_input",
    callback: Optional[Callable[[str], None]] = None,
    placeholder: str = "Hold to record...",
    button_text: str = "🎤 Hold to Talk",
    disabled: bool = False
) -> Optional[str]:
    """
    Voice input component with push-to-talk functionality.
    
    Args:
        key: Unique key for the component
        callback: Function to call with transcribed text
        placeholder: Placeholder text for the input
        button_text: Text for the voice button
        disabled: Whether the component is disabled
        
    Returns:
        Transcribed text if available, None otherwise
    """
    
    # HTML/CSS/JS for voice recording
    voice_component_html = f"""
    <div id="voice-input-{key}">
        <style>
            .voice-container {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 10px 0;
            }}
            
            .voice-button {{
                background: {'#ff4444' if disabled else '#4CAF50'};
                border: none;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: {'not-allowed' if disabled else 'pointer'};
                font-size: 14px;
                font-weight: bold;
                transition: all 0.3s;
                user-select: none;
            }}
            
            .voice-button:hover {{
                background: {'#ff4444' if disabled else '#45a049'};
                transform: {'none' if disabled else 'scale(1.05)'};
            }}
            
            .voice-button:active {{
                background: {'#ff4444' if disabled else '#3d8b40'};
                transform: {'none' if disabled else 'scale(0.95)'};
            }}
            
            .voice-status {{
                font-size: 12px;
                color: #666;
                font-style: italic;
            }}
            
            .recording-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                background: #ff4444;
                border-radius: 50%;
                animation: pulse 1s infinite;
                margin-right: 5px;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
        </style>
        
        <div class="voice-container">
            <button 
                class="voice-button" 
                id="voice-btn-{key}"
                {'disabled' if disabled else ''}
                onmousedown="startRecording('{key}')" 
                onmouseup="stopRecording('{key}')"
                onmouseleave="stopRecording('{key}')"
                ontouchstart="startRecording('{key}')"
                ontouchend="stopRecording('{key}')"
            >
                🎤 {button_text}
            </button>
            <span class="voice-status" id="status-{key}">
                Click and hold to record
            </span>
        </div>
    </div>

    <script>
        let mediaRecorder_{key} = null;
        let audioChunks_{key} = [];
        let isRecording_{key} = false;

        async function startRecording(key) {{
            if (isRecording_{key} || '{disabled}'.toLowerCase() === 'true') return;
            
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                mediaRecorder_{key} = new MediaRecorder(stream, {{
                    mimeType: 'audio/webm;codecs=opus'
                }});
                
                audioChunks_{key} = [];
                
                mediaRecorder_{key}.ondataavailable = (event) => {{
                    audioChunks_{key}.push(event.data);
                }};
                
                mediaRecorder_{key}.onstop = () => {{
                    const audioBlob = new Blob(audioChunks_{key}, {{ type: 'audio/webm' }});
                    processAudio(audioBlob, key);
                    stream.getTracks().forEach(track => track.stop());
                }};
                
                mediaRecorder_{key}.start();
                isRecording_{key} = true;
                
                document.getElementById('voice-btn-{key}').style.background = '#ff4444';
                document.getElementById('voice-btn-{key}').innerHTML = '🔴 Recording...';
                document.getElementById('status-{key}').innerHTML = '<span class="recording-indicator"></span>Recording... Release to stop';
                
            }} catch (error) {{
                console.error('Error accessing microphone:', error);
                document.getElementById('status-{key}').innerHTML = '❌ Microphone access denied';
            }}
        }}

        function stopRecording(key) {{
            if (!isRecording_{key}) return;
            
            if (mediaRecorder_{key} && mediaRecorder_{key}.state === 'recording') {{
                mediaRecorder_{key}.stop();
            }}
            
            isRecording_{key} = false;
            
            document.getElementById('voice-btn-{key}').style.background = '#4CAF50';
            document.getElementById('voice-btn-{key}').innerHTML = '🎤 Hold to Talk';
            document.getElementById('status-{key}').innerHTML = 'Processing audio...';
        }}

        async function processAudio(audioBlob, key) {{
            try {{
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.webm');
                
                // Send audio to Streamlit
                const response = await fetch('/upload_audio', {{
                    method: 'POST',
                    body: formData
                }});
                
                if (response.ok) {{
                    document.getElementById('status-{key}').innerHTML = '✅ Audio processed successfully';
                }} else {{
                    document.getElementById('status-{key}').innerHTML = '❌ Processing failed';
                }}
                
            }} catch (error) {{
                console.error('Error processing audio:', error);
                document.getElementById('status-{key}').innerHTML = '❌ Upload failed';
            }}
        }}
    </script>
    """
    
    # Render the voice component
    st.components.v1.html(voice_component_html, height=100)
    
    # Check for audio data in session state
    audio_key = f"audio_data_{key}"
    if audio_key in st.session_state:
        audio_data = st.session_state[audio_key]
        del st.session_state[audio_key]  # Clear after processing
        
        # Import here to avoid circular imports
        from core.voice import transcribe_audio_file
        
        # Transcribe the audio
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio_file(audio_data, f"audio_{key}.webm")
        
        if transcript:
            st.success(f"🎤 Transcribed: {transcript}")
            if callback:
                callback(transcript)
            return transcript
        else:
            st.error("❌ Transcription failed")
    
    return None


def simple_voice_button(key: str = "simple_voice") -> Optional[str]:
    """
    Simplified voice input button for quick integration.
    
    Args:
        key: Unique key for the component
        
    Returns:
        Transcribed text if available, None otherwise
    """
    
    # Create a simple file uploader for audio
    audio_file = st.file_uploader(
        "🎤 Upload Audio",
        type=['webm', 'mp3', 'wav', 'm4a'],
        key=f"audio_upload_{key}",
        help="Record audio on your device and upload for transcription"
    )
    
    if audio_file is not None:
        # Read audio data
        audio_data = audio_file.read()
        
        # Import here to avoid circular imports
        from core.voice import transcribe_audio_file
        
        # Transcribe
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio_file(audio_data, audio_file.name)
        
        if transcript:
            st.success(f"🎤 Transcribed: {transcript}")
            return transcript
        else:
            st.error("❌ Transcription failed")
    
    return None
