# WellNavigator - Quick Start Guide

## ⚡ Get Running in 3 Steps

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Configure OpenAI API Key
```bash
# Copy template
cp env.example .env

# Edit .env and add your key
nano .env
```

In `.env`:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Get your API key**: https://platform.openai.com/api-keys

### 3️⃣ Run the App
```bash
streamlit run app.py
```

Opens at: http://localhost:8501

## 🎯 What You'll See

### Homepage
- **Disclaimer banner** at top (911 emergency notice)
- **6 suggested prompt tiles** to get started
- **Sidebar** with model selection, temperature, toggles, metrics
- **Chat input** at bottom

### Try These Prompts

✅ **Allowed:**
```
"What questions should I ask my doctor about diabetes?"
"Help me understand cholesterol test results"
"What lifestyle changes support heart health?"
```

❌ **Safety Blocked:**
```
"I'm having chest pain" → Emergency escalation
"Do I have diabetes?" → Diagnostic refusal
"What medication should I take?" → Prescription refusal
```

### Watch the Metrics

Sidebar shows in real-time:
- **Tokens In**: Input token count
- **Tokens Out**: Output token count  
- **Cost**: API cost in USD
- **Latency**: Response time

## 🎛️ Controls

### Model Selection
- **gpt-4o-mini** (default) - Fast, $0.0002/turn
- **gpt-4o** - Best quality, $0.003/turn
- **gpt-3.5-turbo** - Fastest, $0.0005/turn

### Temperature
- **0.0-0.3**: Focused, factual
- **0.4-0.7**: Balanced (default: 0.7)
- **0.8-2.0**: Creative, varied

### Toggles
- **Google Search**: Ready (not connected yet)
- **RAG Vector Store**: Ready (not connected yet)

## 🔧 Troubleshooting

### "OPENAI_API_KEY not found"
- Check `.env` file exists in project root
- Verify key format: `OPENAI_API_KEY=sk-...`
- Restart Streamlit

### "Error calling OpenAI API"
- Verify API key is valid
- Check account has credits
- Try different model (gpt-4o-mini)

### "Module not found"
```bash
pip install -r requirements.txt
```

## 📚 Documentation

- **SETUP.md** - Detailed setup and testing
- **LLM_INTEGRATION.md** - Technical docs for LLM
- **README.md** - Full project overview
- **docs/chatbot-POC-brief.md** - Project requirements

## ✅ What's Working

- ✅ Real-time AI streaming responses
- ✅ Safety guardrails (emergency, diagnostic, prescription)
- ✅ PI redaction (SSN, credit cards, phones, emails)
- ✅ Token counting and cost tracking
- ✅ Conversation history
- ✅ Suggested prompts
- ✅ Model and temperature controls

## 🚧 Coming Next

- RAG vector store integration
- Google Search connector
- Voice input (push-to-talk)

## 💰 Cost Estimates

Typical conversation (165 tokens in, 255 tokens out):

| Model | Per Turn | 100 Turns |
|-------|----------|-----------|
| gpt-4o-mini | $0.0002 | $0.02 |
| gpt-3.5-turbo | $0.0005 | $0.05 |
| gpt-4o | $0.003 | $0.30 |

**Recommendation**: Use `gpt-4o-mini` for development.

## 🎉 You're All Set!

The app is ready to provide empathetic health guidance with:
- Real AI responses from OpenAI
- Safety-first design
- Cost transparency
- Professional quality

**Need help?** Check SETUP.md for detailed testing instructions.

