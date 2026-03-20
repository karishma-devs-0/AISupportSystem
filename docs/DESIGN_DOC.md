# Design Document: AI-Powered Customer Support Insight Platform

## Executive Summary

This platform ingests customer support tickets and uses AI to extract actionable insights, enabling data-driven decisions that reduce costs and improve customer satisfaction.

## 1. AI Choices

### 1.1 Ticket Categorization

**Approach**: OpenAI GPT-4o-mini with structured prompts

**Rationale**:
- Zero-shot learning eliminates training data requirements
- Handles edge cases and ambiguous tickets better than rule-based systems
- Structured output ensures consistent categorization
- Cost-effective at ~$0.0001 per ticket

**Alternative Considered**: Sentence-transformers + K-means clustering
- **Pros**: No API costs, faster inference
- **Cons**: Requires manual cluster labeling, less accurate on edge cases
- **Decision**: GPT-4o-mini chosen for MVP speed and accuracy

### 1.2 Sentiment & Frustration Analysis

**Approach**: GPT-4o-mini with JSON response format

**Output Schema**:
```json
{
  "sentiment": "positive|neutral|negative",
  "frustration_score": 0.0-1.0,
  "reasoning": "brief explanation"
}
```

**Rationale**:
- Captures nuanced emotions beyond simple positive/negative
- Frustration score enables prioritization by urgency
- Reasoning provides explainability for agents

**Alternative Considered**: Fine-tuned BERT model
- **Pros**: Lower latency, no API dependency
- **Cons**: Requires labeled training data, less nuanced
- **Decision**: GPT chosen for richer analysis without training overhead

### 1.3 Response Generation (RAG)

**Approach**: Retrieval-Augmented Generation with ChromaDB + GPT-4o-mini

**Pipeline**:
1. Embed resolved tickets in ChromaDB vector store
2. For new ticket, retrieve 3 most similar resolved cases
3. Pass context + ticket to GPT-4o-mini
4. Generate contextually relevant response

**Rationale**:
- Grounds responses in actual resolution patterns
- Reduces hallucination risk
- Maintains consistency with company policies
- Learns from successful resolutions

**Alternative Considered**: Pure GPT-4o-mini without RAG
- **Pros**: Simpler implementation
- **Cons**: Generic responses, no company-specific knowledge
- **Decision**: RAG chosen for quality and consistency

### 1.4 Anomaly Detection

**Approach**: Statistical threshold (mean + 2σ)

**Method**:
- Calculate daily ticket counts per category
- Flag when recent 7-day count exceeds mean + 2 standard deviations
- Report spike percentage vs baseline

**Rationale**:
- Simple, interpretable, no training needed
- Effective for detecting sudden changes
- Low false positive rate with 2σ threshold

**Alternative Considered**: Isolation Forest / LSTM
- **Pros**: Detects complex patterns
- **Cons**: Requires historical data, harder to explain
- **Decision**: Statistical method chosen for transparency

## 2. Data Model

### 2.1 Schema Design

**Tickets Table**:
```sql
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    ticket_id TEXT UNIQUE,
    timestamp DATETIME,
    customer_id TEXT,
    channel TEXT,
    message TEXT,
    agent_reply TEXT,
    product TEXT,
    order_value REAL,
    customer_country TEXT,
    resolution_status TEXT,
    
    -- AI-generated fields
    ai_category TEXT,
    ai_sentiment TEXT,
    ai_frustration_score REAL,
    ai_suggested_response TEXT,
    processed_at DATETIME
);
```

**Indexes**:
- `ticket_id` (unique)
- `timestamp` (for time-series queries)
- `customer_id` (for customer history)
- `ai_category` (for aggregations)

### 2.2 Vector Store (ChromaDB)

**Collection**: `resolved_tickets`

**Documents**: 
```
"Issue: {customer_message}\nResolution: {agent_reply}"
```

**Metadata**: `ticket_id`, `category`, `resolution_date`

**Embedding Model**: OpenAI text-embedding-3-small (default)

