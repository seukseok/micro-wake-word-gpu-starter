# micro-wake-word-gpu-starter

Train and package custom ESPHome micro wake word models with an NVIDIA GPU.

![Actual trainer UI demo](docs/assets/trainer-ui-demo.gif)

Actual capture from the running trainer UI at `http://localhost:8789`. For a normal video file, use the [raw MP4 recording](https://raw.githubusercontent.com/seukseok/micro-wake-word-gpu-starter/main/docs/assets/trainer-ui-demo.mp4) instead of opening the repository file view.

This starter is for Home Assistant and ESPHome users who want to build a local wake word model without turning the training setup into a weekend archaeology project. It gives you a Windows/WSL2 friendly Docker Compose setup, dataset checks, manifest validation, and ESPHome snippets for the files produced by the upstream microWakeWord training stack.

> Hardware note: you can prepare data, run GPU training, validate manifests, and generate ESPHome config without an ESP32-S3 device. Real false-positive tuning still needs device testing before you ship a model to other people.

## What this program is

This is a GPU training starter kit for ESPHome micro wake word models. It is not a new model architecture and it does not replace the upstream trainer. The value is the glue around the trainer: a reproducible Docker launch, GPU checks, dataset notes, smoke-training scripts, manifest validation, ESPHome export, and a real UI/video demo so people can tell what they are getting before they clone it.

## Why this exists

The useful pieces are already out there:

- [OHF-Voice/micro-wake-word](https://github.com/OHF-Voice/micro-wake-word) trains TensorFlow Lite Micro wake word models.
- [esphome/micro-wake-word-models](https://github.com/esphome/micro-wake-word-models) hosts ready-to-use model manifests.
- [TaterTotterson/microWakeWord-Trainer-Nvidia-Docker](https://github.com/TaterTotterson/microWakeWord-Trainer-Nvidia-Docker) wraps training in a CUDA Docker app.

This repo focuses on the missing "starter kit" layer: predictable folders, GPU launch commands, dataset validation, manifest checks, and copy-paste ESPHome output.

## Quick Start

Requirements:

- Windows 11 or Linux
- NVIDIA GPU with current drivers
- Docker Desktop with WSL2 integration, or Docker Engine on Linux
- Optional: `nvidia-smi` on the host for a quick GPU sanity check

Start the trainer UI:

```bash
docker compose up
```

Open:

```text
http://localhost:8789
```

The trainer stores generated samples, downloaded datasets, and trained model files under:

```text
workspace/
```

Expected final artifacts:

```text
workspace/trained_wake_words/<wake_word>.tflite
workspace/trained_wake_words/<wake_word>.json
```

Validate a trained model manifest:

```bash
python scripts/validate_manifest.py workspace/trained_wake_words/hey_komi.json
```

Generate an ESPHome snippet:

```bash
python scripts/export_esphome.py workspace/trained_wake_words/hey_komi.json
```

Check local WAV samples before training:

```bash
python scripts/prepare_dataset.py data/positive data/negative --manifest data/dataset_manifest.json
```

Run the full local smoke test on Windows/PowerShell:

```powershell
.\scripts\smoke_test.ps1
```

Check the training GPU stack after `/data/.venv` exists:

```powershell
.\scripts\check_trainer_gpu.ps1
```

Run a small end-to-end training smoke test after the trainer datasets are prepared:

```powershell
.\scripts\train_smoke.ps1 -WakeWord "hey komi" -WakeWordTitle "Hey Komi" -Samples 50 -BatchSize 10 -TrainingSteps 20
```

## Tested Hardware

This repo was smoke-tested on an NVIDIA GeForce RTX 5070 Ti with Docker Desktop on Windows 11.

Verified:

- Docker GPU passthrough with `nvidia/cuda:12.4.1-base-ubuntu22.04`
- trainer container starts from `docker compose up -d`
- trainer UI returns `HTTP 200` on `http://localhost:8789`
- Torch inside the trainer reports `cuda_available: true`
- warm restart reaches `HTTP 200` in 5.3 seconds after the first dependency install
- TensorFlow training sees `/physical_device:GPU:0` when the helper scripts set the venv NVIDIA library path

See [examples/rtx-5070-ti-smoke-test.md](examples/rtx-5070-ti-smoke-test.md) for the actual command outputs.

## Actual GPU Training Run

A real `hey komi` training smoke run was completed on the RTX 5070 Ti:

```text
Samples: 50 generated TTS wake-word clips
Training steps: 20
Trainer result: Training complete (GPU path)
Elapsed time: 0:04:53
Model artifact: workspace/output/2026-05-20-10-23-33-hey_komi-50-20/hey_komi.tflite
Manifest artifact: workspace/output/2026-05-20-10-23-33-hey_komi-50-20/hey_komi.json
```

The run used real public data for the path check: `kahrendt/microwakeword` negative archives, MIT RIR, and an AudioSet subset converted to 16 kHz WAV. The generated model validated and exported to ESPHome YAML, but it is not a useful production model: the tiny smoke run calibrated to `probability_cutoff=1.00` with `0.00%` recall on its tiny validation split.

See [examples/hey-komi-gpu-smoke-training.md](examples/hey-komi-gpu-smoke-training.md) for the exact results and limitations.

## Public Datasets

The dataset catalog is in [datasets/catalog.json](datasets/catalog.json), with notes in [datasets/README.md](datasets/README.md).

Recommended first-run sources:

- `kahrendt/microwakeword`: microWakeWord-native feature archives for background and negative data
- Google Speech Commands v0.02: CC-BY-4.0 one-word keyword spotting clips
- MLCommons Multilingual Spoken Words microset: CC-BY-4.0 multilingual spoken-word clips
- FSD50K: CC-BY-4.0 environmental sounds for hard negatives

Common Voice 25.0 is included as a cataloged source for diverse speech, but the repo does not re-host Common Voice audio because Mozilla Data Collective terms require downloading from the original source.

Inspect the catalog:

```bash
python scripts/show_datasets.py --recommended first
```

Create local staging folders for public samples:

```bash
python scripts/stage_dataset_dirs.py
```

For the upstream trainer's full augmentation path, expect tens of GB of local data under `workspace/training_datasets/`. The smoke run produced about 25 GB of negative archives plus extracted AudioSet/MIT RIR data before training.

## Folder Layout

```text
configs/
  trainer.env.example
  wake-word.example.json
data/
  positive/
  negative/
datasets/
  catalog.json
  sample_manifest.example.json
docs/
  dataset-guide.md
  release-playbook.md
  windows-wsl2-rtx.md
examples/
  hey-komi-gpu-smoke-training.md
  rtx-5070-ti-smoke-test.md
  hey-komi/
docs/assets/
  trainer-ui-demo.gif
  trainer-ui-demo.mp4
  trainer-ui-trainer.png
models/
  example_wake_word.json
scripts/
  check_trainer_gpu.ps1
  export_esphome.py
  prepare_dataset.py
  run_trainer.ps1
  show_datasets.py
  stage_dataset_dirs.py
  smoke_test.ps1
  train_smoke.ps1
  validate_manifest.py
workspace/
  personal_samples/
  negative_samples/
  trained_wake_words/
```

## Suggested Workflow

1. Pick a phrase that is short, uncommon, and easy to pronounce.
2. Put optional real positive samples in `data/positive/`.
3. Put hard negatives or false wake clips in `data/negative/`.
4. Run `prepare_dataset.py` to catch bad audio before training.
5. Start the trainer with `docker compose up`.
6. Prepare the upstream training datasets, or use a clearly marked smoke subset for path testing.
7. Run `check_trainer_gpu.ps1` and confirm Torch/TensorFlow see the NVIDIA GPU.
8. Train from the web UI or with `train_smoke.ps1`.
9. Validate the generated JSON manifest with `validate_manifest.py`.
10. Generate the ESPHome YAML snippet with `export_esphome.py`.
11. Ask hardware testers to report false wakes, misses, board, mic, and threshold settings.

## Sample ESPHome Output

For a manifest named `hey_komi.json`, the export script prints something like:

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
```

Copy the generated manifest and `.tflite` file into the same ESPHome-accessible folder.

## Wake Phrase Tips

Good phrases are:

- 2 to 4 syllables
- not common in normal conversation
- easy to say consistently
- not too close to "okay nabu", "alexa", "hey jarvis", or other enabled wake words

Examples to try:

- `hey komi`
- `okay local`
- `nabu start`
- Korean phrase experiment: `ha-i komi`

## What is intentionally not here

- No bundled model weights.
- No claim that the included smoke-training result is production-ready.
- No promise that any model is production-ready before hardware testing.
- No forked copy of upstream training code.

This repo should stay small, useful, and boring in the best way: the trainer can evolve upstream while this starter keeps the user journey clean.

## GitHub Topics

Recommended topics:

```text
home-assistant, esphome, esp32-s3, tinyml, edge-ai, wake-word, tensorflow-lite-micro, nvidia-gpu, cuda, docker
```

## License

MIT. Upstream projects keep their own licenses.
