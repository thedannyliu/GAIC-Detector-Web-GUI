"""
Test script for GAIC Detector API
"""

import requests
import sys
from pathlib import Path

API_URL = "http://localhost:8000"


def test_health():
    """Test API health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_models():
    """Test models endpoint."""
    print("\n🔍 Testing models endpoint...")
    try:
        response = requests.get(f"{API_URL}/models")
        if response.status_code == 200:
            print("✅ Models endpoint passed")
            data = response.json()
            print(f"   Available models: {data.get('models')}")
            print(f"   Default model: {data.get('default')}")
            return True
        else:
            print(f"❌ Models endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint failed: {e}")
        return False


def test_analyze(image_path=None):
    """Test analyze endpoint."""
    print("\n🔍 Testing analyze endpoint...")
    
    # Create a simple test image if none provided
    if image_path is None:
        print("   Creating test image...")
        from PIL import Image
        import numpy as np
        import io
        
        # Create a random noise image
        img_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        files = {"file": ("test.png", img_bytes, "image/png")}
    else:
        print(f"   Using image: {image_path}")
        files = {"file": open(image_path, "rb")}
    
    try:
        data = {
            "model": "SuSy",
            "include_heatmap": "true"
        }
        
        response = requests.post(
            f"{API_URL}/analyze/image",
            files=files,
            data=data,
            timeout=50
        )
        
        if response.status_code == 200:
            print("✅ Analyze endpoint passed")
            result = response.json()
            print(f"   Score: {result.get('score')}/100")
            print(f"   Model: {result.get('model')}")
            print(f"   Inference time: {result.get('inference_ms')}ms")
            print(f"   Heatmap: {'✓' if result.get('heatmap_png_b64') else '✗'}")
            print(f"   Errors: {result.get('errors', [])}")
            return True
        else:
            print(f"❌ Analyze endpoint failed with status {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Analyze endpoint failed: {e}")
        return False
    finally:
        if image_path and 'files' in locals():
            files["file"].close()


def main():
    """Run all tests."""
    print("🧪 GAIC Detector API Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test models
    results.append(("Models List", test_models()))
    
    # Test analyze
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    results.append(("Image Analysis", test_analyze(image_path)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:20s} {status}")
    
    print("=" * 50)
    print(f"   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