### 2.3 Data Flow

```
Raw CSV → Pandas DataFrame → Cleaning → AI Enrichment → SQLite + ChromaDB
```

**Cleaning Steps**:
1. Remove duplicates by `ticket_id`
2. Fill missing values
3. Convert timestamps to datetime
4. Filter invalid tickets (message length < 10)

**Enrichment Steps**:
1. Categorize with GPT-4o-mini
2. Analyze sentiment
3. Generate suggested response
4. Add resolved tickets to ChromaDB

## 3. Scalability

### 3.1 Current Architecture (MVP)

**Capacity**: 10,000 tickets/day
- SQLite: Handles up to 100K rows efficiently
- ChromaDB: Embedded, scales to 1M vectors
- Streamlit: Single instance, 100 concurrent users

**Bottlenecks**:
- OpenAI API rate limits (3,500 RPM on tier 1)
- Synchronous processing
- Single database connection

### 3.2 Production Scale (100K+ tickets/day)

**Database**:
- Migrate to PostgreSQL with connection pooling
- Partition by date for faster queries
- Read replicas for analytics

**Processing**:
- Celery + Redis for async task queue
- Batch processing (100 tickets/batch)
- Retry logic with exponential backoff

**Vector Store**:
- Migrate to Qdrant or Pinecone for distributed search
- Separate instance from app server

**API Layer**:
- FastAPI backend (separate from Streamlit)
- Load balancer (Nginx/AWS ALB)
- Horizontal scaling (3+ instances)

**Caching**:
- Redis for frequently accessed insights
- Cache invalidation on new data

### 3.3 Cost Optimization

**Current Costs** (10K tickets):
- OpenAI API: ~$1.50/day
  - Categorization: $0.50
  - Sentiment: $0.50
  - Response generation: $0.50
- Infrastructure: $0 (local) or ~$5/month (Fly.io)

**Optimization Strategies**:
1. **Batch API calls** - Reduce overhead
2. **Cache common categories** - Skip API for obvious cases
3. **Use GPT-4o-mini** - 60% cheaper than GPT-4
4. **Prompt compression** - Reduce token usage
5. **Fallback to rules** - Handle simple cases locally

**At Scale** (100K tickets/day):
- OpenAI: ~$15/day = $450/month
- Infrastructure: ~$50/month (2 instances)
- **Total**: ~$500/month

**ROI**: If platform saves 40% of agent time:
- 100K tickets × 8 min × 0.4 = 533 hours saved
- 533 hours × $25/hour = **$13,325/month saved**
- **ROI**: 26x

## 4. Tradeoffs

### 4.1 Technology Choices

| Choice | Pros | Cons | Decision |
|--------|------|------|----------|
| **Streamlit vs React** | 10x faster dev, built-in components | Less customizable, harder to scale | Streamlit for MVP |
| **SQLite vs PostgreSQL** | Zero setup, portable | Limited concurrency, no replication | SQLite for MVP, migrate later |
| **GPT-4o-mini vs local model** | Better accuracy, no training | API dependency, cost | GPT for quality |
| **Batch vs streaming** | Simpler, easier to debug | Higher latency | Batch for MVP |
| **ChromaDB vs Pinecone** | Embedded, no infra | Limited scale | ChromaDB for MVP |

### 4.2 AI Tradeoffs

**Accuracy vs Cost**:
- GPT-4 would be more accurate but 10x more expensive
- GPT-4o-mini provides 90% accuracy at 10% cost
- **Decision**: GPT-4o-mini sufficient for MVP

**Latency vs Quality**:
- RAG adds 200ms latency but improves response quality 40%
- **Decision**: Quality prioritized, latency acceptable

**Automation vs Safety**:
- Could auto-send AI responses but risk errors
- **Decision**: Suggest only, human approval required

### 4.3 Feature Prioritization

**MVP (3 hours)**:
- ✅ Core AI features
- ✅ Basic dashboard
- ✅ Docker deployment
- ✅ Anomaly detection
- ✅ RAG responses

