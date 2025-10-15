# ☁️ Quick Streamlit Cloud Setup Guide

## 🎯 5-Minute Deployment

### Step 1: Create GitHub Repository (2 min)

```bash
# Run the automated setup script
./GITHUB_SETUP.sh

# Or manually:
git init
git add .
git commit -m "Initial commit: WellNavigator"
git remote add origin https://github.com/YOUR_USERNAME/wellnavigator.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud (2 min)

1. **Go to:** https://share.streamlit.io/
2. **Click:** "New app"
3. **Select:**
   - Repository: `YOUR_USERNAME/wellnavigator`
   - Branch: `main`
   - Main file: `app.py`
   - App URL: Choose a name (e.g., `wellnavigator`)

### Step 3: Add Secrets (1 min)

Click "Advanced settings" → "Secrets" and add:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

### Step 4: Deploy!

Click "Deploy" and wait 2-3 minutes.

## 🎉 Done!

Your app will be live at: `https://your-app-name.streamlit.app`

## ⚡ Quick Commands

```bash
# Push updates
git add .
git commit -m "Update message"
git push

# Add knowledge base
python ingest.py
git add -f data/index/
git commit -m "Add FAISS index"
git push
```

## 🔧 Streamlit Cloud Secrets

In your app settings → Secrets, add:

```toml
# Required
OPENAI_API_KEY = "sk-proj-..."

# Optional
GOOGLE_API_KEY = "AIza..."
GOOGLE_CSE_ID = "012345..."
MAX_TOKENS_PER_SESSION = "50000"
```

## ✅ Test Checklist

- [ ] App loads without errors
- [ ] Chat responds with streaming
- [ ] Suggested prompts work
- [ ] Safety refusals trigger
- [ ] RAG toggle shows status
- [ ] Metrics display in sidebar
- [ ] Voice input uploads work

## 🐛 Common Issues

**"ModuleNotFoundError"**
→ Check `requirements.txt` has all dependencies

**"RAG Not Available"**
→ Run `python ingest.py` locally, push index to GitHub

**"OpenAI client not available"**
→ Check Secrets in Streamlit Cloud settings

**Slow performance**
→ Normal for free tier, consider upgrading

## 📊 Monitor Your App

- **Dashboard:** https://share.streamlit.io/
- **Logs:** Click your app → "⋮" → "Logs"
- **Analytics:** View usage statistics
- **OpenAI Usage:** https://platform.openai.com/usage

## 🎯 Next Steps

1. Share your app URL with users
2. Gather feedback
3. Monitor usage and costs
4. Iterate and improve!

**Your app is now live! 🚀**

