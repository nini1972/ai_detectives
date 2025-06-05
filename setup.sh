#!/bin/bash

# 🕵️ Dual-AI Detective Game Setup Script
# This script sets up the complete development environment

set -e

echo "🕵️ Setting up Dual-AI Detective Game..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Yarn
if ! command -v yarn &> /dev/null; then
    echo "📦 Installing Yarn..."
    npm install -g yarn
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check MongoDB (optional for development)
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB not found locally. You'll need MongoDB running for the backend."
    echo "   Install MongoDB or use a cloud service like MongoDB Atlas."
fi

echo "✅ Prerequisites check complete!"

# Setup backend
echo ""
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating backend .env file..."
    cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="detective_game"
OPENAI_API_KEY="your_openai_key_here"
ANTHROPIC_API_KEY="your_anthropic_key_here"
FAL_KEY="your_fal_ai_key_here"
EOF
    echo "⚠️  Please edit backend/.env with your actual API keys!"
fi

cd ..

# Setup frontend
echo ""
echo "⚛️  Setting up React frontend..."
cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
yarn install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating frontend .env file..."
    cat > .env << EOF
REACT_APP_BACKEND_URL="http://localhost:8001"
EOF
fi

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env with your API keys:"
echo "   - OpenAI API key from https://platform.openai.com/api-keys"
echo "   - Anthropic API key from https://console.anthropic.com/"
echo "   - FAL.AI API key from https://fal.ai/dashboard/keys"
echo ""
echo "2. Start MongoDB (if using local instance)"
echo ""
echo "3. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python server.py"
echo ""
echo "4. Start the frontend (in new terminal):"
echo "   cd frontend"
echo "   yarn start"
echo ""
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "🕵️ Happy investigating!"