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
MAX_IMAGE_SIZE_MB = 30  # 3x original limit
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]

# Image processing
MAX_LONG_SIDE = 1536 * 3  # allow larger previews while preserving aspect
AIDE_INPUT_SIZE = 256  # AIDE model requires 256x256 for ConvNeXt (model-side fixed)

# ============================================
# VIDEO SETTINGS
# ============================================
# API settings for videos
MAX_VIDEO_SIZE_MB = 150  # 3x original limit
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "webm"]

# Video processing
VIDEO_SAMPLE_FRAMES = 16  # Number of frames to sample from video
VIDEO_MAX_DURATION = 900  # 3x duration budget (seconds)

# ============================================
# TIMEOUT SETTINGS (seconds)
# ============================================
TIMEOUT_TOTAL = 120  # 3x
TIMEOUT_DEGRADE = 75
TIMEOUT_SKIP_HEATMAP = 105
TIMEOUT_LLM = 6

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
    "AIzaSyDcpP36XpRgiA7qM-82yLn0SAqyxrEn4aM"  # Free-tier API key
)
# Gemini model name (multimodal, v1beta)
GEMINI_MODEL = "gemini-1.5-flash-latest"  # Use latest stable version
GEMINI_TIMEOUT = 30  # Allow time for Gemini processing

# ============================================
# SERVER SETTINGS
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Backend URL (for Gradio frontend)
GAIC_BACKEND_URL = os.getenv("GAIC_BACKEND_URL", f"http://localhost:{API_PORT}")
