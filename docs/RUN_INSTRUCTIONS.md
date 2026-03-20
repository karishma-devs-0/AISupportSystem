# 🚀 How to Run This Project

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Key

Create a `.env` file:
```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

### Step 3: Generate Sample Data

```bash
python generate_data.py
```

This creates `support_tickets.csv` with 10,000 synthetic tickets.

### Step 4: Process Data (Optional - for faster demo)

For a quick demo, process just 100 tickets:

```bash
python -c "from pipeline import run_pipeline; run_pipeline(sample_size=100)"
```

Or process all 10,000 tickets (takes ~10 minutes):

```bash
python pipeline.py
```

### Step 5: Launch Dashboard

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## What You'll See

### 📊 Dashboard Page
- Total tickets, avg frustration, revenue at risk
- Top 7 issues with frustration heatmap
- Sentiment distribution pie chart
- Anomaly detection alerts
- Daily ticket trends
- Channel and country breakdowns

### 🔍 Ticket Analysis Page
- Filter by category, sentiment, frustration
- View individual tickets with:
  - Customer message
  - Agent reply (if resolved)
  - AI-suggested response
  - Frustration score
  - Order value and metadata

### 🤖 AI Assistant Page
Test the AI in real-time:
1. Enter a customer message
2. See instant categorization
3. View sentiment analysis
4. Get suggested response

Try these examples:
```
"My order hasn't arrived yet and it's been 10 days. This is unacceptable!"

"The headphones I received are broken. Left ear doesn't work."

"I was told my refund would be processed 5 days ago but I still haven't received it."
```

### 📈 Business Metrics Page
- Cost savings calculation
- Revenue at risk analysis
- Potential churn estimation
- Top 3 insights for leadership
- Recommended actions

### ⚙️ Data Upload Page
- Upload your own CSV files
- Process with AI
- Choose sample size for testing

---

## Using Your Own Data

### CSV Format Required

Your CSV should have these columns:
```
ticket_id, timestamp, customer_id, channel, message, agent_reply, 
product, order_value, customer_country, resolution_status
```

Example:
```csv
ticket_id,timestamp,customer_id,channel,message,agent_reply,product,order_value,customer_country,resolution_status
TKT001,2024-01-15T10:30:00,CUST123,email,My order is late,We apologize...,Laptop,599.99,US,resolved
```

### Upload Process

1. Go to **⚙️ Data Upload** page
2. Click "Browse files" and select your CSV
3. Preview the data
4. Choose sample size (start with 100 for testing)
5. Click "🚀 Process Tickets"
6. Wait for AI processing (progress shown)
7. Check Dashboard for insights

---

## Docker Method (Alternative)

If you prefer Docker:

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8501
```

To stop:
```bash
docker-compose down
```

---

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

### Pipeline is too slow
Process fewer tickets:
```bash
python -c "from pipeline import run_pipeline; run_pipeline(sample_size=50)"
```

### Port 8501 already in use
Kill the existing process:
```bash
# Linux/Mac
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

Or use a different port:
```bash
streamlit run app.py --server.port 8502
```

---

## Testing the AI Features

### 1. Categorization
Navigate to **🤖 AI Assistant** and enter:
```
"My package was supposed to arrive yesterday but tracking shows no updates"
```
Expected: Category = "Shipping Delay"

### 2. Sentiment Analysis
Try:
```
"This is ridiculous! I've been waiting for 2 weeks and no one is helping me!"
```
Expected: Sentiment = "negative", High frustration score

### 3. Response Generation
The AI will suggest a professional response based on similar resolved tickets.

### 4. Anomaly Detection
Check **📊 Dashboard** for alerts like:
```
🚨 Shipping Delay spike detected! 450 tickets in last 7 days (+85% vs baseline of 243)
```

---

## Performance Tips

### For Faster Processing

1. **Use sample size**: Process 100-200 tickets first
2. **Batch processing**: Already optimized (50 tickets/batch)
3. **Cache results**: Dashboard caches data for 5 minutes

### For Production

1. **Upgrade to PostgreSQL**: Better concurrency
2. **Use Celery**: Async background processing
3. **Add Redis**: Caching layer
4. **Scale horizontally**: Multiple instances

---

## API Costs

### Current Usage (10K tickets)
- Categorization: ~$0.50
- Sentiment: ~$0.50
- Response generation: ~$0.50
- **Total**: ~$1.50/day

### At Scale (100K tickets/day)
- **Total**: ~$15/day = $450/month

**ROI**: Saves $13K/month in agent time = 29x return

---

## Next Steps

1. ✅ Run the app locally
2. ✅ Test with sample data
3. ✅ Try the AI assistant
4. ✅ Upload your own data
5. 📹 Record demo video
6. 🚀 Deploy to cloud (see DEPLOYMENT.md)

---

## Need Help?

- Check [QUICKSTART.md](QUICKSTART.md) for detailed setup
- See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment
- Read [DESIGN_DOC.md](DESIGN_DOC.md) for technical details
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

**Enjoy exploring the platform! 🎯**
