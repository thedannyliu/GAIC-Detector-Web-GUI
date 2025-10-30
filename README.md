# GAIC Detector Web GUI

**AI-Generated Image Detection System for Taiwan FactCheck Center**

A complete web-based demo application for detecting AI-generated images using multiple detection models. Features a FastAPI backend and Gradio frontend with real-time analysis, heatmap visualization, and detailed reporting.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

- **Multiple Detection Models**: Switch between SuSy, FatFormer, and DistilDIRE detectors
- **Visual Heatmap Overlay**: Side-by-side comparison with AI detection heatmap
- **Smart Timeout Handling**: Automatic degradation and fallback strategies
- **LLM-Generated Reports**: Detailed explanations with template fallback
- **Session History**: Keep track of last 5 analyses with instant replay
- **Mobile-Friendly**: Responsive design with webcam capture support
- **Privacy-First**: No server-side image persistence

## 📋 Requirements

- Python 3.8 or higher
- CUDA-capable GPU (recommended) or CPU
- 4GB+ RAM
- Modern web browser

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git
cd GAIC-Detector-Web-GUI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Model Setup

Download pre-trained model weights and place them in `models/weights/`:

```bash
mkdir -p models/weights

# Download models (example URLs - replace with actual model sources)
# SuSy model
wget -O models/weights/susy.pth https://example.com/susy_weights.pth

# FatFormer model
wget -O models/weights/fatformer.pth https://example.com/fatformer_weights.pth

# DistilDIRE model
wget -O models/weights/distildire.pth https://example.com/distildire_weights.pth
```

**Note**: The system includes mock detectors for demo purposes when actual weights are unavailable.

### 3. Configuration (Optional)

Create a `.env` file for custom settings:

```bash
# API settings
API_HOST=0.0.0.0
API_PORT=8000

# LLM settings (optional)
LLM_ENABLED=true
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
```

### 4. Run the Application

**Terminal 1 - Start Backend API:**
```bash
python -m app.main
# API will run on http://localhost:8000
```

**Terminal 2 - Start Frontend UI:**
```bash
python gradio_app.py
# UI will open on http://localhost:7860
```

### 5. Access the Interface

Open your browser and navigate to:
- **Frontend UI**: http://localhost:7860
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## 📖 Usage

### Web Interface

1. **Upload Image**: Drag & drop, paste from clipboard, or use webcam
2. **Select Model**: Choose from SuSy (default), FatFormer, or DistilDIRE
3. **Toggle Heatmap**: Enable/disable visual overlay generation
4. **Click Analyze**: Process image and view results
5. **View Results**:
   - AI-generated likelihood score (0-100)
   - Side-by-side original and heatmap images
   - Detailed explanation (expandable)
   - Recent analysis history

### API Usage

```python
import requests

# Analyze an image
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/analyze/image',
        files={'file': f},
        data={
            'model': 'SuSy',
            'include_heatmap': 'true'
        }
    )

result = response.json()
print(f"Score: {result['score']}/100")
print(f"Model: {result['model']}")
```

## 🏗️ Architecture

