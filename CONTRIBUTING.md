# Contributing

Thanks for helping make custom ESPHome wake word training less mysterious.

## Good first contributions

- Add a board-specific ESPHome snippet.
- Improve Windows, WSL2, CUDA, or Docker notes.
- Share a hardware test report with false wake and missed wake observations.
- Add examples for non-English wake phrases.
- Improve validation scripts without adding heavyweight dependencies.

## Hardware test reports

Please include:

- board name
- microphone
- speaker, if relevant
- room type
- wake phrase
- model manifest settings
- false wakes per hour, if measured
- missed wakes out of at least 20 attempts

## Development

Run the local checks:

```bash
python scripts/validate_manifest.py models/example_wake_word.json --allow-missing-model
python scripts/export_esphome.py models/example_wake_word.json
python scripts/prepare_dataset.py data/positive data/negative --manifest data/dataset_manifest.json --allow-empty
python -m unittest discover -s tests
```

On Windows with an NVIDIA GPU, run the end-to-end smoke test:

```powershell
.\scripts\smoke_test.ps1
```

Keep scripts dependency-free unless a dependency removes a lot of real complexity.

## README translations

Keep [README.md](README.md) and [README.en.md](README.en.md) in sync. If a change affects user-facing README content, update both the Korean and English versions in the same commit.
