# Dataset Catalog

This folder lists public datasets that are useful for custom wake word work.

The repository intentionally does **not** vendor public audio clips. Audio datasets are large, licensing terms differ, and some providers allow local download but forbid re-hosting. The catalog gives you sources, roles, license notes, and practical recommendations.

## Recommended Stack

For this starter:

1. Use `kahrendt_microwakeword_features` for microWakeWord-native background and negative features.
2. Use your own recorded wake phrase clips for real positives.
3. Use `google_speech_commands_v0_02` or `mlcommons_multilingual_spoken_words_microset` for keyword spotting sanity checks and extra non-wake speech.
4. Use `fsd50k` for environmental hard negatives.
5. Treat `microsoft_dns_challenge_5` as an advanced augmentation source because it is very large.

## Inspect the Catalog

```bash
python scripts/show_datasets.py
```

Show only recommended first-run sources:

```bash
python scripts/show_datasets.py --recommended first
```

Write a local planning manifest:

```bash
python scripts/show_datasets.py --write-plan data/dataset_plan.json
```

## Local Sample Staging

The example sample manifest at [sample_manifest.example.json](sample_manifest.example.json) shows where to place local files after you download them from the original sources.

Expected local layout:

```text
data/
  positive/
    your_wake_phrase_001.wav
  negative/
    speech_commands/
    mswc/
    fsd50k/
    local_false_wakes/
```

Create the folders:

```bash
python scripts/stage_dataset_dirs.py
```

Run:

```bash
python scripts/prepare_dataset.py data/positive data/negative --manifest data/dataset_manifest.json --allow-empty
```

## License Notes

- Google Speech Commands is tagged as `CC-BY-4.0` on Hugging Face.
- MLCommons Multilingual Spoken Words is `CC-BY-4.0`; do not try to identify speakers.
- Mozilla Common Voice 25.0 scripted datasets are generally `CC0-1.0`, but Mozilla Data Collective terms say not to re-host or re-share Common Voice audio and not to identify speakers. Verify each language datasheet.
- FSD50K is `CC-BY-4.0` at the dataset level, and you should keep the attribution/license files with downloaded clips.
- DNS Challenge bundles multiple source datasets with mixed terms; inspect before using beyond local experiments.
