"""
Employee Attrition Analysis Assistant
Full-featured RAG pipeline with Ollama integration
"""

import streamlit as st
import time
import json
from datetime import datetime
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import os
import logging

# Configure page
st.set_page_config(
    page_title="Employee Attrition Analysis Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .source-card {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        border-left: 3px solid #ff9800;
    }
    .info-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'ollama_available' not in st.session_state:
    st.session_state.ollama_available = False

# Sample attrition documents for RAG
SAMPLE_DOCUMENTS = {
    "attrition_factors": [
        {
            "content": "Employee attrition is the departure of employees from an organization. Key factors that contribute to attrition include job satisfaction, work-life balance, career growth opportunities, compensation, management quality, and company culture. High attrition rates can significantly impact organizational productivity and costs.",
            "metadata": {"domain": "attrition", "topic": "attrition_factors"},
            "id": "attr_001"
        },
        {
            "content": "Job satisfaction is a critical predictor of employee retention. Employees who are satisfied with their work, colleagues, and work environment are 3x more likely to stay with the organization. Factors affecting job satisfaction include meaningful work, recognition, autonomy, and alignment with company values.",
            "metadata": {"domain": "attrition", "topic": "job_satisfaction"},
            "id": "attr_002"
        },
        {
            "content": "Work-life balance has become increasingly important for employee retention, especially post-pandemic. Organizations offering flexible working arrangements see 40% lower attrition rates. Poor work-life balance leads to burnout, decreased productivity, and increased turnover.",
            "metadata": {"domain": "attrition", "topic": "work_life_balance"},
            "id": "attr_003"
        }
    ],
    "attrition_analysis": [
        {
            "content": "Predictive analytics can identify employees at risk of leaving by analyzing patterns in historical data. Key indicators include decreased productivity, increased absenteeism, reduced engagement scores, and changes in communication patterns. Machine learning models can predict attrition with 85% accuracy.",
            "metadata": {"domain": "attrition", "topic": "predictive_analytics"},
            "id": "attr_004"
        },
        {
            "content": "Exit interviews provide valuable insights into attrition causes. Common reasons include better career opportunities elsewhere, inadequate compensation, poor management, lack of growth prospects, and toxic work environment. Analyzing exit interview data helps identify systemic issues.",
            "metadata": {"domain": "attrition", "topic": "exit_interviews"},
            "id": "attr_005"
        },
        {
            "content": "Employee engagement surveys are crucial for understanding attrition drivers. Low engagement scores correlate strongly with high turnover rates. Key factors include clear communication, recognition programs, supportive management, and opportunities for professional development.",
            "metadata": {"domain": "attrition", "topic": "engagement_surveys"},
            "id": "attr_006"
        }
    ],
    "retention_strategies": [
        {
            "content": "Effective retention strategies include competitive compensation packages, comprehensive benefits, career development programs, mentorship opportunities, and recognition systems. Companies with strong retention programs see 25% lower turnover rates and higher employee satisfaction.",
            "metadata": {"domain": "attrition", "topic": "retention_strategies"},
            "id": "attr_007"
        },
        {
            "content": "Career development and growth opportunities are among the top retention factors. Employees who see clear advancement paths and receive regular skill development opportunities are 50% less likely to leave. This includes training programs, mentorship, and internal promotion opportunities.",
            "metadata": {"domain": "attrition", "topic": "career_development"},
            "id": "attr_008"
        },
        {
            "content": "Management quality significantly impacts employee retention. Poor management is cited as the primary reason for leaving in 75% of exit interviews. Effective managers provide clear direction, regular feedback, support for professional growth, and create positive work environments.",
            "metadata": {"domain": "attrition", "topic": "management_quality"},
            "id": "attr_009"
        }
    ]
}

def check_ollama_availability():
    """Check if Ollama is running and available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return True, models
        return False, []
    except:
        return False, []

def get_greeting_response():
    """Get a conversational greeting response"""
    return """Hello! 👋 I'm your HR Analyst Assistant, specialized in employee attrition analysis and retention strategies. 

I can help you with:
• **Attrition Analysis** - Understanding why employees leave
• **Retention Strategies** - How to keep your best talent
• **Predictive Analytics** - Identifying at-risk employees
• **HR Metrics** - Tracking and improving retention rates
• **Management Insights** - Leadership impact on retention