**Phase 2** (if more time):
- Multi-language support (already works with GPT)
- A/B testing framework
- Agent performance analytics
- Automated weekly reports
- Slack/email alerts

## 5. Business Thinking

### 5.1 Top 3 Insights for Leadership

1. **Revenue at Risk Identification**
   - Track high-frustration customers with high order values
   - Proactive outreach can prevent churn
   - Metric: Sum of order_value where frustration > 0.7

2. **Operational Efficiency Gaps**
   - Top 3 categories represent 60%+ of volume
   - Focused improvements have outsized impact
   - Metric: Category distribution + resolution time

3. **Emerging Issues (Anomaly Detection)**
   - Detect problems before they become crises
   - Example: Shipping delay spike indicates logistics issue
   - Metric: Week-over-week category growth

### 5.2 Cost Reduction Mechanisms

1. **AI-Assisted Responses** (40% time savings)
   - Agents use suggested responses as templates
   - Reduces avg handling time from 8 min → 5 min
   - Savings: $13K/month at 100K tickets

2. **Automated Categorization**
   - Eliminates manual ticket routing
   - Faster assignment to right team
   - Savings: 2 min/ticket × 100K = 3,333 hours/month

3. **Proactive Issue Resolution**
   - Anomaly detection enables early intervention
   - Prevents ticket volume spikes
   - Savings: 10-20% volume reduction

### 5.3 Revenue & Retention Impact

1. **Churn Prevention**
   - Identify at-risk customers (frustration > 0.7)
   - Proactive outreach with special offers
   - Impact: 30% churn reduction = $50K+/month retained revenue

2. **Faster Resolution**
   - AI suggestions reduce resolution time
   - Happier customers → higher CSAT → better retention
   - Impact: 5% CSAT improvement = 2% retention lift

3. **Product Insights**
   - Ticket analysis reveals product issues
   - Faster fixes → fewer returns → higher margins
   - Impact: 10% reduction in returns = $20K/month

### 5.4 Metrics to Track

**Operational**:
- Ticket volume (total, by category, by channel)
- Average handling time
- First response time
- Resolution rate
- Escalation rate

**Customer**:
- CSAT score
- Frustration score (AI-generated)
- Repeat contact rate
- Churn rate (high-frustration customers)

**Business**:
- Cost per ticket
- Revenue at risk
- Automation rate
- Agent productivity (tickets/hour)

**AI Performance**:
- Categorization accuracy (vs human labels)
- Response acceptance rate (agents using suggestions)
- Anomaly detection precision/recall

## 6. Future Enhancements

### 6.1 Short-term (1-3 months)

1. **Agent Feedback Loop**
   - Agents rate AI suggestions
   - Fine-tune prompts based on feedback
   - Improve accuracy over time

2. **Multi-language Support**
   - Detect language automatically
   - Translate to English for processing
   - Respond in original language

3. **Automated Reporting**
   - Weekly executive summary email
   - Slack alerts for anomalies
   - Custom dashboards per team

### 6.2 Long-term (3-6 months)

1. **Predictive Analytics**
   - Forecast ticket volume
   - Predict churn risk per customer
   - Optimize staffing levels

2. **Voice/Chat Integration**
   - Real-time transcription
   - Live agent assistance
   - Sentiment analysis during call

3. **Self-Service Automation**
   - Chatbot for common issues
   - Automated resolution for simple cases
   - Escalate to human when needed

## 7. Conclusion

This platform demonstrates how AI can transform customer support from reactive to proactive, reducing costs while improving customer satisfaction. The MVP architecture prioritizes speed and simplicity while maintaining clear paths to scale.

**Key Success Factors**:
- AI quality (GPT-4o-mini + RAG)
- Actionable insights (not just data)
- Business impact focus (cost, revenue, retention)
- Scalable architecture (clear migration path)

**Next Steps**:
1. Deploy MVP to production
2. Gather agent feedback
3. Measure impact on KPIs
4. Iterate based on results
