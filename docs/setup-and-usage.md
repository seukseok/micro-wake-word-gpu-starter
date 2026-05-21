# Setup and Usage Guide

[한국어](setup-and-usage.ko.md) | English

This guide shows the practical path from a fresh clone to a validated ESPHome micro wake word artifact.

## 1. Prepare the machine

Recommended setup:

- Windows 11
- NVIDIA GPU with a current driver
- Docker Desktop with WSL2 integration enabled
- Python 3.11 or newer on the host for helper scripts

Check the host GPU:

```powershell
nvidia-smi
```

Check Docker GPU access:

```powershell
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

Linux users can run the same Docker commands from a shell. Use `/` path separators in Python commands.

## 2. Start the trainer UI

Clone and start the trainer:

```powershell
git clone https://github.com/seukseok/micro-wake-word-gpu-starter.git
cd micro-wake-word-gpu-starter
docker compose up -d
```

Open:

```text
http://localhost:8789
```

The first boot can take a while because the upstream trainer prepares Python environments under `workspace/`.

## 3. Check the current environment

Run the doctor:

```powershell
.\scripts\doctor.ps1
```

The doctor checks:

- Docker CLI and daemon
- `compose.yaml`
- trainer container
- NVIDIA passthrough
- trainer virtual environment
- Torch CUDA
- TensorFlow GPU
- trainer UI
- large trainer dataset folders

If a row fails, follow the fix hint printed below the table.

## 4. Use the candidate model in ESPHome

Download these files from the [v0.2.0 MVP release](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.2.0-mvp):

```text
hey_komi.tflite
hey_komi.json
```

Put both files in the same ESPHome-accessible folder, for example:

```text
/config/esphome/models/
```

Use this ESPHome shape:

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

Important: `Hey Komi` is a candidate model. It is not hardware-validated until real ESP32-S3 microphone reports are collected.

## 5. Train your own wake word

Check dataset readiness:

```powershell
.\scripts\prepare_training_datasets.ps1
```

Open the trainer UI and enter your wake phrase. The trainer writes outputs under:

```text
workspace/trained_wake_words/
```

For a tiny end-to-end path test:

```powershell
.\scripts\train_smoke.ps1 -WakeWord "hey komi" -WakeWordTitle "Hey Komi" -Samples 50 -BatchSize 10 -TrainingSteps 20
```

Smoke training proves the pipeline works. It does not create a production model.

## 6. Validate generated artifacts

Validate the manifest:

```powershell
python scripts\validate_manifest.py workspace\trained_wake_words\hey_komi.json
```

Export an ESPHome snippet:

```powershell
python scripts\export_esphome.py workspace\trained_wake_words\hey_komi.json
```

Expected shape:

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

Copy the generated `.json` and `.tflite` files into the same ESPHome model folder.

## 7. Troubleshooting

If Docker is not reachable:

```powershell
docker info
```

Start Docker Desktop and rerun `.\scripts\doctor.ps1`.

If the trainer UI does not open:

```powershell
docker compose logs trainer
```

If TensorFlow or Torch cannot see the GPU:

```powershell
.\scripts\check_trainer_gpu.ps1
```

If datasets look incomplete:

```powershell
.\scripts\prepare_training_datasets.ps1
```

If a trained model does not validate, check that the `.json` and `.tflite` files are in the same folder and that the `model` field in the JSON matches the `.tflite` filename.

## What to report

For real hardware tests, open an issue and include:

- board
- microphone
- room type
- model version
- `probability_cutoff` and `sliding_window_size`
- false wakes per hour
- missed wakes out of at least 20 attempts
