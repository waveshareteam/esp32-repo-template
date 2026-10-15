from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import CI, FIXTURES, PRODUCT_REPO_ENV, SKELETON, TEMPLATE, product_repo

import product_config  # noqa: E402

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency
    jsonschema = None


SCHEMA = json.loads((TEMPLATE / "schema/product.schema.json").read_text(encoding="utf-8"))
VALID = json.loads((FIXTURES / "product.json").read_text(encoding="utf-8"))


def _invalid_documents() -> dict[str, dict]:
    def changed(**updates: object) -> dict:
        document = copy.deepcopy(VALID)
        document.update(updates)
        return document

    without_frameworks = {k: v for k, v in VALID.items() if k not in ("esp_idf", "arduino")}
    return {
        "unknown key": changed(board="x"),
        "missing product": {k: v for k, v in VALID.items() if k != "product"},
        "tier out of range": changed(tier=3),
        "bad target": changed(target="stm32"),
        "bad idf tag": changed(esp_idf={"versions": ["5.5.5"]}),
        "empty idf versions": changed(esp_idf={"versions": []}),
        "bad arduino core": changed(arduino={"core": "latest", "fqbn": VALID["arduino"]["fqbn"]}),
        "short fqbn": changed(arduino={"core": "3.3.11", "fqbn": "esp32s3"}),
        "no framework": without_frameworks,
        "unknown override": changed(overrides={"build": {}}),
        "relative product url": changed(product_url="www.waveshare.com"),
        "factory firmware as a link": changed(factory_firmware="https://example.com/releases"),
        "bad factory idf tag": changed(factory_firmware={"esp_idf": "5.5.5"}),
    }


class ProductConfigTests(unittest.TestCase):
    def test_fixture_is_valid(self) -> None:
        self.assertEqual(product_config.validate(copy.deepcopy(VALID)), VALID)

    def test_invalid_documents_are_rejected(self) -> None:
        for label, document in _invalid_documents().items():
            with self.subTest(label), self.assertRaises(product_config.ProductConfigError):
                product_config.validate(document)

    @unittest.skipUnless(jsonschema, "jsonschema is not installed")
    def test_schema_agrees_with_the_builtin_validator(self) -> None:
        validator = jsonschema.Draft7Validator(SCHEMA)
        jsonschema.Draft7Validator.check_schema(SCHEMA)
        self.assertEqual(list(validator.iter_errors(VALID)), [])
        for label, document in _invalid_documents().items():
            with self.subTest(label):
                self.assertTrue(list(validator.iter_errors(document)), "schema accepted it")

    def test_skeleton_lists_every_schema_field(self) -> None:
        skeleton = json.loads((SKELETON / ".github/product.json").read_text(encoding="utf-8"))
        expected = set(SCHEMA["properties"]) - {"overrides"}
        self.assertEqual(set(skeleton), expected)
        self.assertEqual(skeleton["$schema"], SCHEMA["$id"])

    def test_overrides_extend_lists_and_replace_scalars(self) -> None:
        merged = product_config.merge_overrides(
            {"patterns": ["a", "b"], "mode": "x", "other": [1]},
            {"patterns": ["b", "c"], "mode": "y", "new": ["z"]},
        )
        self.assertEqual(merged, {
            "patterns": ["a", "b", "c"], "mode": "y", "other": [1], "new": ["z"],
        })

    def test_defaults_load_with_and_without_overrides(self) -> None:
        plain = product_config.load_defaults("ci_routing", VALID)
        self.assertIn(".github/**", plain["global_build_patterns"])
        product = copy.deepcopy(VALID)
        product["overrides"] = {"markdown_audit": {"exclude_patterns": ["vendor/**"]}}
        audit = product_config.load_defaults("markdown_audit", product)
        self.assertEqual(audit["exclude_patterns"], ["vendor/**"])

    def test_cli_exports_the_workflow_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "github-output.txt"
            completed = subprocess.run(
                [
                    sys.executable, str(CI / "product_config.py"),
                    "--product", str(FIXTURES / "product.json"),
                    "--github-output", str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            values = dict(
                line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines()
            )
        self.assertEqual(values["product"], VALID["product"])
        self.assertEqual(values["target"], VALID["target"])
        self.assertEqual(values["idf_versions"], "v5.5.5,v6.0.2")
        self.assertEqual(values["arduino_fqbn"], VALID["arduino"]["fqbn"])
        self.assertEqual(values["factory_esp_idf"], "v5.5.5")

    @unittest.skipUnless(
        product_repo(),
        f"bound to a real product.json: set {PRODUCT_REPO_ENV} to a product repository checkout",
    )
    def test_product_repository_config(self) -> None:
        path = product_repo() / ".github/product.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        product_config.validate(document)
        if jsonschema:
            jsonschema.validate(document, SCHEMA)


if __name__ == "__main__":
    unittest.main()
