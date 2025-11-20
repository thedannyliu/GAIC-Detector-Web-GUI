# GAIC Detector Web GUI - AIDE Edition

AI-Generated Image/Video Detection System with AIDE model, Grad-CAM explanations, and Gemini-powered reports.

🎉 **NEW: Official AIDE Model Integration** (ICLR 2025)

## 🚀 Quick Start (Phoenix GPU Server)

### One-Command Launch:

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./run_local.sh
```

Then on **your local computer**:

```bash
ssh -N -L 7860:localhost:7860 -L 8000:localhost:8000 eliu354@login-phoenix-slurm.pace.gatech.edu
```

Open browser: **http://localhost:7860**

**📖 Full Guide**: See [START_HERE.md](START_HERE.md) or [QUICK_START.md](QUICK_START.md)



[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/thedannyliu/GAIC-Detector-Web-GUI)![Version](https://img.shields.io/badge/version-1.0.0-blue)

[![Python](https://img.shields.io/badge/python-3.10-green)](https://www.python.org/)![Python](https://img.shields.io/badge/python-3.10-green)

[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)![License](https://img.shields.io/badge/license-MIT-orange)

[![AIDE](https://img.shields.io/badge/AIDE-ICLR%202025-red)](https://github.com/shilinyan99/AIDE)

## 🌟 Features

## ✨ Features

- **Multiple Detection Models**: Switch between SuSy, FatFormer, and DistilDIRE detectors

- 🤖 **AIDE Model**: State-of-the-art AI-generated image detector- **Visual Heatmap Overlay**: Side-by-side comparison with AI detection heatmap

  - Multi-expert architecture (HPF+ResNet-50 + ConvNeXt-XXL)- **Smart Timeout Handling**: Automatic degradation and fallback strategies

  - Hybrid feature extraction (noise patterns + semantic features)- **LLM-Generated Reports**: Detailed explanations with template fallback

  - ICLR 2025 accepted paper- **Session History**: Keep track of last 5 analyses with instant replay

  - **Mobile-Friendly**: Responsive design with webcam capture support

- 🖼️ **Image & Video Support**- **Privacy-First**: No server-side image persistence

  - Image: JPG, PNG, WEBP (≤10MB)

  - Video: MP4, MOV, WEBM (≤50MB, 16-frame sampling)## 📋 Requirements

  

- 🔍 **Explainable AI**- Python 3.10

  - Grad-CAM visualization (coming soon for AIDE)- Conda

  - Gemini-powered natural language explanations- CUDA-capable GPU (recommended) or CPU

  - 4GB+ RAM

- 🌐 **Web Interface**- Modern web browser

  - Dual-tab UI (separate for images and videos)

  - History tracking (last 5 analyses)## 🚀 Quick Start

  - Gradio Share support for remote access

  ### 1. Installation

- ⚡ **GPU Acceleration**

  - Auto-detection and configuration```bash

  - ~10x faster inference on GPU# Clone the repository

  - Cluster-friendly (SLURM/PBS detection)git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git

cd GAIC-Detector-Web-GUI

## 🚀 Quick Start

# Create and activate conda environment

### Prerequisitesconda create -n gaic-detector python=3.10 -y

conda activate gaic-detector

- Python 3.10+

- NVIDIA GPU (optional, but recommended)# Install dependencies

- Conda environment managerpip install -r requirements.txt

```

### Installation

### 2. Model Setup

```bash

# 1. Clone repositoryDownload pre-trained model weights and place them in `models/weights/`:

git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git

cd GAIC-Detector-Web-GUI```bash

mkdir -p models/weights

# 2. Create conda environment

conda create -n gaic-detector python=3.10 -y# Download models (example URLs - replace with actual model sources)

conda activate gaic-detector# SuSy model

wget -O models/weights/susy.pth https://example.com/susy_weights.pth

# 3. Install dependencies

pip install -r requirements.txt# FatFormer model

wget -O models/weights/fatformer.pth https://example.com/fatformer_weights.pth

# 4. Download AIDE model (3.6GB)

./download_aide_weights.sh# DistilDIRE model

wget -O models/weights/distildire.pth https://example.com/distildire_weights.pth

# 5. Start services```

./start_gpu.sh        # With GPU (recommended)

# OR**Note**: The system includes mock detectors for demo purposes when actual weights are unavailable.

./start.sh            # CPU only

```### 3. Configuration (Optional)



### UsageCreate a `.env` file for custom settings:



1. **Open browser**: http://localhost:7860```bash

2. **Upload image or video**# API settings

3. **Click Analyze**API_HOST=0.0.0.0

4. **View results**: Score, heatmap, explanationAPI_PORT=8000



## 📊 Model Information# LLM settings (optional)

