#!/bin/bash

# GAIC Detector - Setup Script
# Initializes the project environment

set -e

echo "🔧 Setting up GAIC Detector Web GUI..."

# Check for conda
if ! command -v conda &> /dev/null
then
    echo "❌ Conda is not installed. Please install Conda to continue."
    exit 1
fi

# Create conda environment
ENV_NAME="gaic-detector"
if ! conda env list | grep -q $ENV_NAME; then
    echo "📦 Creating conda environment '$ENV_NAME' with Python 3.10..."
    conda create -n $ENV_NAME python=3.10 -y
else
    echo "✅ Conda environment '$ENV_NAME' already exists"
fi

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.10"

if [[ ! "$PYTHON_VERSION" == "$REQUIRED_VERSION"* ]]; then
    echo "❌ Python $REQUIRED_VERSION is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models/weights
mkdir -p temp

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your configuration"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Place model weights in models/weights/ directory:"
echo "      - susy.pth"
echo "      - fatformer.pth"
echo "      - distildire.pth"
echo "   2. Edit .env file if needed (especially for LLM integration)"
echo "   3. Run: ./start.sh"
echo ""
echo "💡 For demo purposes, the system will work with mock models if weights are not available."
echo ""
