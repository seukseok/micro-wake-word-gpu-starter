# micro-wake-word-gpu-starter

[한국어](README.md) | English

Train and package custom ESPHome micro wake word models with an NVIDIA GPU.

![Actual trainer UI demo](docs/assets/trainer-ui-demo.gif)

This is a real capture from the running trainer UI. Open the [raw MP4 demo](https://raw.githubusercontent.com/seukseok/micro-wake-word-gpu-starter/main/docs/assets/trainer-ui-demo.mp4) if you want the video version.

## Choose Your Path

| Goal | Start Here |
| --- | --- |
| Try the candidate model only | Download `hey_komi.tflite` and `hey_komi.json` from the [v0.2.0 MVP release](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.2.0-mvp), then place them in your ESPHome model folder. |
| Run the GPU trainer | Start Docker Desktop, run `docker compose up -d`, then open `http://localhost:8789`. |
| Train your own wake word | Run `doctor.ps1`, check dataset readiness, run smoke training, validate the manifest, then export ESPHome YAML. |

See the [Setup and usage guide](docs/setup-and-usage.md) for the full walkthrough.

## Quick Start

Windows PowerShell:

```powershell
git clone https://github.com/seukseok/micro-wake-word-gpu-starter.git
cd micro-wake-word-gpu-starter
docker compose up -d
.\scripts\doctor.ps1
```

Open the trainer UI:

```text
http://localhost:8789
```

Check large trainer dataset readiness:

```powershell
.\scripts\prepare_training_datasets.ps1
```

Validate a generated model and print an ESPHome snippet:

```powershell
python scripts\validate_manifest.py workspace\trained_wake_words\hey_komi.json
python scripts\export_esphome.py workspace\trained_wake_words\hey_komi.json
```

Training outputs are created here by default:

```text
workspace/trained_wake_words/<wake_word>.tflite
workspace/trained_wake_words/<wake_word>.json
```

## Use The Candidate Model

Files you can try now:

```text
models/hey-komi-candidate/hey_komi.tflite
models/hey-komi-candidate/hey_komi.json
models/hey-komi-candidate/model-card.md
```

Download from releases:

- [micro-wake-word-gpu-starter v0.2.0 MVP](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.2.0-mvp)
- [Hey Komi v0.1.0 candidate](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.1.0-candidate)

Place the `.tflite` and `.json` files in the same ESPHome model folder, then use the path printed by the export script.

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

This is not a `hardware-validated` model yet. Treat it as a candidate until false wake and missed wake tests are completed on real ESP32-S3 microphone hardware.

## Train Your Own Model

1. Start the trainer with `docker compose up -d`.
2. Run `.\scripts\doctor.ps1` to check Docker, GPU, Torch, TensorFlow, UI, and dataset status.
3. Open `http://localhost:8789` and enter your wake phrase plus training settings.
4. Validate the generated `.tflite` and `.json` files.
5. Paste the `python scripts\export_esphome.py ...` output into your ESPHome config.

Short end-to-end training check:

```powershell
.\scripts\train_smoke.ps1 -WakeWord "hey komi" -WakeWordTitle "Hey Komi" -Samples 50 -BatchSize 10 -TrainingSteps 20
```

## Verified Environment

- NVIDIA GeForce RTX 5070 Ti
- Windows 11 + Docker Desktop
- Docker GPU passthrough verified
- Torch reports `cuda_available: true`
- TensorFlow sees `/physical_device:GPU:0`
- GitHub Actions CI passes

## Datasets

The dataset catalog is in [datasets/catalog.json](datasets/catalog.json).

```powershell
python scripts\show_datasets.py --recommended first
.\scripts\prepare_training_datasets.ps1
```

Representative sources:

- `kahrendt/microwakeword`: background/negative feature archives
- Google Speech Commands v0.02: spoken-word clips
- MLCommons Multilingual Spoken Words microset: multilingual spoken-word clips
- FSD50K: environmental hard negatives

## Future Plan

- Collect ESP32-S3 test reports
- Release a hardware-validated model
- Improve resumable large dataset download/extract/convert flows
- Add real hardware test video or a short demo MP4

## Related Docs

- [Setup and usage guide](docs/setup-and-usage.md)
- [Windows/WSL2/RTX guide](docs/windows-wsl2-rtx.md)
- [Dataset guide](docs/dataset-guide.md)
- [Model quality gates](docs/model-quality-gates.md)
- [Release demo assets](docs/release-demo-assets.md)
- [Release playbook](docs/release-playbook.md)
- [Hey Komi model card](models/hey-komi-candidate/model-card.md)

## License

MIT. Upstream projects keep their own licenses.
