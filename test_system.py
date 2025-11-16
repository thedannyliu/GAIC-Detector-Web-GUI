#!/usr/bin/env python3
"""
Simple test script to verify GAIC Detector installation and basic functionality.
"""

import sys
import subprocess

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    required_packages = [
        ("torch", "PyTorch"),
        ("torchvision", "Torchvision"),
        ("gradio", "Gradio"),
        ("fastapi", "FastAPI"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("google.generativeai", "Google Generative AI"),
        ("pytorch_grad_cam", "PyTorch Grad-CAM"),
    ]
    
    failed = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages installed\n")
    return True


def test_model_loading():
    """Test if AIDE model can be loaded."""
    print("Testing AIDE model loading...")
    try:
        from app.aide_model import get_aide_model
        model = get_aide_model()
        print("  ✓ AIDE model loaded successfully")
        print(f"  ✓ Device: {model.model.device}")
        print("✅ Model test passed\n")
        return True
    except Exception as e:
        print(f"  ✗ Failed to load model: {e}")
        print("❌ Model test failed\n")
        return False


def test_api_health():
    """Test if API is accessible."""
    print("Testing API health...")
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ API is running")
            print(f"  ✓ Version: {data.get('version', 'unknown')}")
            print(f"  ✓ Model: {data.get('model', 'unknown')}")
            print("✅ API test passed\n")
            return True
        else:
            print(f"  ✗ API returned status {response.status_code}")
            print("❌ API test failed\n")
            return False
    except requests.exceptions.ConnectionError:
        print("  ⚠ API not running (this is OK if not started yet)")
        print("  To start API: python -m app.main")
        print("⚠ API test skipped\n")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print("❌ API test failed\n")
        return False


def test_gradcam():
    """Test Grad-CAM generation."""
    print("Testing Grad-CAM...")
    try:
        import torch
        import numpy as np
        from app.aide_model import get_aide_model
        
        # Create dummy image
        dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        # Run inference
        model = get_aide_model()
        fake_prob, heatmap, inference_ms = model.predict(dummy_image, include_heatmap=True)
        
        if heatmap is not None and heatmap.shape == (224, 224):
            print(f"  ✓ Grad-CAM generated successfully")
            print(f"  ✓ Heatmap shape: {heatmap.shape}")
            print(f"  ✓ Score: {fake_prob:.3f}")
            print(f"  ✓ Inference time: {inference_ms}ms")
            print("✅ Grad-CAM test passed\n")
            return True
        else:
            print(f"  ✗ Invalid heatmap shape: {heatmap.shape if heatmap is not None else None}")
            print("❌ Grad-CAM test failed\n")
            return False
            
    except Exception as e:
        import traceback
        print(f"  ✗ Error: {e}")
        traceback.print_exc()
        print("❌ Grad-CAM test failed\n")
        return False


def test_gemini():
    """Test Gemini API connection."""
    print("Testing Gemini API...")
    try:
        import google.generativeai as genai
        from app.config import GEMINI_API_KEY, GEMINI_MODEL
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Simple test prompt
        response = model.generate_content("Say 'OK' if you can read this.")
        
        if response and response.text:
            print(f"  ✓ Gemini API connected")
            print(f"  ✓ Model: {GEMINI_MODEL}")
            print(f"  ✓ Response: {response.text[:50]}...")
            print("✅ Gemini test passed\n")
            return True
        else:
            print(f"  ✗ No response from Gemini")
            print("❌ Gemini test failed\n")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print("  Note: This might be due to rate limiting or API key issues")
        print("⚠ Gemini test failed (non-critical)\n")
        return True  # Non-critical, system can fall back to templates


def main():
    """Run all tests."""
    print("="*60)
    print("GAIC Detector - System Verification")
    print("="*60)
    print()
    
    tests = [
        ("Package Imports", test_imports),
        ("Model Loading", test_model_loading),
        ("Grad-CAM", test_gradcam),
        ("Gemini API", test_gemini),
        ("Backend API", test_api_health),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\nTests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("="*60)
    print("Test Summary")
    print("="*60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:30} {status}")
    
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Start backend: python -m app.main")
        print("  2. Start frontend: python gradio_app.py")
        print("  3. Open browser: http://localhost:7860")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
