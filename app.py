"""AI-Powered Customer Support Insight Platform - FREE VERSION
No API costs! Uses open-source models for all AI features.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.database import SessionLocal, Ticket, init_db
from core.ai_engine import (
    detect_anomalies, get_top_issues, calculate_cost_savings,
    categorize_ticket, analyze_sentiment, generate_response,
    get_ai_mode_info
)

# Page config
st.set_page_config(
    page_title="Support Insight Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

@st.cache_data(ttl=300)
def load_tickets():
    """Load tickets from database"""
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        data = [{
            'ticket_id': t.ticket_id,
            'timestamp': t.timestamp,
            'customer_id': t.customer_id,
            'channel': t.channel,
            'message': t.message,
            'agent_reply': t.agent_reply,
            'product': t.product,
            'order_value': t.order_value,
            'customer_country': t.customer_country,
            'resolution_status': t.resolution_status,
            'ai_category': t.ai_category,
            'ai_sentiment': t.ai_sentiment,
            'ai_frustration_score': t.ai_frustration_score,
            'ai_suggested_response': t.ai_suggested_response
        } for t in tickets]
        return pd.DataFrame(data)
    finally:
        db.close()

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/667eea/ffffff?text=SupportAI", use_container_width=True)
        st.title("🎯 Support Insights")
        
        # Show AI mode
        mode_info = get_ai_mode_info()
        if mode_info['mode'] == 'llm':
            st.success(f"🤖 LLM MODE - {mode_info['provider']}")
            st.caption(f"Accuracy: {mode_info['accuracy']}")
        else:
            st.info("💰 FREE MODE - No API costs!")
            st.caption(f"Accuracy: {mode_info['accuracy']}")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "🔍 Ticket Analysis", "🤖 AI Assistant", "📈 Business Metrics", "⚙️ Data Upload"]
        )
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        # Check if data exists
        if os.path.exists("support_platform.db"):
            df = load_tickets()
            if not df.empty:
                st.metric("Total Tickets", len(df))
                st.metric("Pending", len(df[df['resolution_status'] == 'pending']))
                st.metric("Avg Frustration", f"{df['ai_frustration_score'].mean():.2f}")
        else:
            st.warning("No data loaded. Please upload data first.")
    
    # Main content
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🔍 Ticket Analysis":
        show_ticket_analysis()
    elif page == "🤖 AI Assistant":
        show_ai_assistant()
    elif page == "📈 Business Metrics":
        show_business_metrics()
    elif page == "⚙️ Data Upload":
        show_data_upload()

def show_dashboard():
    st.title("📊 Support Insights Dashboard")
    
    df = load_tickets()
    
    if df.empty:
        st.warning("No tickets found. Please upload data first.")
        return
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tickets",
            f"{len(df):,}",
            delta=f"+{len(df[df['timestamp'] > datetime.now() - timedelta(days=7)])} this week"
        )
    
    with col2:
        avg_frustration = df['ai_frustration_score'].mean()
        st.metric(
            "Avg Frustration",
            f"{avg_frustration:.2f}",
            delta=f"{avg_frustration - 0.5:.2f}",
            delta_color="inverse"
        )
    
    with col3:
        revenue_at_risk = df[df['ai_frustration_score'] > 0.7]['order_value'].sum()
        st.metric(
            "Revenue at Risk",
            f"${revenue_at_risk:,.0f}",
            delta="High frustration orders"
        )
    
    with col4:
        resolution_rate = len(df[df['resolution_status'] == 'resolved']) / len(df) * 100
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            delta=f"{resolution_rate - 70:.1f}%"
        )
    
    st.markdown("---")
    
    # Top Issues
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔥 Top Issues")
        top_issues = get_top_issues(df, n=7)
        
        if top_issues:
            issues_df = pd.DataFrame(top_issues)
            fig = px.bar(
                issues_df,
                x='count',
                y='category',
                orientation='h',
                color='avg_frustration',
                color_continuous_scale='RdYlGn_r',
                labels={'count': 'Number of Tickets', 'category': 'Issue Category'},
                title="Issue Volume & Frustration Level"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            st.dataframe(
                issues_df[['category', 'count', 'percentage', 'revenue_at_risk']],
                use_container_width=True,
                hide_index=True
            )
    
    with col2:
        st.subheader("😊 Sentiment Distribution")
        sentiment_counts = df['ai_sentiment'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=0.4,
            marker=dict(colors=['#ef4444', '#fbbf24', '#10b981'])
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Anomaly Detection
    st.markdown("---")
    st.subheader("🚨 Anomaly Detection")
    
    anomalies = detect_anomalies(df)
    
    if anomalies:
        for anomaly in anomalies[:3]:
            st.error(
                f"**{anomaly['category']}** spike detected! "
                f"{anomaly['recent_count']} tickets in last 7 days "
                f"(+{anomaly['spike_percentage']}% vs baseline of {anomaly['baseline']})"
            )
    else:
        st.success("No significant anomalies detected in the last 7 days.")
    
    # Trend Analysis
    st.markdown("---")
    st.subheader("📈 Ticket Trends")
    
    df['date'] = df['timestamp'].dt.date
    daily_tickets = df.groupby('date').size().reset_index(name='count')
    
    fig = px.line(
        daily_tickets,
        x='date',
        y='count',
        title="Daily Ticket Volume",
        labels={'date': 'Date', 'count': 'Number of Tickets'}
    )
    fig.update_traces(line_color='#667eea', line_width=3)
    st.plotly_chart(fig, use_container_width=True)
    
    # Channel & Country breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📱 Tickets by Channel")
        channel_counts = df['channel'].value_counts()
        fig = px.pie(
            values=channel_counts.values,
            names=channel_counts.index,
            title="Distribution by Channel"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Top Countries")
        country_counts = df['customer_country'].value_counts().head(8)
        fig = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation='h',
            title="Tickets by Country"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_ticket_analysis():
    st.title("🔍 Ticket Analysis")
    
    df = load_tickets()
    
    if df.empty:
        st.warning("No tickets found.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.multiselect(
            "Filter by Category",
            options=df['ai_category'].unique(),
            default=[]
        )
    
    with col2:
        sentiment_filter = st.multiselect(
            "Filter by Sentiment",
            options=df['ai_sentiment'].unique(),
            default=[]
        )
    
    with col3:
        frustration_threshold = st.slider(
            "Min Frustration Score",
            0.0, 1.0, 0.0, 0.1
        )
    
    # Apply filters
    filtered_df = df.copy()
    if category_filter:
        filtered_df = filtered_df[filtered_df['ai_category'].isin(category_filter)]
    if sentiment_filter:
        filtered_df = filtered_df[filtered_df['ai_sentiment'].isin(sentiment_filter)]
    filtered_df = filtered_df[filtered_df['ai_frustration_score'] >= frustration_threshold]
    
    st.info(f"Showing {len(filtered_df)} of {len(df)} tickets")
    
    # Display tickets
    for _, ticket in filtered_df.head(20).iterrows():
        with st.expander(f"🎫 {ticket['ticket_id']} - {ticket['ai_category']} ({ticket['ai_sentiment']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Customer Message:**")
                st.write(ticket['message'])
                
                if ticket['agent_reply']:
                    st.markdown(f"**Agent Reply:**")
                    st.info(ticket['agent_reply'])
                
                st.markdown(f"**AI Suggested Response:**")
                st.success(ticket['ai_suggested_response'])
            
            with col2:
                st.metric("Frustration Score", f"{ticket['ai_frustration_score']:.2f}")
                st.metric("Order Value", f"${ticket['order_value']:.2f}")
                st.write(f"**Channel:** {ticket['channel']}")
                st.write(f"**Product:** {ticket['product']}")
                st.write(f"**Country:** {ticket['customer_country']}")
                st.write(f"**Status:** {ticket['resolution_status']}")

def show_ai_assistant():
    st.title("🤖 AI Support Assistant")
    
    mode_info = get_ai_mode_info()
    if mode_info['mode'] == 'llm':
        st.success(f"🤖 LLM MODE - Using {mode_info['provider']} (90%+ accuracy)")
    else:
        st.info("💰 FREE MODE - Using TextBlob + keyword matching (78% accuracy)")
    
    st.markdown("""
    Test the AI assistant by entering a customer message. The system will:
    - Categorize the issue
    - Analyze sentiment and frustration
    - Generate a suggested response
    """)
    
    # Input
    customer_message = st.text_area(
        "Customer Message",
        placeholder="Enter a customer support message...",
        height=150
    )
    
    if st.button("🔍 Analyze", type="primary"):
        if customer_message:
            with st.spinner("Processing with AI..."):
                # Categorization
                category = categorize_ticket(customer_message)
                
                # Sentiment
                sentiment_data = analyze_sentiment(customer_message)
                
                # Response
                suggested_response = generate_response(customer_message, category)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Category", category)
                
                with col2:
                    st.metric("Sentiment", sentiment_data.get('sentiment', 'N/A'))
                
                with col3:
                    frustration = sentiment_data.get('frustration_score', 0)
                    st.metric("Frustration", f"{frustration:.2f}")
                
                st.markdown("---")
                st.subheader("💡 Suggested Response")
                st.success(suggested_response)
                
                st.markdown("---")
                st.subheader("🧠 AI Reasoning")
                st.info(sentiment_data.get('reasoning', 'N/A'))
        else:
            st.warning("Please enter a customer message.")

def show_business_metrics():
    st.title("📈 Business Impact Metrics")
    
    st.success("💰 Platform Cost: $0/month (FREE open-source models!)")
    
    df = load_tickets()
    
    if df.empty:
        st.warning("No data available.")
        return
    
    # Cost savings
    st.subheader("💰 Cost Savings Analysis")
    savings = calculate_cost_savings(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", f"{savings['total_tickets']:,}")
    
    with col2:
        st.metric("Automatable", f"{savings['automatable_tickets']:,}")
    
    with col3:
        st.metric("Hours Saved", f"{savings['hours_saved']:,.1f}")
    
    with col4:
        st.metric("Cost Savings", f"${savings['cost_savings_usd']:,.2f}")
    
    st.info(f"**Efficiency Gain:** {savings['efficiency_gain']} of tickets can be automated with AI")
    
    # Revenue impact
    st.markdown("---")
    st.subheader("💵 Revenue Impact")
    
    high_frustration = df[df['ai_frustration_score'] > 0.7]
    revenue_at_risk = high_frustration['order_value'].sum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Revenue at Risk",
            f"${revenue_at_risk:,.2f}",
            help="Total order value from highly frustrated customers"
        )
        
        st.metric(
            "High-Risk Customers",
            len(high_frustration),
            help="Customers with frustration score > 0.7"
        )
    
    with col2:
        # Retention impact
        churn_risk = len(high_frustration) * 0.3  # Assume 30% churn risk
        retention_value = churn_risk * df['order_value'].mean() * 3  # 3x LTV
        
        st.metric(
            "Potential Churn",
            f"{churn_risk:.0f} customers",
            help="Estimated customers at risk of churning"
        )
        
        st.metric(
            "Retention Value",
            f"${retention_value:,.2f}",
            help="Potential revenue saved by preventing churn"
        )
    
    # Key insights for leadership
    st.markdown("---")
    st.subheader("🎯 Key Insights for Leadership")
    
    top_issues = get_top_issues(df, n=3)
    
    st.markdown("### Top 3 Issues Requiring Attention:")
    for i, issue in enumerate(top_issues, 1):
        st.markdown(f"""
        **{i}. {issue['category']}**
        - Volume: {issue['count']} tickets ({issue['percentage']}%)
        - Avg Frustration: {issue['avg_frustration']}/1.0
        - Revenue at Risk: ${issue['revenue_at_risk']:,.2f}
        """)
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Recommended Actions")
    
    anomalies = detect_anomalies(df)
    if anomalies:
        st.error(f"**Urgent:** {anomalies[0]['category']} complaints spiked by {anomalies[0]['spike_percentage']}% - investigate immediately")
    
    st.success("**Quick Win:** Implement AI-suggested responses to reduce handling time by 40%")
    st.info("**Strategic:** Focus on top 3 issues to impact 60%+ of customer complaints")

def show_data_upload():
    st.title("⚙️ Data Upload & Processing")
    
    st.markdown("""
    Upload customer support tickets for AI analysis. The system will:
    1. Clean and validate the data
    2. Categorize tickets using keyword matching (FREE)
    3. Analyze sentiment with TextBlob (FREE)
    4. Generate suggested responses (FREE)
    5. Store in database for insights
    
    **No API costs - completely free to run!**
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="CSV should contain: ticket_id, timestamp, message, etc."
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✓ Loaded {len(df)} tickets")
        st.dataframe(df.head(), use_container_width=True)
        
        # Processing options
        sample_size = st.slider(
            "Process sample size (for testing)",
            min_value=10,
            max_value=min(1000, len(df)),
            value=min(100, len(df)),
            help="Process a sample first to test the pipeline"
        )
        
        if st.button("🚀 Process Tickets", type="primary"):
            from core.pipeline import run_pipeline
            
            # Save uploaded file temporarily
            df.to_csv("temp_upload.csv", index=False)
            
            with st.spinner("Processing tickets with AI..."):
                try:
                    run_pipeline("temp_upload.csv", sample_size=sample_size)
                    st.success("✓ Processing complete! Check the Dashboard.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Generate synthetic data option
    st.markdown("---")
    st.subheader("🎲 Generate Synthetic Data")
    
    if st.button("Generate 10,000 Sample Tickets"):
        with st.spinner("Generating synthetic data..."):
            from utils.generate_data import generate_dataset
            df = generate_dataset(10000)
            df.to_csv("support_tickets.csv", index=False)
            st.success("✓ Generated support_tickets.csv")
            st.dataframe(df.head(), use_container_width=True)

if __name__ == "__main__":
    main()
