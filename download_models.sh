#!/bin/bash

# GAIC Detector - Model Download Script
# Downloads pre-trained model weights

set -e

MODELS_DIR="models/weights"
mkdir -p "$MODELS_DIR"

echo "📦 GAIC Detector Model Download Script"
echo "========================================"
echo ""

# Note: These are placeholder URLs
# Replace with actual model sources when available

echo "⚠️  WARNING: This script contains placeholder URLs."
echo "    Please update with actual model download links."
echo ""

read -p "Do you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Download cancelled"
    exit 1
fi

echo ""

# Function to download with progress
download_model() {
    local model_name=$1
    local url=$2
    local filename=$3
    
    echo "📥 Downloading $model_name..."
    
    if command -v wget &> /dev/null; then
        wget -O "$MODELS_DIR/$filename" "$url" --progress=bar:force 2>&1
    elif command -v curl &> /dev/null; then
        curl -L -o "$MODELS_DIR/$filename" "$url" --progress-bar
    else
        echo "❌ Neither wget nor curl found. Please install one of them."
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ $model_name downloaded successfully"
        ls -lh "$MODELS_DIR/$filename"
    else
        echo "❌ Failed to download $model_name"
        return 1
    fi
    echo ""
}

# Check for existing models
existing_models=0
for model in susy.pth fatformer.pth distildire.pth; do
    if [ -f "$MODELS_DIR/$model" ]; then
        echo "✓ Found: $model"
        ((existing_models++))
    fi
done

if [ $existing_models -gt 0 ]; then
    echo ""
    read -p "Some models already exist. Re-download? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing models"
        exit 0
    fi
fi

echo ""
echo "Starting downloads..."
echo ""

# Download SuSy model
# TODO: Replace with actual URL
SUSY_URL="https://example.com/models/susy.pth"
# Uncomment when URL is available:
# download_model "SuSy" "$SUSY_URL" "susy.pth"
echo "⏭️  Skipping SuSy (placeholder URL)"

# Download FatFormer model
# TODO: Replace with actual URL
FATFORMER_URL="https://example.com/models/fatformer.pth"
# Uncomment when URL is available:
# download_model "FatFormer" "$FATFORMER_URL" "fatformer.pth"
echo "⏭️  Skipping FatFormer (placeholder URL)"

# Download DistilDIRE model
# TODO: Replace with actual URL
DISTILDIRE_URL="https://example.com/models/distildire.pth"
# Uncomment when URL is available:
# download_model "DistilDIRE" "$DISTILDIRE_URL" "distildire.pth"
echo "⏭️  Skipping DistilDIRE (placeholder URL)"

echo ""
echo "========================================"
echo "📋 Model Download Summary"
echo "========================================"

# Check what we have now
for model in susy.pth fatformer.pth distildire.pth; do
    if [ -f "$MODELS_DIR/$model" ]; then
        size=$(du -h "$MODELS_DIR/$model" | cut -f1)
        echo "✅ $model ($size)"
    else
        echo "❌ $model (not found)"
    fi
done

echo ""
echo "💡 Tips:"
echo "   - To use mock models (for demo), no weights needed"
echo "   - To use real models, obtain weights from:"
echo "     • Official model repositories"
echo "     • Research paper authors"
echo "     • Hugging Face model hub"
echo "     • Contact maintainers"
echo ""
echo "   Update this script with actual URLs when available."
echo ""
