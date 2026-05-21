# Product Roadmap

This project is useful when it helps a Home Assistant or ESPHome user go from "I want a custom wake word" to "I have a tested model and a clear ESPHome config" without guessing through CUDA, datasets, and manifest details.

## Current State

Working today:

- Docker Compose starts the upstream NVIDIA trainer UI.
- RTX 5070 Ti GPU passthrough is verified.
- Torch and TensorFlow GPU checks are scripted.
- `scripts/doctor.ps1` checks Docker, GPU, trainer UI, trainer venv, TensorFlow, Torch, and dataset folders.
- `scripts/prepare_training_datasets.ps1` summarizes local large-dataset readiness.
- The repo has a real trainer UI video/GIF, not a mocked demo.
- A small end-to-end `hey komi` GPU smoke training run completed and produced `.tflite` plus `.json` artifacts.
- A larger `Hey Komi` candidate model is published with a model card under `models/hey-komi-candidate/`.
- Manifest validation and ESPHome YAML export work against the generated model metadata.

Not production-ready yet:

- The smoke-trained model is too small for real use.
- No ESP32-S3 microphone false-wake/miss testing has been run.
- Dataset setup is still too manual and can be slow or brittle for large public archives.
- The repo does not yet publish a hardware-validated model.

## Improvements For Real Users

### 1. One-command training readiness

Users need a command that checks Docker, NVIDIA passthrough, trainer UI, `/data/.venv`, TensorFlow GPU visibility, and required dataset folders before they start a long training run.

Target:

```powershell
.\scripts\doctor.ps1
```

Status: implemented for the MVP. Keep improving fix hints as tester reports arrive.

### 2. Resumable dataset preparation

Large public datasets should be downloaded, extracted, converted, and counted in a resumable way. The current upstream scripts work, but a product-grade starter should wrap them with progress logs, partial-file detection, disk estimates, and a "continue where I left off" path.

Target folders:

```text
workspace/training_datasets/negative_datasets/
workspace/training_datasets/mit_rirs_16k/
workspace/training_datasets/audioset_16k/
workspace/training_datasets/fma_16k/
workspace/training_datasets/wham_16k/
workspace/training_datasets/chime_16k/
```

### 3. Model quality gates

A public model should not be called stable just because training finished. It should pass documented gates.

Release gates are documented in [model-quality-gates.md](model-quality-gates.md). Minimum signals:

- training run completes on GPU without fallback
- manifest validates
- generated ESPHome YAML validates structurally
- validation recall is reported
- false accepts/hour is reported
- at least one hardware tester reports board, microphone, room type, threshold, false wakes, and misses
- release notes clearly say whether the model is `smoke`, `candidate`, or `hardware-validated`

### 4. Model card per release

Each published model should include a short model card:

```text
models/<wake_word>/
  model-card.md
  <wake_word>.json
  <wake_word>.tflite
```

The model card should list phrase, language, dataset sources, sample count, training steps, GPU, known limitations, validation metrics, and hardware test status.

### 5. Real demo assets

Keep the current UI video, but add release-result assets:

- screenshot of generated model artifacts
- screenshot of `validate_manifest.py`
- screenshot or terminal capture of ESPHome YAML export
- optional short MP4 showing the trainer UI plus final artifact folder

The release-result command snippets are documented in [release-demo-assets.md](release-demo-assets.md).

### 6. Hardware feedback loop

The most valuable contribution from other users will be hardware test reports. Add issue templates for:

- false wake report
- missed wake report
- successful hardware test
- dataset or install problem

### 7. Safer release naming

Use release labels honestly:

- `smoke`: proves the software path only
- `candidate`: trained with larger settings and public datasets, but not hardware validated
- `hardware-validated`: tested on at least one ESP32-S3 microphone setup

## Immediate Next Step

Recruit ESP32-S3 microphone testers for the `Hey Komi` candidate and collect false-wake/miss reports before calling any model stable.
