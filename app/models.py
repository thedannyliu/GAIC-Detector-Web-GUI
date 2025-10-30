"""Model loader and inference logic."""

import time
from typing import Tuple, Optional, Dict
import numpy as np
import torch
from pathlib import Path

from app.config import MODELS_DIR, PATCH_SIZE, DEFAULT_STRIDE, DEGRADED_STRIDE
from app.errors import GAICException, ErrorCode


class ModelRegistry:
    """Registry for AI detection models."""
    
    def __init__(self):
        self._models: Dict[str, object] = {}
        self._loaded: Dict[str, bool] = {}
        
    def register_model(self, name: str, model_class):
        """Register a model class."""
        self._models[name] = model_class
        self._loaded[name] = False
    
    def load_model(self, name: str):
        """Lazy load a model."""
        if name not in self._models:
            raise GAICException(ErrorCode.MODEL_NOT_FOUND)
        
        if not self._loaded[name]:
            try:
                model_path = MODELS_DIR / f"{name.lower()}.pth"
                if not model_path.exists():
                    print(f"Warning: Model weights not found at {model_path}")
                    # For demo, create a mock model
                    self._models[name] = MockDetector(name)
                else:
                    # Load actual model
                    self._models[name] = self._models[name](model_path)
                self._loaded[name] = True
            except Exception as e:
                raise GAICException(ErrorCode.MODEL_ERROR, f"Failed to load {name}: {str(e)}")
    
    def get_model(self, name: str):
        """Get a loaded model."""
        if name not in self._loaded or not self._loaded[name]:
            self.load_model(name)
        return self._models[name]
    
    def is_available(self, name: str) -> bool:
        """Check if model is available."""
        return name in self._models


# Global registry
registry = ModelRegistry()


class MockDetector:
    """Mock detector for demo purposes when actual weights are not available."""
    
    def __init__(self, name: str):
        self.name = name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def predict(self, image: np.ndarray, stride: int = DEFAULT_STRIDE) -> Tuple[float, Optional[np.ndarray]]:
        """
        Mock prediction.
        
        Returns:
            Tuple of (score 0-1, heatmap or None)
        """
        # Simulate processing time
        time.sleep(0.5 + np.random.random() * 0.5)
        
        # Generate mock score based on image characteristics
        gray = np.mean(image, axis=2)
        variance = np.var(gray)
        score = min(1.0, variance / 5000.0)  # Normalize to 0-1
        
        # Generate mock heatmap (patch-based models only)
        if self.name in ["SuSy"]:
            h, w = image.shape[:2]
            heatmap_h = h // stride
            heatmap_w = w // stride
            heatmap = np.random.random((heatmap_h, heatmap_w)) * score
        else:
            heatmap = None
        
        return score, heatmap


class BaseDetector:
    """Base class for actual detectors (to be implemented)."""
    
    def __init__(self, model_path: Path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
    
    def _load_model(self, model_path: Path):
        """Load model from checkpoint."""
        raise NotImplementedError
    
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for model input."""
        # Normalize to [0, 1]
        image_tensor = torch.from_numpy(image).float() / 255.0
        # CHW format
        image_tensor = image_tensor.permute(2, 0, 1)
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        return image_tensor.to(self.device)
    
    def predict(self, image: np.ndarray, stride: int = DEFAULT_STRIDE) -> Tuple[float, Optional[np.ndarray]]:
        """
        Run inference on image.
        
        Returns:
            Tuple of (score 0-1, heatmap array or None)
        """
        raise NotImplementedError


# Register models (using mock for now)
registry.register_model("SuSy", MockDetector)
registry.register_model("FatFormer", MockDetector)
registry.register_model("DistilDIRE", MockDetector)


def run_inference(
    image: np.ndarray,
    model_name: str,
    include_heatmap: bool = True,
    timeout: float = 40.0
) -> Tuple[float, Optional[np.ndarray], int]:
    """
    Run model inference with timeout and degradation logic.
    
    Args:
        image: RGB numpy array
        model_name: Model name
        include_heatmap: Whether to generate heatmap
        timeout: Total timeout in seconds
        
    Returns:
        Tuple of (score 0-1, heatmap or None, inference_ms)
    """
    start_time = time.time()
    model = registry.get_model(model_name)
    
    try:
        # First attempt with default stride
        score, heatmap = model.predict(image, stride=DEFAULT_STRIDE)
        
        elapsed = time.time() - start_time
        
        # Check if we need to degrade
        if elapsed > 25 and elapsed < 35:
            print(f"Inference slow ({elapsed:.1f}s), retrying with degraded stride...")
            score, heatmap = model.predict(image, stride=DEGRADED_STRIDE)
        
        # Skip heatmap if taking too long
        if elapsed > 35 or not include_heatmap:
            heatmap = None
        
        # Check total timeout
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise GAICException(ErrorCode.MODEL_TIMEOUT)
        
        inference_ms = int(elapsed * 1000)
        return score, heatmap, inference_ms
        
    except GAICException:
        raise
    except Exception as e:
        raise GAICException(ErrorCode.MODEL_ERROR, str(e))