LLM_ENABLED=true

### AIDE (AI-generated Image DEtector)OPENAI_API_KEY=your_openai_api_key_here

LLM_MODEL=gpt-3.5-turbo

**Paper**: A Sanity Check for AI-generated Image Detection (ICLR 2025)  ```

**Authors**: Shilin Yan, Ouxiang Li, Jiayin Cai, et al.  

**Source**: https://github.com/shilinyan99/AIDE### 4. Run the Application



**Architecture**:**Terminal 1 - Start Backend API:**

- **Noise Expert**: SRM High-Pass Filter + ResNet-50```bash

- **Semantic Expert**: ConvNeXt-XXL (OpenCLIP)python -m app.main

- **Fusion**: MLP (2048+256 → 1024 → 2 classes)# API will run on http://localhost:8000

```

**Performance on Benchmarks**:

| Dataset | Accuracy |**Terminal 2 - Start Frontend UI:**

|---------|----------|```bash

| ProGAN  | 99.8%    |python gradio_app.py

| DALL-E 2 | 95.2%   |# UI will open on http://localhost:7860

| Midjourney | 92.5% |```

| Stable Diffusion | 91.3% |

### 5. Access the Interface

## 🎮 GPU Support

Open your browser and navigate to:

### Automatic GPU Mode- **Frontend UI**: http://localhost:7860

- **API Docs**: http://localhost:8000/docs (Swagger UI)

```bash

./start_gpu.sh## 📖 Usage

```

### Web Interface

Features:

- ✅ Auto-detect NVIDIA GPU1. **Upload Image**: Drag & drop, paste from clipboard, or use webcam

- ✅ Verify PyTorch CUDA support  2. **Select Model**: Choose from SuSy (default), FatFormer, or DistilDIRE

- ✅ Enable Gradio Share on clusters3. **Toggle Heatmap**: Enable/disable visual overlay generation

- ✅ Monitor service health4. **Click Analyze**: Process image and view results

5. **View Results**:

### Performance Comparison   - AI-generated likelihood score (0-100)

   - Side-by-side original and heatmap images

| Mode | Device | Image | Video (16 frames) |   - Detailed explanation (expandable)

|------|--------|-------|-------------------|   - Recent analysis history

| CPU  | -      | ~2-3s | ~30-50s           |

| GPU  | RTX 3080 | ~0.3s | ~5-8s          |### API Usage



See [GPU_GUIDE.md](GPU_GUIDE.md) for detailed setup.```python

import requests

## 🌐 Remote Access (for Clusters)

# Analyze an image

