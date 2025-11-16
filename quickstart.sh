#!/bin/bash
# Quick start script for GAIC Detector - AIDE Edition

echo "============================================"
echo "GAIC Detector - AIDE Edition"
echo "Quick Start Script"
echo "============================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

# Create conda environment if it doesn't exist
if ! conda env list | grep -q "gaic-detector"; then
    echo "Creating conda environment 'gaic-detector'..."
    conda create -n gaic-detector python=3.10 -y
fi

# Activate environment
echo "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate gaic-detector

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "============================================"
echo "Installation complete!"
echo "============================================"
echo ""
echo "To start the system:"
echo "  1. Backend API:"
echo "     python -m app.main"
echo ""
echo "  2. Frontend UI (in another terminal):"
echo "     python gradio_app.py"
echo ""
echo "Or use the provided scripts:"
echo "  - ./start_simple.sh   (starts both in background)"
echo "  - ./start_cluster.sh  (for cluster environment)"
echo ""
echo "============================================"