```
GAIC-Detector-Web-GUI/
├── app/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── config.py          # Configuration
│   ├── models.py          # Model inference
│   ├── image_utils.py     # Image processing
│   ├── report.py          # Report generation
│   └── errors.py          # Error handling
├── gradio_app.py          # Gradio frontend
├── models/
│   └── weights/           # Model checkpoints
├── docs/
│   └── master_plan.md     # Detailed specifications
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 Key Components

### Backend (FastAPI)
- **Image Preprocessing**: Auto-rotation, RGB conversion, resize to 1536px
- **Timeout Management**: 40s total with degradation at 25s, 35s
- **Error Handling**: Comprehensive error codes and fallback strategies
- **Heatmap Generation**: Viridis colormap overlay with 50% alpha

### Frontend (Gradio)
- **Upload Methods**: File upload, clipboard paste, webcam capture
- **Score Visualization**: Large number display with range indicators
- **History Management**: Client-side session storage (max 5 entries)
- **Responsive Layout**: Mobile-first design with single-column fallback

### Models
- **SuSy**: Patch-based detector with stride-based heatmap
- **FatFormer**: Transformer-based full-image detector
- **DistilDIRE**: Distilled detection model

## ⚙️ Configuration Options

### Image Processing
- **Max File Size**: 10MB
- **Supported Formats**: JPG, PNG, WEBP
- **Max Resolution**: 1536px long side (auto-resize)
- **Patch Size**: 224×224
- **Stride**: 112 (default), 224 (degraded)

### Timeout Settings
- **Total Timeout**: 40 seconds
- **Degrade Trigger**: 25 seconds
- **Skip Heatmap**: 35 seconds
- **LLM Timeout**: 2 seconds

## 🔍 API Endpoints

### `POST /analyze/image`
Analyze an image for AI generation likelihood.

**Request:**
- `file`: Image file (multipart/form-data)
- `model`: Model name (optional, default: "SuSy")
- `include_heatmap`: Boolean (optional, default: true)

**Response:**
```json
{
  "score": 78,
  "model": "SuSy",
  "heatmap_png_b64": "base64_encoded_image",
  "report_md": "## Detailed Report...",
  "inference_ms": 820,
  "errors": []
}
```

### `GET /models`
List available models.

### `GET /`
Health check and service info.

## 🧪 Testing

```bash
# Test API health
curl http://localhost:8000/

# Test image analysis
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@test_image.jpg" \
  -F "model=SuSy" \
  -F "include_heatmap=true"
```

## 🚨 Error Codes

| Code | Status | Message |
|------|--------|---------|
| `IMG_FORMAT_UNSUPPORTED` | 400 | Only JPG/PNG/WEBP supported |
| `IMG_TOO_LARGE` | 400 | File exceeds 10MB limit |
| `IMG_DECODE_FAILED` | 400 | Image cannot be decoded |
| `MODEL_NOT_FOUND` | 400 | Selected model unavailable |
| `MODEL_TIMEOUT` | 504 | Inference exceeded 40s |
| `MODEL_ERROR` | 500 | Model raised an exception |
| `HEATMAP_ERROR` | 500 | Failed to render heatmap |
| `REPORT_GEN_ERROR` | 500 | Report generation failed |

## 🔒 Security & Privacy

- ✅ No server-side image persistence
- ✅ In-memory processing only
- ✅ Client-side history storage
- ✅ No external tracking
- ✅ CORS protection enabled

## ⚠️ Limitations & Disclaimers

**This is a proof-of-concept demo system:**

- Scores are **experimental and non-diagnostic**
- Should **not** be used as sole authenticity verification
- Results influenced by compression, editing, and quality
- Model biases and limitations may affect accuracy
- For critical applications, consult forensic experts

## 🛠️ Development

### Running in Development Mode

```bash
# Backend with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend with debug
python gradio_app.py
```

### Adding New Models

1. Implement model class in `app/models.py`
2. Register in `ModelRegistry`
3. Add to `AVAILABLE_MODELS` in `app/config.py`
4. Update frontend dropdown in `gradio_app.py`

## 📝 TODO / Future Enhancements

- [ ] Video analysis support
- [ ] URL image ingestion
- [ ] Batch processing
- [ ] Multi-language UI (Chinese)
- [ ] Dark mode theme
- [ ] PDF report export
- [ ] Model ensemble mode
- [ ] C2PA provenance integration

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Taiwan FactCheck Center
- Model authors: SuSy, FatFormer, DistilDIRE teams
- Gradio and FastAPI communities

## 📧 Contact

For questions or issues:
- GitHub Issues: https://github.com/thedannyliu/GAIC-Detector-Web-GUI/issues
- Email: contact@example.com

---

**Built with ❤️ for fighting AI-generated misinformation**
