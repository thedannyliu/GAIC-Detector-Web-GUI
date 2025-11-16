"""Image processing utilities."""

import io
import base64
from typing import Tuple, Optional
from PIL import Image, ImageOps
import numpy as np

from app.config import MAX_LONG_SIDE, SUPPORTED_IMAGE_FORMATS
from app.errors import GAICException, ErrorCode


def validate_image_format(filename: str) -> None:
    """Validate image file format."""
    ext = filename.lower().split('.')[-1]
    if ext not in SUPPORTED_IMAGE_FORMATS:
        raise GAICException(ErrorCode.IMG_FORMAT_UNSUPPORTED)


def load_and_preprocess_image(image_bytes: bytes) -> Tuple[np.ndarray, Image.Image]:
    """
    Load image from bytes and preprocess according to master plan.
    
    Returns:
        Tuple of (numpy array RGB, PIL Image)
    """
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Auto EXIF rotation
        image = ImageOps.exif_transpose(image)
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if needed (long side to MAX_LONG_SIDE, preserve aspect)
        width, height = image.size
        long_side = max(width, height)
        
        if long_side > MAX_LONG_SIDE:
            scale = MAX_LONG_SIDE / long_side
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(image)
        
        return image_array, image
        
    except Exception as e:
        if isinstance(e, GAICException):
            raise
        raise GAICException(ErrorCode.IMG_DECODE_FAILED, str(e))


def create_gradcam_overlay(
    original_image: Image.Image,
    gradcam_heatmap: np.ndarray,
    alpha: float = 0.5,
    colormap: str = 'viridis'
) -> Optional[str]:
    """
    Create Grad-CAM heatmap overlay on original image.
    
    Args:
        original_image: PIL Image (RGB)
        gradcam_heatmap: 2D numpy array with values 0-1 (from pytorch-grad-cam)
        alpha: Overlay transparency (0.5 = 50% heatmap + 50% original)
        colormap: Colormap name (viridis, jet, etc.)
        
    Returns:
        Base64 encoded PNG or None on error
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        
        # Convert original image to numpy array
        original_array = np.array(original_image).astype(np.float32) / 255.0
        
        # Resize Grad-CAM heatmap to match original image size
        heatmap_resized = Image.fromarray((gradcam_heatmap * 255).astype(np.uint8))
        heatmap_resized = heatmap_resized.resize(original_image.size, Image.BILINEAR)
        heatmap_array = np.array(heatmap_resized).astype(np.float32) / 255.0
        
        # Apply colormap to heatmap
        cmap = cm.get_cmap(colormap)
        colored_heatmap = cmap(heatmap_array)[:, :, :3]  # Remove alpha channel
        
        # Blend: alpha * heatmap + (1-alpha) * original
        overlay = (alpha * colored_heatmap + (1 - alpha) * original_array)
        overlay = (overlay * 255).astype(np.uint8)
        
        # Convert to PIL and encode as base64
        overlay_image = Image.fromarray(overlay)
        buffer = io.BytesIO()
        overlay_image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        print(f"Grad-CAM overlay error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_heatmap_overlay(
    original_image: Image.Image,
    heatmap: np.ndarray,
    alpha: float = 0.5,
    colormap: str = 'viridis'
) -> Optional[str]:
    """
    Create heatmap overlay on original image (legacy wrapper).
    
    Calls create_gradcam_overlay.
    """
    return create_gradcam_overlay(original_image, heatmap, alpha, colormap)


def image_to_base64(image: Image.Image, max_size: Optional[int] = None) -> str:
    """Convert PIL Image to base64 string."""
    if max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
