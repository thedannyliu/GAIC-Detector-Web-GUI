# Model Sources and Provenance

This repository currently serves one detector in production code:

- **AIDE** (AI-generated Image DEtector with Hybrid Features)

Older references to other detector families are historical and are not part of the active API path.

## 1. Active Model in This Codebase

- Model name exposed by API: `AIDE`
- Backend source wrapper: `app/aide_inference.py`
- Vendored architecture code: `app/aide_original/AIDE.py`
- Expected checkpoint path: `models/weights/GenImage_train.pth`

## 2. Required Weight File

### 2.1 Primary checkpoint

- Filename: `GenImage_train.pth`
- Size: approximately 3.6 GB
- Placement: `models/weights/`

### 2.2 Download

Use the bundled script:

```bash
bash download_aide_weights.sh
```

Or download manually from:

- <https://drive.google.com/file/d/1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz/view>

Then place the file at:

```text
models/weights/GenImage_train.pth
```

## 3. Upstream References

- AIDE paper (arXiv): <https://arxiv.org/abs/2406.19435>
- AIDE repository: <https://github.com/shilinyan99/AIDE>

## 4. Runtime Model Construction Notes

The integrated AIDE stack has two major branches:

1. Noise/artifact branch (SRM high-pass + ResNet)
2. Semantic branch (ConvNeXt via OpenCLIP)

Implementation details to be aware of:

- `app/aide_original/AIDE.py` may attempt to initialize ConvNeXt pretrained weights via OpenCLIP defaults when explicit paths are not supplied.
- First model load can be slow due to checkpoint initialization and large model footprint.

## 5. Verification Checklist

After placing weights, verify quickly:

1. Start backend (`bash start.sh backend` or `uvicorn app.main:app ...`)
2. Check health endpoint (`GET /`)
3. Run one image inference (`POST /analyze/image`)
4. Confirm response includes `model: "AIDE"`

## 6. Model Governance Notes

- Do not commit large binary weights to git history.
- Keep source/version metadata in release notes when rotating checkpoints.
- If checkpoint source changes, update:
  - `download_aide_weights.sh`
  - `README.md`
  - this document

