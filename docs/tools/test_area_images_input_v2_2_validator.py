#!/usr/bin/env python3
"""Positive/negative regression tests for the V2.2 semantic verifier.

All mutations happen in TemporaryDirectory copies. Delivery ZIPs are read-only.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "images-input-packages-v2_2"
SOURCE = ROOT / "docs" / "art" / "images-input-packages-v2_1"
VERIFIER_PATH = ROOT / "docs" / "tools" / "verify_area_images_input_v2_2.py"


spec = importlib.util.spec_from_file_location("v2_2_verifier", VERIFIER_PATH)
verifier = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(verifier)


def extract_area02(parent: Path) -> Path:
    with zipfile.ZipFile(OUT / "AREA_02_IMAGES_INPUT_V2_2.zip") as archive:
        archive.extractall(parent)
    return parent / "AREA_02_IMAGES_INPUT_V2_2"


def run_case(name: str, mutate=None, expect_pass: bool = False) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"v2_2_regression_{name}_") as td:
        root = extract_area02(Path(td))
        if mutate:
            mutate(root)
        errors, _ = verifier.validate_package_dir(root, "area_02", SOURCE / "AREA_02_IMAGES_INPUT_V2_1.zip")
        actual_pass = not errors
        passed = actual_pass == expect_pass
        return {
            "name": name,
            "expected": "PASS" if expect_pass else "FAIL",
            "actual": "PASS" if actual_pass else "FAIL",
            "test_pass": passed,
            "detected_errors": errors,
            "delivery_modified": False,
        }


def inject_stumpy_cast_conflict(root: Path) -> None:
    path = next(root.glob("monsters/*m_stumpy*/GENERATION_SPEC.md"))
    text = path.read_text(encoding="utf-8")
    old = "- required_roles: `PROJECTILE|ICON`"
    assert old in text
    path.write_text(text.replace(old, "- required_roles: `CAST_VFX|ICON`", 1), encoding="utf-8", newline="\n")


def inject_old_exclude_classification(root: Path) -> None:
    style_index = verifier.csv_rows((root / "global_skill_style_library/STYLE_INDEX.csv").read_bytes())
    row = next(item for item in style_index if item["style_priority"] == "EXCLUDE_STYLE")
    prefix = f"{int(row['index']):04d}_"
    path = next((root / "global_skill_style_library/skills").glob(prefix + "*/info.md"))
    text = path.read_text(encoding="utf-8")
    marker = "- style_priority: `EXCLUDE_STYLE`"
    assert marker in text
    path.write_text(text.replace(marker, "- style_priority: `UNKNOWN`", 1), encoding="utf-8", newline="\n")


def main() -> None:
    cases = [
        run_case("positive_unmodified_area02", expect_pass=True),
        run_case("negative_stumpy_cast_role_conflict", inject_stumpy_cast_conflict, expect_pass=False),
        run_case("negative_old_exclude_classification", inject_old_exclude_classification, expect_pass=False),
    ]
    overall = "PASS" if all(case["test_pass"] for case in cases) else "FAIL"
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "method": "temporary extracted copies; delivery ZIPs never modified",
        "cases": cases,
    }
    (OUT / "INPUT_V2_2_REGRESSION_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    lines = [
        "# INPUT V2.2 validator regression results", "",
        f"- overall: **{overall}**",
        "- 모든 오류 주입은 임시 복사본에서만 수행했으며 납품 ZIP은 수정하지 않았다.", "",
        "| case | expected | actual | test | representative detection |",
        "|---|---|---|---|---|",
    ]
    for case in cases:
        detection = case["detected_errors"][0] if case["detected_errors"] else "none"
        lines.append(f"| {case['name']} | {case['expected']} | {case['actual']} | {'PASS' if case['test_pass'] else 'FAIL'} | {detection} |")
    (OUT / "INPUT_V2_2_REGRESSION_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if overall != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
