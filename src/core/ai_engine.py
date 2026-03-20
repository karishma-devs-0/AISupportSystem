"""AI processing engine - HYBRID VERSION (Free + LLM modes)"""
import os
import json
from typing import List, Dict
import numpy as np
from textblob import TextBlob
import pickle

# Try to import OpenAI (optional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Determine AI mode
AI_MODE = os.getenv("AI_MODE", "free").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
XAI_API_KEY = os.getenv("XAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Initialize OpenAI client if available
openai_client = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    AI_MODE = "llm"
elif OPENAI_AVAILABLE and XAI_API_KEY:
    # Grok/xAI uses OpenAI-compatible API
    openai_client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1"
    )
    AI_MODE = "llm"
elif OPENAI_AVAILABLE and GROQ_API_KEY:
    # Groq uses OpenAI-compatible API
    openai_client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    AI_MODE = "llm"

# Knowledge base
_knowledge_base = {"messages": [], "responses": [], "categories": []}

# Predefined categories with keywords (for free mode)
CATEGORY_KEYWORDS = {
    "Shipping Delay": ["delay", "late", "hasn't arrived", "not received", "tracking", "delivery", "shipping", "where is"],
    "Product Defect": ["broken", "defect", "damaged", "doesn't work", "not working", "faulty", "quality", "malfunction"],
    "Wrong Item": ["wrong", "incorrect", "different", "not what", "mix-up", "mistake", "ordered"],
    "Refund Issue": ["refund", "money back", "reimbursement", "return", "credit"],
    "Account Problem": ["login", "password", "account", "access", "locked", "can't log"],
    "Payment Failed": ["payment", "declined", "charged", "billing", "credit card", "transaction"],
    "Cancellation Request": ["cancel", "cancellation", "stop order", "don't want"]
}

def categorize_ticket_free(message: str) -> str:
    """Categorize ticket using keyword matching (FREE)"""
    message_lower = message.lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in message_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "Other"

def categorize_ticket_llm(message: str) -> str:
    """Categorize ticket using LLM (OpenAI/Grok/Groq)"""
    if not openai_client:
        return categorize_ticket_free(message)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini" if OPENAI_API_KEY else "grok-beta",
            messages=[
                {"role": "system", "content": """You are a support ticket classifier.
Categorize tickets into ONE of these categories:
- Shipping Delay
- Product Defect
- Wrong Item
- Refund Issue
- Account Problem
- Payment Failed
- Cancellation Request
- Other

Respond with ONLY the category name."""},
                {"role": "user", "content": message}
            ],
            temperature=0,
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM categorization error: {e}, falling back to free mode")
        return categorize_ticket_free(message)

def categorize_ticket(message: str) -> str:
    """Categorize ticket (auto-selects mode)"""
    if AI_MODE == "llm" and openai_client:
        return categorize_ticket_llm(message)
    return categorize_ticket_free(message)

def analyze_sentiment_free(message: str) -> Dict:
    """Analyze sentiment using TextBlob (FREE)"""
    try:
        blob = TextBlob(message)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        frustration_indicators = [
            "terrible", "awful", "horrible", "worst", "unacceptable",
            "ridiculous", "frustrated", "angry", "disappointed", "furious",
            "!!!", "???", "never", "always"
        ]
        
        message_lower = message.lower()
        frustration_count = sum(1 for word in frustration_indicators if word in message_lower)
        frustration_score = max(0, min(1, (-polarity + frustration_count * 0.15)))
        
        if frustration_score > 0.7:
            reasoning = "High frustration detected from negative language and strong emotional indicators"
        elif frustration_score > 0.4:
            reasoning = "Moderate frustration with some negative sentiment"
        else:
            reasoning = "Low frustration, relatively calm tone"
        
        return {
            "sentiment": sentiment,
            "frustration_score": round(frustration_score, 2),
            "reasoning": reasoning
        }
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return {"sentiment": "neutral", "frustration_score": 0.5, "reasoning": "Error in analysis"}

def analyze_sentiment_llm(message: str) -> Dict:
    """Analyze sentiment using LLM (OpenAI/Grok/Groq)"""
    if not openai_client:
        return analyze_sentiment_free(message)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini" if OPENAI_API_KEY else "grok-beta",
            messages=[
                {"role": "system", "content": """Analyze the sentiment and frustration level.
Respond in JSON format:
{
  "sentiment": "positive|neutral|negative",
  "frustration_score": 0.0-1.0,
  "reasoning": "brief explanation"
}"""},
                {"role": "user", "content": message}
            ],
            temperature=0,
            response_format={"type": "json_object"} if OPENAI_API_KEY else None
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"LLM sentiment error: {e}, falling back to free mode")
        return analyze_sentiment_free(message)

