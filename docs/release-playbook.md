# Release Playbook

The first 10 stars usually come from a repo that solves one specific problem clearly.

## Day 1

- Publish the repo.
- Add a screenshot of the trainer UI when available.
- Verify the scripts on a clean machine or GitHub Actions.
- Run `.\scripts\doctor.ps1` on the main NVIDIA workstation.
- Add GitHub topics:

```text
home-assistant, esphome, esp32-s3, tinyml, edge-ai, wake-word, tensorflow-lite-micro, nvidia-gpu, cuda, docker
```

## Day 2

- Train one toy phrase end to end.
- Add the command output from `validate_manifest.py`.
- Add a small table with GPU, driver, training status, and notes.
- Confirm the current model label against [model-quality-gates.md](model-quality-gates.md).

## Day 3

Post a short, practical note:

```text
I made a small NVIDIA GPU starter for training ESPHome micro wake word models.
It does not require ESP32 hardware to prepare and validate artifacts, but I am looking for hardware testers for false-positive tuning.
```

Good places:

- Home Assistant community forum
- ESPHome Discord or forum
- Reddit `r/homeassistant`
- Reddit `r/esp32`
- GitHub Discussions in related projects, only if relevant

## Day 4 to 7

- Add one board-specific ESPHome snippet from a tester.
- Turn repeated questions into docs.
- Keep issues small and friendly.
- Label tester reports with `hardware-test`.
- Use the issue templates for false wake, missed wake, successful hardware test, and install/dataset problems.

## Star hooks

Make these visible in the README:

- Works without ESP32 hardware for the training prep stage.
- Windows/WSL2/RTX path is documented.
- Outputs ESPHome-ready JSON and YAML snippets.
- The project is small enough to understand in 10 minutes.

## v0.2.0 MVP release checklist

- `scripts/doctor.ps1` runs on the NVIDIA workstation.
- `scripts/prepare_training_datasets.ps1` reports dataset readiness.
- Candidate manifest validates and ESPHome export works.
- Issue templates are present for tester feedback.
- Release notes clearly say `candidate`, not stable or hardware-validated.