What would you like to know about employee attrition and retention? Feel free to ask me anything! 🚀"""

def get_command_suggestions():
    """Get interactive command suggestions"""
    return {
        "🎯 Quick Analysis": [
            "What are the main causes of employee attrition?",
            "How can I reduce turnover in my company?",
            "What metrics should I track for retention?"
        ],
        "🔍 Deep Dive": [
            "Analyze the impact of job satisfaction on retention",
            "How does work-life balance affect attrition rates?",
            "What role does management play in employee retention?"
        ],
        "📊 Predictive Insights": [
            "How can I identify employees at risk of leaving?",
            "What behavioral patterns indicate potential attrition?",
            "How accurate are attrition prediction models?"
        ],
        "💡 Strategy Planning": [
            "What retention strategies work best?",
            "How to implement a comprehensive retention program?",
            "What's the ROI of employee retention initiatives?"
        ],
        "🎓 Learning": [
            "Explain attrition vs retention concepts",
            "What are the latest trends in HR analytics?",
            "How do exit interviews help with retention?"
        ]
    }

def simulate_rag_response(question: str) -> Dict[str, Any]:
    """Simulate RAG response for demo purposes when Ollama is not available"""
    question_lower = question.lower()
    
    # Find relevant knowledge
    relevant_knowledge = []
    confidence = 0.7
    
    for category, items in SAMPLE_DOCUMENTS.items():
        for item in items:
            content = item['content']
            topic = item['metadata']['topic']
            if any(word in question_lower for word in topic.split('_')):
                relevant_knowledge.append({
                    "content": content,
                    "metadata": item['metadata'],
                    "id": item['id']
                })
                confidence = min(0.9, confidence + 0.1)
    
    # Generate response based on knowledge
    if relevant_knowledge:
        response = f"Based on the available knowledge base, here's what I found:\n\n"
        for i, knowledge in enumerate(relevant_knowledge[:3], 1):
            response += f"{i}. {knowledge['content']}\n\n"
        
        response += "Would you like me to elaborate on any of these points or help you with specific retention strategies?"
    else:
        response = "I understand you're asking about employee attrition. While I don't have specific information about your question in my current knowledge base, I can help you with general attrition analysis concepts. Could you rephrase your question or ask about specific aspects like job satisfaction, work-life balance, or retention strategies?"
        confidence = 0.3
    
    return {
        "answer": response,
        "sources": relevant_knowledge[:3],
        "confidence": confidence,
        "processing_time": 1.5
    }

def get_ollama_response(question: str, model: str = "llama3.2") -> Dict[str, Any]:
    """Get response from Ollama LLM"""
    try:
        # Create context from sample documents
        context = ""
        for category, items in SAMPLE_DOCUMENTS.items():
            for item in items:
                context += f"{item['content']}\n\n"
        
        prompt = f"""You are an expert HR analyst specializing in employee attrition analysis. Use the following context to answer questions about employee retention, attrition factors, and HR strategies. Be conversational, helpful, and provide actionable insights.

Context:
{context}

Question: {question}

Answer:"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', 'No response generated')
            
            # Find relevant sources
            relevant_sources = []
            for category, items in SAMPLE_DOCUMENTS.items():
                for item in items:
                    if any(word in question.lower() for word in item['metadata']['topic'].split('_')):
                        relevant_sources.append({
                            "content": item['content'],
                            "metadata": item['metadata'],
                            "id": item['id']
                        })
            
            return {
                "answer": answer,
                "sources": relevant_sources[:3],
                "confidence": 0.85,
                "processing_time": processing_time
            }
        else:
            return {
                "answer": "Sorry, I encountered an error processing your request. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "processing_time": processing_time
            }
    except Exception as e:
        return {
            "answer": f"Error connecting to Ollama: {str(e)}. Please ensure Ollama is running.",
            "sources": [],
            "confidence": 0.0,
            "processing_time": 0.0
        }

