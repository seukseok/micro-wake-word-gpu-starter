# Hey Komi GPU Smoke Training

Date: 2026-05-20

This is a real end-to-end training smoke run on the initial development machine. It proves that the trainer can generate samples, augment them, train through TensorFlow on the GPU path, export a quantized TFLite model, and validate the ESPHome manifest.

This is not a production-quality wake word model. The run used only 50 generated samples and 20 training steps, so the detector calibration selected a conservative cutoff with 0% recall on the tiny validation set.

## Hardware

| Item | Value |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5070 Ti |
| Driver | 591.86 |
| VRAM | 16303 MiB |
| GPU compute capability | 12.0 |
| Docker | Docker Desktop 4.53.0 / Engine 29.0.1 |

## GPU Checks

`scripts/check_trainer_gpu.ps1` reported:

```json
{
  "torch": "2.9.1+cu129",
  "cuda_available": true,
  "device_count": 1,
  "device": "NVIDIA GeForce RTX 5070 Ti"
}
```

```json
{
  "tensorflow": "2.21.0",
  "gpus": [
    "/physical_device:GPU:0"
  ]
}
```

During training, `nvidia-smi` showed up to about 12.5 GiB of GPU memory in use. TensorFlow also emitted the expected Blackwell warning that compute capability 12.0 kernels may be JIT-compiled from PTX on first use.

## Data Used

The smoke run used real public data, but only as a small path-validation subset:

- `kahrendt/microwakeword` negative feature archives: `dinner_party`, `dinner_party_eval`, `no_speech`, `speech`
- MIT RIR: 270 impulse response WAV files normalized to 16 kHz
- AudioSet balanced training FLACs: 10,000 files extracted locally; 80 files converted to 16 kHz WAV for smoke backgrounds
- The trainer-required `fma_16k`, `wham_16k`, and `chime_16k` folders were populated with 40 converted public AudioSet WAV files each for this smoke run only

For a publishable model, run the full upstream dataset setup and train with more samples and more steps.

## Command

```powershell
.\scripts\train_smoke.ps1 -WakeWord "hey komi" -WakeWordTitle "Hey Komi" -Samples 50 -BatchSize 10 -TrainingSteps 20
```

Equivalent command inside the container:

```bash
train_wake_word --data-dir=/data --samples=50 --batch-size=10 --training-steps=20 "hey komi" "Hey Komi"
```

`tensorboard` was installed into `/data/.venv` because the current upstream runtime calls `tf.summary.scalar` during training.

## Result

Final artifacts:

```text
workspace/output/2026-05-20-10-23-33-hey_komi-50-20/hey_komi.tflite
workspace/output/2026-05-20-10-23-33-hey_komi-50-20/hey_komi.json
workspace/output/2026-05-20-10-23-33-hey_komi-50-20/logs/training.log
```

Copied for ESPHome-style local validation:

```text
workspace/trained_wake_words/hey_komi.tflite
workspace/trained_wake_words/hey_komi.json
```

Artifact sizes:

```text
hey_komi.tflite  64,904 bytes
hey_komi.json       481 bytes
training.log     55,794 bytes
```

Training summary:

```text
Generated samples: 50
Training steps: 20
Total elapsed time: 0:04:53
Training log marker: Training complete (GPU path)
TFLite AUC on tiny test split: 1.00000
Calibration selected: probability_cutoff=1.00, sliding_window_size=5
Calibration recall on tiny validation split: 0.00%
Ambient false accepts/hour on tiny validation split: 0.000
```

Validation:

```text
python scripts/validate_manifest.py workspace/trained_wake_words/hey_komi.json
OK: Hey Komi (workspace\trained_wake_words\hey_komi.json)

python scripts/export_esphome.py workspace/trained_wake_words/hey_komi.json
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

## Important Limitations

- The run proves the software path, not model quality.
- `probability_cutoff=1.00` and `recall=0.00%` are signs that 50 samples and 20 steps are too small for a useful release.
- No ESP32-S3 microphone test was run.
- The generated `.tflite` and runtime datasets are intentionally ignored by Git.
