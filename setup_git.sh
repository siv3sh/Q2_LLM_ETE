#!/bin/bash

# Git Deployment Setup Script for Employee Attrition Analysis Assistant
# Prepares the project for GitHub and Streamlit Cloud deployment

echo "🚀 Setting up Employee Attrition Analysis Assistant for Git deployment..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✅ Git found: $(git --version)"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Initial commit: Employee Attrition Analysis Assistant

Features:
- Conversational AI assistant for attrition analysis
- Interactive Streamlit interface
- RAG implementation with FAISS
- Ollama integration for local deployment
- Cloud-compatible version for Streamlit Cloud
- Comprehensive documentation and examples

Ready for GitHub deployment and Streamlit Cloud!"
    echo "✅ Changes committed successfully"
fi

# Check if remote is already set
if git remote get-url origin &> /dev/null; then
    echo "✅ Remote origin already configured"
    echo "Current remote: $(git remote get-url origin)"
else
    echo "⚠️  No remote repository configured"
    echo ""
    echo "To connect to GitHub:"
    echo "1. Create a new repository on GitHub"
    echo "2. Run: git remote add origin https://github.com/yourusername/your-repo-name.git"
    echo "3. Run: git push -u origin main"
fi

# Show current status
echo ""
echo "📊 Current Git Status:"
git status

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps for deployment:"
echo ""
echo "1. **GitHub Repository:**"
echo "   - Create a new repository on GitHub"
echo "   - Add remote: git remote add origin <your-repo-url>"
echo "   - Push: git push -u origin main"
echo ""
echo "2. **Streamlit Cloud Deployment:**"
echo "   - Go to https://share.streamlit.io"
echo "   - Sign in with GitHub"
echo "   - Click 'New app'"
echo "   - Select your repository"
echo "   - Main file: streamlit_app_cloud.py (for cloud version)"
echo "   - Or streamlit_app.py (for local version with Ollama)"
echo ""
echo "3. **Local Development:**"
echo "   - Run: streamlit run streamlit_app.py"
echo "   - Or: streamlit run streamlit_app_cloud.py"
echo ""
echo "📚 Files included:"
echo "   - streamlit_app.py (main local app)"
echo "   - streamlit_app_cloud.py (cloud-compatible version)"
echo "   - simple_rag.py (core RAG implementation)"
echo "   - requirements.txt (dependencies)"
echo "   - README.md (comprehensive documentation)"
echo "   - .streamlit/config.toml (Streamlit configuration)"
echo "   - .gitignore (Git ignore rules)"
echo ""
echo "🌐 Ready for deployment! 🚀"
