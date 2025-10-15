#!/bin/bash

# WellNavigator GitHub Setup Script
# This script helps you push the project to GitHub

set -e  # Exit on error

echo "🏥 WellNavigator - GitHub Setup"
echo "================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first:"
    echo "   https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required"
    exit 1
fi

# Get repository name
read -p "Enter repository name (default: wellnavigator): " REPO_NAME
REPO_NAME=${REPO_NAME:-wellnavigator}

echo ""
echo "📦 Repository will be created at:"
echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
read -p "Is this correct? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "🔧 Setting up Git repository..."

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "❌ .gitignore not found. Creating..."
    cat > .gitignore << 'EOF'
# Environment variables
.env
*.env

# Python
__pycache__/
*.py[cod]
venv/
ENV/
env/

# Logs
logs/
*.log
*.jsonl

# Streamlit
.streamlit/secrets.toml

# OS
.DS_Store

# Data
data/index/*.faiss
data/index/*.pkl
EOF
    echo "✅ .gitignore created"
fi

# Add all files
echo "📁 Adding files..."
git add .

# Create initial commit
echo "💾 Creating commit..."
git commit -m "Initial commit: WellNavigator POC - Production ready" || echo "⚠️  No changes to commit"

# Set up remote
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "🔗 Setting up remote: $REMOTE_URL"

# Remove existing origin if it exists
git remote remove origin 2>/dev/null || true

# Add new origin
git remote add origin "$REMOTE_URL"

# Set main branch
git branch -M main

echo ""
echo "✅ Git repository configured!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Create the GitHub repository:"
echo "   → Go to: https://github.com/new"
echo "   → Repository name: $REPO_NAME"
echo "   → Description: AI-powered health information assistant"
echo "   → Choose Public or Private"
echo "   → Do NOT initialize with README"
echo "   → Click 'Create repository'"
echo ""
echo "2. Push to GitHub:"
echo "   → Run: git push -u origin main"
echo ""
echo "3. Deploy to Streamlit Cloud:"
echo "   → Go to: https://share.streamlit.io/"
echo "   → Click 'New app'"
echo "   → Select your repository: $GITHUB_USERNAME/$REPO_NAME"
echo "   → Main file: app.py"
echo "   → Add secrets (OPENAI_API_KEY)"
echo "   → Deploy!"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
echo ""
read -p "Press Enter to continue with git push..."

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "🎉 Success! Your code is now on GitHub!"
echo ""
echo "🔗 Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "Next: Deploy to Streamlit Cloud (see DEPLOYMENT.md)"

