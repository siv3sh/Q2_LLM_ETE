# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Main File**: Ensure `streamlit_app.py` is in the root directory

## Deployment Steps

### 1. Prepare Your Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Employee Attrition Analysis Assistant"

# Add remote repository
git remote add origin https://github.com/yourusername/employee-attrition-assistant.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your repository
   - Choose the main branch

3. **Configure App Settings**
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.8+
   - **Branch**: main

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Access your live app at `https://your-app-name.streamlit.app`

## Important Notes for Cloud Deployment

### Ollama Considerations

⚠️ **Important**: Ollama models are not available on Streamlit Cloud by default. You have several options:

1. **Use Alternative LLM Services**:
   - OpenAI API
   - Anthropic API
   - Hugging Face Inference API

2. **Modify for Cloud Deployment**:
   - Update the code to use cloud-based LLM services
   - Remove Ollama dependencies for cloud version

3. **Local Development Only**:
   - Keep Ollama for local development
   - Use cloud services for production deployment

### Environment Variables

If you need environment variables:

1. **In Streamlit Cloud**:
   - Go to your app settings
   - Add environment variables in the "Secrets" section

2. **Example secrets.toml**:
   ```toml
   [secrets]
   OPENAI_API_KEY = "your-openai-api-key"
   ANTHROPIC_API_KEY = "your-anthropic-api-key"
   ```

### File Structure for Cloud

Ensure your repository has this structure:
```
├── streamlit_app.py          # Main app file
├── simple_rag.py             # Core RAG implementation
├── requirements.txt          # Dependencies
├── .streamlit/               # Streamlit config
│   └── config.toml
├── README.md                 # Documentation
└── .gitignore               # Git ignore file
```

## Alternative: Cloud-Compatible Version

For a cloud-ready version, you can modify the code to use:

1. **OpenAI API** instead of Ollama
2. **Hugging Face Inference API** for embeddings
3. **Streamlit's built-in caching** for better performance

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version compatibility

2. **File Not Found**
   - Verify file paths are correct
   - Check that all necessary files are committed

3. **Memory Issues**
   - Reduce model size or use lighter alternatives
   - Implement proper caching

4. **Timeout Issues**
   - Optimize code for faster execution
   - Use async operations where possible

## Performance Optimization

1. **Caching**
   ```python
   @st.cache_data
   def load_embeddings():
       # Load embeddings once
       pass
   ```

2. **Lazy Loading**
   ```python
   if st.button("Load Model"):
       # Load model only when needed
       pass
   ```

3. **Streaming Responses**
   ```python
   # For long responses
   for chunk in response:
       st.write(chunk)
   ```

## Security Considerations

1. **API Keys**
   - Never commit API keys to repository
   - Use Streamlit secrets for sensitive data

2. **Rate Limiting**
   - Implement proper rate limiting
   - Handle API quota limits

3. **Input Validation**
   - Validate all user inputs
   - Sanitize data before processing

## Monitoring and Analytics

1. **Streamlit Analytics**
   - Enable usage analytics in Streamlit Cloud
   - Monitor app performance

2. **Custom Metrics**
   - Track user interactions
   - Monitor response times

3. **Error Handling**
   - Implement proper error handling
   - Log errors for debugging

## Next Steps

1. **Deploy**: Follow the deployment steps above
2. **Test**: Verify all features work in cloud environment
3. **Monitor**: Keep track of performance and usage
4. **Iterate**: Make improvements based on user feedback

## Support

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Create issues in your repository

---

*Happy deploying! 🚀*
