# micro-wake-word-gpu-starter

Train and package custom ESPHome micro wake word models with an NVIDIA GPU.

![Actual trainer UI demo](docs/assets/trainer-ui-demo.gif)

Actual capture from the running trainer UI at `http://localhost:8789`. For a normal video file, use the [raw MP4 recording](https://raw.githubusercontent.com/seukseok/micro-wake-word-gpu-starter/main/docs/assets/trainer-ui-demo.mp4) instead of opening the repository file view.

This starter is for Home Assistant and ESPHome users who want to build a local wake word model without turning the training setup into a weekend archaeology project. It gives you a Windows/WSL2 friendly Docker Compose setup, dataset checks, manifest validation, and ESPHome snippets for the files produced by the upstream microWakeWord training stack.

> Hardware note: you can prepare data, run GPU training, validate manifests, and generate ESPHome config without an ESP32-S3 device. Real false-positive tuning still needs device testing before you ship a model to other people.

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

## Tested Hardware

This repo was smoke-tested on an NVIDIA GeForce RTX 5070 Ti with Docker Desktop on Windows 11.

Verified:

- Docker GPU passthrough with `nvidia/cuda:12.4.1-base-ubuntu22.04`
- trainer container starts from `docker compose up -d`
- trainer UI returns `HTTP 200` on `http://localhost:8789`
- Torch inside the trainer reports `cuda_available: true`
- warm restart reaches `HTTP 200` in 5.3 seconds after the first dependency install

See [examples/rtx-5070-ti-smoke-test.md](examples/rtx-5070-ti-smoke-test.md) for the actual command outputs.

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
  rtx-5070-ti-smoke-test.md
  hey-komi/
docs/assets/
  trainer-ui-demo.gif
  trainer-ui-demo.mp4
  trainer-ui-trainer.png
models/
  example_wake_word.json
scripts/
  export_esphome.py
  prepare_dataset.py
  run_trainer.ps1
  show_datasets.py
  stage_dataset_dirs.py
  smoke_test.ps1
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
6. Train from the web UI.
7. Validate the generated JSON manifest with `validate_manifest.py`.
8. Generate the ESPHome YAML snippet with `export_esphome.py`.
9. Ask hardware testers to report false wakes, misses, board, mic, and threshold settings.

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
- No promise that a model is production-ready before hardware testing.
- No forked copy of upstream training code.

This repo should stay small, useful, and boring in the best way: the trainer can evolve upstream while this starter keeps the user journey clean.

## GitHub Topics

Recommended topics:

```text
home-assistant, esphome, esp32-s3, tinyml, edge-ai, wake-word, tensorflow-lite-micro, nvidia-gpu, cuda, docker
```

## License

MIT. Upstream projects keep their own licenses.
