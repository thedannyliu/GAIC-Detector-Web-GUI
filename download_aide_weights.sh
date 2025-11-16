#!/bin/bash
# Download AIDE model weights
# Model: GenImage_train.pth (3.6GB)
# Source: https://drive.google.com/file/d/1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz/view

set -e

WEIGHTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/models/weights"
MODEL_FILE="$WEIGHTS_DIR/GenImage_train.pth"
GOOGLE_DRIVE_ID="1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz"

echo "=========================================="
echo "  AIDE Model Downloader"
echo "=========================================="
echo ""

# Check if already exists
if [ -f "$MODEL_FILE" ]; then
    echo "✅ Model already exists: $MODEL_FILE"
    FILE_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo "   Size: $FILE_SIZE"
    echo ""
    read -p "Re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping download."
        exit 0
    fi
fi

# Create directory
mkdir -p "$WEIGHTS_DIR"

# Check if gdown is installed
if ! command -v gdown &> /dev/null; then
    echo "📦 Installing gdown..."
    pip install gdown -q
fi

# Download
echo "📥 Downloading AIDE model (3.6GB)..."
echo "   This may take 5-10 minutes depending on your connection..."
echo ""

cd "$WEIGHTS_DIR"
gdown "$GOOGLE_DRIVE_ID"

# Verify
if [ -f "$MODEL_FILE" ]; then
    FILE_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo ""
    echo "=========================================="
    echo "✅ Download Complete!"
    echo "=========================================="
    echo ""
    echo "Model: $MODEL_FILE"
    echo "Size: $FILE_SIZE"
    echo ""
    echo "You can now run:"
    echo "  ./start_gpu.sh    # Start with GPU"
    echo "  ./start.sh        # Start with CPU"
else
    echo ""
    echo "❌ Download failed!"
    echo ""
    echo "Please download manually from:"
    echo "https://drive.google.com/file/d/1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz/view"
    echo ""
    echo "Save to: $MODEL_FILE"
    exit 1
fi
