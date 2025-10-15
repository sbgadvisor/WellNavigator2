# Testing Voice Input & Listening Mode

## 🧪 Quick Test Guide

The voice input and listening mode features are now live! Here's how to test them:

### **1. Verify Voice Input Status**

In the Streamlit app sidebar, you should see:
```
Enable Voice Input - ❌ Not configured
[Toggle is disabled]
```

This is expected - voice input requires OpenAI API key for Whisper transcription.

### **2. Test Voice Input (File Upload)**

**Enable Voice Input:**
1. Toggle "Enable Voice Input - ❌ Not configured" (if API key is available)
2. Or test with the toggle disabled to see the interface

**Upload Audio:**
1. Look for "🎤 Voice Input" section above chat input
2. Click "Upload Audio" file picker
3. Select an audio file (WebM, MP3, WAV, M4A)
4. Wait for transcription to complete
5. Transcribed text appears in chat input

**Test Files:**
- Record yourself saying: "I have diabetes and need help"
- Or use any audio file with speech
- Supported formats: WebM, MP3, WAV, M4A

### **3. Test Listening Mode**

**Enable Listening Mode:**
1. Toggle "Enable Listening Mode" in sidebar
2. You should see "✅ Listening mode active"
3. Session stats appear: Duration, Messages, Suggestions

**Start Chatting:**
1. Type or voice input: "I have diabetes and high blood pressure"
2. Get a response from the chatbot
3. The message is automatically captured in listening mode

**View Panel:**
1. Click "📊 View Panel" in sidebar
2. See the listening mode panel with:
   - Live notes with timestamps
   - Coach suggestions cards
   - Session statistics

### **4. Test Coach Suggestions**

**Health Topic Detection:**
Try these phrases to trigger suggestions:

```
"I have diabetes" → Diabetes Management suggestion
"My blood pressure is high" → Blood Pressure Control suggestion  
"I have a doctor appointment" → Appointment Preparation suggestion
"I'm taking medication" → Medication Review suggestion
"I got test results" → Test Results Discussion suggestion
"I need to exercise more" → Lifestyle Optimization suggestion
"I can't afford my medication" → Financial Resources suggestion
```

**Expected Results:**
- **High Priority** (red cards): Diabetes, Blood Pressure, Medication
- **Medium Priority** (green cards): Appointments, Tests, Lifestyle, Insurance

### **5. Test Combined Features**

**Full Workflow:**
1. Enable both Voice Input and Listening Mode
2. Upload audio: "I have diabetes and need help managing it"
3. Transcribed text appears in chat input
4. Send the message
5. Get response with RAG + Search context
6. View listening mode panel
7. See live notes and "Diabetes Management" suggestion

### **6. Test Session Management**

**Session Stats:**
- Duration updates in real-time
- Message count increments with each user message
- Suggestions accumulate based on conversation topics

**Clear Session:**
1. Click "🗑️ Clear Session" in sidebar
2. All notes and suggestions are cleared
3. Session timer resets
4. Message count resets to 0

### **7. Test UI States**

**Voice Input States:**
- **Disabled**: "❌ Not configured" (no API key)
- **Enabled**: "✅ Available" (with API key)
- **Uploading**: Shows file picker
- **Processing**: "Transcribing audio..." spinner
- **Success**: "🎤 Transcribed: [text]"
- **Error**: "❌ Transcription failed"

**Listening Mode States:**
- **Inactive**: "💤 Listening mode inactive"
- **Active**: "✅ Listening mode active"
- **Panel Open**: Full listening mode panel visible
- **Panel Closed**: Hidden, accessible via "📊 View Panel"

## 🎯 Expected Results

### **Voice Input Test**
```
Input: Audio file "help-me.webm"
Expected: "🎤 Transcribed: I need help with my diabetes"
Status: Text appears in chat input field
```

### **Listening Mode Test**
```
Input: "I have diabetes and high blood pressure"
Expected Panel:
- Live Notes: "14:23:45 - I have diabetes and high blood pressure"
- Suggestions: 
  🔥 Diabetes Management (high priority)
  🔥 Blood Pressure Control (high priority)
- Stats: 1 message, 2 suggestions
```

### **Coach Suggestions Test**
```
Input: "I'm taking metformin for diabetes"
Expected:
- Live note captured with timestamp
- "Medication Review" suggestion (high priority)
- "Diabetes Management" suggestion (high priority)
- Red suggestion cards with medication icon 💊
```

## ✅ Success Indicators

- ✅ Voice input toggle shows correct status
- ✅ Audio file upload works (even without API key)
- ✅ Listening mode captures user messages
- ✅ Coach suggestions appear based on content
- ✅ Suggestion cards are color-coded (red/green)
- ✅ Session stats update in real-time
- ✅ Panel opens/closes correctly
- ✅ Clear session resets all data

## 🔧 Troubleshooting

### **Voice Input Issues**
- **No file picker**: Check if voice input is enabled
- **Transcription fails**: Verify OpenAI API key is set
- **Wrong format**: Use WebM, MP3, WAV, or M4A files

### **Listening Mode Issues**
- **No notes captured**: Ensure listening mode is enabled
- **No suggestions**: Try health-related keywords
- **Panel not opening**: Click "📊 View Panel" button

### **Coach Suggestions Issues**
- **No suggestions**: Use health-related terms
- **Wrong suggestions**: Check keyword matching
- **Cards not appearing**: Refresh the panel

## 🚀 Advanced Testing

### **Multi-Message Session**
1. Enable listening mode
2. Send multiple health-related messages
3. Watch suggestions accumulate
4. Verify session stats update
5. Check live notes scroll correctly

### **Mixed Content**
1. Send non-health messages
2. Send health messages
3. Verify only health messages trigger suggestions
4. Check that all messages appear in live notes

### **Long Session**
1. Chat for 5+ minutes
2. Send 10+ messages
3. Verify performance remains good
4. Check memory usage doesn't grow excessively

## 🎉 Ready for Production

The voice input and listening mode system provides:

- **Easy voice interaction** - Simple file upload approach
- **Live conversation tracking** - Automatic message capture
- **Smart coaching** - Context-aware health suggestions
- **Professional UI** - Clean, intuitive interface
- **Session management** - Persistent state tracking
- **Error resilience** - Works without API keys

Test it out and see how it enhances the WellNavigator experience! 🎤🎧

---

**Current Status:** ✅ Voice Input & Listening Mode Complete  
**App Running:** http://localhost:8504  
**Features:** File upload transcription + live notes + coach suggestions
