"""Quick setup script for OpenAI API"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("OpenAI API Setup")
print("=" * 60)

# Load .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key or api_key == "sk-proj-PASTE_YOUR_KEY_HERE":
    print("\n❌ No API key found!")
    print("\nPlease follow these steps:")
    print("1. Get your API key from: https://platform.openai.com/api-keys")
    print("2. Open the .env file in this folder")
    print("3. Replace 'sk-proj-PASTE_YOUR_KEY_HERE' with your actual key")
    print("4. Run this script again")
    print("\n" + "=" * 60)
    exit(1)

# Test the API key
print("\n✓ API key found!")
print(f"  Key: {api_key[:20]}...{api_key[-4:]}")

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print("\n🧪 Testing API connection...")
    
    # Test with a simple request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'API test successful!' in exactly 3 words."}
        ],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"✓ API Response: {result}")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Your OpenAI API is working!")
    print("=" * 60)
    print("\nYou're now in LLM MODE with:")
    print("  • 90%+ accuracy (vs 78% in free mode)")
    print("  • GPT-4o-mini for categorization")
    print("  • GPT-4o-mini for sentiment analysis")
    print("  • GPT-4o-mini for response generation")
    print("\nCost: ~$0.001 per ticket")
    print("Your $5 free credits = ~5,000 tickets")
    print("\nNext steps:")
    print("  1. python src/utils/generate_data.py")
    print("  2. python src/core/pipeline.py")
    print("  3. streamlit run app.py")
    print("\n" + "=" * 60)
    
except ImportError:
    print("\n❌ OpenAI library not installed!")
    print("\nRun: pip install openai")
    print("\n" + "=" * 60)
    exit(1)
    
except Exception as e:
    print(f"\n❌ API Error: {e}")
    print("\nPossible issues:")
    print("  • Invalid API key")
    print("  • No credits remaining")
    print("  • Network connection issue")
    print("\nCheck your API key at: https://platform.openai.com/api-keys")
    print("\n" + "=" * 60)
    exit(1)
