# GAIC Detector - AIDE Edition

**Version 2.0** - AI-Generated Content Detection with AIDE + Grad-CAM + Gemini

🔍 Complete PoC implementation for Taiwan FactCheck Center

## ✨ What's New in v2.0

- ✅ **AIDE Model**: AI-generated Image DEtector based on ResNet-50
- ✅ **Mandatory Grad-CAM**: Visual explanations for every analysis
- ✅ **Video Support**: Frame-by-frame analysis with aggregation
- ✅ **Gemini Integration**: AI-powered explanations via Gemini 1.5 Flash
- ✅ **Dual-Tab UI**: Separate interfaces for Image and Video analysis
- ✅ **Session History**: Keep track of last 5 analyses per mode

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda (Anaconda or Miniconda)
- CUDA-capable GPU (recommended) or CPU

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git
cd GAIC-Detector-Web-GUI

# 2. Run quick start script
chmod +x quickstart.sh
./quickstart.sh
```

### Running the System

#### Option 1: Manual Start (Recommended for Development)

**Terminal 1 - Backend API:**
```bash
conda activate gaic-detector
python -m app.main
# API runs on http://localhost:8000
```

**Terminal 2 - Frontend UI:**
```bash
conda activate gaic-detector
python gradio_app.py
# UI runs on http://localhost:7860
```

#### Option 2: Simple Background Start

```bash
./start_simple.sh
```

#### Option 3: Cluster Environment

```bash
./start_cluster.sh
```

### Accessing the Interface

- **Web UI**: http://localhost:7860
- **API Docs**: http://localhost:8000/docs

## 📋 Features

### Image Analysis
- Upload via drag-drop, clipboard, or webcam
- AIDE model detection (ResNet-50 based)
- Grad-CAM heatmap visualization
- Gemini-generated explanations
- Score: 0-100 (Low/Medium/High)

### Video Analysis
- Support: MP4, MOV, WEBM (≤50MB)
- Automatic frame sampling (16 frames)
- Per-frame AIDE analysis
- Video score = max(frame scores)
- Key frame + heatmap visualization

### Explainability
- **Grad-CAM Heatmaps**: Shows which regions triggered detection
- **AI Explanations**: Gemini 1.5 Flash generates context-aware reports
- **Template Fallback**: If Gemini times out, uses template reports

## 🏗️ Architecture

```
GAIC-Detector-Web-GUI/
├── app/                      # FastAPI Backend
│   ├── aide_model.py        # AIDE implementation + Grad-CAM
│   ├── main.py              # API endpoints
│   ├── config.py            # Configuration
│   ├── image_utils.py       # Image processing
│   ├── video_utils.py       # Video processing
│   ├── report.py            # Gemini report generation
│   └── errors.py            # Error handling
├── gradio_app.py            # Gradio Frontend (Image/Video tabs)
├── requirements.txt         # Dependencies
├── docs/
│   └── master_plan.md       # Detailed specification
└── test_samples/            # Test images/videos
```

## 🔧 Configuration

### Environment Variables

```bash
# API Settings
export API_HOST=0.0.0.0
export API_PORT=8000

# Gemini API (already configured)
export GEMINI_API_KEY="AIzaSyDcpP36XpRgiA7qM-82yLn0SAqyxrEn4aM"

# Gradio Share (for cluster/remote access)
export GRADIO_SHARE=true

# Backend URL (for frontend)
export GAIC_BACKEND_URL=http://localhost:8000
```

### Model Configuration

Edit `app/config.py`:
- `MAX_IMAGE_SIZE_MB = 10`
- `MAX_VIDEO_SIZE_MB = 50`
- `VIDEO_SAMPLE_FRAMES = 16`
- `GRADCAM_ALPHA = 0.5`

## 🎯 API Usage

### Analyze Image

```bash
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@image.jpg" \
  -F "include_heatmap=true"
