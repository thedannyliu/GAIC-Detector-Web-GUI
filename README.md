# GAIC Detector Web GUI

[![Python](https://img.shields.io/badge/python-3.10-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)
[![AIDE](https://img.shields.io/badge/AIDE-ICLR%202025-red)](https://arxiv.org/abs/2406.19435)

A web-based AI-Generated Image & Video detection system powered by the **AIDE** model (ICLR 2025), **Grad-CAM** visual explanations, and **Gemini**-generated analysis reports. Designed to run on GPU compute nodes on the **Georgia Tech PACE Phoenix** HPC cluster, with SSH tunnel access from a local browser.

---

## Features

| Feature | Details |
|---|---|
| **AIDE Detection** | State-of-the-art AI-generated image detector (ICLR 2025) |
| **Grad-CAM Heatmaps** | Visual overlay showing suspicious regions |
| **Gemini Reports** | AI-generated natural language analysis |
| **Image & Video** | JPG/PNG/WEBP (≤ 10 MB) and MP4/MOV/WEBM (≤ 50 MB) |
| **Session History** | Last 5 analyses tracked in-browser |
| **REST API** | FastAPI backend with interactive Swagger docs |

---

## Architecture

```
GAIC-Detector-Web-GUI/
├── app/                       # FastAPI backend
│   ├── main.py                # API endpoints (/analyze/image, /analyze/video)
│   ├── aide_inference.py      # AIDE model wrapper + Grad-CAM
│   ├── aide_original/         # Official AIDE source (AIDE.py, srm_filter_kernel.py)
│   ├── config.py              # All configuration constants
│   ├── errors.py              # Custom error codes + HTTP exceptions
│   ├── image_utils.py         # Image I/O, preprocessing, heatmap overlay
│   ├── video_utils.py         # Video frame sampling
│   └── report.py              # Gemini report generation
├── gradio_app.py              # Gradio web frontend
├── models/
│   └── weights/               # AIDE checkpoint (downloaded separately)
├── docs/
│   ├── DEPLOYMENT.md          # Deployment notes
│   └── MODEL_SOURCES.md       # Where to get model weights
├── test_samples/              # Sample images for testing
├── start.sh                   # Service launcher (run on compute node)
├── submit_job.sh              # Slurm job submission script
├── download_aide_weights.sh   # Download AIDE checkpoint from Google Drive
├── requirements.txt
├── .env.example
└── test_api.py / test_system.py
```

**AIDE Architecture**:
- **Noise branch**: SRM High-Pass Filter → ResNet-50 (detects low-level artifacts)
- **Semantic branch**: ConvNeXt-XXL via OpenCLIP (detects semantic inconsistencies)
- **Fusion**: MLP (2048 + 256 → 1024 → 2 classes)

---

## Requirements

- Python 3.10
- Conda
- NVIDIA GPU with CUDA (recommended; CPU mode also works)
- 8 GB+ RAM (model is ~3.6 GB)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git
cd GAIC-Detector-Web-GUI
```

### 2. Create the conda environment

```bash
conda create -n gaic-detector python=3.10 -y
conda activate gaic-detector
```

### 3. Install PyTorch (GPU)

Follow [pytorch.org](https://pytorch.org/get-started/locally/) to install the version matching your CUDA driver. Example for CUDA 12.1:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 4. Install remaining dependencies

```bash
pip install -r requirements.txt
```

### 5. Download the AIDE model weights

The AIDE checkpoint (`GenImage_train.pth`, ~3.6 GB) is hosted on Google Drive.

```bash
bash download_aide_weights.sh
```

> The script installs `gdown` automatically if needed and saves the file to `models/weights/GenImage_train.pth`. You can also download it manually from:  
> <https://drive.google.com/file/d/1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz/view>

### 6. Configure environment (optional)

```bash
cp .env.example .env
nano .env   # Add your GEMINI_API_KEY for AI reports
```

---

## Running on PACE Phoenix (Recommended)

PACE Phoenix is a Slurm-managed HPC cluster. Since the login node has no compute resources, you must submit a job to a GPU node.

### Option A – Interactive session (for development)

```bash
# 1. On the login node: request a GPU node
salloc --gres=gpu:1 --mem=32G --cpus-per-task=4 -t 4:00:00

# 2. On the allocated compute node:
conda activate gaic-detector
bash start.sh
```

### Option B – Batch submission

```bash
# On the login node:
sbatch submit_job.sh
```

`submit_job.sh` requests GPU resources and automatically starts all services. Check `gaic_slurm_<jobid>.log` for the SSH tunnel command.

### Accessing the UI via SSH tunnel

Once the services are running on the compute node, forward ports to your **local machine**:

```bash
# Run this on YOUR LOCAL machine (replace USERNAME and COMPUTE-NODE):
ssh -N \
  -L 7860:localhost:7860 \
  -L 8000:localhost:8000 \
  -J USERNAME@login-phoenix.pace.gatech.edu \
  USERNAME@COMPUTE-NODE
```

Then open **<http://localhost:7860>** in your browser.

> **Tip**: `start.sh` prints the exact SSH command (with your actual username and node hostname) after the services are up.

---

## Running Locally (non-cluster)

```bash
conda activate gaic-detector
bash start.sh          # starts backend + frontend
# or separately:
bash start.sh backend  # http://localhost:8000
bash start.sh frontend # http://localhost:7860

bash start.sh stop     # stop all services
```

---

## API Reference

FastAPI interactive docs available at **<http://localhost:8000/docs>**.

### `GET /`
Health check.

### `GET /models`
List available models.

### `POST /analyze/image`

| Field | Type | Description |
|---|---|---|
| `file` | multipart | JPG / PNG / WEBP, ≤ 10 MB |
| `include_heatmap` | bool | Generate Grad-CAM overlay (default: `true`) |

**Response:**
```json
{
  "score": 85,
  "model": "AIDE",
  "heatmap_png_b64": "<base64>",
  "report_md": "## Analysis...",
  "inference_ms": 420,
  "errors": []
}
```

### `POST /analyze/video`

| Field | Type | Description |
|---|---|---|
| `file` | multipart | MP4 / MOV / WEBM, ≤ 50 MB |
| `include_heatmap` | bool | Grad-CAM on key frame (default: `true`) |

**Response** includes `key_frame_index`, `key_frame_ts`, `key_frame_png_b64`, plus the same fields as image analysis.

### Error codes

| Code | HTTP | Meaning |
|---|---|---|
| `IMG_FORMAT_UNSUPPORTED` | 400 | Not JPG/PNG/WEBP |
| `IMG_TOO_LARGE` | 400 | Exceeds 10 MB |
| `IMG_DECODE_FAILED` | 400 | Corrupt image |
| `VIDEO_TOO_LARGE` | 400 | Exceeds 50 MB |
| `MODEL_NOT_FOUND` | 400 | Weights file missing |
| `MODEL_TIMEOUT` | 504 | Inference > 120 s |
| `MODEL_ERROR` | 500 | Model raised exception |
| `HEATMAP_ERROR` | 500 | Grad-CAM failed |
| `REPORT_GEN_ERROR` | 500 | Gemini call failed |

---

## Configuration

Key constants live in `app/config.py`. The most commonly changed settings can be overridden via `.env`:

| `.env` key | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(empty)* | Google Gemini API key |
| `API_HOST` | `0.0.0.0` | Backend bind address |
| `API_PORT` | `8000` | Backend port |
| `GAIC_BACKEND_URL` | `http://localhost:8000` | Frontend → backend URL |
| `GRADIO_SHARE` | `false` | Enable Gradio public share link |

---

## Testing

```bash
conda activate gaic-detector

# Import / system checks (no GPU required)
python test_system.py

# API tests (requires running backend)
python test_api.py
```

---

## Disclaimer

> **This tool is experimental and non-diagnostic.** Scores should not be used as the sole basis for determining content authenticity. For critical applications, consult forensic experts and use multiple verification methods.

---

## Acknowledgements

- **[AIDE](https://github.com/shilinyan99/AIDE)** – Shilin Yan et al., ICLR 2025
- **[OpenCLIP](https://github.com/mlfoundations/open_clip)** – ConvNeXt-XXL backbone
- **[pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam)** – Grad-CAM library
- **[Gradio](https://github.com/gradio-app/gradio)** – Web UI framework
- **[FastAPI](https://fastapi.tiangolo.com/)** – Backend API framework

## Citation

If you use this work, please cite the AIDE paper:

```bibtex
@article{yan2024sanity,
  title   = {A Sanity Check for AI-generated Image Detection},
  author  = {Yan, Shilin and Li, Ouxiang and Cai, Jiayin and Hao, Yanbin and
             Jiang, Xiaolong and Hu, Yao and Xie, Weidi},
  journal = {arXiv preprint arXiv:2406.19435},
  year    = {2024}
}
```

## License

MIT License – see [LICENSE](LICENSE) for details.
