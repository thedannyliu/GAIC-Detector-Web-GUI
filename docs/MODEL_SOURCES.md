# GAIC Detector - Model Information & Sources

## 📋 Overview

This document provides information about the detection models used in GAIC Detector and how to obtain them.

## 🔬 Available Models

### 1. SuSy (Supervised Synthesis Detection)

**Type**: Patch-based CNN detector  
**Architecture**: ResNet-based with spatial attention  
**Strengths**: Good for localized manipulation detection  
**Output**: Global score + spatial heatmap

**Potential Sources**:
- Search GitHub for "SuSy AI detection" or "supervised synthesis detection"
- Check papers on IEEE Xplore, arXiv for official implementations
- Look for "fake image detection" or "deepfake detection" models

**Alternative Similar Models**:
- ManTra-Net
- SPAN (SPatial Pyramid Attention Network)
- Noiseprint

### 2. FatFormer (Forensic Analysis Transformer)

**Type**: Vision Transformer-based full-image detector  
**Architecture**: ViT with forensic-specific attention  
**Strengths**: Fast full-image analysis, good generalization  
**Output**: Single authenticity score

**Potential Sources**:
- Search for "Vision Transformer deepfake detection"
- Look for "FatFormer" or similar transformer-based forensic models
- Check Hugging Face model hub

**Alternative Similar Models**:
- UnivFD (Universal Fake Detector)
- DIRE (Diffusion Reconstruction Error)
- NPR (Neural Parametric Representation)

### 3. DistilDIRE (Distilled Detection)

**Type**: Lightweight distilled model  
**Architecture**: Compressed version of DIRE  
**Strengths**: Fast inference, good for production  
**Output**: Single authenticity score

**Potential Sources**:
- DIRE official implementation: https://github.com/ZhendongWang6/DIRE
- Look for knowledge distillation variants
- Check model compression papers

**Alternative Similar Models**:
- Compressed versions of other detectors
- MobileNet-based detectors
- EfficientNet variants

## 🔍 How to Find Models

### Research Papers

Search on:
- **arXiv**: https://arxiv.org/search/
  - Keywords: "AI-generated image detection", "deepfake detection", "synthetic image detection"
- **Google Scholar**: https://scholar.google.com/
- **IEEE Xplore**: https://ieeexplore.ieee.org/
- **Papers with Code**: https://paperswithcode.com/task/deepfake-detection

### Code Repositories

Check:
- **GitHub**: https://github.com/search
  - Search: "AI image detection", "fake image detection", "GAN detection"
- **Hugging Face**: https://huggingface.co/models
  - Filter by "Computer Vision" > "Image Classification"
- **ModelScope**: https://modelscope.cn/

### Recommended Starting Points

1. **UnivFD (Universal Fake Detector)**
   - Paper: https://arxiv.org/abs/2302.10174
   - GitHub: https://github.com/Yuheng-Li/UniversalFakeDetect
   - Very good general-purpose detector

2. **DIRE (Diffusion Reconstruction Error)**
   - Paper: https://arxiv.org/abs/2303.09295
   - GitHub: https://github.com/ZhendongWang6/DIRE
   - Excellent for diffusion model detection

3. **NPR (Neural Parametric Representation)**
   - Paper: https://arxiv.org/abs/2209.00904
   - GitHub: https://github.com/chail/patch-forensics
   - Good for localized detection

4. **Dragnets/CNNDetection**
   - GitHub: https://github.com/peterwang512/CNNDetection
   - Classic CNN-based detector
   - Good baseline

## 🛠️ Adapting Models for GAIC Detector

### Integration Steps

1. **Create Detector Class** (`app/models.py`):
```python
class YourModelDetector(BaseDetector):
    def __init__(self, model_path: Path):
        super().__init__(model_path)
        # Load your specific model architecture
        self.model = load_your_model(model_path)
    
    def predict(self, image: np.ndarray, stride: int) -> Tuple[float, Optional[np.ndarray]]:
        # Implement inference
        tensor = self.preprocess(image)
        with torch.no_grad():
            output = self.model(tensor)
        score = output.item()  # Should be 0-1
        heatmap = None  # or generate spatial map
        return score, heatmap
```

2. **Register Model**:
```python
registry.register_model("YourModel", YourModelDetector)
```

3. **Update Config** (`app/config.py`):
```python
AVAILABLE_MODELS = ["SuSy", "FatFormer", "DistilDIRE", "YourModel"]
```

4. **Test**:
```bash
python test_api.py your_test_image.jpg
```

## 📦 Model Format Requirements

Models should be saved as PyTorch checkpoints containing:

```python
checkpoint = {
    'model_state_dict': model.state_dict(),
    'architecture': 'model_name',
    'input_size': (224, 224),
    'num_classes': 1,
    # Optional metadata
}
torch.save(checkpoint, 'model.pth')
```

## 🔄 Mock Mode (No Weights Needed)

The system includes **intelligent mock detectors** that:
- Work without actual model weights
- Generate realistic scores based on image statistics
- Useful for:
  - UI/UX development and testing
  - System integration testing
  - Demos when models aren't available
  - Teaching and workshops

**Mock detectors analyze**:
- Image variance and complexity
- Color distribution
- Edge characteristics
- Compression artifacts

## 📚 Suggested Model Training

If you want to train your own models:

### Datasets

1. **CIFAKE**: Real vs AI-generated images
   - https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images

2. **DiffusionDB**: Large-scale diffusion model outputs
   - https://github.com/poloclub/diffusiondb

3. **RAISE**: Real images for baseline
   - http://loki.disi.unitn.it/RAISE/

4. **GAN-generated datasets**: Various GAN outputs
   - Check Papers with Code datasets section

### Training Tips

- Use balanced real/fake data
- Include multiple generation methods (GAN, Diffusion, etc.)
- Apply data augmentation carefully
- Validate on diverse test sets
- Consider domain adaptation

## 🌐 Community Resources

### Forums & Communities

- **Reddit**: r/MachineLearning, r/deepfakes
- **Discord**: ML/AI servers
- **Twitter/X**: Follow #DeepfakeDetection, #AIForensics

### Conferences

- **CVPR**: Computer Vision papers
- **ICCV**: International Conference on Computer Vision  
- **ECCV**: European Conference on Computer Vision
- **WACV**: Winter Conference on Applications of CV

## ⚠️ Important Notes

1. **Licensing**: Always check model licenses before use
2. **Attribution**: Credit original authors properly
3. **Evaluation**: Test models on your specific use case
4. **Ethics**: Use responsibly for legitimate verification
5. **Updates**: Models may need retraining as generators improve

## 🤝 Contributing Models

If you have models to share:
1. Fork the repository
2. Add model integration code
3. Update documentation
4. Submit pull request
5. We'll help with integration

## 📧 Need Help?

**Can't find specific models?**
- Open a GitHub issue
- Contact Taiwan FactCheck Center
- Reach out to model authors
- Check academic collaborations

**Model integration issues?**
- See docs/DEPLOYMENT.md
- Review app/models.py examples
- Test with mock mode first

---

**Last Updated**: 2025-10-30  
**Maintained by**: GAIC Detector Team
