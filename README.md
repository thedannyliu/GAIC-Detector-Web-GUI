# GAIC Detector Web GUI

[![Python](https://img.shields.io/badge/python-3.10-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)
[![AIDE](https://img.shields.io/badge/AIDE-ICLR%202025-red)](https://arxiv.org/abs/2406.19435)

GAIC Detector is a web application for AI-generated image/video screening.
The current implementation uses a single detector: **AIDE** (ICLR 2025), with Grad-CAM overlays and optional Gemini-generated narrative reports.

## Current Scope

- Backend: FastAPI (`app/main.py`)
- Frontend: Gradio (`gradio_app.py`)
- Model: AIDE only (`models/weights/GenImage_train.pth`)
- Media types:
  - Image: `jpg`, `jpeg`, `png`, `webp` (max 10 MB)
  - Video: `mp4`, `mov`, `webm` (max 50 MB, max 300 seconds)

## Repository Layout

```text
GAIC-Detector-Web-GUI/
├── app/
│   ├── main.py                # API endpoints
│   ├── aide_inference.py      # AIDE wrapper + Grad-CAM generation
│   ├── aide_original/         # Vendored AIDE implementation
│   ├── config.py              # Runtime settings and limits
│   ├── errors.py              # Error codes and HTTP mapping
│   ├── image_utils.py         # Image decode/preprocess/overlay helpers
│   ├── video_utils.py         # Video frame sampling helpers
│   └── report.py              # Gemini + template fallback reports
├── docs/
│   ├── DEPLOYMENT.md
│   └── MODEL_SOURCES.md
├── models/
│   └── README.md
├── gradio_app.py
├── start.sh
├── submit_job.sh
├── download_aide_weights.sh
├── requirements.txt
└── .env.example
```

## Requirements

- Python 3.10
- Linux/macOS (Linux recommended for GPU workloads)
- NVIDIA GPU + CUDA for practical throughput (CPU mode works but is slow)
- 8 GB+ RAM
- 4 GB+ free disk for model weights and temp files

## Installation

1. Clone repository

```bash
git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git
cd GAIC-Detector-Web-GUI
```

2. Create environment

```bash
conda create -n gaic-detector python=3.10 -y
conda activate gaic-detector
```

3. Install PyTorch (match your CUDA version)

```bash
# Example: CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

4. Install remaining dependencies

```bash
pip install -r requirements.txt
```

5. Download AIDE checkpoint

```bash
bash download_aide_weights.sh
```

Expected path:

```text
models/weights/GenImage_train.pth
```

## Environment Configuration

Create `.env` from template:

```bash
cp .env.example .env
```

Common variables:

- `GEMINI_API_KEY`: enables Gemini reports when set
- `API_HOST`, `API_PORT`: FastAPI bind host/port
- `GAIC_BACKEND_URL`: frontend target backend URL
- `GRADIO_SHARE`: Gradio share mode flag

Important behavior:

- `submit_job.sh` **does** load `.env` automatically.
- `start.sh` **does not** load `.env` automatically.
- `start.sh` currently exports `GRADIO_SHARE=true` when launching frontend.

If you need custom env vars for local runs via `start.sh`, preload them in shell:

```bash
set -a
source .env
set +a
bash start.sh
```

## Run Locally

Start both services:

```bash
bash start.sh
```

Or start separately:

```bash
bash start.sh backend
bash start.sh frontend
```

Stop services:

```bash
bash start.sh stop
```

## Run on PACE Phoenix

Batch mode (recommended on cluster login node):

```bash
sbatch submit_job.sh
```

Then inspect logs:

```bash
tail -f logs/gaic_slurm_<jobid>.log
tail -f logs/frontend.log
```

To print the public Gradio URL:

```bash
grep -i "public URL" logs/frontend.log
```

## API Summary

Swagger docs:

- `http://localhost:8000/docs`

Endpoints:

- `GET /`: health check
- `GET /models`: model metadata (AIDE only)
- `POST /analyze/image`
- `POST /analyze/video`

Image response fields include:

- `score` (0-100)
- `model`
- `heatmap_png_b64` (optional)
- `report_md`
- `inference_ms`
- `errors` (non-fatal issues/fallback markers)

Video response adds:

- `key_frame_index`
- `key_frame_ts`
- `key_frame_png_b64`

Video score policy:

- Sample multiple frames uniformly.
- Analyze each sampled frame.
- Use the **maximum frame score** as video-level score.

## Testing

Backend smoke test (backend must already be running):

```bash
python test_api.py
```

## Known Documentation Notes

- This repository is now AIDE-only. Any mention of SuSy/FatFormer/DistilDIRE in older materials should be considered historical.
- UI labels and backend file-size limits may diverge in some releases; backend limits in `app/config.py` are the source of truth.

## Disclaimer

This system is experimental and non-diagnostic.
Detection scores should not be treated as conclusive evidence of authenticity.

## Acknowledgements

- [AIDE](https://github.com/shilinyan99/AIDE)
- [OpenCLIP](https://github.com/mlfoundations/open_clip)
- [pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam)
- [Gradio](https://github.com/gradio-app/gradio)
- [FastAPI](https://fastapi.tiangolo.com/)

## License

MIT License. See `LICENSE`.
