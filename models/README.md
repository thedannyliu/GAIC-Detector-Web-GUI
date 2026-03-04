# Models Directory

This folder stores local model artifacts required by the GAIC Detector runtime.

## Current Expected Structure

```text
models/
├── weights/
│   └── GenImage_train.pth
└── README.md
```

## Active Model

The current backend implementation is **AIDE-only**.

- API model identifier: `AIDE`
- Required checkpoint: `models/weights/GenImage_train.pth`

## Downloading Weights

Run:

```bash
bash download_aide_weights.sh
```

Manual source:

- <https://drive.google.com/file/d/1ZJCJmzyIrbSOROS7bKTgSm-Fe6yHsVXz/view>

## Validation

Check file existence and size:

```bash
ls -lh models/weights/GenImage_train.pth
```

## Operational Notes

- Do not commit weight binaries to git.
- Keep this directory writable by the runtime user.
- On shared systems, verify free disk space before downloading.

## Troubleshooting

### Missing model file

Symptoms:

- backend inference fails
- startup/inference logs mention missing checkpoint path

Fix:

1. Re-run `bash download_aide_weights.sh`
2. Confirm path and permissions
3. Restart backend process

### Slow first inference

Expected behavior for large checkpoints.
Warm-up requests or preloading model on service start can reduce first-request latency.

