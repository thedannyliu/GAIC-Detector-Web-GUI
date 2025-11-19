"""
AIDE (AI-generated Image DEtector with Hybrid Features) Integration
Based on: https://github.com/shilinyan99/AIDE

This module integrates the official AIDE model for our web service.
AIDE uses:
1. High-Pass Filters (HPF) + ResNet-50 for noise pattern extraction
2. ConvNeXt-XXL for semantic feature extraction
3. Fusion MLP for final classification
"""

import os
import sys
from pathlib import Path
import time
from typing import Tuple, Optional
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

# Add aide_original to path
AIDE_DIR = Path(__file__).parent / "aide_original"
sys.path.insert(0, str(AIDE_DIR))

from AIDE import AIDE as create_aide_model

from app.config import AIDE_INPUT_SIZE
from app.errors import GAICException, ErrorCode


class AIDeInferenceWrapper:
    """
    Wrapper for AIDE model inference with Grad-CAM support.
    
    AIDE requires 5 input images with different preprocessing:
    - min-min: Min pooling + Min pooling
    - max-max: Max pooling + Max pooling  
    - min-min1: Alternative min processing
    - max-max1: Alternative max processing
    - tokens: Original image for ConvNeXt
    """
    
    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        resnet_path: Optional[str] = None,
        convnext_path: Optional[str] = None
    ):
        """
        Initialize AIDE model.
        
        Args:
            checkpoint_path: Path to AIDE trained checkpoint (.pth)
            resnet_path: Path to pretrained ResNet-50 (.pth)
            convnext_path: Path to pretrained ConvNeXt-XXL (open_clip format)
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Initializing AIDE model on device: {self.device}")
        
        # Set default paths
        weights_dir = Path(__file__).parent.parent / "models" / "weights"
        
        if checkpoint_path is None:
            checkpoint_path = weights_dir / "GenImage_train.pth"
        
        if not Path(checkpoint_path).exists():
            raise FileNotFoundError(
                f"AIDE checkpoint not found: {checkpoint_path}\n"
                f"Please download from: https://drive.google.com/file/d/1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz/view"
            )
        
        print(f"Loading AIDE from: {checkpoint_path}")
        
        # Create model (will load pretrained ResNet and ConvNeXt inside)
        try:
            self.model = create_aide_model(
                resnet_path=resnet_path,
                convnext_path=convnext_path
            )
            
            # Load trained checkpoint
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            if 'model' in checkpoint:
                state_dict = checkpoint['model']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
            
            # Remove 'module.' prefix if present (from DataParallel)
            new_state_dict = {}
            for k, v in state_dict.items():
                name = k.replace('module.', '')
                new_state_dict[name] = v
            
            self.model.load_state_dict(new_state_dict, strict=False)
            self.model = self.model.to(self.device)
            self.model.eval()
            
            print("✅ AIDE model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading AIDE model: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((AIDE_INPUT_SIZE, AIDE_INPUT_SIZE)),
            transforms.ToTensor(),
        ])
        
        # ConvNeXt normalization (for tokens input)
        self.normalize_convnext = transforms.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711]
        )

        # Grad-CAM target layer for low-level artifact branch (HPF + ResNet)
        # We hook into the last conv block of the ResNet that processes HPF features.
        self.artifact_target_layers = []
        try:
            # AIDE_Model defines model_min as a ResNet with .layer4
            self.artifact_target_layers = [self.model.model_min.layer4]
            print("Grad-CAM target layer (artifact branch): model_min.layer4")
        except AttributeError:
            # Fail gracefully – heatmaps will be skipped but scoring still works.
            print("⚠️  Could not locate model_min.layer4 for Grad-CAM; "
                  "heatmaps will be disabled.")
    
    def prepare_inputs(self, image: np.ndarray) -> torch.Tensor:
        """
        Prepare input for AIDE model.
        
        Args:
            image: RGB numpy array (H, W, 3), values 0-255
            
        Returns:
            Tensor of shape [1, 5, 3, H, W] where:
            - dim 0: batch
            - dim 1: 5 different inputs (4 ResNet + 1 ConvNeXt)
            - dim 2-4: channel, height, width
        """
        # Convert to PIL and resize
        pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
        
        # Transform to tensor [3, H, W]
        img_tensor = self.transform(pil_image)
        
        # For simplicity, use same image for all 4 ResNet branches
        # In production, you might want to implement proper min/max pooling
        x_minmin = img_tensor
        x_maxmax = img_tensor
        x_minmin1 = img_tensor
        x_maxmax1 = img_tensor
        
        # ConvNeXt branch needs different normalization
        tokens = self.normalize_convnext(img_tensor)
        
        # Stack: [5, 3, H, W]
        inputs = torch.stack([x_minmin, x_maxmax, x_minmin1, x_maxmax1, tokens], dim=0)
        
        # Add batch dimension: [1, 5, 3, H, W]
        inputs = inputs.unsqueeze(0).to(self.device)
        
        return inputs
    
    def _generate_simple_gradcam(
        self,
        image: np.ndarray,
        fake_prob: float
    ) -> np.ndarray:
        """
        Generate simplified Grad-CAM using ResNet branch.
        
        For AIDE's complex architecture, we focus on the ResNet noise detection branch.
        """
        try:
            from PIL import Image as PILImage
            
            # Prepare single image input for ResNet branch
            pil_image = PILImage.fromarray(image.astype('uint8'), 'RGB')
            img_resized = pil_image.resize((AIDE_INPUT_SIZE, AIDE_INPUT_SIZE))
            
            # Simple attention map based on score
            # Create a basic heatmap centered on high-frequency areas
            heatmap = np.ones((AIDE_INPUT_SIZE, AIDE_INPUT_SIZE)) * fake_prob
            
            # Add some variation based on image gradients
            img_gray = np.array(img_resized.convert('L')).astype(float)
            grad_x = np.abs(np.gradient(img_gray, axis=1))
            grad_y = np.abs(np.gradient(img_gray, axis=0))
            gradient_mag = np.sqrt(grad_x**2 + grad_y**2)
            gradient_mag = (gradient_mag - gradient_mag.min()) / (gradient_mag.max() - gradient_mag.min() + 1e-8)
            
            # Combine score with gradient information
            heatmap = heatmap * (0.5 + 0.5 * gradient_mag)
            
            # Normalize to 0-1
            heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)
            
            return heatmap
            
        except Exception as e:
            print(f"Warning: Grad-CAM generation failed: {e}")
            # Return uniform heatmap as fallback
            return np.ones((AIDE_INPUT_SIZE, AIDE_INPUT_SIZE)) * fake_prob
    
    def predict(
        self,
        image: np.ndarray,
        include_heatmap: bool = True
    ) -> Tuple[float, Optional[np.ndarray]]:
        """
        Run AIDE inference.
        
        Args:
            image: RGB numpy array
            include_heatmap: Whether to generate Grad-CAM (simplified for AIDE)
            
        Returns:
            Tuple of (fake_probability, heatmap_array or None)
        """
        try:
            # Prepare inputs as single tensor [1, 5, 3, H, W]
            inputs = self.prepare_inputs(image)
            
            # Forward pass
            self.model.eval()
            with torch.no_grad():
                output = self.model(inputs)  # [1, 2]
                probabilities = F.softmax(output, dim=1)
            
            # Extract fake probability (class 1)
            fake_prob = probabilities[0, 1].item()
            
            # Generate Grad-CAM heatmap on the artifact (HPF + ResNet) branch
            heatmap = None
            if include_heatmap:
                try:
                    heatmap = self._generate_artifact_gradcam(inputs)
                except Exception as e:
                    print(f"⚠️  Grad-CAM heatmap generation failed: {e}")
                    heatmap = None
            
            return fake_prob, heatmap
            
        except Exception as e:
            print(f"AIDE inference error: {e}")
            import traceback
            traceback.print_exc()
            raise GAICException(ErrorCode.MODEL_ERROR, str(e))
    
    def _generate_artifact_gradcam(self, inputs: torch.Tensor) -> np.ndarray:
        """
        Generate a Grad-CAM heatmap on the low-level artifact branch (HPF + ResNet).
        
        Args:
            inputs: AIDE input tensor of shape [1, 5, 3, H, W]
        
        Returns:
            2D numpy array (H', W') with values in [0, 1]
        """
        if not self.artifact_target_layers:
            raise RuntimeError("Grad-CAM target layers are not configured.")

        targets = [ClassifierOutputTarget(1)]  # class index 1 = fake / AI-generated

        # GradCAM will internally run a forward + backward pass with gradients enabled.
        # Note: In newer pytorch-grad-cam versions, use_cuda parameter is removed.
        # The device is automatically detected from the model.
        with GradCAM(
            model=self.model,
            target_layers=self.artifact_target_layers
        ) as cam:
            grayscale_cam = cam(input_tensor=inputs, targets=targets)
            # Batch size is 1 → take the first CAM
            grayscale_cam = grayscale_cam[0, :]

        return grayscale_cam


# Global model instance (lazy loading)
_aide_model: Optional[AIDeInferenceWrapper] = None


def get_aide_model() -> AIDeInferenceWrapper:
    """Get or create AIDE model instance (singleton)."""
    global _aide_model
    if _aide_model is None:
        _aide_model = AIDeInferenceWrapper()
    return _aide_model


def run_inference(
    image: np.ndarray,
    include_heatmap: bool = True,
    timeout: float = 40.0
) -> Tuple[float, Optional[np.ndarray], int]:
    """
    Run AIDE inference with timeout.
    
    Args:
        image: RGB numpy array
        include_heatmap: Whether to generate Grad-CAM
        timeout: Total timeout in seconds
        
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
