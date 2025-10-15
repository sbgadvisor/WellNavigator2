# 🚀 Deploying WellNavigator to Streamlit Cloud

## Prerequisites

1. **GitHub Account** - Create one at https://github.com
2. **Streamlit Cloud Account** - Sign up at https://streamlit.io/cloud
3. **OpenAI API Key** - Get from https://platform.openai.com/api-keys

## 📦 Step 1: Push to GitHub

### Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `wellnavigator` (or your choice)
3. Description: "AI-powered health information assistant"
4. Choose: **Public** or **Private** (your choice)
5. **Do NOT** initialize with README (we have one)
6. Click "Create repository"

### Initialize Git and Push

Run these commands in your terminal:

```bash
# Navigate to project directory
cd "/Users/sbg/VSCode - Workspaces/V2 - WellNavigator"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: WellNavigator POC - Production ready"

# Add your GitHub repository as remote
# Replace YOUR_USERNAME and REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Alternative: Using GitHub Desktop

1. Download GitHub Desktop: https://desktop.github.com/
2. Open GitHub Desktop
3. File → Add Local Repository
4. Choose: `/Users/sbg/VSCode - Workspaces/V2 - WellNavigator`
5. Click "Publish repository"
6. Choose public/private and click "Publish"

## ☁️ Step 2: Deploy to Streamlit Cloud

### Connect to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app" or "Deploy an app"
3. Connect your GitHub account (if not already connected)
4. Select your repository: `YOUR_USERNAME/REPO_NAME`
5. Main file path: `app.py`
6. App URL: Choose a custom URL (e.g., `wellnavigator`)

### Configure Secrets

Before deploying, you need to add your API keys:

1. In Streamlit Cloud dashboard, click your app
2. Click "⚙️ Settings" → "Secrets"
3. Add the following secrets:

```toml
# Required
OPENAI_API_KEY = "sk-your-actual-openai-api-key"

# Optional (for real Google Search)
GOOGLE_API_KEY = "your-google-api-key"
GOOGLE_CSE_ID = "your-search-engine-id"

# Optional configuration
DEBUG_MODE = "false"
MAX_TOKENS_PER_SESSION = "50000"
```

4. Click "Save"

### Deploy

1. Click "Deploy!"
2. Wait 2-5 minutes for deployment
3. Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

## 🔧 Step 3: Build Knowledge Base

Since the FAISS index is git-ignored, you need to build it after first deployment:

### Option A: Pre-build Locally (Recommended)

```bash
# Build index locally
python ingest.py

# Force add the index files
git add -f data/index/

# Commit and push
git commit -m "Add pre-built FAISS index"
git push
```

### Option B: Build on First Run

The app will show "RAG ❌ Not available" until you:
1. Clone repo locally
2. Run `python ingest.py`
3. Push index files to GitHub
4. Streamlit Cloud will auto-redeploy

## ✅ Step 4: Verify Deployment

### Test Core Features

1. **Chat Interface** - Send a test message
2. **Streaming** - Verify real-time responses
3. **RAG Toggle** - Check if knowledge base is available
4. **Search Toggle** - Should work with stub results
5. **Voice Input** - Upload an audio file
6. **Safety Checks** - Try "I have chest pain" (should refuse)
7. **Metrics** - Check sidebar for session stats

### Check Logs

In Streamlit Cloud dashboard:
1. Click "⋮" menu on your app
2. Select "Logs"
3. Verify no errors

## 🔒 Security Checklist

- [x] `.env` file in `.gitignore`
- [x] Secrets configured in Streamlit Cloud
- [x] No API keys in code
- [x] Logs directory git-ignored
- [x] PI redaction active
- [x] Safety disclaimers visible

## 📊 Monitoring

### Streamlit Cloud Metrics

Monitor your app at: https://share.streamlit.io/

- **Analytics** - View usage statistics
- **Logs** - Debug issues
- **Resources** - CPU/Memory usage
- **Secrets** - Manage API keys

### Cost Monitoring

- OpenAI API usage: https://platform.openai.com/usage
- Set billing alerts in OpenAI dashboard
- Monitor per-session token limits (50K default)

## 🐛 Troubleshooting

### Issue: "RAG Not Available"

**Solution:**
```bash
python ingest.py
git add -f data/index/
git commit -m "Add FAISS index"
git push
```

### Issue: "OpenAI client not available"

**Solution:**
1. Check Streamlit Cloud Secrets
2. Verify `OPENAI_API_KEY` is set correctly
3. No extra spaces or quotes

### Issue: App won't start

**Solution:**
1. Check logs in Streamlit Cloud
2. Verify `requirements.txt` has all dependencies
3. Check Python version compatibility

### Issue: Slow performance

**Solution:**
1. Consider upgrading to paid Streamlit plan
2. Optimize token usage
3. Reduce MAX_TOKENS_PER_SESSION

## 🔄 Updating the App

### Push Updates

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push

# Streamlit Cloud will auto-redeploy
```

### Rollback

In Streamlit Cloud:
1. Go to app settings
2. "Reboot app" to clear cache
3. Or redeploy from specific commit

## 🎯 Production Considerations

### Before Public Launch

- [ ] Review all safety disclaimers
- [ ] Test with real users
- [ ] Set up error monitoring
- [ ] Configure rate limiting
- [ ] Review HIPAA compliance needs
- [ ] Add analytics tracking
- [ ] Set up backup/disaster recovery

### Scaling Options

1. **Free Tier** - Good for POC, limited resources
2. **Paid Tier** - More resources, custom domains
3. **Enterprise** - Dedicated resources, SLA

## 📞 Support

- **Streamlit Docs:** https://docs.streamlit.io/
- **Community Forum:** https://discuss.streamlit.io/
- **GitHub Issues:** Create issues in your repo

## 🎉 Success!

Your WellNavigator app should now be live at:
**https://YOUR-APP-NAME.streamlit.app**

Share the link and gather feedback! 🚀

---

## Quick Reference Commands

```bash
# Clone and run locally
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API key
python ingest.py
streamlit run app.py

# Update deployed app
git add .
git commit -m "Your changes"
git push

# Build knowledge base
python ingest.py
git add -f data/index/
git commit -m "Update knowledge base"
git push
```

---

**Note:** Keep your API keys secure and never commit them to GitHub!

