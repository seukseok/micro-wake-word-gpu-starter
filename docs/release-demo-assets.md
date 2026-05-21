# Release Demo Assets

The repo already includes a real trainer UI GIF and MP4:

- `docs/assets/trainer-ui-demo.gif`
- `docs/assets/trainer-ui-demo.mp4`

Use these result checks in release notes and screenshots so a visitor can quickly see that the project is real:

## Manifest Validation

```bash
python scripts/validate_manifest.py models/hey-komi-candidate/hey_komi.json
```

Expected result:

```text
OK: Hey Komi (models/hey-komi-candidate/hey_komi.json)
```

## ESPHome Export

```bash
python scripts/export_esphome.py models/hey-komi-candidate/hey_komi.json
```

Expected snippet:

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

## Release Assets

The public prerelease should attach:

```text
hey_komi.tflite
hey_komi.json
```

Link the model card from the release body and clearly label the model as `candidate` until hardware reports are available.
