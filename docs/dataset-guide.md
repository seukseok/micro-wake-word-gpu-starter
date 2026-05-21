# Dataset Guide

You can train with generated samples only, but real samples help a lot once you have hardware testers.

For public dataset sources, see [../datasets/catalog.json](../datasets/catalog.json). The catalog was last reviewed on 2026-05-19 and includes microWakeWord-native features, keyword spotting datasets, diverse speech corpora, and environmental sound datasets.

Inspect the recommended first-run dataset stack:

```bash
python scripts/show_datasets.py --recommended first
```

Check the local trainer dataset folders:

```powershell
.\scripts\prepare_training_datasets.ps1
```

The status script does not download large archives by itself. It shows which `workspace/training_datasets/` folders are ready, partial, or missing so you can resume preparation without guessing.

## Positive samples

Positive samples contain the wake phrase.

Recommended:

- WAV
- 16 kHz
- mono
- 16-bit PCM
- 0.8 to 2.0 seconds
- one wake phrase per file

Put them in:

```text
data/positive/
```

## Negative samples

Negative samples are clips that should not trigger the wake word.

Useful negatives:

- words that sound similar to the wake phrase
- normal household speech
- TV or podcast snippets
- real false wake clips from testers
- mic noise from the target room

Put them in:

```text
data/negative/
```

## Validate before training

```bash
python scripts/prepare_dataset.py data/positive data/negative --manifest data/dataset_manifest.json
```

This checks WAV format and writes a small JSON manifest with counts and durations.

## Convert files with ffmpeg

```bash
ffmpeg -i input.mp3 -ac 1 -ar 16000 -sample_fmt s16 output.wav
```

For a folder, convert carefully into a new directory so you do not overwrite originals.

## Naming convention

Use simple filenames:

```text
positive/hey_komi_001.wav
positive/hey_komi_002.wav
negative/tv_speech_001.wav
negative/false_wake_001.wav
```

Avoid spaces and non-ASCII characters in filenames when possible.
