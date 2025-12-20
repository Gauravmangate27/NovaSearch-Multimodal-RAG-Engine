#!/usr/bin/env bash
# NovaSearch Quick Start Script

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         NovaSearch - Multimodal RAG Engine                ║"
echo "║              Quick Start Script                            ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${BLUE}Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\n${BLUE}Creating virtual environment...${NC}"
    python -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo -e "\n${BLUE}Activating virtual environment...${NC}"
source venv/Scripts/activate || . venv/bin/activate
echo "✓ Virtual environment activated"

# Install/upgrade dependencies
echo -e "\n${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and add your OPENAI_API_KEY${NC}"
fi

# Verify configuration
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "\n${YELLOW}⚠️  Warning: OPENAI_API_KEY not properly configured${NC}"
    echo "Please edit .env and add your valid OpenAI API key"
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo "  1. Edit .env and add your OPENAI_API_KEY"
echo "  2. Start the server:"
echo "     ${GREEN}python -m uvicorn src.api.main:app --reload${NC}"
echo "  3. Visit API documentation:"
echo "     ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}Other commands:${NC}"
echo "  Run example:  ${GREEN}python example_usage.py${NC}"
echo "  Run tests:    ${GREEN}pytest tests/ -v${NC}"
echo "  Check config: ${GREEN}python src/config.py${NC}"
echo ""