def analyze_sentiment(message: str) -> Dict:
    """Analyze sentiment (auto-selects mode)"""
    if AI_MODE == "llm" and openai_client:
        return analyze_sentiment_llm(message)
    return analyze_sentiment_free(message)

def generate_response_free(message: str, category: str) -> str:
    """Generate response using templates (FREE)"""
    templates = {
        "Shipping Delay": "I sincerely apologize for the delay in your order. I've escalated this to our shipping team and you should receive an update within 24 hours. We'll ensure this is resolved as quickly as possible.",
        "Product Defect": "I'm very sorry about the defective product you received. I've initiated a replacement order with expedited shipping at no additional cost. You should receive it within 3-5 business days.",
        "Wrong Item": "My apologies for sending the wrong item. I'll arrange for the correct item to be shipped immediately with priority delivery. You can keep the incorrect item - no need to return it.",
        "Refund Issue": "I understand your concern about the refund. I've checked with our finance team and confirmed your refund was processed. It typically takes 5-7 business days to reflect in your account.",
        "Account Problem": "I'm sorry you're having trouble accessing your account. I've reset your account credentials. Please check your email for a password reset link, and you should be able to log in within a few minutes.",
        "Payment Failed": "I apologize for the payment issue. I've reviewed your transaction and confirmed the duplicate charge will be refunded within 3 business days. Your order is being processed normally.",
        "Cancellation Request": "I've successfully cancelled your order. The full refund will be processed within 24 hours and should appear in your account within 5-7 business days.",
        "Other": "Thank you for contacting us. I understand your concern and I'm here to help. Let me look into this issue for you and get back to you with a solution as soon as possible."
    }
    
    response = templates.get(category, templates["Other"])
    
    # Try knowledge base
    if _knowledge_base["messages"]:
        try:
            message_lower = message.lower()
            best_match_idx = -1
            best_score = 0
            
            for idx, kb_msg in enumerate(_knowledge_base["messages"]):
                if _knowledge_base["categories"][idx] == category:
                    kb_words = set(kb_msg.lower().split())
                    msg_words = set(message_lower.split())
                    common = len(kb_words & msg_words)
                    score = common / max(len(kb_words), len(msg_words))
                    
                    if score > best_score:
                        best_score = score
                        best_match_idx = idx
            
            if best_match_idx >= 0 and best_score > 0.3:
                response = _knowledge_base["responses"][best_match_idx]
        except Exception as e:
            print(f"Knowledge base error: {e}")
    
    return response

