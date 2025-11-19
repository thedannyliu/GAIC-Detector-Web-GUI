#!/usr/bin/env python3
"""
Test script to verify AIDE + Grad-CAM implementation works correctly.
This script tests the backend directly without starting the full API server.
"""

import sys
import numpy as np
from PIL import Image
import io
import base64

# Add app to path
sys.path.insert(0, '/storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI')

from app.aide_inference import get_aide_model, run_inference
from app.image_utils import load_and_preprocess_image, create_gradcam_overlay

def create_test_image():
    """Create a simple test image (gradient pattern)."""
    print("Creating test image...")
    # Create a 512x512 RGB image with gradient pattern
    img_array = np.zeros((512, 512, 3), dtype=np.uint8)
    
    # Create a gradient
    for i in range(512):
        for j in range(512):
            img_array[i, j, 0] = int(i / 2)  # Red channel
            img_array[i, j, 1] = int(j / 2)  # Green channel
            img_array[i, j, 2] = 128          # Blue channel
    
    return img_array

def test_aide_model_loading():
    """Test 1: Can we load the AIDE model?"""
    print("\n" + "="*60)
    print("TEST 1: Loading AIDE Model")
    print("="*60)
    
    try:
        model = get_aide_model()
        print("✅ AIDE model loaded successfully")
        print(f"   Device: {model.device}")
        print(f"   Grad-CAM target layers configured: {len(model.artifact_target_layers) > 0}")
        return True
    except Exception as e:
        print(f"❌ Failed to load AIDE model: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_inference_without_heatmap(image_array):
    """Test 2: Can we run inference without heatmap?"""
    print("\n" + "="*60)
    print("TEST 2: Inference Without Heatmap")
    print("="*60)
    
    try:
        fake_prob, heatmap, inference_ms = run_inference(
            image_array,
            include_heatmap=False,
            timeout=40.0
        )
        
        print(f"✅ Inference completed successfully")
        print(f"   Fake probability: {fake_prob:.4f}")
        print(f"   Score (0-100): {int(fake_prob * 100)}")
        print(f"   Inference time: {inference_ms}ms")
        print(f"   Heatmap generated: {heatmap is not None}")
        
        if heatmap is not None:
            print(f"   ⚠️  Warning: Heatmap should be None when include_heatmap=False")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_inference_with_heatmap(image_array):
    """Test 3: Can we run inference with Grad-CAM heatmap?"""
    print("\n" + "="*60)
    print("TEST 3: Inference With Grad-CAM Heatmap")
    print("="*60)
    
    try:
        fake_prob, heatmap, inference_ms = run_inference(
            image_array,
            include_heatmap=True,
            timeout=40.0
        )
        
        print(f"✅ Inference completed successfully")
        print(f"   Fake probability: {fake_prob:.4f}")
        print(f"   Score (0-100): {int(fake_prob * 100)}")
        print(f"   Inference time: {inference_ms}ms")
        print(f"   Heatmap generated: {heatmap is not None}")
        
        if heatmap is None:
            print(f"   ❌ ERROR: Heatmap should not be None when include_heatmap=True")
            return False
        
        print(f"   Heatmap shape: {heatmap.shape}")
        print(f"   Heatmap dtype: {heatmap.dtype}")
        print(f"   Heatmap range: [{heatmap.min():.4f}, {heatmap.max():.4f}]")
        
        # Verify heatmap is 2D
        if len(heatmap.shape) != 2:
            print(f"   ❌ ERROR: Heatmap should be 2D, got shape {heatmap.shape}")
            return False
        
        # Verify heatmap values are in [0, 1]
        if heatmap.min() < 0 or heatmap.max() > 1:
            print(f"   ⚠️  Warning: Heatmap values should be in [0, 1]")
        
        return True
    except Exception as e:
        print(f"❌ Inference with heatmap failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_heatmap_overlay(image_array, heatmap):
    """Test 4: Can we create the overlay visualization?"""
    print("\n" + "="*60)
    print("TEST 4: Grad-CAM Overlay Creation")
    print("="*60)
    
    try:
        # Convert numpy to PIL
        pil_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
        
        # Create overlay
        heatmap_b64 = create_gradcam_overlay(
            pil_image,
            heatmap,
            alpha=0.5,
            colormap='viridis'
        )
        
        if heatmap_b64 is None:
            print(f"❌ Failed to create overlay: returned None")
            return False
        
        print(f"✅ Overlay created successfully")
        print(f"   Base64 length: {len(heatmap_b64)} characters")
        print(f"   Estimated size: ~{len(heatmap_b64) * 0.75 / 1024:.1f} KB")
        
        # Verify it's valid base64
        try:
            decoded = base64.b64decode(heatmap_b64)
            overlay_img = Image.open(io.BytesIO(decoded))
            print(f"   Overlay image size: {overlay_img.size}")
            print(f"   Overlay image mode: {overlay_img.mode}")
        except Exception as e:
            print(f"   ❌ ERROR: Invalid base64 or image data: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Overlay creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AIDE + Grad-CAM Integration Test")
    print("="*60)
    
    # Create test image
    test_image = create_test_image()
    print(f"Test image shape: {test_image.shape}")
    print(f"Test image dtype: {test_image.dtype}")
    
    # Run tests
    results = []
    
    # Test 1: Model loading
    results.append(("Model Loading", test_aide_model_loading()))
    
    if not results[-1][1]:
        print("\n❌ Model loading failed. Stopping tests.")
        return False
    
    # Test 2: Inference without heatmap
    results.append(("Inference (no heatmap)", test_inference_without_heatmap(test_image)))
    
    # Test 3: Inference with heatmap
    fake_prob, heatmap, _ = run_inference(test_image, include_heatmap=True, timeout=40.0)
    results.append(("Inference (with heatmap)", heatmap is not None))
    
    if heatmap is not None:
        # Test 4: Overlay creation
        results.append(("Heatmap Overlay", test_heatmap_overlay(test_image, heatmap)))
    else:
        results.append(("Heatmap Overlay", False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nThe AIDE + Grad-CAM implementation is working correctly.")
        print("You can now start the backend and frontend to test the full system.")
        print("\nNext steps:")
        print("1. Start backend: python -m app.main")
        print("2. Start frontend: python gradio_app.py")
        print("3. Upload an image and verify the heatmap displays correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before proceeding.")
    
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
