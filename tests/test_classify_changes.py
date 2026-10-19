from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import CI, DEFAULTS, FIXTURES, WORKFLOW, make_product_repo

import classify_changes  # noqa: E402


class ClassifyChangesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = classify_changes._load_config(DEFAULTS / "ci-routing.json")
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = make_product_repo(Path(cls._tmp.name) / "repo")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def classify(self, *paths: str) -> dict[str, object]:
        return classify_changes.classify(list(paths), self.config)

    def test_markdown_never_selects_examples(self) -> None:
        result = self.classify(
            "README.md",
            "examples/esp-idf/01_AXP2101/README.md",
            "examples/arduino/examples/01_HelloWorld/README.md",
            "examples/arduino/libraries/lvgl/README.md",
        )
        self.assertEqual(result["esp_idf"]["mode"], "none")
        self.assertEqual(result["arduino"]["mode"], "none")
        self.assertTrue(result["docs_only"])

    def test_direct_sources_select_only_the_affected_entries(self) -> None:
        result = self.classify(
            "examples/esp-idf/02_lvgl_demo_v9/main/main.c",
            "examples/esp-idf/02_lvgl_demo_v9/CMakeLists.txt",
            "examples/arduino/examples/06_ES7210/06_ES7210.ino",
        )
        self.assertEqual(result["esp_idf"], {
            "mode": "selected",
            "selectors": ["examples/esp-idf/02_lvgl_demo_v9"],
        })
        self.assertEqual(result["arduino"], {
            "mode": "selected",
            "selectors": ["examples/arduino/examples/06_ES7210"],
        })

    def test_governance_only_changes_select_no_examples(self) -> None:
        result = self.classify("LICENSE", ".github/ISSUE_TEMPLATE/config.yml")
        self.assertEqual(result["esp_idf"]["mode"], "none")
        self.assertEqual(result["arduino"]["mode"], "none")

    def test_shared_and_global_inputs(self) -> None:
        idf = self.classify("config/sdkconfig.defaults")
        self.assertEqual(idf["esp_idf"]["mode"], "all")
        self.assertEqual(idf["arduino"]["mode"], "none")

        arduino = self.classify("examples/arduino/libraries/board_config/pin_config.h")
        self.assertEqual(arduino["esp_idf"]["mode"], "none")
        self.assertEqual(arduino["arduino"]["mode"], "all")

        for path in (".github/workflows/build.yml", ".github/product.json"):
            global_result = self.classify(path)
            self.assertEqual(global_result["esp_idf"]["mode"], "all", path)
            self.assertEqual(global_result["arduino"]["mode"], "all", path)

    def test_factory_firmware_source_builds_only_the_factory_firmware(self) -> None:
        result = self.classify("firmware/sourcecode/main/main.cpp")
        self.assertTrue(result["factory_firmware"])
        self.assertEqual(result["esp_idf"]["mode"], "none")
        self.assertEqual(result["arduino"]["mode"], "none")
        self.assertFalse(result["docs_only"])

        docs = self.classify("firmware/sourcecode/README.md")
        self.assertFalse(docs["factory_firmware"])
        self.assertTrue(docs["docs_only"])

        self.assertFalse(self.classify("examples/esp-idf/01_first/main/main.c")["factory_firmware"])
        self.assertTrue(classify_changes.classify([], self.config, force_all=True)["factory_firmware"])

    def test_committed_firmware_images_build_nothing(self) -> None:
        result = self.classify("firmware/ESP32-S3-Touch-AMOLED-2.06_FactoryOnly_20261019.bin")
        self.assertFalse(result["factory_firmware"])
        self.assertEqual(result["esp_idf"]["mode"], "none")
        self.assertEqual(result["arduino"]["mode"], "none")
        self.assertTrue(result["docs_only"])

    def test_unknown_non_document_path_routes_all(self) -> None:
        result = self.classify("tooling/custom.build")
        self.assertEqual(result["esp_idf"]["mode"], "all")
        self.assertEqual(result["arduino"]["mode"], "all")
        self.assertEqual(result["unknown_paths"], ["tooling/custom.build"])

    def test_manual_dispatch_routes_all(self) -> None:
        result = classify_changes.classify([], self.config, force_all=True)
        self.assertEqual(result["esp_idf"]["mode"], "all")
        self.assertEqual(result["arduino"]["mode"], "all")
        self.assertFalse(result["docs_only"])

    def run_cli(self, repo: Path, changes: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        """The invocation used by .github/workflows/build.yml."""
        return subprocess.run(
            [
                sys.executable,
                str(CI / "classify_changes.py"),
                "--repo", str(repo),
                "--changed-files-from", str(changes),
                "--product", ".github/product.json",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_exact_workflow_cli_handles_rename_and_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            changes = tmp_path / "changed-files.txt"
            output = tmp_path / "github-output.txt"
            changes.write_text(
                "R100\texamples/esp-idf/01_AXP2101/main/old.c\tdocs/old.md\n"
                "D\texamples/arduino/examples/02_GFX_AsciiTable/02_GFX_AsciiTable.ino\n",
                encoding="utf-8",
            )
            completed = self.run_cli(self.repo, changes, "--github-output", str(output))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            values = dict(
                line.split("=", 1)
                for line in output.read_text(encoding="utf-8").splitlines()
            )
            result = json.loads(values["routing"])
            self.assertEqual(result["esp_idf"]["selectors"], [
                "examples/esp-idf/01_AXP2101"
            ])
            self.assertEqual(result["arduino"]["selectors"], [
                "examples/arduino/examples/02_GFX_AsciiTable"
            ])

    def test_empty_changed_file_scope_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changes = Path(tmp) / "empty.txt"
            changes.write_text("", encoding="utf-8")
            completed = self.run_cli(self.repo, changes)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("changed-file set is empty", completed.stderr)

    def test_missing_product_json_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changes = Path(tmp) / "changed-files.txt"
            changes.write_text("M\tREADME.md\n", encoding="utf-8")
            completed = self.run_cli(Path(tmp), changes)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("cannot read product config", completed.stderr)

    def test_product_overrides_extend_the_defaults(self) -> None:
        product = json.loads((FIXTURES / "product.json").read_text(encoding="utf-8"))
        product["overrides"] = {"ci_routing": {"esp_idf_shared_patterns": ["shared/**"]}}
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_product_repo(Path(tmp) / "repo", product)
            changes = Path(tmp) / "changed-files.txt"

            changes.write_text("M\tshared/sdkconfig.common\n", encoding="utf-8")
            overridden = json.loads(self.run_cli(repo, changes).stdout)
            self.assertEqual(overridden["esp_idf"]["mode"], "all")
            self.assertEqual(overridden["arduino"]["mode"], "none")
            self.assertEqual(overridden["unknown_paths"], [])

            # The default list is extended, not replaced.
            changes.write_text("M\tconfig/sdkconfig.defaults\n", encoding="utf-8")
            default = json.loads(self.run_cli(repo, changes).stdout)
            self.assertEqual(default["esp_idf"]["mode"], "all")
            self.assertEqual(default["arduino"]["mode"], "none")

    def test_workflow_uses_the_tested_classifier_invocation(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'python3 "$TEMPLATE_DIR/ci/classify_changes.py" --repo . '
            '--changed-files-from "$RUNNER_TEMP/changed-files.txt" '
            '--product .github/product.json --github-output "$GITHUB_OUTPUT"',
            workflow,
        )
        self.assertNotIn("--config", workflow)


if __name__ == "__main__":
    unittest.main()
