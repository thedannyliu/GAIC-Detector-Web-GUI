#!/usr/bin/env python3
"""
Simple test to verify Grad-CAM implementation without loading full model.
Tests import paths and basic structure.
"""

import sys
sys.path.insert(0, '/storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI')

def test_imports():
    """Test 1: Can we import the required modules?"""
    print("\n" + "="*60)
    print("TEST 1: Import Required Modules")
    print("="*60)
    
    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        print("✅ pytorch-grad-cam imports successful")
        
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        
        from app.aide_inference import AIDeInferenceWrapper
        print("✅ AIDeInferenceWrapper import successful")
        
        from app.image_utils import create_gradcam_overlay
        print("✅ create_gradcam_overlay import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_aide_code_structure():
    """Test 2: Check AIDE code has Grad-CAM integration."""
    print("\n" + "="*60)
    print("TEST 2: Check AIDE Code Structure")
    print("="*60)
    
    try:
        import inspect
        from app.aide_inference import AIDeInferenceWrapper
        
        # Check __init__ has target_layers
        init_source = inspect.getsource(AIDeInferenceWrapper.__init__)
        if 'artifact_target_layers' in init_source:
            print("✅ AIDeInferenceWrapper.__init__ sets up artifact_target_layers")
        else:
            print("❌ artifact_target_layers not found in __init__")
            return False
        
        # Check predict method has heatmap logic
        predict_source = inspect.getsource(AIDeInferenceWrapper.predict)
        if 'include_heatmap' in predict_source and 'gradcam' in predict_source.lower():
            print("✅ predict() method has heatmap generation logic")
        else:
            print("❌ Heatmap logic not found in predict()")
            return False
        
        # Check _generate_artifact_gradcam exists
        if hasattr(AIDeInferenceWrapper, '_generate_artifact_gradcam'):
            print("✅ _generate_artifact_gradcam method exists")
        else:
            print("❌ _generate_artifact_gradcam method not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Code structure check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_weights_exist():
    """Test 3: Check if model weights are available."""
    print("\n" + "="*60)
    print("TEST 3: Check Model Weights")
    print("="*60)
    
    try:
        from pathlib import Path
        
        weights_dir = Path('/storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI/models/weights')
        aide_weight = weights_dir / 'GenImage_train.pth'
        
        if aide_weight.exists():
            size_gb = aide_weight.stat().st_size / (1024**3)
            print(f"✅ AIDE weights found: {aide_weight}")
            print(f"   Size: {size_gb:.2f} GB")
            return True
        else:
            print(f"❌ AIDE weights not found: {aide_weight}")
            return False
    except Exception as e:
        print(f"❌ Weight check failed: {e}")
        return False

def test_api_endpoints():
    """Test 4: Check FastAPI endpoints have correct structure."""
    print("\n" + "="*60)
    print("TEST 4: Check API Endpoints")
    print("="*60)
    
    try:
        import inspect
        from app.main import analyze_image
        
        source = inspect.getsource(analyze_image)
        
        checks = [
            ('include_heatmap', '✅ include_heatmap parameter exists'),
            ('run_inference', '✅ Calls run_inference'),
            ('create_gradcam_overlay', '✅ Creates Grad-CAM overlay'),
            ('heatmap_png_b64', '✅ Returns heatmap_png_b64'),
        ]
        
        all_pass = True
        for keyword, message in checks:
            if keyword in source:
                print(message)
            else:
                print(f"❌ Missing: {keyword}")
                all_pass = False
        
        return all_pass
    except Exception as e:
        print(f"❌ API endpoint check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AIDE + Grad-CAM Implementation Verification")
    print("="*60)
    print("This test verifies the code structure without loading the model.")
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Code structure
    results.append(("Code Structure", test_aide_code_structure()))
    
    # Test 3: Model weights
    results.append(("Model Weights", test_model_weights_exist()))
    
    # Test 4: API endpoints
    results.append(("API Endpoints", test_api_endpoints()))
    
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
        print("🎉 ALL STRUCTURE TESTS PASSED!")
        print("="*60)
        print("\nThe Grad-CAM implementation is correctly integrated.")
        print("\nNext steps:")
        print("1. Start backend: conda run -n gaic-detector python -m app.main")
        print("2. Start frontend: conda run -n gaic-detector python gradio_app.py")
        print("3. Upload an image and verify the heatmap displays")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above.")
    
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
