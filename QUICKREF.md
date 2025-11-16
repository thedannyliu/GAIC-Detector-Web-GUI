# GAIC Detector v2.0 - Quick Reference

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install
chmod +x quickstart.sh
./quickstart.sh

# 2. Start Backend (Terminal 1)
conda activate gaic-detector
python -m app.main

# 3. Start Frontend (Terminal 2)
conda activate gaic-detector
python gradio_app.py

# 4. Open Browser
http://localhost:7860
```

## 📊 What You Get

### Image Analysis
- Upload: JPG/PNG/WEBP (≤10MB)
- Output: Score (0-100) + Grad-CAM + Explanation
- Model: AIDE (ResNet-50)

### Video Analysis
- Upload: MP4/MOV/WEBM (≤50MB)
- Output: Video score + Key frame + Grad-CAM + Explanation
- Processing: 16 frames sampled, max score used

## 🔑 Key Features

- ✅ **AIDE Model**: ResNet-50 based detector
- ✅ **Grad-CAM**: Visual explanations (mandatory)
- ✅ **Gemini AI**: Auto-generated reports
- ✅ **Dual UI**: Separate Image/Video tabs
- ✅ **History**: Last 5 analyses per mode

## 📡 API Endpoints

```bash
# Image
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@image.jpg" \
  -F "include_heatmap=true"

# Video
curl -X POST http://localhost:8000/analyze/video \
  -F "file=@video.mp4" \
  -F "include_heatmap=true"
```

## 🧪 Test Installation

```bash
python test_system.py
```

## 📁 Key Files

```
app/aide_model.py      - AIDE + Grad-CAM implementation
app/main.py            - FastAPI backend (Image + Video)
app/video_utils.py     - Video processing
gradio_app.py          - Dual-tab UI
test_system.py         - System verification
```

## ⚙️ Configuration

Edit `app/config.py`:
- `MAX_IMAGE_SIZE_MB = 10`
- `MAX_VIDEO_SIZE_MB = 50`
- `VIDEO_SAMPLE_FRAMES = 16`
- `GEMINI_API_KEY = "..."`

## 🐛 Troubleshooting

**Port already in use:**
```bash
export API_PORT=8001  # Backend
# Frontend will auto-detect
```

**CUDA out of memory:**
```bash
export CUDA_VISIBLE_DEVICES=""  # Force CPU
```

**Gemini rate limit:**
- System auto-falls back to templates
- Free tier: ~60 requests/minute

## 📖 Documentation

- Full Docs: `README_AIDE.md`
- Implementation: `IMPLEMENTATION_SUMMARY.md`
- Spec: `docs/master_plan.md`
- API Docs: http://localhost:8000/docs

## ⚠️ Important Notes

- **No Mock Detectors**: All analysis uses real AIDE
- **Grad-CAM Mandatory**: Generated every time
- **Experimental**: PoC system, not production-ready
- **Free Gemini**: Rate limits apply

## 🎯 Score Interpretation

- **0-30**: Low likelihood (likely real)
- **30-70**: Medium (inconclusive)
- **70-100**: High likelihood (AI-generated indicators)

## 📞 Support

- GitHub: https://github.com/thedannyliu/GAIC-Detector-Web-GUI
- Issues: Create an issue on GitHub
- Docs: Read `README_AIDE.md`

---

**Version**: 2.0.0 AIDE Edition  
**Updated**: 2025-01-14  
**Status**: ✅ Production Ready (PoC Level)
