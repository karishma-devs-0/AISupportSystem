"""Generate synthetic customer support ticket dataset"""
import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Problem categories with realistic complaints
CATEGORIES = {
    "Shipping Delay": [
        "My order hasn't arrived yet and it's been {days} days",
        "Where is my package? Tracking shows no updates",
        "Delivery was supposed to be yesterday, still waiting",
        "Order #{order} is delayed, need urgent delivery"
    ],
    "Product Defect": [
        "Received damaged product, need replacement",
        "Item doesn't work as described",
        "Product quality is terrible, want refund",
        "Broken on arrival, very disappointed"
    ],
    "Wrong Item": [
        "Got the wrong item in my order",
        "This isn't what I ordered, please fix",
        "Received different color/size than ordered",
        "Order mix-up, need correct item sent"
    ],
    "Refund Issue": [
        "Haven't received my refund yet",
        "Refund was approved but money not in account",
        "How long does refund take? It's been {days} days",
        "Need refund processed urgently"
    ],
    "Account Problem": [
        "Can't log into my account",
        "Password reset not working",
        "Account locked, need help",
        "Email not updating in profile"
    ],
    "Payment Failed": [
        "Payment declined but money was deducted",
        "Can't complete checkout, payment error",
        "Credit card not being accepted",
        "Payment went through twice, need refund"
    ],
    "Cancellation Request": [
        "Need to cancel order #{order}",
        "Want to cancel before shipping",
        "How do I cancel my order?",
        "Cancel order and refund please"
    ]
}

PRODUCTS = [
    "Wireless Headphones", "Laptop Stand", "USB-C Cable", "Phone Case",
    "Bluetooth Speaker", "Webcam", "Keyboard", "Mouse", "Monitor",
    "Desk Lamp", "Backpack", "Water Bottle", "Yoga Mat", "Sneakers"
]

CHANNELS = ["chat", "email", "web"]
COUNTRIES = ["US", "UK", "CA", "AU", "DE", "FR", "IN", "BR"]

AGENT_RESPONSES = {
    "Shipping Delay": "I apologize for the delay. I've escalated your order to our shipping team. You should receive an update within 24 hours.",
    "Product Defect": "I'm sorry about the defective product. I've initiated a replacement order with expedited shipping at no cost.",
    "Wrong Item": "My apologies for the mix-up. I'll send the correct item right away and you can keep the wrong one.",
    "Refund Issue": "I see your refund was approved. It typically takes 5-7 business days to reflect in your account.",
    "Account Problem": "I've reset your account. Please check your email for a password reset link.",
    "Payment Failed": "I've checked with our payment team. The duplicate charge will be refunded within 3 business days.",
    "Cancellation Request": "Your order has been cancelled successfully. Refund will be processed within 24 hours."
}

def generate_ticket():
    """Generate a single realistic support ticket"""
    category = random.choice(list(CATEGORIES.keys()))
    template = random.choice(CATEGORIES[category])
    
    # Add variation to messages
    days = random.randint(3, 14)
    order_id = f"ORD{random.randint(10000, 99999)}"
    message = template.format(days=days, order=order_id)
    
    # Add frustration indicators randomly
    if random.random() < 0.3:
        frustration_words = [
            "This is unacceptable!", "Very frustrated!", "Terrible service!",
            "Not happy at all.", "This is ridiculous!", "Extremely disappointed."
        ]
        message += " " + random.choice(frustration_words)
    
    # Generate timestamp (last 90 days)
    timestamp = datetime.now() - timedelta(days=random.randint(0, 90))
    
    # Order value correlates with frustration
    base_value = random.uniform(20, 500)
    if "frustrated" in message.lower() or "terrible" in message.lower():
        base_value *= random.uniform(1.5, 3.0)  # High-value customers more vocal
    
    # Resolution status
    resolution = random.choices(
        ["resolved", "pending", "escalated"],
        weights=[0.7, 0.2, 0.1]
    )[0]
    
    agent_reply = AGENT_RESPONSES[category] if resolution == "resolved" else ""
    
    return {
        "ticket_id": f"TKT{random.randint(100000, 999999)}",
        "timestamp": timestamp.isoformat(),
        "customer_id": f"CUST{random.randint(1000, 9999)}",
        "channel": random.choice(CHANNELS),
        "message": message,
        "agent_reply": agent_reply,
        "product": random.choice(PRODUCTS),
        "order_value": round(base_value, 2),
        "customer_country": random.choice(COUNTRIES),
        "resolution_status": resolution,
        "category": category  # Ground truth for validation
    }

def generate_dataset(n=10000):
    """Generate full dataset with temporal patterns"""
    tickets = []
    
    # Create spike in "Shipping Delay" complaints in last 2 weeks (anomaly)
    recent_date = datetime.now() - timedelta(days=14)
    
    for i in range(n):
        ticket = generate_ticket()
        
        # Inject anomaly: 40% of recent tickets are shipping delays
        if datetime.fromisoformat(ticket["timestamp"]) > recent_date:
            if random.random() < 0.4:
                category = "Shipping Delay"
                template = random.choice(CATEGORIES[category])
                ticket["message"] = template.format(
                    days=random.randint(7, 21),
                    order=f"ORD{random.randint(10000, 99999)}"
                )
                ticket["category"] = category
        
        tickets.append(ticket)
    
    df = pd.DataFrame(tickets)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df

if __name__ == "__main__":
    print("Generating synthetic customer support dataset...")
    df = generate_dataset(10000)
    df.to_csv("support_tickets.csv", index=False)
    print(f"Generated {len(df)} tickets")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Categories: {df['category'].value_counts().to_dict()}")
    print(f"Saved to support_tickets.csv")
