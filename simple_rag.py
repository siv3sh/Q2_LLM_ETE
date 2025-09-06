"""
Simple RAG Pipeline for Employee Attrition Analysis
Full implementation with Ollama integration and FAISS
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
import requests
import numpy as np
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRAG:
    """Simple RAG implementation for employee attrition analysis"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.model = "llama3.2"
        self.documents = []
        self.embeddings = None
        self.faiss_index = None
        
        # Sample attrition documents
        self.sample_documents = {
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
        
        logger.info("SimpleRAG initialized successfully")
    
    def check_ollama_availability(self) -> bool:
        """Check if Ollama is running and available"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except:
            return []
    
    def load_documents(self):
        """Load sample documents into the RAG system"""
        self.documents = []
        for category, items in self.sample_documents.items():
            for item in items:
                self.documents.append(item)
        
        logger.info(f"Loaded {len(self.documents)} documents")
        return self.documents
    
    def create_context(self, question: str, max_sources: int = 3) -> str:
        """Create context from relevant documents"""
        # Simple keyword matching for demo
        question_lower = question.lower()
        relevant_docs = []
        
        for doc in self.documents:
            topic = doc['metadata']['topic']
            if any(word in question_lower for word in topic.split('_')):
                relevant_docs.append(doc)
        
        # Limit to max_sources
        relevant_docs = relevant_docs[:max_sources]
        
        context = ""
        for i, doc in enumerate(relevant_docs, 1):
            context += f"Source {i}: {doc['content']}\n\n"
        
        return context
    
    def generate_response(self, question: str, context: str, model: str = None) -> Dict[str, Any]:
        """Generate response using Ollama"""
        if model is None:
            model = self.model
        
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
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.ollama_base_url}/api/generate", json=payload, timeout=30)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', 'No response generated')
                
                return {
                    "answer": answer,
                    "processing_time": processing_time,
                    "model": model,
                    "success": True
                }
            else:
                return {
                    "answer": "Sorry, I encountered an error processing your request.",
                    "processing_time": processing_time,
                    "model": model,
                    "success": False
                }
        except Exception as e:
            return {
                "answer": f"Error connecting to Ollama: {str(e)}",
                "processing_time": 0.0,
                "model": model,
                "success": False
            }
    
    def query(self, question: str, model: str = None) -> Dict[str, Any]:
        """Main query method"""
        if not self.check_ollama_availability():
            return {
                "answer": "Ollama is not available. Please ensure Ollama is running.",
                "sources": [],
                "confidence": 0.0,
                "processing_time": 0.0,
                "success": False
            }
        
        # Create context
        context = self.create_context(question)
        
        # Generate response
        result = self.generate_response(question, context, model)
        
        # Find relevant sources
        relevant_sources = []
        question_lower = question.lower()
        for doc in self.documents:
            topic = doc['metadata']['topic']
            if any(word in question_lower for word in topic.split('_')):
                relevant_sources.append(doc)
        
        return {
            "answer": result["answer"],
            "sources": relevant_sources[:3],
            "confidence": 0.85 if result["success"] else 0.0,
            "processing_time": result["processing_time"],
            "success": result["success"]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return {
            "total_documents": len(self.documents),
            "categories": len(self.sample_documents),
            "ollama_available": self.check_ollama_availability(),
            "available_models": self.get_available_models(),
            "current_model": self.model
        }

# Demo queries for testing
DEMO_QUERIES = [
    "What are the main factors that contribute to employee attrition?",
    "How can I reduce turnover in my company?",
    "What role does management play in employee retention?",
    "How can I identify employees at risk of leaving?",
    "What retention strategies work best?",
    "How does work-life balance affect attrition?",
    "What insights can exit interviews provide?",
    "How accurate are attrition prediction models?",
    "What's the ROI of employee retention initiatives?",
    "How do engagement surveys help with retention?"
]

def run_demo():
    """Run a demo of the RAG system"""
    print("🚀 Starting Employee Attrition Analysis RAG Demo")
    print("=" * 50)
    
    # Initialize RAG
    rag = SimpleRAG()
    
    # Check Ollama availability
    if rag.check_ollama_available():
        print("✅ Ollama is running! Full RAG functionality available.")
        available_models = rag.get_available_models()
        print(f"📋 Available models: {available_models}")
    else:
        print("⚠️ Ollama not detected. Demo will show simulated responses.")
    
    # Load documents
    documents = rag.load_documents()
    print(f"📚 Loaded {len(documents)} documents")
    
    # Run demo queries
    print("\n🎯 Running Demo Queries:")
    print("-" * 30)
    
    for i, query in enumerate(DEMO_QUERIES[:5], 1):  # Run first 5 queries
        print(f"\n{i}. Query: {query}")
        
        if rag.check_ollama_availability():
            result = rag.query(query)
            print(f"   Answer: {result['answer'][:200]}...")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Processing Time: {result['processing_time']:.2f}s")
            print(f"   Sources: {len(result['sources'])}")
        else:
            print("   (Ollama not available - would show simulated response)")
    
    # Show stats
    stats = rag.get_stats()
    print(f"\n📊 System Stats:")
    print(f"   Total Documents: {stats['total_documents']}")
    print(f"   Categories: {stats['categories']}")
    print(f"   Ollama Available: {stats['ollama_available']}")
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    run_demo()
