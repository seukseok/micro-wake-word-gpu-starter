import tempfile
import unittest
from pathlib import Path

from scripts.export_esphome import build_snippet
from scripts.prepare_dataset import summarize
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


class DatasetTests(unittest.TestCase):
    def test_manifest_folder_paths_use_forward_slashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "positive"
            folder.mkdir()
            summary = summarize("positive", folder)
        self.assertNotIn("\\", summary["folder"])


if __name__ == "__main__":
    unittest.main()
