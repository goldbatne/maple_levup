#!/usr/bin/env python3
"""Regression tests proving the V2.3 semantic validator rejects key regressions."""

from __future__ import annotations

import copy
import csv
import io
import json
import zipfile
from pathlib import Path

import verify_area_images_input_v2_3 as verifier


OUT = Path(__file__).resolve().parents[1] / "art" / "images-input-packages-v2_3"


def rows(zf: zipfile.ZipFile, suffix: str) -> list[dict[str, str]]:
    name = verifier.zip_member(zf, "/" + suffix)
    return list(csv.DictReader(io.StringIO(zf.read(name).decode("utf-8-sig"))))


def run_case(
    name: str,
    manifest: list[dict[str, str]],
    scope: list[dict[str, str]],
    output: list[dict[str, str]],
    binding: list[dict[str, str]],
    should_pass: bool,
) -> dict[str, object]:
    audit = verifier.Audit()
    verifier.verify_scope(audit, "02", manifest, scope, output, binding)
    passed = not audit.errors
    return {
        "case": name,
        "expected": "PASS" if should_pass else "FAIL",
        "actual": "PASS" if passed else "FAIL",
        "test_result": "PASS" if passed == should_pass else "FAIL",
        "detected_errors": audit.errors[:5],
    }


def mutate_role(scope: list[dict[str, str]], skill: str, role: str, **values: str) -> None:
    row = next(r for r in scope if r["skill_id"] == skill and r["effect_role"] == role)
    row.update(values)


def main() -> int:
    path = OUT / "AREA_02_IMAGES_INPUT_V2_3.zip"
    with zipfile.ZipFile(path) as zf:
        manifest = rows(zf, "AREA_MANIFEST.csv")
        base_scope = rows(zf, "FULL_ART_SCOPE.csv")
        output = rows(zf, "OUTPUT_REQUIREMENTS.csv")
        binding = rows(zf, "ASSET_BINDING_PLAN.csv")

    results = [run_case("positive_unmodified_area02", manifest, base_scope, output, binding, True)]

    keep_scope = copy.deepcopy(base_scope)
    mutate_role(keep_scope, "s_mon_stumpy", "PROJECTILE", production_decision="KEEP_EXISTING")
    results.append(run_case("reject_projectile_keep", manifest, keep_scope, output, binding, False))

    cast_scope = copy.deepcopy(base_scope)
    mutate_role(
        cast_scope, "s_mon_stumpy", "CAST_VFX",
        production_decision="NEW_ART", required_file_set="CAST/F00.png",
    )
    results.append(run_case("reject_invented_stumpy_cast", manifest, cast_scope, output, binding, False))

    hit_scope = copy.deepcopy(base_scope)
    mutate_role(
        hit_scope, "s_mon_stone", "HIT_VFX",
        production_decision="NEW_ART", required_file_set="HIT/F00.png",
    )
    results.append(run_case("reject_invented_hit_role", manifest, hit_scope, output, binding, False))

    timing_scope = copy.deepcopy(base_scope)
    mutate_role(timing_scope, "s_mon_stumpy", "PROJECTILE", total_seconds="0.96")
    results.append(run_case("reject_projectile_lifetime_overrun", manifest, timing_scope, output, binding, False))

    overall = "PASS" if all(r["test_result"] == "PASS" for r in results) else "FAIL"
    payload = {"overall": overall, "cases": results}
    (OUT / "VALIDATOR_REGRESSION_RESULTS.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    md = ["# V2.3 validator regression results", "", f"- overall: **{overall}**", "", "| Case | Expected | Actual | Test |", "|---|---|---|---|"]
    md.extend(f"| {r['case']} | {r['expected']} | {r['actual']} | {r['test_result']} |" for r in results)
    md.extend(["", "The negative cases run on in-memory copies only; delivery ZIPs are not modified.", ""])
    (OUT / "VALIDATOR_REGRESSION_RESULTS.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
