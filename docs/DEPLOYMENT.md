# GAIC Detector Deployment Guide

This document describes deployment for the **current codebase state** (AIDE-only backend + Gradio frontend).

## 1. Architecture at Runtime

Two long-running processes are expected:

1. FastAPI backend (default port `8000`)
2. Gradio frontend (default local URL around `7860`)

Frontend calls backend via `GAIC_BACKEND_URL`.

## 2. Prerequisites

- Python 3.10
- Conda environment with project dependencies
- AIDE checkpoint at:
  - `models/weights/GenImage_train.pth`
- Optional: `GEMINI_API_KEY` for LLM report generation

## 3. Quick Start (Local)

```bash
conda activate gaic-detector
bash start.sh
```

This launches backend + frontend and writes logs to:

- `logs/backend.log`
- `logs/frontend.log`

Stop services:

```bash
bash start.sh stop
```

## 4. Environment Variables

Template file: `.env.example`

Common variables:

- `API_HOST` (default `0.0.0.0`)
- `API_PORT` (default `8000`)
- `GAIC_BACKEND_URL` (default `http://localhost:${API_PORT}`)
- `GEMINI_API_KEY` (empty means template fallback reports)
- `GRADIO_SHARE`

Important process behavior:

- `submit_job.sh` loads `.env` automatically.
- `start.sh` does not source `.env` automatically.
- `start.sh` currently sets `GRADIO_SHARE=true` before launching frontend.

If you need `.env` values locally with `start.sh`:

```bash
set -a
source .env
set +a
bash start.sh
```

## 5. PACE Phoenix Deployment (Slurm)

Submit from login node:

```bash
sbatch submit_job.sh
```

What the script does:

1. Activates `gaic-detector` conda env
2. Loads `.env` if present
3. Verifies AIDE checkpoint exists
4. Runs `start.sh all`

Monitor logs:

```bash
tail -f logs/gaic_slurm_<jobid>.log
tail -f logs/backend.log
tail -f logs/frontend.log
```

Find public Gradio URL:

```bash
grep -i "public URL" logs/frontend.log
```

## 6. API/Media Limits (Source of Truth)

Configured in `app/config.py`:

- Images: 10 MB max
- Videos: 50 MB max
- Video duration: 300 seconds max
- Sampled frames per video: 16

If UI labels or external docs disagree with these values, treat `app/config.py` as authoritative.

## 7. Operational Checks

Health endpoint:

```bash
curl http://localhost:8000/
```

Models endpoint:

```bash
curl http://localhost:8000/models
```

API smoke test:

```bash
python test_api.py
```

## 8. Common Failure Modes

### 8.1 Missing checkpoint

Symptom: backend fails during first inference/model load.

Fix:

```bash
bash download_aide_weights.sh
```

Ensure file exists:

```bash
ls -lh models/weights/GenImage_train.pth
```

### 8.2 Frontend cannot reach backend

Symptom: frontend returns request/network errors.

Check:

- backend process is alive
- backend bound to expected host/port
- `GAIC_BACKEND_URL` visible in frontend process environment

### 8.3 Gemini errors or timeout

Behavior is non-fatal by design:

- backend falls back to template report
- `errors` array includes `REPORT_GEN_ERROR`

### 8.4 Port conflict

Use provided stop command first:

```bash
bash start.sh stop
```

Then restart.

## 9. Security Notes

- This repo is configured for research/demo usage by default.
- CORS currently allows all origins.
- Public Gradio sharing should be reviewed before production use.
- Do not commit `.env` or private API keys.

## 10. Production Hardening Checklist

- Restrict CORS origins
- Put backend behind authenticated gateway/reverse proxy
- Enforce HTTPS/TLS at edge
- Add request rate limiting and upload abuse protections
- Centralize logs and health probes
- Pin dependency versions for reproducible builds

