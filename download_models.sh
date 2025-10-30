#!/bin/bash
# GAIC Detector - Model Download Script (weights only)
# Models: SuSy (HF), FatFormer (Google Drive), DistilDIRE (HF)

set -euo pipefail

MODELS_DIR="models/weights"
mkdir -p "$MODELS_DIR"

echo "📦 GAIC Detector Model Download Script"
echo "========================================"

# -------- helpers --------
need_cmd() { command -v "$1" >/dev/null 2>&1; }
hash_ok() { # hash_ok <file> <sha256>
  local f="$1"; local want="$2"
  if [ -z "$want" ]; then return 0; fi
  if ! need_cmd sha256sum; then
    echo "ℹ️  sha256sum not found; skipping checksum for $f"
    return 0
  fi
  local got
  got="$(sha256sum "$f" | awk '{print $1}')"
  if [ "$got" != "$want" ]; then
    echo "❌ Checksum mismatch for $f"
    echo "    got:  $got"
    echo "    want: $want"
    return 1
  fi
  return 0
}

download_wget_or_curl() { # download_wget_or_curl <url> <outfile>
  local url="$1"; local out="$2"
  if need_cmd wget; then
    wget -O "$out" "$url" --progress=bar:force 2>&1
  elif need_cmd curl; then
    curl -L -o "$out" "$url" --progress-bar
  else
    echo "❌ Neither wget nor curl found."; exit 1
  fi
}

download_hf() { # download_hf <url_resolve> <outfile> <sha256 or empty>
  local url="$1"; local out="$2"; local sha="$3"
  echo "📥 Downloading (HF): $(basename "$out")"
  download_wget_or_curl "$url" "$out"
  if ! hash_ok "$out" "$sha"; then
    echo "   → Retrying once..."
    rm -f "$out"
    download_wget_or_curl "$url" "$out"
    hash_ok "$out" "$sha"
  fi
  echo "✅ Saved: $out ($(du -h "$out" | cut -f1))"
}

download_gdrive() { # download_gdrive <file_id> <outfile>
  local fid="$1"; local out="$2"
  echo "📥 Downloading (Google Drive): $(basename "$out")"
  if need_cmd gdown; then
    gdown --no-cookies --fuzzy "https://drive.google.com/uc?id=${fid}" -O "$out"
  else
    echo "ℹ️  gdown not found. Attempting pip install to a temp venv..."
    python3 - <<'PY'
import sys, subprocess, venv, pathlib
p=pathlib.Path(".dlvenv"); venv.EnvBuilder(with_pip=True).create(p)
pip=str(p/("Scripts/pip.exe" if sys.platform=="win32" else "bin/pip"))
subprocess.check_call([pip, "install", "gdown"])
print(str(p))
PY
    VENV_PATH="$(python3 - <<'PY'
import sys, pathlib
p=pathlib.Path(".dlvenv")
print(str(p/("Scripts" if sys.platform=="win32" else "bin")))
PY
)"
    "${VENV_PATH}/gdown" --no-cookies --fuzzy "https://drive.google.com/uc?id=${fid}" -O "$out"
  fi
  echo "✅ Saved: $out ($(du -h "$out" | cut -f1))"
}

# -------- model URLs / IDs / checksums --------
# 1) SuSy (HPAI-BSC) — TorchScript .pt
SUSY_URL="https://huggingface.co/HPAI-BSC/SuSy/resolve/main/SuSy.pt"   # HF direct "resolve" URL
SUSY_OUT="${MODELS_DIR}/susy.pt"
# (HF 未提供官方 SHA；若你想固定版本，可改 pin commit：/resolve/<commit>/SuSy.pt)
SUSY_SHA=""

# 2) FatFormer (CVPR 2024) — Google Drive checkpoint (4-class)
# Model Zoo 提供 GDrive：file id below
FATFORMER_FILE_ID="1Q_Kgq4ygDf8XEHgAf-SgDN6Ru_IOTLkj"
FATFORMER_OUT="${MODELS_DIR}/fatformer_4class_ckpt.pth"
FATFORMER_SHA=""  # 官方未提供 SHA

# 3) DistilDIRE — Hugging Face (ImageNet 224x224 checkpoint)
DISTILDIRE_URL="https://huggingface.co/yevvonlim/distildire/resolve/main/imagenet-distil-dire-11e.pth"
DISTILDIRE_OUT="${MODELS_DIR}/distildire-imagenet-11e.pth"
# HF 顯示的是 pointer 的 SHA，非檔本體；這裡先不校驗
DISTILDIRE_SHA=""

echo "Models will be saved to: $MODELS_DIR"
echo

# -------- skip existing prompt --------
found_any=0
for f in "$SUSY_OUT" "$FATFORMER_OUT" "$DISTILDIRE_OUT"; do
  if [ -f "$f" ]; then
    echo "✓ Found: $(basename "$f")"
    found_any=1
  fi
done
if [ "$found_any" -eq 1 ]; then
  echo
  read -p "Some weights exist. Re-download them? (y/N) " -n 1 -r; echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Keeping existing files. Done."; exit 0
  fi
fi
echo

# -------- downloads --------
download_hf "$SUSY_URL" "$SUSY_OUT" "$SUSY_SHA"
download_gdrive "$FATFORMER_FILE_ID" "$FATFORMER_OUT"
download_hf "$DISTILDIRE_URL" "$DISTILDIRE_OUT" "$DISTILDIRE_SHA"

echo
echo "========================================"
echo "📋 Model Download Summary"
echo "========================================"
for f in "$SUSY_OUT" "$FATFORMER_OUT" "$DISTILDIRE_OUT"; do
  if [ -f "$f" ]; then
    size=$(du -h "$f" | cut -f1)
    echo "✅ $(basename "$f") ($size)"
  else
    echo "❌ $(basename "$f") (not found)"
  fi
done

echo
echo "💡 Notes:"
echo " - SuSy and DistilDIRE use Hugging Face resolve URLs; consider pinning to a specific commit for reproducibility."
echo " - FatFormer uses Google Drive; script supports gdown automatically."
echo " - Place files under $MODELS_DIR; adapters expect these default names."
