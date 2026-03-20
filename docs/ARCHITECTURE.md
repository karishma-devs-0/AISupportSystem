# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                     Streamlit Dashboard                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │ Tickets  │  │   AI     │  │ Business │       │
│  │ Overview │  │ Analysis │  │Assistant │  │ Metrics  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                   Data Pipeline                         │    │
│  │  CSV Upload → Clean → Enrich → Store                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    AI Engine                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│  │  │Categorization│  │  Sentiment   │  │  Response   │ │    │
│  │  │  (GPT-4o)    │  │  Analysis    │  │ Generation  │ │    │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │    │
│  │                                                         │    │
│  │  ┌──────────────┐  ┌──────────────┐                  │    │
│  │  │   Anomaly    │  │  Top Issues  │                  │    │
│  │  │  Detection   │  │  Extraction  │                  │    │
│  │  └──────────────┘  └──────────────┘                  │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│                                                                  │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │   SQLite Database   │         │   ChromaDB Vector   │       │
│  │                     │         │       Store         │       │
│  │  ┌──────────────┐  │         │  ┌──────────────┐  │       │
│  │  │   Tickets    │  │         │  │  Embeddings  │  │       │
│  │  │   Table      │  │         │  │  (Resolved)  │  │       │
│  │  └──────────────┘  │         │  └──────────────┘  │       │
│  │                     │         │                     │       │
│  │  ┌──────────────┐  │         │  ┌──────────────┐  │       │
│  │  │   Insights   │  │         │  │   Metadata   │  │       │
│  │  │   Table      │  │         │  │              │  │       │
│  │  └──────────────┘  │         │  └──────────────┘  │       │
│  └─────────────────────┘         └─────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │   OpenAI API        │                                        │
│  │   - GPT-4o-mini     │                                        │
│  │   - Embeddings      │                                        │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Ticket Ingestion
```
CSV File → Pandas DataFrame → Validation → Deduplication
```

### 2. AI Processing Pipeline
```
Raw Ticket
    │
    ├─→ Categorization (GPT-4o-mini)
    │       │
    │       └─→ Category Label
    │
    ├─→ Sentiment Analysis (GPT-4o-mini)
    │       │
    │       └─→ Sentiment + Frustration Score
    │
    └─→ Response Generation (RAG)
            │
            ├─→ Query ChromaDB for similar tickets
            │
            ├─→ Retrieve top 3 matches
            │
            └─→ Generate response with context (GPT-4o-mini)
```

### 3. Storage
```
Processed Ticket → SQLite (structured data)
                → ChromaDB (if resolved, for RAG)
```

### 4. Analytics
```
SQLite Query → Pandas Aggregation → Plotly Visualization → Streamlit
```

## Component Details

### Frontend (Streamlit)
- **Pages**: Dashboard, Ticket Analysis, AI Assistant, Business Metrics, Data Upload
- **Visualizations**: Plotly charts (bar, line, pie, scatter)
- **Interactivity**: Filters, search, real-time updates

### Backend (Python)
- **Framework**: Streamlit (integrated frontend + backend)
- **Database ORM**: SQLAlchemy
- **Data Processing**: Pandas
- **AI Integration**: OpenAI Python SDK

### AI Engine
- **Categorization**: Zero-shot classification with GPT-4o-mini
- **Sentiment**: JSON-structured output from GPT-4o-mini
- **RAG**: ChromaDB for vector similarity search
- **Anomaly Detection**: Statistical (mean + 2σ)

### Data Storage
- **SQLite**: Relational data (tickets, insights)
- **ChromaDB**: Vector embeddings for RAG
- **File System**: CSV uploads, logs

## Deployment Architecture

### Development
```
Local Machine
    │
    ├─→ Python 3.11+
    ├─→ Virtual Environment
    └─→ Streamlit Dev Server (port 8501)
```

### Production (Docker)
```
Docker Container
    │
    ├─→ Python 3.11-slim base image
    ├─→ Application code
    ├─→ Dependencies (requirements.txt)
    └─→ Streamlit production server
```

### Cloud Deployment (Fly.io / Railway / Render)
```
Git Push
    │
    └─→ CI/CD Pipeline (GitHub Actions)
            │
            ├─→ Build Docker image
            ├─→ Run tests
            └─→ Deploy to cloud
                    │
                    └─→ Container instance
                            │
                            ├─→ Public URL
                            └─→ Health checks
```

## Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **Database**: SQLite file permissions restricted
3. **Input Validation**: All user inputs sanitized
4. **Rate Limiting**: OpenAI API calls batched and cached
5. **HTTPS**: Enforced in production deployment

## Scalability Path

### Current (MVP)
- Single instance
- SQLite database
- Synchronous processing
- **Capacity**: 10K tickets/day

### Phase 2 (Growth)
- PostgreSQL database
- Celery + Redis for async processing
- Multiple worker instances
- **Capacity**: 100K tickets/day

### Phase 3 (Enterprise)
- Kubernetes orchestration
- Distributed vector database (Qdrant/Pinecone)
- Load balancer
- Auto-scaling
- **Capacity**: 1M+ tickets/day

## Monitoring & Observability

### Metrics
- Request latency
- API call success rate
- Database query performance
- Error rates

### Logging
- Application logs (Python logging)
- API call logs (OpenAI)
- User interaction logs (Streamlit)

### Alerts
- High error rate
- API quota exceeded
- Database connection failures
- Anomaly detection triggers

## Cost Structure

### Development
- OpenAI API: ~$1-2/day
- Infrastructure: $0 (local)

### Production (10K tickets/day)
- OpenAI API: ~$50/month
- Hosting: ~$10/month (Fly.io/Railway)
- **Total**: ~$60/month

### At Scale (100K tickets/day)
- OpenAI API: ~$500/month
- Hosting: ~$100/month (multiple instances)
- Database: ~$50/month (managed PostgreSQL)
- **Total**: ~$650/month

**ROI**: $13K+ saved in agent time → 20x return
