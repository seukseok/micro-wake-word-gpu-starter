# RTX 5070 Ti Smoke Test

Date: 2026-05-19

This is a real smoke test from the initial development machine for this starter.

## Host

| Item | Value |
| --- | --- |
| OS | Microsoft Windows 11 Pro 10.0.26200 |
| GPU | NVIDIA GeForce RTX 5070 Ti |
| Driver | 591.86 |
| VRAM | 16303 MiB |
| Docker | Docker version 29.0.1 |
| Docker Compose | v2.40.3-desktop.1 |

## Docker GPU passthrough

Command:

```powershell
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
```

Output:

```text
NVIDIA GeForce RTX 5070 Ti, 591.86, 16303 MiB
```

## Trainer image

Image:

```text
ghcr.io/tatertotterson/microwakeword:latest
```

Digest observed during this test:

```text
sha256:e26b24a968e15f9683494c9bb255544e32fd3ff0d86204b6cfbb8eee4be73a41
```

## Trainer UI

Command:

```powershell
docker compose up -d
```

Container state:

```text
micro-wake-word-gpu-starter   ghcr.io/tatertotterson/microwakeword:latest   Up   0.0.0.0:8789->8789/tcp
```

HTTP check:

```text
GET http://localhost:8789 -> HTTP 200
```

First boot note:

```text
The first run created /data/.recorder-venv and installed the trainer UI dependencies, including Torch/CUDA packages. On this machine the first UI-ready boot took roughly 15-20 minutes. A warm restart reached HTTP 200 in 5.3 seconds.
```

Warm restart check:

```text
warm_restart_http_200_seconds=5.3
```

## Torch CUDA check inside trainer container

Command:

```bash
docker exec micro-wake-word-gpu-starter bash -lc "source /data/.recorder-venv/bin/activate && python - <<'PY'
import json
import torch
print(json.dumps({
    'torch': torch.__version__,
    'cuda_available': torch.cuda.is_available(),
    'cuda_device_count': torch.cuda.device_count(),
    'cuda_device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
}, indent=2))
PY"
```

Output:

```json
{
  "torch": "2.12.0+cu130",
  "cuda_available": true,
  "cuda_device_count": 1,
  "cuda_device_name": "NVIDIA GeForce RTX 5070 Ti"
}
```

## Local script checks

```text
python scripts/validate_manifest.py models/example_wake_word.json --allow-missing-model
OK: Hey Komi (models/example_wake_word.json)

python scripts/export_esphome.py models/example_wake_word.json
micro_wake_word:
  models:
    - model: /config/esphome/models/example_wake_word.json
      id: hey_komi_wake_word

python -m unittest discover -s tests
Ran 4 tests
OK
```

## Not covered by this smoke test

- Full wake-word training run
- ESP32-S3 flashing
- Real microphone false-positive tuning
- Hardware wake/miss measurements

Those need real samples and device testers.

For the later end-to-end GPU training smoke run, see [hey-komi-gpu-smoke-training.md](hey-komi-gpu-smoke-training.md).
