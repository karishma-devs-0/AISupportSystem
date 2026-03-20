#!/bin/bash

echo "🚀 Setting up AI-Powered Customer Support Insight Platform"
echo "============================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "❗ Please edit .env and add your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter to continue after adding your API key..."
fi

# Generate synthetic data
echo ""
echo "🎲 Generating synthetic data..."
python generate_data.py

# Run pipeline (sample)
echo ""
echo "🔄 Running AI pipeline on sample data..."
python pipeline.py

# Success message
echo ""
echo "============================================================"
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"
echo "============================================================"
