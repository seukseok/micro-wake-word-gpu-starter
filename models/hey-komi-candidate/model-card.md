# Hey Komi Candidate Model

Status: candidate, not hardware-validated

This folder contains a trained ESPHome micro wake word candidate for the phrase `Hey Komi`.

It is a real trained model, but it should not be described as production-stable until it is tested on ESP32-S3 microphone hardware in normal rooms.

Quality gates are documented in [../../docs/model-quality-gates.md](../../docs/model-quality-gates.md).

## Files

```text
hey_komi.json
hey_komi.tflite
```

## Training Run

| Item | Value |
| --- | --- |
| Date | 2026-05-20 |
| GPU | NVIDIA GeForce RTX 5070 Ti |
| Driver | 591.86 |
| Trainer | TaterTotterson/microWakeWord-Trainer-Nvidia-Docker |
| Wake phrase | Hey Komi |
| Language | en |
| Generated samples | 5,000 |
| Batch size | 100 |
| Training steps | 5,000 |
| CPU fallback | false |
| Total elapsed | 0:21:31 |
| Model size | 64,904 bytes |

## Local Data Used

The run used locally downloaded/generated data under `workspace/`:

- 5,000 generated wake-word clips from the upstream Piper sample generator
- `kahrendt/microwakeword` negative feature archives
- MIT RIR converted to 270 16 kHz WAV files
- AudioSet balanced training audio converted to 10,080 16 kHz WAV files
- FMA small conversion produced 7,994 usable 16 kHz WAV files from 8,000 MP3 tracks; the local `fma_16k` folder also contained 40 earlier smoke placeholders
- Small WHAM/CHiME smoke placeholders were still present, so this is not a full-background release

Dataset notes:

- AudioSet examples point to YouTube segments; do not redistribute AudioSet source audio. The AudioSet ontology is published under CC BY-SA 4.0.
- FMA small is 8,000 tracks of 30s audio. FMA metadata is CC BY 4.0, while the audio is distributed under licenses chosen by the artists.
- Keep dataset attribution visible when publishing model cards or release notes.

References:

- AudioSet: https://research.google.com/audioset/
- AudioSet ontology: https://github.com/audioset/ontology
- FMA dataset: https://github.com/mdeff/fma

## Validation Metrics

From the training log:

```text
Step 3500 validation:
  recall at no faph = 94.040
  cutoff = 0.82
  estimated false positives/hour = 0.10341
  auc = 0.99689

Step 5000 validation:
  recall at no faph = 85.120
  cutoff = 0.99
  estimated false positives/hour = 5.79082
  auc = 0.99757

TFLite streaming test:
  cutoff 0.89 -> frr=0.0520, faph=0.000
  cutoff 0.84 -> frr=0.0500, faph=0.187
  cutoff 0.74 -> frr=0.0380, faph=0.375
```

Calibration selected:

```text
probability_cutoff = 0.34
sliding_window_size = 3
recall = 97.70%
ambient_faph = 0.724
```

## ESPHome Snippet

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

## Known Limitations

- No ESP32-S3 microphone validation yet.
- No real human positive recordings were used.
- No hard-negative false-wake clips from real homes were used.
- WHAM and CHiME were not fully prepared for this candidate run.
- Treat the model as a release candidate for testers, not a stable public wake word.
