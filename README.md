# 🏥 WellNavigator - AI Health Information Assistant

> **Production-ready POC** for an empathetic AI health assistant that helps users understand health information, prepare for doctor visits, and navigate healthcare systems.

[![Status](https://img.shields.io/badge/status-production--ready-green)]()
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-blue)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue)]()
[![Streamlit](https://img.shields.io/badge/streamlit-1.29+-red)]()

## 🎯 **What is WellNavigator?**

WellNavigator is an AI-powered health information assistant that:
- ✅ **Educates** - Explains health conditions in plain language
- ✅ **Prepares** - Helps users get ready for doctor appointments
- ✅ **Navigates** - Guides through healthcare systems and processes
- ✅ **Empowers** - Provides actionable next steps and questions
- ✅ **Protects** - Multi-layer safety system prevents harmful guidance
- ✅ **Cites** - Transparent source attribution for all information

**What it is NOT:**
- ❌ Not a diagnostic tool
- ❌ Not a prescription service
- ❌ Not a replacement for healthcare providers
- ❌ Not for medical emergencies (always call 911)

## ⚡ **Quick Start**

```bash
# 1. Clone and navigate
git clone <repository>
cd V2-WellNavigator

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Build knowledge base (optional but recommended)
python ingest.py

# 6. Run the app
streamlit run app.py

# 7. Open browser
# Visit: http://localhost:8501 (or port shown in terminal)
```

## 🚀 **Complete Feature Set**

### **Core Chat Interface**
- **Real-time Streaming** - Token-by-token LLM responses
- **Conversation History** - Full context maintained
- **Suggested Prompts** - 8 clickable health questions
- **Multiple Models** - GPT-4o, 4o-mini, 4-turbo, 3.5-turbo
- **Adjustable Temperature** - Control response creativity

### **Safety & Compliance** 🛡️
- **Emergency Detection** - Immediate 911 escalation (70+ keywords)
- **Diagnostic Refusal** - Won't diagnose medical conditions
- **Prescription Blocking** - Refuses medication advice
- **Self-Harm Support** - Crisis resources (988, 741741)
- **Illicit Request Blocking** - Substance abuse resources
- **PI Redaction** - Auto-removes SSN, cards, phones, emails
- **Medical Disclaimers** - Clear boundaries on all interactions

### **Context Enhancement**
- **RAG Knowledge Base** - 7 documents, 167 chunks, FAISS indexing
- **Web Search** - Curated health sources (Mayo Clinic, WebMD, CDC)
- **Source Citations** - Inline [KB1] [Web1] references
- **Context Injection** - Relevant info in system prompt

### **Voice & Coaching** 🎤🎧
- **Voice Input** - Whisper transcription (WebM, MP3, WAV, M4A)
- **Listening Mode** - Live notes capture with timestamps
- **Coach Suggestions** - 7 health topic categories, priority-based
- **Session Tracking** - Conversation insights and patterns

### **Observability & Management** 📊
- **JSON Lines Logging** - Every turn logged to `/logs/`
- **Session Metrics** - Requests, tokens, cost, latency, features
- **Token Limits** - Soft cap (50K tokens) with gentle nudges
- **Visual Indicators** - 🟢🟡🔴 status for usage levels
- **Cost Tracking** - Real-time cost estimation

## 📋 **System Requirements**

- Python 3.9 or higher
- OpenAI API key (required)
- Google Custom Search API (optional, uses stubs by default)
- 4GB RAM minimum
- Internet connection

## 🏗️ **Architecture**

```
User Input → PI Redaction → Safety Check → Context Retrieval (RAG + Search)
    ↓
LLM Processing (OpenAI GPT) → Response + Citations
    ↓
Listening Mode (optional) → Logging → Session Metrics
```

### **Directory Structure**
```
V2-WellNavigator/
├── app.py                    # Main Streamlit application
├── ingest.py                 # Knowledge base ingestion
├── requirements.txt          # Python dependencies
├── .env                      # API keys (create from env.example)
├── /core/                    # Core modules
│   ├── llm.py               # OpenAI streaming
│   ├── prompts.py           # System prompts & context
│   ├── safety.py            # Safety checks & PI redaction
│   ├── rag.py               # Knowledge base retrieval
│   ├── search.py            # Web search interface
│   ├── voice.py             # Audio transcription
│   └── observe.py           # Logging & metrics
├── /components/             # UI components
│   ├── voice_input.py      # Voice input interface
│   └── listening_mode.py   # Listening mode panel
├── /data/
│   ├── corpus/             # Source documents (7 .md files)
│   └── index/              # FAISS index & metadata
└── /logs/                  # JSON lines logs (auto-created)
```

## 📊 **Key Statistics**

- **Knowledge Base:** 7 documents, 167 semantic chunks
- **Safety Keywords:** 130+ patterns across 5 categories
- **Models Supported:** 4 OpenAI models
- **Token Limit:** 50,000 per session (configurable)
- **Cost Range:** $0.0002 - $0.003 per turn
- **Search Sources:** 7+ curated health organizations
- **Coach Suggestions:** 7 health topic categories

## 🧪 **Testing**

See detailed test guides:
- `TEST_SAFETY.md` - Safety and refusal testing
- `TEST_RAG.md` - Knowledge base testing
- `TEST_SEARCH.md` - Web search testing
- `TEST_VOICE.md` - Voice input and listening mode

**Quick Test:**
```bash
# Test basic query
"What are the symptoms of diabetes?"
→ Should return comprehensive answer with RAG + Search citations

# Test emergency detection
"I'm having chest pain"
→ Should show 911 emergency escalation

# Test diagnostic refusal
"Do I have diabetes?"
→ Should refuse and suggest seeing healthcare provider
```

## 📖 **Documentation**

- **`SETUP.md`** - Detailed installation guide
- **`COMPLETE_FEATURE_SET.md`** - All features overview
- **`SAFETY_IMPLEMENTATION.md`** - Safety system details
- **`RAG_IMPLEMENTATION.md`** - Knowledge base technical docs
- **`SEARCH_IMPLEMENTATION.md`** - Web search system
- **`VOICE_IMPLEMENTATION.md`** - Voice & listening mode
- **`OBSERVABILITY_IMPLEMENTATION.md`** - Logging & metrics

## 🛡️ **Safety First**

WellNavigator is designed with multiple safety layers:

1. **Pre-LLM Safety Check** - Blocks unsafe queries before API call
2. **PI Redaction** - Removes sensitive personal information
3. **Refusal Templates** - Clear, helpful refusal messages
4. **Emergency Escalation** - Immediate 911 directive when needed
5. **Crisis Resources** - Mental health support (988, 741741)
6. **Medical Disclaimers** - Clear limitations communicated
7. **Token Limits** - Prevents runaway costs

## 💰 **Cost Management**

- **Refusals:** $0 (no API call)
- **Safety Blocks:** $0 (no API call)
- **Token Limits:** $0 when exceeded
- **GPT-4o-mini:** ~$0.0002 per turn (typical)
- **GPT-4o:** ~$0.002 per turn (typical)
- **Session Tracking:** Real-time cost display
- **Soft Caps:** 50K token limit with warnings

## 🔐 **Privacy & Compliance**

**POC Privacy Notice:**
- ✅ Session-only data (no persistence)
- ✅ No PHI stored in this POC
- ✅ PI automatically redacted
- ✅ Logs are git-ignored
- ✅ No external data sharing

**For Production:**
- [ ] HIPAA compliance review
- [ ] Encrypted data storage
- [ ] Audit logging
- [ ] User authentication
- [ ] Data retention policies

## 🎯 **Use Cases**

### **1. Doctor Visit Preparation**
```
Query: "Help me prepare for my diabetes follow-up appointment"
→ Comprehensive checklist of questions to ask, information to bring
```

### **2. Health Education**
```
Query: "Explain hypertension in simple terms"
→ Plain-language explanation with lifestyle recommendations
```

### **3. Test Results Understanding**
```
Query: "What questions should I ask about my blood work?"
→ List of relevant questions for healthcare provider
```

### **4. Healthcare Navigation**
```
Query: "How do I find the right specialist for my condition?"
→ Step-by-step guide to specialist referrals
```

### **5. Insurance Guidance**
```
Query: "What does this insurance EOB mean?"
→ Explanation of insurance terms and next steps
```

## 🚦 **System Status**

- ✅ **Core Chat** - Production ready
- ✅ **LLM Integration** - Fully functional
- ✅ **Safety System** - Comprehensive
- ✅ **RAG Knowledge Base** - 167 chunks indexed
- ✅ **Web Search** - Stub mode (API ready)
- ✅ **Voice Input** - File upload transcription
- ✅ **Listening Mode** - Live notes & coaching
- ✅ **Observability** - Logging & metrics active
- ✅ **Documentation** - Complete

## 🔮 **Future Enhancements**

### **Phase 2:**
- Real-time audio (browser push-to-talk)
- Advanced AI coaching (LLM-powered)
- Real Google Search integration
- Semantic safety classification

### **Phase 3:**
- HIPAA compliance certification
- User authentication & profiles
- Encrypted storage
- Audit logging dashboard
- Mobile applications

## 🤝 **Contributing**

This is a proof-of-concept system. For production deployment:

1. **Security audit** - Review all safety mechanisms
2. **Legal review** - Verify disclaimers and compliance
3. **HIPAA assessment** - Healthcare data handling
4. **Performance testing** - Load and stress tests
5. **User testing** - Gather feedback and iterate

## 📞 **Emergency Resources**

**Always available:**
- **911** - Medical emergencies
- **988** - Suicide & Crisis Lifeline
- **741741** - Crisis Text Line (text HOME)
- **1-800-662-4357** - SAMHSA National Helpline

## 📄 **License**

See LICENSE file for details.

## 🙏 **Acknowledgments**

Built with:
- OpenAI GPT models
- Streamlit framework
- FAISS vector search
- Sentence Transformers
- Python ecosystem

---

**⚠️ Important Reminder:**

WellNavigator provides **educational health information only**. It is **not a substitute for professional medical advice, diagnosis, or treatment**. Always consult with qualified healthcare providers about your specific health concerns. In emergencies, call 911 immediately.

---

**Status:** ✅ Production-Ready POC  
**Version:** 1.0  
**Last Updated:** October 2025

For questions, issues, or suggestions, see documentation files or contact the development team.

🏥 **WellNavigator - Empowering health literacy, one conversation at a time.** 🤖