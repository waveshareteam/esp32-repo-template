"""Schematic-backed pin contracts for Arduino board headers.

A contract lives in `tests/contracts/<product>.json`. The checker itself is exercised against a
fixture header on every run. Checking a real product header needs a product checkout, so that
test is skipped unless the `PRODUCT_REPO` environment variable points to one.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from support import FIXTURES, PRODUCT_REPO_ENV, TEMPLATE, product_repo


CONTRACTS = TEMPLATE / "tests" / "contracts"
FIXTURE_CONTRACT = CONTRACTS / "ESP32-S3-Touch-AMOLED-1.75C.json"
FIXTURE_HEADER = FIXTURES / "pin_config.h"
DEFINE = re.compile(r"^\s*#define\s+(\w+)\s+(\d+)\s*$", re.MULTILINE)


def contract_violations(header_text: str, contract: dict) -> list[str]:
    definitions = {name: int(value) for name, value in DEFINE.findall(header_text)}
    problems = []
    for macro, expected in contract["defines"].items():
        if macro not in definitions:
            problems.append(f"{macro} must be defined")
        elif definitions[macro] != expected:
            problems.append(f"{macro} is {definitions[macro]}, the schematic requires {expected}")
    for group in contract.get("distinct", []):
        values = [definitions.get(macro) for macro in group]
        if len(set(values)) != len(values):
            problems.append(f"{', '.join(group)} must remain distinct schematic signals")
    return problems


class HardwareContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(FIXTURE_CONTRACT.read_text(encoding="utf-8"))
        cls.header = FIXTURE_HEADER.read_text(encoding="utf-8")

    def test_fixture_header_satisfies_the_contract(self) -> None:
        self.assertEqual(contract_violations(self.header, self.contract), [])

    def test_wrong_and_missing_pins_are_reported(self) -> None:
        wrong = self.header.replace("#define LCD_CS 12", "#define LCD_CS 13")
        self.assertEqual(
            contract_violations(wrong, self.contract),
            ["LCD_CS is 13, the schematic requires 12"],
        )
        missing = self.header.replace("#define TP_INT 11", "")
        self.assertEqual(contract_violations(missing, self.contract), ["TP_INT must be defined"])

    def test_conflated_reset_signals_are_reported(self) -> None:
        conflated = self.header.replace("#define TP_RST 2", "#define TP_RST 1")
        self.assertIn(
            "LCD_RESET, TP_RST must remain distinct schematic signals",
            contract_violations(conflated, self.contract),
        )

    @unittest.skipUnless(
        product_repo(),
        f"bound to a real board header: set {PRODUCT_REPO_ENV} to a product repository checkout",
    )
    def test_product_repository_header(self) -> None:
        repo = product_repo()
        product = json.loads((repo / ".github/product.json").read_text(encoding="utf-8"))["product"]
        contract_path = CONTRACTS / f"{product}.json"
        if not contract_path.is_file():
            self.skipTest(f"no schematic-backed pin contract recorded for {product}")
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        header = Path(repo / contract["header"])
        self.assertTrue(header.is_file(), f"{contract['header']} is missing in {product}")
        self.assertEqual(contract_violations(header.read_text(encoding="utf-8"), contract), [])


if __name__ == "__main__":
    unittest.main()
