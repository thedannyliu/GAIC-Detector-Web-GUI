#!/bin/bash
# Simple backend starter for debugging

cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI

# Activate conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector

# Start backend
echo "Starting backend on port 8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
