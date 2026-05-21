# Model Quality Gates

Use honest release labels so testers know what a model can and cannot prove.

## Labels

| Label | Meaning | Minimum evidence |
| --- | --- | --- |
| `smoke` | The software path works. | Training completes, manifest validates, ESPHome export works. |
| `candidate` | The model is useful enough for testers. | GPU training completes without CPU fallback, validation metrics are reported, release assets include `.tflite`, `.json`, and a model card. |
| `hardware-validated` | The model has at least one real device report. | Candidate evidence plus ESP32-S3 microphone test data with false wakes and missed wakes. |

## Candidate Gate

A candidate release must include:

- wake phrase, language, sample count, training steps, GPU, and trainer source
- CPU fallback status
- validation recall and false accepts/hour
- calibrated `probability_cutoff` and `sliding_window_size`
- manifest validation result
- ESPHome snippet
- known limitations
- dataset source notes

## Hardware-Validated Gate

Do not mark a model as `hardware-validated` until at least one tester reports:

- board and microphone
- room type and noise source, if relevant
- model version and manifest settings
- false wakes per hour or total listening time
- missed wakes out of at least 20 attempts
- distance from microphone

## Current Status

`Hey Komi v0.1.0 candidate` is a real GPU-trained candidate model. It is not stable or hardware-validated yet because no ESP32-S3 microphone report has been collected.