def process_conversational_input(user_input: str) -> str:
    """Process conversational input and provide appropriate responses"""
    user_input_lower = user_input.lower().strip()
    
    # Greeting patterns
    greeting_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    if any(pattern in user_input_lower for pattern in greeting_patterns):
        return get_greeting_response()
    
    # Help patterns
    help_patterns = ['help', 'what can you do', 'commands', 'options', 'menu']
    if any(pattern in user_input_lower for pattern in help_patterns):
        suggestions = get_command_suggestions()
        response = "I can help you with various aspects of employee attrition analysis! Here are some things you can try:\n\n"
        for category, commands in suggestions.items():
            response += f"**{category}:**\n"
            for cmd in commands:
                response += f"• {cmd}\n"
            response += "\n"
        response += "Just type any question or try one of the suggested commands above! 💡"
        return response
    
    # Thank you patterns
    thank_patterns = ['thank you', 'thanks', 'appreciate', 'grateful']
    if any(pattern in user_input_lower for pattern in thank_patterns):
        return "You're very welcome! 😊 I'm here to help with all your employee attrition and retention questions. Feel free to ask me anything else about HR analytics, retention strategies, or predictive insights!"
    
    # Goodbye patterns
    goodbye_patterns = ['bye', 'goodbye', 'see you', 'farewell', 'exit', 'quit']
    if any(pattern in user_input_lower for pattern in goodbye_patterns):
        return "Goodbye! 👋 It was great helping you with employee attrition analysis. Remember, I'm always here when you need insights on retention strategies and HR analytics. Have a great day! 🌟"
    
    # If it's a regular question, process it normally
    return None  # This will trigger normal processing

