"""Data processing pipeline - FREE VERSION (No API costs!)"""
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import SessionLocal, Ticket, init_db
from core.ai_engine import (
    categorize_ticket, analyze_sentiment, generate_response,
    add_to_knowledge_base
)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate raw ticket data"""
    # Remove duplicates
    df = df.drop_duplicates(subset=['ticket_id'])
    
    # Handle missing values
    df['message'] = df['message'].fillna('')
    df['agent_reply'] = df['agent_reply'].fillna('')
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Remove invalid tickets
    df = df[df['message'].str.len() > 10]
    
    return df

def enrich_with_ai(df: pd.DataFrame, batch_size: int = 50) -> pd.DataFrame:
    """Enrich tickets with AI analysis (FREE - no API calls!)"""
    print(f"Processing {len(df)} tickets with FREE AI models...")
    
    results = []
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"  Processed {idx}/{len(df)} tickets...")
        
        try:
            # AI categorization (keyword-based)
            category = categorize_ticket(row['message'])
            
            # Sentiment analysis (TextBlob)
            sentiment_data = analyze_sentiment(row['message'])
            
            # Generate suggested response (template + knowledge base)
            suggested_response = generate_response(row['message'], category)
            
            # Add to knowledge base if resolved
            if row['resolution_status'] == 'resolved' and row['agent_reply']:
                add_to_knowledge_base(
                    row['ticket_id'],
                    row['message'],
                    row['agent_reply'],
                    category
                )
            
            results.append({
                'ai_category': category,
                'ai_sentiment': sentiment_data.get('sentiment', 'neutral'),
                'ai_frustration_score': sentiment_data.get('frustration_score', 0.5),
                'ai_suggested_response': suggested_response
            })
                
        except Exception as e:
            print(f"Error processing ticket {row['ticket_id']}: {e}")
            results.append({
                'ai_category': 'Other',
                'ai_sentiment': 'neutral',
                'ai_frustration_score': 0.5,
                'ai_suggested_response': 'Processing error'
            })
    
    # Merge AI results back
    ai_df = pd.DataFrame(results)
    df = pd.concat([df.reset_index(drop=True), ai_df], axis=1)
    
    return df

def store_to_database(df: pd.DataFrame):
    """Store processed tickets to database"""
    print("Storing tickets to database...")
    
    init_db()
    db = SessionLocal()
    
    try:
        for _, row in df.iterrows():
            ticket = Ticket(
                ticket_id=row['ticket_id'],
                timestamp=row['timestamp'],
                customer_id=row['customer_id'],
                channel=row['channel'],
                message=row['message'],
                agent_reply=row['agent_reply'],
                product=row['product'],
                order_value=row['order_value'],
                customer_country=row['customer_country'],
                resolution_status=row['resolution_status'],
                ai_category=row.get('ai_category'),
                ai_sentiment=row.get('ai_sentiment'),
                ai_frustration_score=row.get('ai_frustration_score'),
                ai_suggested_response=row.get('ai_suggested_response'),
                processed_at=datetime.utcnow()
            )
            db.merge(ticket)
        
        db.commit()
        print(f"[OK] Stored {len(df)} tickets to database")
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
    finally:
        db.close()

def run_pipeline(csv_path: str = "support_tickets.csv", sample_size: int = None):
    """Run the complete data pipeline"""
    print("=" * 60)
    print("STARTING DATA PIPELINE")
    print("=" * 60)
    
    # 1. Load raw data
    print("\n[1/4] Loading data...")
    df = pd.read_csv(csv_path)
    print(f"[OK] Loaded {len(df)} tickets")
    
    # Sample for faster processing during development
    if sample_size:
        df = df.sample(n=min(sample_size, len(df)), random_state=42)
        print(f"[OK] Sampled {len(df)} tickets for processing")
    
    # 2. Clean data
    print("\n[2/4] Cleaning data...")
    df = clean_data(df)
    print(f"[OK] Cleaned data: {len(df)} valid tickets")
    
    # 3. AI enrichment
    print("\n[3/4] AI enrichment...")
    df = enrich_with_ai(df)
    print(f"[OK] AI processing complete")
    
    # 4. Store to database
    print("\n[4/4] Storing to database...")
    store_to_database(df)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    
    return df

if __name__ == "__main__":
    # Run pipeline with sample for testing
    run_pipeline(sample_size=200)
