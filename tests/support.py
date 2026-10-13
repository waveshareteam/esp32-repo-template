"""Shared helpers for the template self-tests."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


TEMPLATE = Path(__file__).resolve().parents[1]
CI = TEMPLATE / "ci"
DEFAULTS = TEMPLATE / "defaults"
SKELETON = TEMPLATE / "skeleton"
FIXTURES = TEMPLATE / "tests" / "fixtures"
WORKFLOW = TEMPLATE / ".github/workflows/build.yml"
PRODUCT_REPO_ENV = "PRODUCT_REPO"

if str(CI) not in sys.path:
    sys.path.insert(0, str(CI))

IDF_NAMES = ("01_first", "02_second")
ARDUINO_SKETCHES = {
    # Sketch directory -> .ino file name. The second one deliberately differs from its directory.
    "01_HelloWorld": "01_HelloWorld.ino",
    "02_Renamed": "05_Renamed.ino",
    "03_Audio": "03_Audio.ino",
}


def product_repo() -> Path | None:
    """A product checkout to run product-bound contracts against, if one was provided."""
    value = os.environ.get(PRODUCT_REPO_ENV)
    return Path(value).resolve() if value else None


def make_product_repo(root: Path, product: dict | None = None) -> Path:
    """Create a minimal product repository that follows docs/spec.md."""
    (root / ".github").mkdir(parents=True)
    if product is None:
        shutil.copy(FIXTURES / "product.json", root / ".github/product.json")
    else:
        (root / ".github/product.json").write_text(json.dumps(product), encoding="utf-8")

    for name in IDF_NAMES:
        project = root / "examples/esp-idf" / name
        (project / "main").mkdir(parents=True)
        (project / "CMakeLists.txt").write_text("", encoding="utf-8")
    # Not a project: no main/ directory.
    (root / "examples/esp-idf/not_a_project").mkdir()

    for directory, ino in ARDUINO_SKETCHES.items():
        sketch = root / "examples/arduino/examples" / directory
        sketch.mkdir(parents=True)
        (sketch / ino).write_text("", encoding="utf-8")
    bundled = root / "examples/arduino/libraries/SomeLib/examples/Demo"
    bundled.mkdir(parents=True)
    (bundled / "Demo.ino").write_text("", encoding="utf-8")
    return root
