import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.export_esphome import build_snippet
from scripts.prepare_dataset import summarize
from scripts.show_datasets import load_catalog, select_datasets
from scripts.stage_dataset_dirs import FOLDERS
from scripts.validate_manifest import validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class ManifestValidationTests(unittest.TestCase):
    def test_example_manifest_is_valid_without_model_file(self):
        errors = validate_manifest(
            ROOT / "models" / "example_wake_word.json",
            allow_missing_model=True,
        )
        self.assertEqual(errors, [])

    def test_missing_model_is_reported_by_default(self):
        errors = validate_manifest(ROOT / "models" / "example_wake_word.json")
        self.assertIn(
            "model file does not exist next to manifest: example_wake_word.tflite",
            errors,
        )

    def test_probability_cutoff_allows_calibrated_one(self):
        data = {
            "type": "micro",
            "wake_word": "Hey Komi",
            "model": "hey_komi.tflite",
            "trained_languages": ["en"],
            "version": 2,
            "micro": {
                "probability_cutoff": 1.0,
                "feature_step_size": 10,
                "sliding_window_size": 5,
                "tensor_arena_size": 30000,
            },
        }
        with patch("scripts.validate_manifest.load_json", return_value=data):
            self.assertEqual(validate_manifest(Path("hey_komi.json"), True), [])


class ExportTests(unittest.TestCase):
    def test_export_snippet_uses_default_model_path(self):
        snippet = build_snippet(ROOT / "models" / "example_wake_word.json", None)
        self.assertIn("/config/esphome/models/example_wake_word.json", snippet)
        self.assertIn("id: hey_komi_wake_word", snippet)

    def test_export_snippet_accepts_custom_model_path(self):
        snippet = build_snippet(
            ROOT / "models" / "example_wake_word.json",
            "github://owner/repo/models/hey_komi.json",
        )
        self.assertIn("github://owner/repo/models/hey_komi.json", snippet)

    def test_candidate_manifest_and_export_are_valid(self):
        manifest = ROOT / "models" / "hey-komi-candidate" / "hey_komi.json"
        self.assertEqual(validate_manifest(manifest), [])
        snippet = build_snippet(manifest, None)
        self.assertIn("/config/esphome/models/hey_komi.json", snippet)
        self.assertIn("id: hey_komi_wake_word", snippet)


class DatasetTests(unittest.TestCase):
    def test_manifest_folder_paths_use_forward_slashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "positive"
            folder.mkdir()
            summary = summarize("positive", folder)
        self.assertNotIn("\\", summary["folder"])

    def test_dataset_catalog_has_first_run_sources(self):
        catalog = load_catalog()
        selected = select_datasets(catalog, "first")
        ids = {item["id"] for item in selected}
        self.assertIn("kahrendt_microwakeword_features", ids)
        self.assertIn("google_speech_commands_v0_02", ids)
        self.assertIn("fsd50k", ids)
        self.assertGreaterEqual(len(selected), 4)

    def test_staging_folders_are_declared(self):
        suffixes = {folder.as_posix().split("data/")[-1] for folder in FOLDERS}
        self.assertIn("positive", suffixes)
        self.assertIn("negative/speech_commands", suffixes)
        self.assertIn("negative/fsd50k", suffixes)


class MvpReadinessTests(unittest.TestCase):
    def test_mvp_scripts_are_present(self):
        doctor = ROOT / "scripts" / "doctor.ps1"
        datasets = ROOT / "scripts" / "prepare_training_datasets.ps1"
        self.assertTrue(doctor.exists())
        self.assertTrue(datasets.exists())
        self.assertIn("tensorflow gpu", doctor.read_text(encoding="utf-8"))
        self.assertIn("negative_datasets", datasets.read_text(encoding="utf-8"))

    def test_model_quality_docs_are_linked(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_en = (ROOT / "README.en.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs" / "product-roadmap.md").read_text(encoding="utf-8")
        self.assertIn("docs/model-quality-gates.md", readme)
        self.assertIn("docs/model-quality-gates.md", readme_en)
        self.assertIn("model-quality-gates.md", roadmap)

    def test_setup_usage_guide_is_linked(self):
        guide = ROOT / "docs" / "setup-and-usage.md"
        guide_ko = ROOT / "docs" / "setup-and-usage.ko.md"
        self.assertTrue(guide.exists())
        self.assertTrue(guide_ko.exists())
        guide_text = guide.read_text(encoding="utf-8")
        guide_ko_text = guide_ko.read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_en = (ROOT / "README.en.md").read_text(encoding="utf-8")
        self.assertIn("docs/setup-and-usage.ko.md", readme)
        self.assertIn("docs/setup-and-usage.md", readme_en)
        self.assertIn("docker compose up -d", guide_text)
        self.assertIn("doctor.ps1", guide_text)
        self.assertIn("docker compose up -d", guide_ko_text)
        self.assertIn("doctor.ps1", guide_ko_text)

    def test_issue_templates_collect_required_hardware_fields(self):
        templates = {
            "false-wake-report.yml": [
                "model_version",
                "board",
                "microphone",
                "false_wakes_per_hour",
                "manifest_settings",
            ],
            "missed-wake-report.yml": [
                "model_version",
                "board",
                "microphone",
                "attempts",
                "missed_wakes",
                "manifest_settings",
            ],
            "successful-hardware-test.yml": [
                "model_version",
                "board",
                "microphone",
                "attempts",
                "false_wakes_per_hour",
                "missed_wakes",
            ],
            "install-dataset-problem.yml": [
                "problem_area",
                "os",
                "command",
                "output",
                "doctor_output",
            ],
        }

        template_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
        for filename, fields in templates.items():
            text = (template_dir / filename).read_text(encoding="utf-8")
            for field in fields:
                self.assertIn(f"id: {field}", text)


if __name__ == "__main__":
    unittest.main()
