#!/bin/bash
# GAIC Detector – PACE Phoenix Slurm Job Submission Script
#
# This script allocates a GPU node via Slurm and then starts the GAIC Detector
# services (FastAPI backend + Gradio frontend) on that node.
#
# Usage (from the PACE Phoenix login node):
#   chmod +x submit_job.sh
#   ./submit_job.sh
#
# After submission the script will print:
#   1. The Slurm job ID
#   2. An SSH tunnel command to run on your LOCAL machine for browser access
#
# Requirements:
#   - Conda environment "gaic-detector" must exist (see README for setup)
#   - AIDE model weights must be present at models/weights/GenImage_train.pth
#   - GEMINI_API_KEY set in .env (optional, for AI-generated reports)

# ── Slurm resource configuration ─────────────────────────────
#SBATCH --job-name=gaic-detector
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=4:00:00
#SBATCH --output=logs/gaic_slurm_%j.log
#SBATCH --error=logs/gaic_slurm_%j.log
# Adjust --partition and --account as needed for your cluster allocation
# #SBATCH --partition=gpu
# #SBATCH --account=<your-account>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================"
echo "  GAIC Detector – PACE Phoenix Job"
echo "  Job ID   : ${SLURM_JOB_ID:-interactive}"
echo "  Node     : $(hostname)"
echo "  Started  : $(date)"
echo "================================================================"
echo ""

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate gaic-detector

# Load .env if present
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "[INFO] Loaded .env"
fi

# Verify model weights exist
WEIGHTS="$SCRIPT_DIR/models/weights/GenImage_train.pth"
if [ ! -f "$WEIGHTS" ]; then
    echo "[ERROR] AIDE model weights not found: $WEIGHTS"
    echo "        Run: bash download_aide_weights.sh"
    exit 1
fi

# Start all services
bash "$SCRIPT_DIR/start.sh" all

# Print Web Access instructions
echo ""
echo "================================================================"
echo "  Accessing the Web GUI"
echo "================================================================"
echo ""
echo "  The Gradio frontend is starting. A public share link will be generated."
echo "  Check the output in logs/frontend.log for the 'Public URL'."
echo ""
echo "    cat logs/frontend.log"
echo ""
echo "================================================================"

# Keep job running while services are alive
wait
