# 🚀 Quick Start Guide

Get the platform running in under 5 minutes!

## Prerequisites

- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Git

## Option 1: Automated Setup (Recommended)

### On Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

### On Windows:
```cmd
setup.bat
```

Then start the app:
```bash
streamlit run app.py
```

## Option 2: Manual Setup

### 1. Clone & Install
```bash
git clone <repo-url>
cd support-insight-platform
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

### 3. Generate Data
```bash
python generate_data.py
```
Creates `support_tickets.csv` with 10,000 synthetic tickets.

### 4. Run Pipeline
```bash
python pipeline.py
```
Processes tickets with AI (takes 5-10 minutes for full dataset).

**Tip**: For faster testing, edit `pipeline.py` line 108 to use `sample_size=100`

### 5. Launch Dashboard
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Option 3: Docker

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8501
```

## First Steps in the App

1. **📊 Dashboard** - See overview of all insights
2. **🔍 Ticket Analysis** - Explore individual tickets
3. **🤖 AI Assistant** - Test AI on custom messages
4. **📈 Business Metrics** - View cost savings and revenue impact
5. **⚙️ Data Upload** - Upload your own CSV data

## Testing the AI

Navigate to **🤖 AI Assistant** and try these examples:

**Example 1: Shipping Delay**
```
My order hasn't arrived yet and it's been 10 days. 
This is unacceptable! I need it urgently.
```

**Example 2: Product Defect**
```
The headphones I received are broken. 
Left ear doesn't work at all.
```

**Example 3: Refund Issue**
```
I was told my refund would be processed 5 days ago 
but I still haven't received it.
```

## Troubleshooting

### "No module named 'openai'"
```bash
pip install -r requirements.txt
```

### "OpenAI API key not found"
Make sure `.env` file exists with:
```
OPENAI_API_KEY=sk-your-actual-key
```

### "No tickets found"
Run the pipeline first:
```bash
python pipeline.py
```

### Pipeline is slow
Edit `pipeline.py` and change:
```python
run_pipeline(sample_size=100)  # Process only 100 tickets
```

### Docker port already in use
Change port in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Use 8502 instead
```

## Next Steps

- Read [DESIGN_DOC.md](DESIGN_DOC.md) for architecture details
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [README.md](README.md) for full documentation

## Demo Video Script

Record a 5-10 minute demo covering:

1. **Introduction** (30s)
   - Problem: E-commerce company drowning in support tickets
   - Solution: AI-powered insights platform

2. **Dashboard Tour** (2 min)
   - Show top metrics
   - Highlight top issues
   - Point out anomaly detection

3. **Ticket Analysis** (2 min)
   - Filter by category
   - Show AI categorization
   - Display suggested responses

4. **AI Assistant Demo** (2 min)
   - Enter live customer message
   - Show real-time categorization
   - Display sentiment analysis
   - Generate suggested response

5. **Business Impact** (2 min)
   - Cost savings calculation
   - Revenue at risk identification
   - Key insights for leadership

6. **Technical Highlights** (1 min)
   - RAG implementation
   - Anomaly detection
   - Scalability approach

7. **Conclusion** (30s)
   - Recap benefits
   - Call to action

## Support

For issues or questions:
- Open a GitHub issue
- Check documentation
- Review code comments

---

**Happy analyzing! 🎯**
