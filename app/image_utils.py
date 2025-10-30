"""Image processing utilities."""

import io
import base64
from typing import Tuple, Optional
from PIL import Image, ImageOps
import numpy as np

from app.config import MAX_LONG_SIDE, SUPPORTED_FORMATS
from app.errors import GAICException, ErrorCode


def validate_image_format(filename: str) -> None:
    """Validate image file format."""
    ext = filename.lower().split('.')[-1]
    if ext not in SUPPORTED_FORMATS:
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


def create_heatmap_overlay(
    original_image: Image.Image,
    heatmap: np.ndarray,
    alpha: float = 0.5,
    colormap: str = 'viridis'
) -> Optional[str]:
    """
    Create heatmap overlay on original image.
    
    Args:
        original_image: PIL Image (RGB)
        heatmap: 2D numpy array with values 0-1
        alpha: Overlay transparency
        colormap: Colormap name
        
    Returns:
        Base64 encoded PNG or None on error
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        
        # Resize heatmap to match image size
        heatmap_resized = Image.fromarray((heatmap * 255).astype(np.uint8))
        heatmap_resized = heatmap_resized.resize(original_image.size, Image.BILINEAR)
        heatmap_array = np.array(heatmap_resized) / 255.0
        
        # Apply colormap
        cmap = cm.get_cmap(colormap)
        colored_heatmap = cmap(heatmap_array)
        colored_heatmap = (colored_heatmap[:, :, :3] * 255).astype(np.uint8)
        
        # Create overlay
        original_array = np.array(original_image)
        overlay = (alpha * colored_heatmap + (1 - alpha) * original_array).astype(np.uint8)
        
        # Convert to base64
        overlay_image = Image.fromarray(overlay)
        buffer = io.BytesIO()
        overlay_image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        print(f"Heatmap overlay error: {e}")
        return None


def image_to_base64(image: Image.Image, max_size: Optional[int] = None) -> str:
    """Convert PIL Image to base64 string."""
    if max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
