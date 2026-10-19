from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import ARDUINO_SKETCHES, CI, FIXTURES, IDF_NAMES, WORKFLOW, make_product_repo

import discover_examples  # noqa: E402


PRODUCT = json.loads((FIXTURES / "product.json").read_text(encoding="utf-8"))


class DiscoverExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = make_product_repo(Path(cls._tmp.name) / "repo")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CI / "discover_examples.py"), "--repo", str(self.repo), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_inventory_counts_and_library_exclusion(self) -> None:
        idf = discover_examples.discover_esp_idf(self.repo)
        arduino = discover_examples.discover_arduino(self.repo)
        self.assertEqual({item["name"] for item in idf}, set(IDF_NAMES))
        self.assertEqual({item["name"] for item in arduino}, set(ARDUINO_SKETCHES))
        self.assertEqual({item["ino"] for item in arduino}, set(ARDUINO_SKETCHES.values()))
        self.assertTrue(all("/libraries/" not in item["path"] for item in arduino))

    def test_name_path_and_legacy_selectors(self) -> None:
        idf_entry = {"name": "01_AXP2101", "path": "examples/esp-idf/01_AXP2101"}
        self.assertTrue(discover_examples.selector_matches(idf_entry, "01_AXP2101"))
        self.assertTrue(discover_examples.selector_matches(
            idf_entry, "examples/esp-idf/01_AXP2101"
        ))
        self.assertTrue(discover_examples.selector_matches(
            idf_entry, "examples/ESP-IDF-v5.5/01_AXP2101"
        ))

        arduino_entry = {
            "name": "01_HelloWorld",
            "path": "examples/arduino/examples/01_HelloWorld",
            "ino": "01_HelloWorld.ino",
        }
        self.assertTrue(discover_examples.selector_matches(arduino_entry, "01_HelloWorld.ino"))
        self.assertTrue(discover_examples.selector_matches(
            arduino_entry,
            "examples/Arduino-v3.3.5/examples/01_HelloWorld",
        ))

    def test_multiple_selectors(self) -> None:
        entries = discover_examples.discover_esp_idf(self.repo)
        selected = [
            item for item in entries
            if discover_examples.selector_matches(
                item,
                f"{IDF_NAMES[0]},examples/esp-idf/{IDF_NAMES[1]}",
            )
        ]
        self.assertEqual({item["name"] for item in selected}, set(IDF_NAMES))

    def test_cli_matrix_comes_from_product_json(self) -> None:
        idf = self.run_cli("--surface", "esp-idf")
        arduino = self.run_cli("--surface", "arduino")
        self.assertEqual(idf.returncode, 0, idf.stderr)
        self.assertEqual(arduino.returncode, 0, arduino.stderr)
        idf_matrix = json.loads(idf.stdout)["include"]
        arduino_matrix = json.loads(arduino.stdout)["include"]

        versions = PRODUCT["esp_idf"]["versions"]
        self.assertEqual(len(idf_matrix), len(IDF_NAMES) * len(versions))
        self.assertEqual({item["idf"] for item in idf_matrix}, set(versions))
        self.assertEqual(len(arduino_matrix), len(ARDUINO_SKETCHES))
        self.assertEqual({item["core"] for item in arduino_matrix}, {PRODUCT["arduino"]["core"]})
        self.assertEqual({item["fqbn"] for item in arduino_matrix}, {PRODUCT["arduino"]["fqbn"]})
        for entry in idf_matrix + arduino_matrix:
            self.assertEqual(entry["product"], PRODUCT["product"])
            self.assertEqual(entry["target"], PRODUCT["target"])

    def test_surface_missing_from_product_json_builds_nothing(self) -> None:
        product = {key: value for key, value in PRODUCT.items() if key != "arduino"}
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_product_repo(Path(tmp) / "repo", product)
            completed = subprocess.run(
                [
                    sys.executable, str(CI / "discover_examples.py"),
                    "--repo", str(repo), "--surface", "arduino",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["include"], [])

    def test_missing_product_json_fails_closed(self) -> None:
        completed = self.run_cli("--surface", "esp-idf", "--product", ".github/missing.json")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("product config error", completed.stderr)

    def test_scripts_carry_no_framework_defaults(self) -> None:
        source = (CI / "discover_examples.py").read_text(encoding="utf-8")
        for flag in ("--idf-versions", "--arduino-core", "--fqbn"):
            self.assertNotIn(flag, source, f"{flag} must come from product.json")

    def test_workflow_takes_versions_and_fqbn_from_the_matrix(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        discover_job = workflow.split("  discover-arduino:\n", 1)[1].split(
            "  build-arduino:\n", 1
        )[0]
        self.assertIn('python3 "$TEMPLATE_DIR/ci/discover_examples.py"', discover_job)
        self.assertIn("--product .github/product.json", discover_job)
        self.assertIn('--fqbn "${{ matrix.fqbn }}"', workflow)
        self.assertIn('set-target "${{ matrix.target }}"', workflow)
        self.assertIn("espressif/idf:${{ matrix.idf }}", workflow)
        for hardcoded in ("esp32s3", "v5.5", "v6.0", "3.3.11", "FlashSize"):
            self.assertNotIn(hardcoded, workflow, f"{hardcoded} must come from product.json")

    def test_release_expects_one_archive_per_example_and_none_for_the_factory_firmware(self) -> None:
        import prepare_release_assets

        examples = len(IDF_NAMES) * len(PRODUCT["esp_idf"]["versions"]) + len(ARDUINO_SKETCHES)
        self.assertIn("factory_firmware", PRODUCT)
        self.assertEqual(prepare_release_assets.expected_asset_count(self.repo, PRODUCT), examples)

    def test_workflow_builds_the_factory_firmware_but_keeps_it_out_of_releases(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("idf.py -C firmware/sourcecode", workflow)
        self.assertIn('"release-artifacts/${PRODUCT}_FactoryOnly.bin"', workflow)
        self.assertNotIn("release-downloads/*_FactoryOnly.bin", workflow)


if __name__ == "__main__":
    unittest.main()
