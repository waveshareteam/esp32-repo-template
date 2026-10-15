#!/usr/bin/env python3
"""Load and validate a product repository's `.github/product.json`.

`product.json` is the single product-specific input of the shared CI. Every
other script in this directory reads framework versions, the ESP-IDF target and
the Arduino FQBN through this module instead of carrying its own defaults.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
DEFAULTS_DIR = TEMPLATE_ROOT / "defaults"
DEFAULT_PRODUCT_PATH = ".github/product.json"
OVERRIDE_DEFAULTS = {
    "ci_routing": "ci-routing.json",
    "markdown_audit": "markdown-audit.json",
}
TOP_LEVEL_KEYS = {
    "$schema",
    "product",
    "product_url",
    "tier",
    "target",
    "esp_idf",
    "arduino",
    "factory_firmware",
    "overrides",
}
TARGET_PATTERN = re.compile(r"^esp32([a-z][0-9]+)?$")
IDF_VERSION_PATTERN = re.compile(r"^v[0-9]+\.[0-9]+(\.[0-9]+)?$")
ARDUINO_CORE_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
FQBN_PATTERN = re.compile(r"^[^:\s]+:[^:\s]+:[^:\s]+(:[^\s]+)?$")


class ProductConfigError(RuntimeError):
    """`product.json` is missing, unreadable, or does not follow the schema."""


def _require_string(data: dict, key: str, where: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProductConfigError(f"{where}{key} must be a non-empty string")
    return value


def validate(data: object) -> dict:
    """Mirror `schema/product.schema.json` without third-party dependencies."""
    if not isinstance(data, dict):
        raise ProductConfigError("product.json must contain a JSON object")
    unknown = sorted(set(data) - TOP_LEVEL_KEYS)
    if unknown:
        raise ProductConfigError(f"unknown product.json keys: {', '.join(unknown)}")

    _require_string(data, "product", "")
    if not _require_string(data, "product_url", "").startswith(("https://", "http://")):
        raise ProductConfigError("product_url must be an http(s) URL")
    tier = data.get("tier")
    if isinstance(tier, bool) or tier not in (0, 1, 2):
        raise ProductConfigError("tier must be 0, 1, or 2")
    if not TARGET_PATTERN.match(_require_string(data, "target", "")):
        raise ProductConfigError("target must be an ESP-IDF target name such as esp32s3")

    esp_idf = data.get("esp_idf")
    if esp_idf is not None:
        if not isinstance(esp_idf, dict) or set(esp_idf) != {"versions"}:
            raise ProductConfigError("esp_idf must be an object with only a versions list")
        versions = esp_idf["versions"]
        if (
            not isinstance(versions, list)
            or not versions
            or len(set(versions)) != len(versions)
            or not all(isinstance(item, str) and IDF_VERSION_PATTERN.match(item) for item in versions)
        ):
            raise ProductConfigError("esp_idf.versions must list unique tags such as v5.5.5")

    arduino = data.get("arduino")
    if arduino is not None:
        if not isinstance(arduino, dict) or set(arduino) != {"core", "fqbn"}:
            raise ProductConfigError("arduino must be an object with exactly core and fqbn")
        if not ARDUINO_CORE_PATTERN.match(_require_string(arduino, "core", "arduino.")):
            raise ProductConfigError("arduino.core must be a version such as 3.3.11")
        if not FQBN_PATTERN.match(_require_string(arduino, "fqbn", "arduino.")):
            raise ProductConfigError("arduino.fqbn must be a full arduino-cli FQBN")

    if esp_idf is None and arduino is None:
        raise ProductConfigError("product.json must describe esp_idf, arduino, or both")
    factory = data.get("factory_firmware")
    if factory is not None and (
        not isinstance(factory, dict)
        or set(factory) != {"esp_idf"}
        or not isinstance(factory["esp_idf"], str)
        or not IDF_VERSION_PATTERN.match(factory["esp_idf"])
    ):
        raise ProductConfigError("factory_firmware must be an object with only an esp_idf tag such as v5.5.5")

    overrides = data.get("overrides", {})
    if not isinstance(overrides, dict) or set(overrides) - set(OVERRIDE_DEFAULTS):
        raise ProductConfigError(
            f"overrides may only contain: {', '.join(sorted(OVERRIDE_DEFAULTS))}"
        )
    if any(not isinstance(value, dict) for value in overrides.values()):
        raise ProductConfigError("every overrides entry must be an object")
    return data


def load_product(path: str | Path = DEFAULT_PRODUCT_PATH) -> dict:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductConfigError(f"cannot read product config {path}") from exc
    return validate(data)


def merge_overrides(defaults: dict, overrides: dict) -> dict:
    """Lists are extended without duplicates; every other value is replaced."""
    merged = copy.deepcopy(defaults)
    for key, value in overrides.items():
        if isinstance(value, list) and isinstance(merged.get(key), list):
            merged[key] = merged[key] + [item for item in value if item not in merged[key]]
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_defaults(section: str, product: dict | None = None) -> dict:
    """Read `defaults/<section>` and merge `product.json` overrides into it."""
    path = DEFAULTS_DIR / OVERRIDE_DEFAULTS[section]
    try:
        defaults = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductConfigError(f"cannot read template defaults {path}") from exc
    overrides = (product or {}).get("overrides", {}).get(section, {})
    return merge_overrides(defaults, overrides)


def idf_versions(product: dict) -> list[str]:
    return list(product.get("esp_idf", {}).get("versions", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate product.json and export its values.")
    parser.add_argument("--product", default=DEFAULT_PRODUCT_PATH)
    parser.add_argument("--github-output")
    args = parser.parse_args()
    try:
        product = load_product(args.product)
    except ProductConfigError as exc:
        print(f"product config error: {exc}", file=sys.stderr)
        return 2

    arduino = product.get("arduino", {})
    values = {
        "product": product["product"],
        "target": product["target"],
        "tier": str(product["tier"]),
        "idf_versions": ",".join(idf_versions(product)),
        "arduino_core": arduino.get("core", ""),
        "arduino_fqbn": arduino.get("fqbn", ""),
        "factory_esp_idf": product.get("factory_firmware", {}).get("esp_idf", ""),
    }
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write(f"{key}={value}\n")
    else:
        print(json.dumps(values, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
