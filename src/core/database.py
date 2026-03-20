"""Database models and operations"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, index=True)
    customer_id = Column(String, index=True)
    channel = Column(String)
    message = Column(Text)
    agent_reply = Column(Text)
    product = Column(String)
    order_value = Column(Float)
    customer_country = Column(String)
    resolution_status = Column(String)
    
    # AI-generated fields
    ai_category = Column(String)
    ai_sentiment = Column(String)
    ai_frustration_score = Column(Float)
    ai_suggested_response = Column(Text)
    processed_at = Column(DateTime)

class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True)
    insight_type = Column(String)  # "top_issue", "sentiment_trend", "anomaly"
    content = Column(Text)
    meta_data = Column(Text)  # JSON string (renamed from metadata to avoid SQLAlchemy conflict)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
engine = create_engine("sqlite:///support_platform.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    """Get database session (for direct use)"""
    return SessionLocal()
