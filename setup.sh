#!/bin/bash

# AI Chess Learning Platform - Quick Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "🤖♟️  AI Chess Learning Platform - Setup Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "ℹ $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    print_error "npm not found. Please install npm"
    exit 1
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version | cut -d' ' -f3 || echo "unknown")
    print_success "Ollama $OLLAMA_VERSION found"
else
    print_warning "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    if [ $? -eq 0 ]; then
        print_success "Ollama installed successfully"
    else
        print_error "Failed to install Ollama. Please install manually from https://ollama.ai"
        exit 1
    fi
fi

# Check Stockfish
if command -v stockfish &> /dev/null; then
    print_success "Stockfish found"
else
    print_warning "Stockfish not found."
    echo "Please install Stockfish:"
    echo "  macOS: brew install stockfish"
    echo "  Ubuntu: sudo apt install stockfish"
    echo "  Windows: Download from stockfishchess.org"
    read -p "Continue without Stockfish? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Setting up backend..."
echo ""

# Setup backend
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_info "Installing Python dependencies (this may take a minute)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Python dependencies installed"

# Create .env file
if [ ! -f ".env" ]; then
    print_info "Creating .env configuration..."
    cp .env.example .env
    print_success ".env file created"
else
    print_info ".env file already exists"
fi

cd ..

echo ""
echo "Setting up frontend..."
echo ""

# Setup frontend
cd frontend

# Install dependencies
print_info "Installing Node.js dependencies (this may take 2-3 minutes)..."
npm install --silent
print_success "Node.js dependencies installed"

# Create .env.local file
if [ ! -f ".env.local" ]; then
    print_info "Creating .env.local configuration..."
    cp .env.local.example .env.local
    print_success ".env.local file created"
else
    print_info ".env.local file already exists"
fi

cd ..

echo ""
echo "Checking Ollama setup..."
echo ""

# Start Ollama service
print_info "Starting Ollama service..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
sleep 2

# Check if llama3 is installed
if ollama list | grep -q "llama3"; then
    print_success "Llama 3 model already installed"
else
    print_warning "Llama 3 model not found. Downloading (this is a 4.7GB download)..."
    print_info "This will take 5-10 minutes depending on your internet speed..."
    ollama pull llama3
    if [ $? -eq 0 ]; then
        print_success "Llama 3 model downloaded successfully"
    else
        print_error "Failed to download Llama 3 model"
        print_info "You can download it later with: ollama pull llama3"
    fi
fi

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "To start the platform:"
echo ""
echo "1. Start Ollama (if not already running):"
echo "   ${GREEN}ollama serve${NC}"
echo ""
echo "2. Start the backend (in a new terminal):"
echo "   ${GREEN}cd backend${NC}"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo "   ${GREEN}uvicorn app.main:app --reload${NC}"
echo ""
echo "3. Start the frontend (in another terminal):"
echo "   ${GREEN}cd frontend${NC}"
echo "   ${GREEN}npm run dev${NC}"
echo ""
echo "4. Open your browser:"
echo "   ${GREEN}http://localhost:3000${NC}"
echo ""
echo "For detailed documentation, see:"
echo "  - README.md (Quick start guide)"
echo "  - docs/DEPLOYMENT.md (Full deployment guide)"
echo "  - docs/OLLAMA_SETUP.md (LLM configuration)"
echo "  - docs/API.md (API reference)"
echo ""
echo "Happy learning! 🎉"
