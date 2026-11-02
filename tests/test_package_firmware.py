from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import support  # noqa: F401

import package_firmware  # noqa: E402


def package_with_esptool_args(root: Path, extra_esptool_args: dict) -> dict:
    build_dir = root / "build"
    build_dir.mkdir()
    (build_dir / "app.bin").write_bytes(b"\x00")
    (build_dir / "flasher_args.json").write_text(
        json.dumps({
            "flash_files": {"0x10000": "app.bin"},
            "extra_esptool_args": extra_esptool_args,
        }),
        encoding="utf-8",
    )
    package_firmware.package(Namespace(
        framework="esp-idf",
        project="examples/esp-idf/01_first",
        build_dir=str(build_dir),
        output_dir=str(root / "out"),
        name="fixture",
        framework_version="v6.1",
        target="esp32s31",
        git_sha="",
    ))
    return json.loads((root / "out/fixture/manifest.json").read_text(encoding="utf-8"))


class PackageFirmwareTests(unittest.TestCase):
    def test_flash_commands_keep_no_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = package_with_esptool_args(Path(tmp), {"stub": False})
        for key in ("flash_command", "combined_flash_command"):
            self.assertIn("--no-stub write_flash", manifest[key])

    def test_flash_commands_use_the_stub_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = package_with_esptool_args(Path(tmp), {"stub": True})
        for key in ("flash_command", "combined_flash_command"):
            self.assertNotIn("--no-stub", manifest[key])


if __name__ == "__main__":
    unittest.main()