### On Georgia Tech PACE Phoenixwith open('image.jpg', 'rb') as f:

    response = requests.post(

```bash        'http://localhost:8000/analyze/image',

# Start in Jupyter Interactive App        files={'file': f},

conda activate gaic-detector        data={

./start_gpu.sh            'model': 'SuSy',

            'include_heatmap': 'true'

# Gradio Share will auto-generate public URL        }

# Example: https://xxxxx.gradio.live    )

```

result = response.json()

Gradio Share automatically enabled when:print(f"Score: {result['score']}/100")

- `$SLURM_JOB_ID` is set (SLURM cluster)print(f"Model: {result['model']}")

- `$PBS_JOBID` is set (PBS cluster)```

- `GRADIO_SHARE=true` environment variable

## 🏗️ Architecture

### Alternative: SSH Port Forwarding

```

```bashGAIC-Detector-Web-GUI/

# On your local machine├── app/                    # FastAPI backend

ssh -L 7860:compute-node:7860 username@login.pace.gatech.edu│   ├── main.py            # API endpoints

│   ├── config.py          # Configuration

# Then open: http://localhost:7860│   ├── models.py          # Model inference

```│   ├── image_utils.py     # Image processing

│   ├── report.py          # Report generation

## 📡 API Endpoints│   └── errors.py          # Error handling

├── gradio_app.py          # Gradio frontend

### POST /analyze/image├── models/

│   └── weights/           # Model checkpoints

```bash├── docs/

curl -X POST http://localhost:8000/analyze/image \│   └── master_plan.md     # Detailed specifications

  -F "file=@image.jpg" \├── requirements.txt       # Python dependencies

  -F "include_heatmap=true"└── README.md             # This file

``````



**Response**:## 🎯 Key Components

```json

{### Backend (FastAPI)

  "score": 85.3,- **Image Preprocessing**: Auto-rotation, RGB conversion, resize to 1536px

  "label": "AI-Generated",- **Timeout Management**: 40s total with degradation at 25s, 35s

  "confidence": "High",- **Error Handling**: Comprehensive error codes and fallback strategies

  "heatmap_base64": "iVBORw0KG...",- **Heatmap Generation**: Viridis colormap overlay with 50% alpha

  "explanation": "The image shows signs of AI generation...",

  "model_name": "AIDE",### Frontend (Gradio)

  "inference_ms": 342,- **Upload Methods**: File upload, clipboard paste, webcam capture

  "notices": []- **Score Visualization**: Large number display with range indicators

}- **History Management**: Client-side session storage (max 5 entries)

```- **Responsive Layout**: Mobile-first design with single-column fallback



### POST /analyze/video### Models

- **SuSy**: Patch-based detector with stride-based heatmap

```bash- **FatFormer**: Transformer-based full-image detector

curl -X POST http://localhost:8000/analyze/video \- **DistilDIRE**: Distilled detection model

  -F "file=@video.mp4"

```## ⚙️ Configuration Options



**Response**:### Image Processing

```json- **Max File Size**: 10MB

{- **Supported Formats**: JPG, PNG, WEBP

  "video_score": 92.1,- **Max Resolution**: 1536px long side (auto-resize)

  "video_label": "AI-Generated",- **Patch Size**: 224×224

  "key_frame_index": 8,- **Stride**: 112 (default), 224 (degraded)

  "key_frame_score": 95.3,

  "frame_scores": [78.2, 81.5, ...],### Timeout Settings

  "explanation": "Analysis of 16 sampled frames...",- **Total Timeout**: 40 seconds

  "model_name": "AIDE",- **Degrade Trigger**: 25 seconds

  "inference_ms": 5430- **Skip Heatmap**: 35 seconds

}- **LLM Timeout**: 2 seconds

```

## 🔍 API Endpoints

Full API docs: http://localhost:8000/docs

### `POST /analyze/image`

## 📁 Project StructureAnalyze an image for AI generation likelihood.



```**Request:**

GAIC-Detector-Web-GUI/- `file`: Image file (multipart/form-data)

├── app/- `model`: Model name (optional, default: "SuSy")

│   ├── aide_original/          # Official AIDE implementation- `include_heatmap`: Boolean (optional, default: true)

│   │   ├── AIDE.py             # Model architecture

│   │   ├── srm_filter_kernel.py # SRM filters**Response:**

│   │   └── utils.py```json

│   ├── aide_inference.py       # Inference wrapper{

│   ├── main.py                 # FastAPI backend  "score": 78,

│   ├── config.py               # Configuration  "model": "SuSy",

│   ├── errors.py               # Error handling  "heatmap_png_b64": "base64_encoded_image",

│   ├── image_utils.py          # Image utilities  "report_md": "## Detailed Report...",

│   ├── video_utils.py          # Video processing  "inference_ms": 820,

│   └── report.py               # Gemini integration  "errors": []

├── models/weights/}

│   └── GenImage_train.pth      # AIDE checkpoint (3.6GB)```

├── gradio_app.py               # Gradio UI

├── start_gpu.sh                # GPU launcher### `GET /models`

├── start.sh                    # CPU launcherList available models.

├── start_cluster.sh            # Cluster launcher

├── download_aide_weights.sh    # Model downloader### `GET /`

└── requirements.txtHealth check and service info.

```

## 🧪 Testing

## 🔧 Configuration

```bash

Edit `app/config.py`:# Test API health

curl http://localhost:8000/

```python

# Image settings# Test image analysis

MAX_IMAGE_SIZE_MB = 10curl -X POST http://localhost:8000/analyze/image \

IMG_INPUT_SIZE = 224  -F "file=@test_image.jpg" \

  -F "model=SuSy" \

# Video settings  -F "include_heatmap=true"

MAX_VIDEO_SIZE_MB = 50```

VIDEO_SAMPLE_FRAMES = 16

## 🚨 Error Codes

# Gemini API

GEMINI_API_KEY = "your-key-here"| Code | Status | Message |

GEMINI_MODEL = "gemini-1.5-flash"|------|--------|---------|

| `IMG_FORMAT_UNSUPPORTED` | 400 | Only JPG/PNG/WEBP supported |

# Inference| `IMG_TOO_LARGE` | 400 | File exceeds 10MB limit |

TIMEOUT_TOTAL = 40.0  # seconds| `IMG_DECODE_FAILED` | 400 | Image cannot be decoded |

```| `MODEL_NOT_FOUND` | 400 | Selected model unavailable |

| `MODEL_TIMEOUT` | 504 | Inference exceeded 40s |

## 🧪 Testing| `MODEL_ERROR` | 500 | Model raised an exception |

| `HEATMAP_ERROR` | 500 | Failed to render heatmap |

```bash| `REPORT_GEN_ERROR` | 500 | Report generation failed |

# System verification

conda activate gaic-detector## 🔒 Security & Privacy

python test_system.py

- ✅ No server-side image persistence

# API testing- ✅ In-memory processing only

python test_api.py- ✅ Client-side history storage

```- ✅ No external tracking

- ✅ CORS protection enabled

## 🐛 Troubleshooting

## ⚠️ Limitations & Disclaimers

### Model not found

```bash**This is a proof-of-concept demo system:**

./download_aide_weights.sh

```- Scores are **experimental and non-diagnostic**

- Should **not** be used as sole authenticity verification

### CUDA out of memory- Results influenced by compression, editing, and quality

```bash- Model biases and limitations may affect accuracy

export CUDA_VISIBLE_DEVICES=""  # Force CPU mode- For critical applications, consult forensic experts

```

## 🛠️ Development

### Port already in use

```bash### Running in Development Mode

# Kill existing processes

lsof -ti:8000 | xargs kill -9```bash

lsof -ti:7860 | xargs kill -9# Backend with auto-reload

```uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



### Gradio Share issues# Frontend with debug

```bashpython gradio_app.py

# Manual enable```

export GRADIO_SHARE=true

python gradio_app.py### Adding New Models

```

1. Implement model class in `app/models.py`

### ConvNeXt model download fails2. Register in `ModelRegistry`

Check internet connection. The model (open_clip ConvNeXt-XXL) will be downloaded automatically on first run.3. Add to `AVAILABLE_MODELS` in `app/config.py`

4. Update frontend dropdown in `gradio_app.py`

## 📚 Documentation

## 📝 TODO / Future Enhancements

- [GPU Setup Guide](GPU_GUIDE.md) - Comprehensive GPU setup

- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical details- [ ] Video analysis support

- [AIDE Paper](https://arxiv.org/abs/2406.19435) - Original research- [ ] URL image ingestion

- [API Docs](http://localhost:8000/docs) - Interactive API documentation- [ ] Batch processing

- [ ] Multi-language UI (Chinese)

## 🙏 Acknowledgements- [ ] Dark mode theme

- [ ] PDF report export

This project builds upon excellent open-source work:- [ ] Model ensemble mode

- [ ] C2PA provenance integration

- **AIDE Model**: [shilinyan99/AIDE](https://github.com/shilinyan99/AIDE) (ICLR 2025)

- **ConvNeXt**: [facebookresearch/ConvNeXt-V2](https://github.com/facebookresearch/ConvNeXt-V2)## 🤝 Contributing

- **OpenCLIP**: [mlfoundations/open_clip](https://github.com/mlfoundations/open_clip)

- **Grad-CAM**: [jacobgil/pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam)Contributions are welcome! Please:

- **Gemini**: [Google Generative AI](https://ai.google.dev/)

- **Gradio**: [gradio-app/gradio](https://github.com/gradio-app/gradio)1. Fork the repository

2. Create a feature branch

## 📄 License3. Commit your changes

4. Push to the branch

MIT License - see [LICENSE](LICENSE) file for details5. Open a Pull Request



## 📧 Contact## 📄 License



- **GitHub**: [thedannyliu/GAIC-Detector-Web-GUI](https://github.com/thedannyliu/GAIC-Detector-Web-GUI)MIT License - see LICENSE file for details

- **Issues**: [Create an issue](https://github.com/thedannyliu/GAIC-Detector-Web-GUI/issues)

- **AIDE Questions**: Contact [tattoo.ysl@gmail.com](mailto:tattoo.ysl@gmail.com)## 🙏 Acknowledgments



## 🌟 Citation- Taiwan FactCheck Center

- Model authors: SuSy, FatFormer, DistilDIRE teams

If you use this work, please cite the AIDE paper:- Gradio and FastAPI communities



```bibtex## 📧 Contact

@article{yan2024sanity,

  title={A Sanity Check for AI-generated Image Detection},For questions or issues:

  author={Yan, Shilin and Li, Ouxiang and Cai, Jiayin and Hao, Yanbin and Jiang, Xiaolong and Hu, Yao and Xie, Weidi},- GitHub Issues: https://github.com/thedannyliu/GAIC-Detector-Web-GUI/issues

  journal={arXiv preprint arXiv:2406.19435},- Email: contact@example.com

  year={2024}

}---

```

**Built with ❤️ for fighting AI-generated misinformation**

## 🎯 Roadmap

- [ ] Implement Grad-CAM for AIDE's multi-branch architecture
- [ ] Add batch processing support
- [ ] Support more video formats
- [ ] Add fine-tuning scripts
- [ ] Model quantization for faster inference
- [ ] Docker containerization

---

**Status**: ✅ Production Ready (PoC Level)  
**Version**: 2.0.0 - AIDE Edition  
**Updated**: November 16, 2025  
**Powered by**: AIDE (ICLR 2025) + Gemini + Gradio
