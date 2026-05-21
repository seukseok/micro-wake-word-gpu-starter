# micro-wake-word-gpu-starter

[한국어](README.md) | English

Train and package custom ESPHome micro wake word models with an NVIDIA GPU.

![Actual trainer UI demo](docs/assets/trainer-ui-demo.gif)

This is a real capture from the running trainer UI. Open the [raw MP4 demo](https://raw.githubusercontent.com/seukseok/micro-wake-word-gpu-starter/main/docs/assets/trainer-ui-demo.mp4) if you want the video version.

## What Can It Do?

- Run the NVIDIA GPU-backed microWakeWord trainer UI with Docker Compose.
- Validate generated `.tflite` models and ESPHome `.json` manifests.
- Help with public dataset staging, GPU checks, and ESPHome YAML export scripts.
- Provide a real RTX 5070 Ti-trained `Hey Komi` candidate model with a model card.

## Quick Start

Requirements:

- Windows 11 or Linux
- NVIDIA GPU with current drivers
- Docker Desktop with WSL2 integration, or Docker Engine on Linux

Start the trainer:

```bash
docker compose up
```

Open:

```text
http://localhost:8789
```

Training outputs are created here by default:

```text
workspace/trained_wake_words/<wake_word>.tflite
workspace/trained_wake_words/<wake_word>.json
```

Validate a manifest and generate an ESPHome snippet:

```bash
python scripts/validate_manifest.py workspace/trained_wake_words/hey_komi.json
python scripts/export_esphome.py workspace/trained_wake_words/hey_komi.json
```

Check the GPU training environment:

```powershell
.\scripts\check_trainer_gpu.ps1
.\scripts\doctor.ps1
```

## Candidate Model

The `Hey Komi` candidate model was trained on a real RTX 5070 Ti GPU.

```text
models/hey-komi-candidate/hey_komi.tflite
models/hey-komi-candidate/hey_komi.json
models/hey-komi-candidate/model-card.md
```

Download: [Hey Komi v0.1.0 candidate](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.1.0-candidate)

```text
Samples: 5,000 generated wake-word clips
Training steps: 5,000
Trainer result: Training complete (GPU path)
CPU fallback: false
Elapsed time: 0:21:31
Calibration: cutoff=0.34, window=3, recall=97.70%, ambient_faph=0.724
TFLite streaming test: cutoff=0.89 -> frr=0.0520, faph=0.000
```

This is not a `hardware-validated` model yet. Stable release needs ESP32-S3 microphone testing for false wakes and missed wakes.

## Verified Environment

- NVIDIA GeForce RTX 5070 Ti
- Windows 11 + Docker Desktop
- Docker GPU passthrough verified
- Torch reports `cuda_available: true`
- TensorFlow sees `/physical_device:GPU:0`
- GitHub Actions CI passes

The small end-to-end GPU smoke run is documented in [examples/hey-komi-gpu-smoke-training.md](examples/hey-komi-gpu-smoke-training.md).

## Datasets

The dataset catalog is in [datasets/catalog.json](datasets/catalog.json). See [datasets/README.md](datasets/README.md) and [docs/dataset-guide.md](docs/dataset-guide.md) for details.

Representative sources:

- `kahrendt/microwakeword`: background/negative feature archives
- Google Speech Commands v0.02: spoken-word clips
- MLCommons Multilingual Spoken Words microset: multilingual spoken-word clips
- FSD50K: environmental hard negatives

Inspect the catalog:

```bash
python scripts/show_datasets.py --recommended first
```

Check large trainer dataset readiness:

```powershell
.\scripts\prepare_training_datasets.ps1
```

## Future Plan

- ESP32-S3 test reports: collect board, microphone, room, threshold, false wake, and missed wake data
- Hardware-validated model release: collect at least one real microphone test report
- Improved resumable dataset prep: make large download/extract/convert jobs restartable
- More release demo assets: add real hardware test video or a short demo MP4

The full roadmap is in [docs/product-roadmap.md](docs/product-roadmap.md).

## Related Docs

- [Windows/WSL2/RTX guide](docs/windows-wsl2-rtx.md)
- [Dataset guide](docs/dataset-guide.md)
- [Model quality gates](docs/model-quality-gates.md)
- [Release demo assets](docs/release-demo-assets.md)
- [Release playbook](docs/release-playbook.md)
- [Hey Komi model card](models/hey-komi-candidate/model-card.md)
- [RTX 5070 Ti smoke test](examples/rtx-5070-ti-smoke-test.md)

## License

MIT. Upstream projects keep their own licenses.
