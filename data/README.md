# Local Data Staging

Put local audio samples here after downloading them from the original public dataset sources.

Tracked files in this folder are only placeholders and instructions. Audio files are ignored by git.

Recommended layout:

```text
positive/
  your_wake_phrase_001.wav
negative/
  speech_commands/
  mswc/
  fsd50k/
  local_false_wakes/
```

Validate staged files:

```bash
python scripts/prepare_dataset.py data/positive data/negative --manifest data/dataset_manifest.json --allow-empty
```

See [../datasets/catalog.json](../datasets/catalog.json) for source dataset links and license notes.
