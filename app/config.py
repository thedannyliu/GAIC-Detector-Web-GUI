"""Configuration settings for GAIC Detector API."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models" / "weights"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# API settings
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "webp"]

# Image processing
MAX_LONG_SIDE = 1536
PATCH_SIZE = 224
DEFAULT_STRIDE = 112
DEGRADED_STRIDE = 224

# Timeout settings (seconds)
TIMEOUT_TOTAL = 40
TIMEOUT_DEGRADE = 25
TIMEOUT_SKIP_HEATMAP = 35
TIMEOUT_LLM = 2

# Model settings
AVAILABLE_MODELS = ["SuSy", "FatFormer", "DistilDIRE"]
DEFAULT_MODEL = "SuSy"

# LLM settings
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Server settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
