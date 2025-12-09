#!/bin/bash

# Reflectly Enhanced Setup Script
# Automates installation of LLM + GNN dependencies

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          Reflectly Enhanced Setup - LLM + GNN               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 not found. Please install pip."
    exit 1
fi
print_status "pip3 found"

# Setup Python virtual environment
echo ""
echo "🐍 Setting up Python environment..."

cd backend

if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
print_status "Installing Flask, Ollama, PyTorch, etc..."

pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    print_status "Python dependencies installed successfully"
else
    print_error "Failed to install some Python dependencies"
    print_warning "Try manually: pip install -r backend/requirements.txt"
fi

# Create data directory
print_status "Creating data directory..."
mkdir -p data
chmod 755 data

cd ..

# Check/Install Ollama
echo ""
echo "🤖 Checking Ollama installation..."

if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n 1)
    print_status "Ollama found: $OLLAMA_VERSION"
else
    print_warning "Ollama not found. Installing..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        # Linux or macOS
        curl -fsSL https://ollama.ai/install.sh | sh
        
        if [ $? -eq 0 ]; then
            print_status "Ollama installed successfully"
        else
            print_error "Failed to install Ollama automatically"
            print_warning "Please install manually from: https://ollama.ai"
            exit 1
        fi
    else
        # Windows or other
        print_error "Automatic Ollama installation not supported on this OS"
        print_warning "Please install manually from: https://ollama.ai/download"
        exit 1
    fi
fi

# Start Ollama service (if not running)
echo ""
echo "🚀 Starting Ollama service..."

if ! pgrep -x "ollama" > /dev/null; then
    print_status "Starting Ollama service..."
    ollama serve &> /dev/null &
    sleep 3
    print_status "Ollama service started"
else
    print_status "Ollama service already running"
fi

# Pull LLM models
echo ""
echo "📥 Downloading LLM models..."

print_status "Pulling Mistral 7B (primary model) - this may take a few minutes..."
ollama pull mistral:7b

if [ $? -eq 0 ]; then
    print_status "Mistral 7B downloaded successfully"
else
    print_warning "Failed to download Mistral 7B"
    print_warning "Trying alternative model: Llama 3.2 3B..."
    ollama pull llama3.2:3b
    
    if [ $? -eq 0 ]; then
        print_status "Llama 3.2 3B downloaded successfully"
    else
        print_error "Failed to download any LLM models"
        print_warning "You can manually pull models later with: ollama pull mistral:7b"
    fi
fi

# Verify Ollama models
echo ""
echo "🔍 Verifying available models..."
ollama list

# Test backend setup
echo ""
echo "🧪 Testing backend setup..."

cd backend
source venv/bin/activate || . venv/Scripts/activate

# Quick test of imports
print_status "Testing Python imports..."
python3 -c "import flask; import ollama; import torch; print('All core imports successful')" 2>&1

if [ $? -eq 0 ]; then
    print_status "Backend setup verified"
else
    print_error "Some imports failed - check dependencies"
fi

cd ..

# Check frontend (optional)
echo ""
echo "📱 Checking frontend..."

if [ -d "frontend" ]; then
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        NODE_VERSION=$(node --version)
        NPM_VERSION=$(npm --version)
        print_status "Node $NODE_VERSION and npm $NPM_VERSION found"
        
        print_warning "To install frontend dependencies, run: cd frontend && npm install"
    else
        print_warning "Node.js/npm not found - frontend setup skipped"
        print_warning "Install from: https://nodejs.org"
    fi
else
    print_warning "Frontend directory not found"
fi

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                     Setup Complete! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
print_status "Python environment configured"
print_status "Ollama installed and models downloaded"
print_status "Data directory created"
echo ""
echo "📖 Next steps:"
echo "   1. Start the backend:    cd backend && source venv/bin/activate && python intelligent_agent.py"
echo "   2. Start the frontend:   cd frontend && npm install && npm start"
echo "   3. Access the app:       http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide:           SETUP_GUIDE.md"
echo "   - README:                README.md"
echo ""
echo "🔧 Quick commands:"
echo "   - Test LLM:              ollama run mistral:7b \"Hello\""
echo "   - Check API:             curl http://localhost:5000/api/health"
echo "   - View logs:             tail -f backend/logs/*.log"
echo ""
print_status "Setup complete! Happy coding! 🚀"