```

### Analyze Video

```bash
curl -X POST http://localhost:8000/analyze/video \
  -F "file=@video.mp4" \
  -F "include_heatmap=true"
```

### Response Format

```json
{
  "score": 75,
  "model": "AIDE",
  "heatmap_png_b64": "...",
  "report_md": "## Analysis Report\n...",
  "inference_ms": 1250,
  "errors": []
}
```

## 📊 Model Details

### AIDE (AI-generated Image DEtector)

- **Architecture**: ResNet-50 backbone + Binary classifier
- **Input**: 224×224 RGB images
- **Output**: Real vs AI-generated probability
- **Explainability**: Grad-CAM on layer4 (last conv block)

### Grad-CAM Configuration

- **Target Layer**: `model.layer4` (ResNet-50)
- **Colormap**: viridis (color-blind friendly)
- **Alpha Blending**: 50% heatmap + 50% original

### Video Processing

1. Sample 16 frames uniformly across timeline
2. Run AIDE + Grad-CAM on each frame
3. Video score = max(frame scores)
4. Report top-3 suspicious frames to Gemini

## ⚠️ Important Notes

### Disclaimer

This is a **proof-of-concept** system:
- Scores are experimental and non-diagnostic
- Should NOT be sole basis for authenticity determination
- For critical applications, consult forensic experts

### Limitations

- AIDE uses pre-trained ResNet-50 (not fine-tuned on specific datasets)
- Scores may vary with compression, editing, and quality
- Gemini explanations are AI-generated (may have inaccuracies)

### Free Tier Limits

- **Gemini API**: Free tier allows ~60 requests/minute
- **Grad-CAM**: No limit, computed locally
- **Video**: Max 50MB, max 5 minutes duration

## 🧪 Testing

### Test with Sample Images

```bash
# Create test images
python -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (512, 512), 'white')
draw = ImageDraw.Draw(img)
draw.rectangle([100, 100, 400, 400], fill='blue')
img.save('test_samples/test_blue.jpg')
"

# Test via API
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@test_samples/test_blue.jpg"
```

### Test with Video

Upload any MP4/MOV/WEBM file ≤50MB via the web interface.

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
export API_PORT=8001
python -m app.main
```

### Gradio won't start

```bash
# Check if port 7860 is in use
lsof -i :7860

# Frontend will use API_PORT from config
```

### CUDA out of memory

```bash
# Force CPU mode
export CUDA_VISIBLE_DEVICES=""
python -m app.main
```

### Gemini API errors

- Check API key is set correctly
- Free tier has rate limits (~60 req/min)
- System falls back to template reports automatically

## 📝 Development

### Adding New Features

1. Backend changes: Edit `app/main.py`
2. Frontend changes: Edit `gradio_app.py`
3. Model changes: Edit `app/aide_model.py`
4. Configuration: Edit `app/config.py`

### Code Structure

- `app/aide_model.py`: AIDE + Grad-CAM implementation
- `app/main.py`: FastAPI endpoints
- `app/video_utils.py`: Video frame sampling
- `app/report.py`: Gemini integration
- `gradio_app.py`: Dual-tab UI

## 📖 Documentation

- **Master Plan**: `docs/master_plan.md` (detailed specification)
- **API Docs**: http://localhost:8000/docs (when running)
- **Model Sources**: `docs/MODEL_SOURCES.md`

## 🤝 Contributing

This is a PoC for Taiwan FactCheck Center. For production deployment:

1. Fine-tune AIDE on specific datasets
2. Add user authentication
3. Implement rate limiting
4. Add persistent storage (optional)
5. Deploy with proper infrastructure (Docker, K8s)

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Taiwan FactCheck Center
- PyTorch Grad-CAM library
- Google Gemini API
- Gradio framework

## 📧 Contact

- GitHub: https://github.com/thedannyliu/GAIC-Detector-Web-GUI
- Issues: https://github.com/thedannyliu/GAIC-Detector-Web-GUI/issues

---

**Built with ❤️ for fighting AI-generated misinformation**
