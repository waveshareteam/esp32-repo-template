"""Homepage contract shared by the skeleton README and every product README."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from support import DEFAULTS, PRODUCT_REPO_ENV, SKELETON, product_repo


HOMEPAGES = ("README.md", "README_ZH.md")
HERO_IMAGE = re.compile(r'<img src="(docs/images/[^"]+)" alt="([^"]+)" width="500">')
H2 = re.compile(r"^## (\S+) ", re.MULTILINE)
QUICK_LINK_ICONS = {
    "product": "🌐",
    "firmware": "📦",
    "esp_idf": "🧩",
    "arduino": "🔧",
    "documentation": "📚",
}
# Local `releases/` links are maintainer tooling; the GitHub `.../releases/latest` URL is not.
MAINTAINER_ONLY = (
    "docs/ci", "docs/firmware", "(releases/", '"releases/', "CONTRIBUTING", "ci-routing"
)


def homepage_config() -> dict:
    config = json.loads((DEFAULTS / "markdown-audit.json").read_text(encoding="utf-8"))
    return config["homepage_pairs"][0]


def homepage_violations(repo: Path, require_hero_file: bool) -> list[str]:
    homepage = homepage_config()
    product = json.loads((repo / ".github/product.json").read_text(encoding="utf-8"))
    problems = []
    for name in HOMEPAGES:
        text = (repo / name).read_text(encoding="utf-8")
        hero = HERO_IMAGE.search(text)
        if not hero:
            problems.append(f"{name}: no hero image below docs/images/")
        else:
            if product["product"] not in hero.group(2):
                problems.append(f"{name}: hero alt text must name the product")
            if require_hero_file and not (repo / hero.group(1)).is_file():
                problems.append(f"{name}: hero image {hero.group(1)} does not exist")
        if product["product_url"] not in text:
            problems.append(f"{name}: product_url from product.json is not linked")
        if "workflows/build.yml/badge.svg" not in text:
            problems.append(f"{name}: build badge must point at build.yml")
        if H2.findall(text) != homepage["required_h2_icons"]:
            problems.append(f"{name}: ## sections are {H2.findall(text)}")
        header = text.split("\n---\n", 1)[0]
        for link in homepage["required_quick_links"]:
            if f">{QUICK_LINK_ICONS[link]} " not in header:
                problems.append(f"{name}: quick link {link} is missing")
        for reference in MAINTAINER_ONLY:
            if reference in text:
                problems.append(f"{name}: user-facing homepage mentions {reference}")
    return problems


class HomepageContractTests(unittest.TestCase):
    def test_default_profile(self) -> None:
        homepage = homepage_config()
        self.assertEqual(homepage["profile"], "single-product")
        self.assertIn("hero_image", homepage["required_components"])
        self.assertEqual(homepage["required_quick_links"][0], "product")
        self.assertEqual(set(homepage["required_quick_links"]), set(QUICK_LINK_ICONS))
        self.assertEqual(
            homepage["required_h2_icons"], ["✨", "📦", "🧪", "🛠️", "📚", "🤝", "📄"]
        )

    def test_skeleton_homepage(self) -> None:
        # The skeleton hero image is a placeholder path that a new repository fills in.
        self.assertEqual(homepage_violations(SKELETON, require_hero_file=False), [])

    @unittest.skipUnless(
        product_repo(),
        f"bound to a real homepage: set {PRODUCT_REPO_ENV} to a product repository checkout",
    )
    def test_product_repository_homepage(self) -> None:
        self.assertEqual(homepage_violations(product_repo(), require_hero_file=True), [])


if __name__ == "__main__":
    unittest.main()
