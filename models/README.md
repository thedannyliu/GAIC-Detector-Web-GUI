# Models Directory

This directory contains the model weights for the AI detection models.

## Structure

```
models/
├── weights/          # Model checkpoint files
│   ├── susy.pth
│   ├── fatformer.pth
│   └── distildire.pth
└── README.md        # This file
```

## Getting Model Weights

### Option 1: Download Pre-trained Models

**Note**: Replace these URLs with actual model sources when available.

```bash
# SuSy Model
wget -O weights/susy.pth https://example.com/susy_weights.pth

# FatFormer Model
wget -O weights/fatformer.pth https://example.com/fatformer_weights.pth

# DistilDIRE Model
wget -O weights/distildire.pth https://example.com/distildire_weights.pth
```

### Option 2: Research Papers & Official Implementations

1. **SuSy (Supervised Synthesis Detection)**
   - Search for official implementation and pre-trained weights
   - Paper: [Include reference if available]
   - GitHub: [Include link if available]

2. **FatFormer (Forensic Analysis Transformer)**
   - Check official repository for model weights
   - Paper: [Include reference if available]
   - GitHub: [Include link if available]

3. **DistilDIRE (Distilled Detection)**
   - Look for official releases
   - Paper: [Include reference if available]
   - GitHub: [Include link if available]

### Option 3: Demo Mode (No Weights Needed)

The system includes **mock detectors** that work without actual model weights. These generate realistic-looking results based on image statistics and are suitable for:
- Testing the UI/UX
- Demonstrating the system flow
- Development and integration testing

**Note**: Mock detectors are automatically used when weight files are not found.

## Model Information

### SuSy
- **Type**: Patch-based detector
- **Input**: 224×224 patches with stride
- **Output**: Score + spatial heatmap
- **Use Case**: General AI-image detection

### FatFormer
- **Type**: Transformer-based full-image detector
- **Input**: Full image (resized)
- **Output**: Single score
- **Use Case**: Fast full-image analysis

### DistilDIRE
- **Type**: Distilled detection model
- **Input**: Full image
- **Output**: Single score
- **Use Case**: Lightweight deployment

## File Format

Models should be saved as PyTorch checkpoint files (`.pth` or `.pt`) containing:
- Model state dict
- Architecture configuration (if needed)
- Any preprocessing parameters

## Custom Models

To add your own model:

1. Create a detector class in `app/models.py`:
```python
class CustomDetector(BaseDetector):
    def __init__(self, model_path: Path):
        super().__init__(model_path)
        # Load your model
    
    def predict(self, image, stride):
        # Implement prediction
        return score, heatmap
```

2. Register the model:
```python
registry.register_model("CustomModel", CustomDetector)
```

3. Add to `AVAILABLE_MODELS` in `app/config.py`

4. Place weights file: `models/weights/custommodl.pth`

## Storage Considerations

⚠️ **Large Files**: Model weights are typically large (100MB - 2GB). 
- Excluded from git by default (see `.gitignore`)
- Consider using Git LFS for version control
- Use model hosting services (Hugging Face, AWS S3) for distribution

## Troubleshooting

**Model not loading?**
- Check file exists: `ls -lh models/weights/`
- Verify file permissions
- Check logs for loading errors
- System will fallback to mock detector if weights missing

**Out of memory?**
- Reduce input image size
- Use CPU instead of GPU
- Consider model quantization

**Slow inference?**
- Enable GPU if available
- Reduce stride (increases speed, decreases accuracy)
- Use degraded mode (automatic at 25s timeout)
