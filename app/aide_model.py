"""AIDE Model implementation with Grad-CAM support."""

import os
import time
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from PIL import Image

from app.config import AIDE_INPUT_SIZE, MODEL_NAME
from app.errors import GAICException, ErrorCode


class AIDeDetector(nn.Module):
    """
    AIDE: AI-generated Image DEtector with Hybrid Features.
    
    Based on ResNet-50 backbone with binary classification head.
    """
    
    def __init__(self, pretrained: bool = True):
        super(AIDeDetector, self).__init__()
        
        # Load pre-trained ResNet-50
        resnet = models.resnet50(pretrained=pretrained)
        
        # Remove the final FC layer
        self.features = nn.Sequential(*list(resnet.children())[:-1])
        
        # Binary classifier (Real vs AI-generated)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 2)  # 2 classes: [real, fake]
        )
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)
    
    def forward(self, x):
        """Forward pass."""
        features = self.features(x)
        output = self.classifier(features)
        return output


class AIDeInference:
    """Inference wrapper for AIDE model with Grad-CAM support."""
    
    def __init__(self, checkpoint_path: Optional[str] = None):
        """Initialize AIDE model and preprocessing."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Initializing AIDE model on device: {device}")
        
        # Create model
        self.model = AIDeDetector(pretrained=True)
        
        # Try to load checkpoint if available
        if checkpoint_path is None:
            # Look for default checkpoint
            project_root = Path(__file__).parent.parent
            checkpoint_path = project_root / "models" / "weights" / "aide_resnet50.pth"
        
        if isinstance(checkpoint_path, str):
            checkpoint_path = Path(checkpoint_path)
        
        if checkpoint_path.exists():
            print(f"Loading AIDE checkpoint from: {checkpoint_path}")
            try:
                checkpoint = torch.load(checkpoint_path, map_location=device)
                if 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                    print("✅ Loaded fine-tuned AIDE weights")
                else:
                    self.model.load_state_dict(checkpoint)
                    print("✅ Loaded AIDE weights")
            except Exception as e:
                print(f"⚠️  Failed to load checkpoint: {e}")
                print("   Using pretrained ResNet-50 backbone with random classifier")
        else:
            print(f"⚠️  No checkpoint found at: {checkpoint_path}")
            print("   Using pretrained ResNet-50 backbone with random classifier")
            print("   For production use, please fine-tune the model first!")
        
        self.model.eval()
        
        # ImageNet normalization (ResNet-50 was pre-trained on ImageNet)
        self.transform = transforms.Compose([
            transforms.Resize((AIDE_INPUT_SIZE, AIDE_INPUT_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Grad-CAM setup: target last conv layer (layer4)
        self.target_layers = [self.model.features[-1]]
        
        print("AIDE model loaded successfully")
    
    def preprocess_image(self, image: np.ndarray) -> Tuple[torch.Tensor, np.ndarray]:
        """
        Preprocess image for AIDE.
        
        Args:
            image: RGB numpy array (H, W, 3), values 0-255
            
        Returns:
            Tuple of (tensor for model, normalized numpy for visualization)
        """
        # Convert to PIL
        pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
        
        # Transform for model
        tensor = self.transform(pil_image).unsqueeze(0).to(self.model.device)
        
        # Normalized numpy for Grad-CAM visualization (0-1 range)
        viz_image = np.array(pil_image.resize((AIDE_INPUT_SIZE, AIDE_INPUT_SIZE))) / 255.0
        
        return tensor, viz_image
    
    def predict(
        self,
        image: np.ndarray,
        include_heatmap: bool = True
    ) -> Tuple[float, Optional[np.ndarray]]:
        """
        Run AIDE inference with optional Grad-CAM.
        
        Args:
            image: RGB numpy array
            include_heatmap: Whether to generate Grad-CAM heatmap
            
        Returns:
            Tuple of (fake_probability, heatmap_array or None)
            
        Raises:
            GAICException: On model error
        """
        try:
            with torch.no_grad():
                # Preprocess
                tensor, viz_image = self.preprocess_image(image)
                
                # Forward pass
                output = self.model(tensor)
                probabilities = F.softmax(output, dim=1)
                
                # Extract fake probability (index 1)
                fake_prob = probabilities[0, 1].item()
            
            # Generate Grad-CAM heatmap if requested
            heatmap = None
            if include_heatmap:
                try:
                    heatmap = self._generate_gradcam(tensor, viz_image)
                except Exception as e:
                    print(f"Grad-CAM generation failed: {e}")
                    # Don't fail the whole request, just skip heatmap
                    heatmap = None
            
            return fake_prob, heatmap
            
        except Exception as e:
            print(f"AIDE inference error: {e}")
            import traceback
            traceback.print_exc()
            raise GAICException(ErrorCode.MODEL_ERROR, str(e))
    
    def _generate_gradcam(
        self,
        tensor: torch.Tensor,
        viz_image: np.ndarray
    ) -> np.ndarray:
        """
        Generate Grad-CAM heatmap.
        
        Args:
            tensor: Input tensor (already preprocessed)
            viz_image: Normalized image for visualization (0-1 range)
            
        Returns:
            Heatmap as 2D numpy array (values 0-1)
        """
        # Target class 1 (fake/AI-generated)
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        targets = [ClassifierOutputTarget(1)]
        
        # Generate Grad-CAM
        with GradCAM(model=self.model, target_layers=self.target_layers) as cam:
            grayscale_cam = cam(input_tensor=tensor, targets=targets)
            
            # Extract single image cam (batch size = 1)
            grayscale_cam = grayscale_cam[0, :]
        
        return grayscale_cam


# Global model instance (lazy loading)
_aide_model: Optional[AIDeInference] = None


def get_aide_model() -> AIDeInference:
    """Get or create AIDE model instance (singleton)."""
    global _aide_model
    if _aide_model is None:
        _aide_model = AIDeInference()
    return _aide_model


def run_inference(
    image: np.ndarray,
    include_heatmap: bool = True,
    timeout: float = 40.0
) -> Tuple[float, Optional[np.ndarray], int]:
    """
    Run AIDE inference with timeout and Grad-CAM.
    
    Args:
        image: RGB numpy array
        include_heatmap: Whether to generate Grad-CAM heatmap
        timeout: Total timeout in seconds (unused for now, can add later)
        
    Returns:
        Tuple of (fake_score_0_to_1, heatmap_2d_array or None, inference_ms)
    """
    start_time = time.time()
    
    try:
        model = get_aide_model()
        fake_prob, heatmap = model.predict(image, include_heatmap=include_heatmap)
        
        elapsed = time.time() - start_time
        inference_ms = int(elapsed * 1000)
        
        # Check timeout
        if elapsed > timeout:
            raise GAICException(ErrorCode.MODEL_TIMEOUT)
        
        return fake_prob, heatmap, inference_ms
        
    except GAICException:
        raise
    except Exception as e:
        print(f"Unexpected inference error: {e}")
        raise GAICException(ErrorCode.MODEL_ERROR, str(e))