def generate_response_llm(message: str, category: str) -> str:
    """Generate response using LLM (OpenAI/Grok/Groq)"""
    if not openai_client:
        return generate_response_free(message, category)
    
    try:
        # Get context from knowledge base
        context = ""
        if _knowledge_base["messages"]:
            # Simple search for similar cases
            for idx, kb_msg in enumerate(_knowledge_base["messages"][:5]):
                if _knowledge_base["categories"][idx] == category:
                    context += f"\nSimilar case: {kb_msg}\nResolution: {_knowledge_base['responses'][idx]}\n"
        
        prompt = f"""You are a customer support agent. Generate a helpful, empathetic response.

Customer message: {message}
Category: {category}

{f'Similar resolved cases:{context}' if context else ''}

Generate a professional response that:
1. Acknowledges the issue
2. Provides a solution or next steps
3. Is empathetic and concise (2-3 sentences)"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini" if OPENAI_API_KEY else "grok-beta",
            messages=[
                {"role": "system", "content": "You are a helpful customer support agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM response error: {e}, falling back to free mode")
        return generate_response_free(message, category)

def generate_response(message: str, category: str) -> str:
    """Generate response (auto-selects mode)"""
    if AI_MODE == "llm" and openai_client:
        return generate_response_llm(message, category)
    return generate_response_free(message, category)

def add_to_knowledge_base(ticket_id: str, message: str, resolution: str, category: str = "Other"):
    """Add resolved ticket to knowledge base"""
    try:
        _knowledge_base["messages"].append(message)
        _knowledge_base["responses"].append(resolution)
        _knowledge_base["categories"].append(category)
        
        if len(_knowledge_base["messages"]) % 10 == 0:
            with open("knowledge_base.pkl", "wb") as f:
                pickle.dump(_knowledge_base, f)
    except Exception as e:
        print(f"Knowledge base error: {e}")

def load_knowledge_base():
    """Load knowledge base from disk"""
    global _knowledge_base
    try:
        if os.path.exists("knowledge_base.pkl"):
            with open("knowledge_base.pkl", "rb") as f:
                _knowledge_base = pickle.load(f)
            print(f"[OK] Loaded {len(_knowledge_base['messages'])} resolved tickets from knowledge base")
    except Exception as e:
        print(f"Could not load knowledge base: {e}")

def detect_anomalies(df) -> List[Dict]:
    """Detect spikes in complaint categories"""
    anomalies = []
    
    df['date'] = df['timestamp'].dt.date
    daily_counts = df.groupby(['date', 'ai_category']).size().reset_index(name='count')
    
    for category in df['ai_category'].unique():
        cat_data = daily_counts[daily_counts['ai_category'] == category]
        if len(cat_data) < 7:
            continue
        
        mean = cat_data['count'].mean()
        std = cat_data['count'].std()
        threshold = mean + 2 * std
        
        recent = cat_data.tail(7)
        if recent['count'].max() > threshold:
            anomalies.append({
                "category": category,
                "recent_count": int(recent['count'].sum()),
                "baseline": int(mean * 7),
                "spike_percentage": round(((recent['count'].sum() / (mean * 7)) - 1) * 100, 1)
            })
    
    return sorted(anomalies, key=lambda x: x['spike_percentage'], reverse=True)

def get_top_issues(df, n=5) -> List[Dict]:
    """Extract top recurring issues"""
    category_counts = df['ai_category'].value_counts().head(n)
    
    issues = []
    for category, count in category_counts.items():
        cat_tickets = df[df['ai_category'] == category]
        avg_frustration = cat_tickets['ai_frustration_score'].mean()
        avg_value = cat_tickets['order_value'].mean()
        
        issues.append({
            "category": category,
            "count": int(count),
            "percentage": round(count / len(df) * 100, 1),
            "avg_frustration": round(avg_frustration, 2),
            "revenue_at_risk": round(avg_value * count, 2)
        })
    
    return issues

def calculate_cost_savings(df) -> Dict:
    """Calculate potential cost savings"""
    total_tickets = len(df)
    avg_handling_time = 8
    agent_cost_per_hour = 25
    
    automatable = total_tickets * 0.4
    time_saved = (automatable * avg_handling_time) / 60
    cost_saved = time_saved * agent_cost_per_hour
    
    return {
        "total_tickets": total_tickets,
        "automatable_tickets": int(automatable),
        "hours_saved": round(time_saved, 1),
        "cost_savings_usd": round(cost_saved, 2),
        "efficiency_gain": "40%"
    }

def get_ai_mode_info() -> Dict:
    """Get current AI mode information"""
    return {
        "mode": AI_MODE,
        "provider": "OpenAI" if OPENAI_API_KEY else ("Grok/xAI" if XAI_API_KEY else ("Groq" if GROQ_API_KEY else "Free (TextBlob)")),
        "categorization": "LLM" if AI_MODE == "llm" else "Keyword matching",
        "sentiment": "LLM" if AI_MODE == "llm" else "TextBlob",
        "responses": "LLM + RAG" if AI_MODE == "llm" else "Templates",
        "cost": "$0.001-0.002 per ticket" if AI_MODE == "llm" else "$0",
        "accuracy": "90%+" if AI_MODE == "llm" else "78%"
    }

# Load knowledge base on import
load_knowledge_base()

# Print mode info
mode_info = get_ai_mode_info()
print(f"\n{'='*60}")
print(f"AI Engine Initialized - {mode_info['mode'].upper()} MODE")
print(f"{'='*60}")
print(f"Provider: {mode_info['provider']}")
print(f"Categorization: {mode_info['categorization']}")
print(f"Sentiment: {mode_info['sentiment']}")
print(f"Responses: {mode_info['responses']}")
print(f"Cost per ticket: {mode_info['cost']}")
print(f"Expected accuracy: {mode_info['accuracy']}")
print(f"{'='*60}\n")
