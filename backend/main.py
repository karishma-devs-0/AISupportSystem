"""FastAPI Backend for Customer Support Insight Platform"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.ai_engine import (
    categorize_ticket, analyze_sentiment, generate_response,
    detect_anomalies, get_top_issues, calculate_cost_savings,
    get_ai_mode_info
)
from src.core.database import Ticket, init_db, get_session

app = FastAPI(title="Support Insight API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

class AnalyzeRequest(BaseModel):
    message: str

class AnalyzeResponse(BaseModel):
    category: str
    sentiment: str
    frustration_score: float
    reasoning: str
    suggested_response: str

@app.get("/")
def root():
    return {"message": "Support Insight API", "version": "1.0.0"}

@app.get("/api/mode")
def get_mode():
    """Get current AI mode information"""
    return get_ai_mode_info()

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_message(request: AnalyzeRequest):
    """Analyze a customer message"""
    try:
        category = categorize_ticket(request.message)
        sentiment_data = analyze_sentiment(request.message)
        response = generate_response(request.message, category)
        
        return AnalyzeResponse(
            category=category,
            sentiment=sentiment_data["sentiment"],
            frustration_score=sentiment_data["frustration_score"],
            reasoning=sentiment_data["reasoning"],
            suggested_response=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets")
def get_tickets(
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    min_frustration: Optional[float] = None,
    limit: int = 100
):
    """Get tickets with optional filters"""
    try:
        session = get_session()
        query = session.query(Ticket)
        
        if category:
            query = query.filter(Ticket.ai_category == category)
        if sentiment:
            query = query.filter(Ticket.ai_sentiment == sentiment)
        if min_frustration is not None:
            query = query.filter(Ticket.ai_frustration_score >= min_frustration)
        
        tickets = query.order_by(Ticket.timestamp.desc()).limit(limit).all()
        
        return [{
            "id": t.id,
            "ticket_id": t.ticket_id,
            "customer_id": t.customer_id,
            "message": t.message,
            "timestamp": t.timestamp.isoformat(),
            "order_value": t.order_value,
            "ai_category": t.ai_category,
            "ai_sentiment": t.ai_sentiment,
            "ai_frustration_score": t.ai_frustration_score,
            "ai_suggested_response": t.ai_suggested_response
        } for t in tickets]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        session = get_session()
        tickets = session.query(Ticket).all()
        
        if not tickets:
            return {
                "total_tickets": 0,
                "avg_frustration": 0,
                "revenue_at_risk": 0,
                "top_issues": [],
                "anomalies": [],
                "cost_savings": {}
            }
        
        df = pd.DataFrame([{
            "ticket_id": t.ticket_id,
            "timestamp": t.timestamp,
            "ai_category": t.ai_category,
            "ai_sentiment": t.ai_sentiment,
            "ai_frustration_score": t.ai_frustration_score,
            "order_value": t.order_value
        } for t in tickets])
        
        high_frustration = df[df['ai_frustration_score'] > 0.7]
        revenue_at_risk = high_frustration['order_value'].sum()
        
        return {
            "total_tickets": len(df),
            "avg_frustration": round(df['ai_frustration_score'].mean(), 2),
            "revenue_at_risk": round(revenue_at_risk, 2),
            "top_issues": get_top_issues(df, n=7),
            "anomalies": detect_anomalies(df),
            "cost_savings": calculate_cost_savings(df),
            "sentiment_distribution": df['ai_sentiment'].value_counts().to_dict(),
            "category_distribution": df['ai_category'].value_counts().to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
def get_trends():
    """Get daily trends"""
    try:
        session = get_session()
        tickets = session.query(Ticket).all()
        
        if not tickets:
            return {"daily_trends": []}
        
        df = pd.DataFrame([{
            "timestamp": t.timestamp,
            "ai_frustration_score": t.ai_frustration_score
        } for t in tickets])
        
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily = df.groupby('date').agg({
            'ai_frustration_score': ['count', 'mean']
        }).reset_index()
        
        daily.columns = ['date', 'count', 'avg_frustration']
        
        return {
            "daily_trends": [{
                "date": str(row['date']),
                "count": int(row['count']),
                "avg_frustration": round(row['avg_frustration'], 2)
            } for _, row in daily.iterrows()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
