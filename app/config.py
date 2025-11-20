"""Configuration settings for GAIC Detector API."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models" / "weights"
TEMP_DIR = BASE_DIR / "temp"
TEST_SAMPLES_DIR = BASE_DIR / "test_samples"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
TEST_SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# IMAGE SETTINGS
# ============================================
# API settings for images
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]

# Image processing
MAX_LONG_SIDE = 1536
AIDE_INPUT_SIZE = 224  # ResNet-50 input size

# ============================================
# VIDEO SETTINGS
# ============================================
# API settings for videos
MAX_VIDEO_SIZE_MB = 50
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "webm"]

# Video processing
VIDEO_SAMPLE_FRAMES = 16  # Number of frames to sample from video
VIDEO_MAX_DURATION = 300  # Maximum video duration in seconds (5 min)

# ============================================
# TIMEOUT SETTINGS (seconds)
# ============================================
TIMEOUT_TOTAL = 120  # Total timeout for inference
TIMEOUT_DEGRADE = 90
TIMEOUT_SKIP_HEATMAP = 100
TIMEOUT_LLM = 60  # Gemini timeout increased to 60 seconds

# ============================================
# MODEL SETTINGS - AIDE ONLY
# ============================================
MODEL_NAME = "AIDE"  # Fixed model name
USE_PRETRAINED = True

# ============================================
# GRAD-CAM SETTINGS
# ============================================
GRADCAM_COLORMAP = "viridis"  # Color-blind friendly colormap
GRADCAM_ALPHA = 0.5  # Blending ratio (0.5 = 50% heatmap + 50% original)
GRADCAM_TARGET_LAYER = "layer4"  # ResNet-50 last conv block

# ============================================
# GEMINI API SETTINGS
# ============================================
GEMINI_ENABLED = True
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", 
    "AIzaSyDcpP36XpRgiA7qM-82yLn0SAqyxrEn4aM"  # Default free-tier key
)
GEMINI_MODEL = "gemini-2.5-flash"  # Use Gemini 2.5 Flash
GEMINI_TIMEOUT = 60  # 60 seconds timeout for Gemini

# ============================================
# SERVER SETTINGS
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Backend URL (for Gradio frontend)
GAIC_BACKEND_URL = os.getenv("GAIC_BACKEND_URL", f"http://localhost:{API_PORT}")