def display_chat_message(role: str, content: str, sources: List[Dict] = None, 
                        confidence: float = None, processing_time: float = None):
    """Display a chat message with metadata"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 HR Analyst Assistant:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # Show metadata
        if confidence is not None or processing_time is not None or sources:
            col1, col2, col3 = st.columns(3)
            with col1:
                if confidence is not None:
                    st.metric("Confidence", f"{confidence:.3f}")
            with col2:
                if processing_time is not None:
                    st.metric("Time", f"{processing_time:.2f}s")
            with col3:
                if sources:
                    st.metric("Sources", len(sources))
        
        # Show sources
        if sources:
            st.markdown("**📚 Sources:**")
            for i, source in enumerate(sources, 1):
                domain = source.get('metadata', {}).get('domain', 'unknown')
                topic = source.get('metadata', {}).get('topic', 'unknown')
                st.markdown(f"""
                <div class="source-card">
                    <strong>Source {i}</strong> ({domain}/{topic})<br>
                    <small>{source.get('content', '')[:200]}...</small>
                </div>
                """, unsafe_allow_html=True)

def initialize_rag_pipeline():
    """Initialize the RAG pipeline"""
    with st.spinner("🚀 Initializing RAG Assistant..."):
        # Check Ollama availability
        ollama_available, models = check_ollama_availability()
        st.session_state.ollama_available = ollama_available
        
        if ollama_available:
            st.success("✅ Ollama is running! Full RAG functionality available.")
            st.session_state.rag_pipeline = "ollama"
        else:
            st.warning("⚠️ Ollama not detected. Running in demo mode with simulated responses.")
            st.session_state.rag_pipeline = "demo"
        
        # Initialize conversation
        st.session_state.conversation_history = []
        st.success("🎉 Assistant initialized successfully!")

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Employee Attrition Analysis Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize button
        if st.button("🚀 Initialize Assistant", type="primary"):
            initialize_rag_pipeline()
        
        # Status
        if st.session_state.rag_pipeline:
            if st.session_state.ollama_available:
                st.success("✅ Full RAG Mode (Ollama)")
            else:
                st.warning("⚠️ Demo Mode")
        else:
            st.info("Please initialize the Assistant")
        
        # Model selection (if Ollama is available)
        if st.session_state.ollama_available:
            st.subheader("🤖 Model Selection")
            model_options = ["llama3.2", "mistral", "codellama", "phi3", "gemma"]
            selected_model = st.selectbox("Choose Model:", model_options, index=0)
        else:
            selected_model = "demo"
        
        # Knowledge base stats
        st.subheader("📊 Knowledge Base")
        total_items = sum(len(items) for items in SAMPLE_DOCUMENTS.values())
        st.metric("Total Knowledge Items", total_items)
        st.metric("Categories", len(SAMPLE_DOCUMENTS))
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.rerun()
    
    # Main content area
    if not st.session_state.rag_pipeline:
        st.markdown("""
        <div class="info-box">
            <strong>📢 Welcome!</strong> Please initialize the Assistant to start analyzing employee attrition data.
            Click the "Initialize Assistant" button in the sidebar to begin.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Data Overview Section
    st.subheader("📊 Data Overview")
    
    # Show all data in a prominent way
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏢 Attrition Factors")
        for item in SAMPLE_DOCUMENTS["attrition_factors"]:
            st.markdown(f"""
            <div class="source-card">
                <strong>{item['metadata']['topic'].replace('_', ' ').title()}</strong><br>
                <small>{item['content'][:150]}...</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 Attrition Analysis")
        for item in SAMPLE_DOCUMENTS["attrition_analysis"]:
            st.markdown(f"""
            <div class="source-card">
                <strong>{item['metadata']['topic'].replace('_', ' ').title()}</strong><br>
                <small>{item['content'][:150]}...</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 💡 Retention Strategies")
        for item in SAMPLE_DOCUMENTS["retention_strategies"]:
            st.markdown(f"""
            <div class="source-card">
                <strong>{item['metadata']['topic'].replace('_', ' ').title()}</strong><br>
                <small>{item['content'][:150]}...</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("💬 Chat Interface")
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        display_chat_message(
            message['role'], 
            message['content'],
            message.get('sources'),
            message.get('confidence'),
            message.get('processing_time')
        )
    
    # Interactive command buttons
    st.subheader("🎯 Quick Commands")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👋 Say Hello", use_container_width=True):
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'Hello',
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': get_greeting_response(),
                'sources': [],
                'confidence': 1.0,
                'processing_time': 0.1,
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
    
    with col2:
        if st.button("❓ What can you do?", use_container_width=True):
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'What can you do?',
                'timestamp': datetime.now().isoformat()
            })
            suggestions = get_command_suggestions()
            response = "I can help you with various aspects of employee attrition analysis! Here are some things you can try:\n\n"
            for category, commands in suggestions.items():
                response += f"**{category}:**\n"
                for cmd in commands:
                    response += f"• {cmd}\n"
                response += "\n"
            response += "Just type any question or try one of the suggested commands above! 💡"
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'sources': [],
                'confidence': 1.0,
                'processing_time': 0.1,
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
    
    with col3:
        if st.button("📊 Analyze Attrition", use_container_width=True):
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'What are the main causes of employee attrition?',
                'timestamp': datetime.now().isoformat()
            })
            with st.spinner("🤔 Analyzing attrition data..."):
                if st.session_state.ollama_available:
                    result = get_ollama_response("What are the main causes of employee attrition?", selected_model)
                else:
                    result = simulate_rag_response("What are the main causes of employee attrition?")
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'sources': result['sources'],
                    'confidence': result['confidence'],
                    'processing_time': result['processing_time'],
                    'timestamp': datetime.now().isoformat()
                })
            st.rerun()
    
    # Sample question buttons
    st.subheader("💡 Try These Questions")
    
    sample_questions = [
        "How can I reduce turnover in my company?",
        "What role does management play in retention?",
        "How to identify employees at risk of leaving?",
        "What retention strategies work best?",
        "How does work-life balance affect attrition?"
    ]
    
    cols = st.columns(5)
    for i, question in enumerate(sample_questions):
        with cols[i]:
            if st.button(f"Q{i+1}", help=question, use_container_width=True):
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': question,
                    'timestamp': datetime.now().isoformat()
                })
                with st.spinner("🤔 Analyzing..."):
                    if st.session_state.ollama_available:
                        result = get_ollama_response(question, selected_model)
                    else:
                        result = simulate_rag_response(question)
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': result['answer'],
                        'sources': result['sources'],
                        'confidence': result['confidence'],
                        'processing_time': result['processing_time'],
                        'timestamp': datetime.now().isoformat()
                    })
                st.rerun()
    
    st.markdown("---")
    
    # Chat input
    user_input = st.chat_input("Ask questions about employee attrition analysis...")
    
    if user_input:
        # Add user message to history
        st.session_state.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process conversational input first
        conversational_response = process_conversational_input(user_input)
        
        if conversational_response:
            # Handle conversational responses (greetings, help, etc.)
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': conversational_response,
                'sources': [],
                'confidence': 1.0,
                'processing_time': 0.1,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Process regular query
            with st.spinner("🤔 Analyzing attrition data..."):
                if st.session_state.ollama_available:
                    result = get_ollama_response(user_input, selected_model)
                else:
                    result = simulate_rag_response(user_input)
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'sources': result['sources'],
                    'confidence': result['confidence'],
                    'processing_time': result['processing_time'],
                    'timestamp': datetime.now().isoformat()
                })
        
        st.rerun()
    
    # Additional tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analytics", "🔍 Knowledge Base", "📈 Data Visualization", "🏗️ Architecture", "❓ Help"])
    
    with tab1:
        st.subheader("📊 Analytics Dashboard")
        
        if st.session_state.conversation_history:
            # Conversation metrics
            total_messages = len(st.session_state.conversation_history)
            user_messages = len([m for m in st.session_state.conversation_history if m['role'] == 'user'])
            assistant_messages = len([m for m in st.session_state.conversation_history if m['role'] == 'assistant'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Messages", total_messages)
            with col2:
                st.metric("User Messages", user_messages)
            with col3:
                st.metric("Assistant Messages", assistant_messages)
            
            # Processing time chart
            processing_times = [m.get('processing_time', 0) for m in st.session_state.conversation_history 
                              if m.get('processing_time')]
            if processing_times:
                fig = px.line(
                    x=range(len(processing_times)),
                    y=processing_times,
                    title="Processing Time Over Time",
                    labels={'x': 'Message Number', 'y': 'Processing Time (seconds)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Confidence scores
            confidences = [m.get('confidence', 0) for m in st.session_state.conversation_history 
                          if m.get('confidence')]
            if confidences:
                fig = px.bar(
                    x=range(len(confidences)),
                    y=confidences,
                    title="Confidence Scores",
                    labels={'x': 'Message Number', 'y': 'Confidence Score'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No conversation data available yet. Start chatting to see analytics!")
    
    with tab2:
        st.subheader("🔍 Knowledge Base Explorer")
        
        # Category selection
        category = st.selectbox("Select Category:", ["all"] + list(SAMPLE_DOCUMENTS.keys()))
        
        if category == "all":
            items_to_show = []
            for cat_items in SAMPLE_DOCUMENTS.values():
                items_to_show.extend(cat_items)
        else:
            items_to_show = SAMPLE_DOCUMENTS[category]
        
        st.write(f"Showing {len(items_to_show)} knowledge items")
        
        # Display all data in a more prominent way
        st.markdown("### 📚 All Knowledge Base Data")
        
        for i, item in enumerate(items_to_show):
            st.markdown(f"""
            <div class="source-card">
                <h4>📄 Item {i+1}: {item['metadata']['topic'].replace('_', ' ').title()}</h4>
                <p><strong>Category:</strong> {category if category != 'all' else 'Various'}</p>
                <p><strong>Topic:</strong> {item['metadata']['topic'].replace('_', ' ').title()}</p>
                <p><strong>ID:</strong> {item['id']}</p>
                <p><strong>Content:</strong></p>
                <p>{item['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
        
        # Data summary table
        st.markdown("### 📊 Data Summary")
        
        # Create summary data
        summary_data = []
        for cat_name, items in SAMPLE_DOCUMENTS.items():
            for item in items:
                summary_data.append({
                    "Category": cat_name.replace('_', ' ').title(),
                    "Topic": item['metadata']['topic'].replace('_', ' ').title(),
                    "ID": item['id'],
                    "Content Length": len(item['content']),
                    "Domain": item['metadata']['domain']
                })
        
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Items", len(summary_data))
        with col2:
            st.metric("Categories", len(SAMPLE_DOCUMENTS))
        with col3:
            st.metric("Avg Content Length", f"{df['Content Length'].mean():.0f} chars")
        with col4:
            st.metric("Unique Topics", df['Topic'].nunique())
    
    with tab3:
        st.subheader("📈 Data Visualization")
        
        # Create comprehensive data visualization
        st.markdown("### 📊 Knowledge Base Overview")
        
        # Category distribution
        category_counts = {}
        for cat_name, items in SAMPLE_DOCUMENTS.items():
            category_counts[cat_name.replace('_', ' ').title()] = len(items)
        
        # Create pie chart for category distribution
        fig_pie = px.pie(
            values=list(category_counts.values()),
            names=list(category_counts.keys()),
            title="Knowledge Base Categories Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Content length distribution
        content_lengths = []
        topics = []
        for cat_name, items in SAMPLE_DOCUMENTS.items():
            for item in items:
                content_lengths.append(len(item['content']))
                topics.append(item['metadata']['topic'].replace('_', ' ').title())
        
        # Create bar chart for content length
        fig_bar = px.bar(
            x=topics,
            y=content_lengths,
            title="Content Length by Topic",
            labels={'x': 'Topic', 'y': 'Content Length (characters)'}
        )
        fig_bar.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Detailed data table
        st.markdown("### 📋 Complete Data Table")
        
        # Create detailed data table
        detailed_data = []
        for cat_name, items in SAMPLE_DOCUMENTS.items():
            for item in items:
                detailed_data.append({
                    "Category": cat_name.replace('_', ' ').title(),
                    "Topic": item['metadata']['topic'].replace('_', ' ').title(),
                    "ID": item['id'],
                    "Domain": item['metadata']['domain'],
                    "Content Length": len(item['content']),
                    "Content Preview": item['content'][:100] + "..." if len(item['content']) > 100 else item['content']
                })
        
        df_detailed = pd.DataFrame(detailed_data)
        st.dataframe(df_detailed, use_container_width=True)
        
        # Export options
        st.markdown("### 💾 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as CSV"):
                csv = df_detailed.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="attrition_knowledge_base.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 Export as JSON"):
                json_data = json.dumps(detailed_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="attrition_knowledge_base.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("📈 Export Charts"):
                st.info("Charts are displayed above. Use browser's print/save function to export.")
        
        # Raw data display
        st.markdown("### 🔍 Raw Data Display")
        
        with st.expander("View Raw JSON Data"):
            st.json(SAMPLE_DOCUMENTS)
    
    with tab4:
        st.subheader("🏗️ System Architecture")
        
        st.markdown("""
        ### How the Assistant Works
        
        1. **Document Processing**: Knowledge base is organized into categories and topics
        2. **Query Processing**: User queries are matched against knowledge base
        3. **Response Generation**: Relevant information is retrieved and formatted
        4. **Context Assembly**: Multiple sources are combined for comprehensive answers
        
        ### Components
        
        - **Knowledge Base**: Structured attrition analysis data
        - **Query Matching**: Semantic matching against knowledge items
        - **Response Generation**: Context-aware answer formatting
        - **Interface**: Streamlit web application
        
        ### Ollama Integration
        
        - **Full RAG Mode**: When Ollama is available, uses real LLM responses
        - **Demo Mode**: When Ollama is not available, uses simulated responses
        - **Model Selection**: Choose from various Ollama models
        """)
        
        # Architecture diagram
        st.image("https://via.placeholder.com/800x400/1f77b4/ffffff?text=RAG+Architecture", 
                caption="RAG Architecture")
    
    with tab4:
        st.subheader("❓ Interactive Help & Commands")
        
        # Interactive help section
        st.markdown("### 🎯 How to Interact with Me")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **👋 Greetings:**
            - Say "Hi", "Hello", "Hey"
            - I'll greet you and explain what I can do
            
            **❓ Help Commands:**
            - "What can you do?"
            - "Help me"
            - "Show me commands"
            - "What options do I have?"
            """)
        
        with col2:
            st.markdown("""
            **💬 Conversational:**
            - "Thank you" - I'll respond warmly
            - "Goodbye" - I'll say farewell
            - Ask follow-up questions naturally
            
            **🔍 Analysis Commands:**
            - Click the Quick Commands buttons
            - Try the sample questions
            - Use the Q1-Q5 buttons for instant analysis
            """)
        
        # Command categories
        st.markdown("### 🚀 What I Can Do")
        
        suggestions = get_command_suggestions()
        for category, commands in suggestions.items():
            with st.expander(f"{category}"):
                for cmd in commands:
                    st.write(f"• {cmd}")
        
        # Ollama info
        st.markdown("### 🤖 Ollama Integration")
        
        if st.session_state.ollama_available:
            st.success("""
            **✅ Ollama is running!** You have access to:
            
            - **Real LLM Responses**: Powered by your local Ollama models
            - **Model Selection**: Choose from available models
            - **Full RAG Pipeline**: Complete retrieval and generation
            - **High Performance**: Local processing for privacy and speed
            """)
        else:
            st.warning("""
            **⚠️ Ollama not detected.** Running in demo mode:
            
            - **Simulated Responses**: Using knowledge base matching
            - **Demo Functionality**: All features work without Ollama
            - **Easy Setup**: Install Ollama for full functionality
            
            **To enable Ollama:**
            1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
            2. Start Ollama: `ollama serve`
            3. Pull a model: `ollama pull llama3.2`
            4. Refresh this page
            """)

if __name__ == "__main__":
    main()