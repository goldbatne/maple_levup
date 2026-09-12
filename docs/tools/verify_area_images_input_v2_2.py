#!/usr/bin/env python3
"""Semantic verifier and evidence finalizer for AREA INPUT V2.2."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "art" / "images-input-packages-v2_1"
OUT = ROOT / "docs" / "art" / "images-input-packages-v2_2"
BASELINE = ROOT / "docs" / "art" / "images-input-packages-v2" / "SOURCE_BASELINE.json"
CROSSCHECK = Path(r"C:/Users/dddd/Downloads/V2_1_EVIDENCE_CROSSCHECK_20260912.zip")
TARGET_IDS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]
IMMUTABLE_MANIFEST_COLUMNS = [
    "work_order", "level", "area_id", "area_name", "monster_id", "monster_name",
    "monster_image_ruid", "monster_image_status", "skill_id", "skill_name",
    "skill_type", "actual_effect", "boss", "folder",
]
PROJECTILE_SECONDS = 0.35
PROJECTILE_HIT_RADIUS = 0.8
BOSS_RANGE_MULTIPLIER = 0.667
STUMPY_ID = "s_mon_stumpy"
STONE_MASK_ID = "s_mon_mutant_stone_mask"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(data: bytes | str) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def git_bytes(commit: str, rel: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{rel}"], cwd=ROOT)


def normalize_role(role: str) -> str:
    if role in {"IMPACT_CAST_VFX", "SELF_BUFF_CAST_VFX"}:
        return "CAST_VFX"
    if role == "APPROVED_REUSE_CAST_VFX+ICON":
        return "APPROVED_REUSE"
    return role


def parse_current_style(info: str) -> dict[str, str]:
    match = re.search(r"(?ms)^## 현행 분류 — V2\.2\n(.*?)(?=^## |\Z)", info)
    if not match:
        return {}
    result = {}
    for key in ("RUID", "reference_role", "style_priority", "preview_usable"):
        found = re.search(rf"^- {key}: `?([^`\n]+)`?$", match.group(1), re.M)
        if found:
            result[key] = found.group(1).strip()
    return result


def parse_status(text: str) -> dict[str, str]:
    result = {}
    for axis in ("PACKAGE_VALIDATION", "GENERATION_READY", "RUNTIME_VALIDATION", "ART_APPROVAL"):
        match = re.search(rf"^\| {axis} \| ([^|]+) \|", text, re.M)
        if match:
            result[axis] = match.group(1).strip()
    return result


def validate_package_dir(root: Path, aid: str, source_zip: Path | None = None) -> tuple[list[str], dict]:
    errors: list[str] = []
    required = [
        "AREA_MANIFEST.csv", "AREA_MANIFEST.md", "ASSET_BINDING_PLAN.csv",
        "OUTPUT_REQUIREMENTS.csv", "OUTPUT_NAMING_SPEC.md", "OUTPUT_FORMAT_SPEC.md",
        "CHATGPT_IMAGES_MASTER_PROMPT.md", "README_START_HERE.md",
        "PROJECTILE_SCOPE_REVIEW.md", "RUNTIME_CONFLICTS_V2_2.md",
        "PACKAGE_STATUS_V2_2.md", "PACKAGE_REVISION_V2_2.md",
        "global_skill_style_library/STYLE_INDEX.csv",
        "global_skill_style_library/STYLE_INDEX.md",
        "global_skill_style_library/summary/STYLE_ATLAS.md",
    ]
    for rel in required:
        if not (root / rel).is_file():
            errors.append(f"missing {rel}")
    if errors:
        return errors, {}

    manifest = csv_rows((root / "AREA_MANIFEST.csv").read_bytes())
    binding = csv_rows((root / "ASSET_BINDING_PLAN.csv").read_bytes())
    requirements = csv_rows((root / "OUTPUT_REQUIREMENTS.csv").read_bytes())
    style_rows = csv_rows((root / "global_skill_style_library/STYLE_INDEX.csv").read_bytes())
    by_skill_binding: dict[str, list[dict]] = {}
    by_skill_req: dict[str, list[dict]] = {}
    for row in binding:
        by_skill_binding.setdefault(row["skill_id"], []).append(row)
    for row in requirements:
        by_skill_req.setdefault(row["skill_id"], []).append(row)

    if source_zip:
        with zipfile.ZipFile(source_zip) as archive:
            src_root = f"{aid.upper()}_IMAGES_INPUT_V2_1/"
            source_manifest = csv_rows(archive.read(src_root + "AREA_MANIFEST.csv"))
        if len(source_manifest) != len(manifest):
            errors.append("manifest row count changed")
        for before, after in zip(source_manifest, manifest):
            for column in IMMUTABLE_MANIFEST_COLUMNS:
                if before.get(column, "") != after.get(column, ""):
                    errors.append(f"{after.get('skill_id')}: immutable manifest field changed: {column}")

    projectile_count = 0
    passive_count = 0
    for row in manifest:
        sid = row["skill_id"]
        folder = root / row["folder"]
        spec_path = folder / "GENERATION_SPEC.md"
        role_path = folder / "RUNTIME_ROLE_MAP.md"
        if not spec_path.is_file() or not role_path.is_file():
            errors.append(f"{sid}: missing GENERATION_SPEC/RUNTIME_ROLE_MAP")
            continue
        spec = spec_path.read_text(encoding="utf-8")
        role_map = role_path.read_text(encoding="utf-8")
        if spec.count("## V2.2 현행 런타임·납품 계약") != 1:
            errors.append(f"{sid}: current contract section count != 1")
        if "## V2.1 실제 동작·납품 동기화" in spec:
            errors.append(f"{sid}: obsolete V2.1 current section remains")
        for key in ("required_roles", "replacement_target_fields", "generation_ready"):
            value = row[key]
            if f"- {key}: `{value}`" not in spec or f"- {key}: `{value}`" not in role_map:
                errors.append(f"{sid}: {key} differs across manifest/spec/role map")

        expected_roles = set(row["required_roles"].split("|"))
        req_roles = {x["role"] for x in by_skill_req.get(sid, []) if x["required"].lower() == "true"}
        if expected_roles != req_roles:
            errors.append(f"{sid}: required roles mismatch manifest={sorted(expected_roles)} output={sorted(req_roles)}")
        expected_targets = set(row["replacement_target_fields"].split("|"))
        req_targets = {x["target_field"] for x in by_skill_req.get(sid, []) if x["required"].lower() == "true"}
        if expected_targets != req_targets:
            errors.append(f"{sid}: target fields mismatch manifest={sorted(expected_targets)} output={sorted(req_targets)}")

        if expected_roles == {"APPROVED_REUSE"}:
            if not any(x["decision"] == "APPROVED_REUSE" for x in by_skill_binding.get(sid, [])):
                errors.append(f"{sid}: approved reuse binding missing")
        else:
            generated_binding = {
                normalize_role(x["effect_role"]): x["target_field"]
                for x in by_skill_binding.get(sid, [])
                if x.get("generation_required") == "true"
            }
            if set(generated_binding) != expected_roles:
                errors.append(f"{sid}: generated binding roles mismatch {generated_binding}")
            for role, target in generated_binding.items():
                matching = [x for x in by_skill_req.get(sid, []) if x["role"] == role]
                if not matching or matching[0]["target_field"] != target:
                    errors.append(f"{sid}: {role} target_field mismatch")

        if row["skill_type"] == "패시브":
            passive_count += 1
            if row["required_roles"] != "REFERENCE_VFX|ICON" or row["runtime_use"] != "false|ui":
                errors.append(f"{sid}: passive role/runtime contract invalid")
            if any(normalize_role(x["effect_role"]) == "CAST_VFX" and x.get("generation_required") == "true" for x in by_skill_binding.get(sid, [])):
                errors.append(f"{sid}: passive has required CAST delivery")
            ref = [x for x in by_skill_binding.get(sid, []) if x["effect_role"] == "REFERENCE_VFX"]
            if len(ref) != 1 or ref[0].get("runtime_use") != "false":
                errors.append(f"{sid}: passive REFERENCE_VFX runtime_use must be false")
            if "현행 CAST 레이어는 one-shot" in spec or "현행 CAST 레이어는 one-shot" in role_map:
                errors.append(f"{sid}: obsolete passive CAST one-shot template remains")

        if row["targeting_range"] != "n/a":
            projectile_count += 1
            try:
                targeting = float(row["targeting_range"])
                monster_targeting = float(row["monster_targeting_range"])
                impact = float(row["impact_radius"])
                delay = float(row["impact_delay"])
            except ValueError:
                errors.append(f"{sid}: projectile numeric contract malformed")
            else:
                if abs(monster_targeting - targeting * BOSS_RANGE_MULTIPLIER) > 0.001:
                    errors.append(f"{sid}: monster targeting multiplier mismatch")
                if impact != PROJECTILE_HIT_RADIUS or delay != PROJECTILE_SECONDS:
                    errors.append(f"{sid}: impact radius/delay mismatch")
                if targeting == impact:
                    errors.append(f"{sid}: targeting and impact radius unexpectedly conflated")
            for item in by_skill_binding.get(sid, []):
                if item["targeting_range"] != row["targeting_range"] or item["impact_radius"] != row["impact_radius"] or item["impact_delay"] != row["impact_delay"] or item["max_targets"] != row["max_targets"]:
                    errors.append(f"{sid}: projectile fields differ in binding plan")
                    break

        if sid == STUMPY_ID:
            if row["required_roles"] != "PROJECTILE|ICON" or row["replacement_target_fields"] != "projectile_ruid|icon_ruid":
                errors.append("Stumpy current role is not PROJECTILE+ICON")
            if "CAST_VFX=발사" in spec or "CAST 필요 파일" in spec or "CAST_VFX: 12" in spec:
                errors.append("Stumpy obsolete CAST generation instruction remains")
            match = re.search(r"PROJECTILE:\s*(\d+) frames.*?([0-9.]+) sec/frame", spec)
            if not match:
                errors.append("Stumpy projectile frame contract missing")
            else:
                total = int(match.group(1)) * float(match.group(2))
                if total > PROJECTILE_SECONDS:
                    errors.append(f"Stumpy art period {total:.3f}s exceeds lifetime")
            primary = [x for x in by_skill_binding[sid] if x["effect_role"] == "PROJECTILE"]
            if len(primary) != 1 or primary[0]["target_field"] != "projectile_ruid" or primary[0]["loop"] != "false":
                errors.append("Stumpy projectile binding contract invalid")
            if primary and primary[0]["flip_x"] != "none in actual PROJECTILE path":
                errors.append("Stumpy claims unsupported projectile FlipX")

        if sid == STONE_MASK_ID and row["runtime_validation"] != "UNRESOLVED":
            errors.append("stone mask DEF conflict not exposed as UNRESOLVED")

    # STYLE_INDEX and 15 EXCLUDE info files must expose one current classification.
    excludes = [row for row in style_rows if row["style_priority"] == "EXCLUDE_STYLE"]
    if len(style_rows) != 183 or len(excludes) != 15:
        errors.append(f"style counts mismatch: total={len(style_rows)} exclude={len(excludes)}")
    for row in excludes:
        prefix = f"{int(row['index']):04d}_"
        matches = list((root / "global_skill_style_library" / "skills").glob(prefix + "*/info.md"))
        if len(matches) != 1:
            errors.append(f"style {row['index']}: info path count {len(matches)}")
            continue
        info = matches[0].read_text(encoding="utf-8")
        current = parse_current_style(info)
        for key in ("RUID", "reference_role", "style_priority", "preview_usable"):
            if current.get(key) != row[key]:
                errors.append(f"style {row['index']}: current {key} differs index={row[key]} info={current.get(key)}")
        if info.count("## 현행 분류 — V2.2") != 1:
            errors.append(f"style {row['index']}: current classification section count != 1")

    naming = (root / "OUTPUT_NAMING_SPEC.md").read_text(encoding="utf-8")
    format_doc = (root / "OUTPUT_FORMAT_SPEC.md").read_text(encoding="utf-8")
    for doc_name, text in (("naming", naming), ("format", format_doc)):
        if "labeled_preview.png" not in text or "AREA_OVERVIEW_PREVIEW.png" not in text or "필수" not in text:
            errors.append(f"{doc_name}: mandatory preview rule missing")
        if "contact" not in text.lower() or "선택" not in text:
            errors.append(f"{doc_name}: optional contact preview rule missing")
        if "V2.1 mandatory delivery contract" in text:
            errors.append(f"{doc_name}: obsolete V2.1 contract remains")

    status = parse_status((root / "PACKAGE_STATUS_V2_2.md").read_text(encoding="utf-8"))
    if set(status) != {"PACKAGE_VALIDATION", "GENERATION_READY", "RUNTIME_VALIDATION", "ART_APPROVAL"}:
        errors.append("status axes incomplete")
    if status.get("RUNTIME_VALIDATION") == "PASS":
        errors.append("runtime status falsely marked PASS")

    conflicts = (root / "RUNTIME_CONFLICTS_V2_2.md").read_text(encoding="utf-8")
    required_conflict_phrases = ["passive_stat=DEF", "GetCollectionBonus(\"DEF\")", "현재 Maker 등록", "SpawnLayer 실행 시점", "11종"]
    for phrase in required_conflict_phrases:
        if phrase not in conflicts:
            errors.append(f"runtime conflict report missing: {phrase}")

    return errors, {
        "manifest_rows": len(manifest),
        "passives": passive_count,
        "projectiles": projectile_count,
        "styles": len(style_rows),
        "exclude_styles": len(excludes),
        "style_index_sha256": sha_file(root / "global_skill_style_library/STYLE_INDEX.csv"),
    }


def validate_all() -> dict:
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(), "areas": [], "errors": []}
    style_hashes = set()
    total_manifest = total_passive = total_projectile = 0
    for aid in TARGET_IDS:
        zip_path = OUT / f"{aid.upper()}_IMAGES_INPUT_V2_2.zip"
        source_zip = SOURCE / f"{aid.upper()}_IMAGES_INPUT_V2_1.zip"
        area_errors = []
        stats = {}
        if not zip_path.is_file():
            area_errors.append("missing V2.2 ZIP")
        else:
            with zipfile.ZipFile(zip_path) as archive:
                bad = archive.testzip()
                if bad:
                    area_errors.append(f"CRC failure: {bad}")
                with tempfile.TemporaryDirectory(prefix=f"verify_{aid}_") as td:
                    archive.extractall(td)
                    root = Path(td) / f"{aid.upper()}_IMAGES_INPUT_V2_2"
                    area_errors.extend(validate_package_dir(root, aid, source_zip)[0])
                    _, stats = validate_package_dir(root, aid, source_zip)
        if stats:
            total_manifest += stats["manifest_rows"]
            total_passive += stats["passives"]
            total_projectile += stats["projectiles"]
            style_hashes.add(stats["style_index_sha256"])
        area_result = {
            "area_id": aid,
            "zip": zip_path.name,
            "sha256": sha_file(zip_path) if zip_path.is_file() else "",
            "package_validation": "PASS" if not area_errors else "FAIL",
            "generation_ready": "READY" if not area_errors else "BLOCKED",
            "runtime_validation": "UNRESOLVED" if aid == "area_20" else "NOT_RUN",
            "art_approval": "NOT_REVIEWED",
            "errors": area_errors,
            **stats,
        }
        result["areas"].append(area_result)
        result["errors"].extend(f"{aid}: {error}" for error in area_errors)

    if total_manifest != 99:
        result["errors"].append(f"global manifest rows {total_manifest} != 99")
    if total_passive != 35:
        result["errors"].append(f"global passives {total_passive} != 35")
    if total_projectile != 12:
        result["errors"].append(f"global projectile placements {total_projectile} != 12")
    if len(style_hashes) != 1:
        result["errors"].append(f"style libraries diverge: {len(style_hashes)} hashes")
    if (OUT / "AREA_06_IMAGES_INPUT_V2_2.zip").exists():
        result["errors"].append("reserved Area 06 was created")

    # Source preservation: each V2.1 source hash must match the V2.2 revision record.
    for area in result["areas"]:
        aid = area["area_id"]
        with zipfile.ZipFile(OUT / area["zip"]) as archive:
            revision = archive.read(f"{aid.upper()}_IMAGES_INPUT_V2_2/PACKAGE_REVISION_V2_2.md").decode("utf-8-sig")
        recorded = re.search(r"source_sha256: `([0-9a-f]{64})`", revision)
        actual = sha_file(SOURCE / f"{aid.upper()}_IMAGES_INPUT_V2_1.zip")
        if not recorded or recorded.group(1) != actual:
            result["errors"].append(f"{aid}: V2.1 source changed or revision hash mismatch")

    # Area 00 frozen hashes from the prior baseline.
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    area00 = {
        "input_zip": ROOT / "docs/art/images-input-packages/AREA_00_IMAGES_INPUT.zip",
        "output_manifest": ROOT / "docs/art/area00-images-output/AREA_00_IMAGES_OUTPUT/OUTPUT_MANIFEST.md",
        "resource_map": ROOT / "docs/art/area00-images-output/AREA_00_IMAGES_RESOURCE_MAP.csv",
        "import_report": ROOT / "docs/art/area00-images-output/AREA_00_IMAGES_IMPORT_REPORT.md",
    }
    frozen = baseline["area00_frozen_sha256"]
    result["area00_preservation"] = {}
    for key, path in area00.items():
        actual = sha_file(path)
        ok = actual == frozen[key]
        result["area00_preservation"][key] = {"path": str(path.relative_to(ROOT)), "sha256": actual, "expected": frozen[key], "match": ok}
        if not ok:
            result["errors"].append(f"Area00 changed: {key}")

    result.update({
        "target_areas": len(result["areas"]),
        "package_pass": sum(a["package_validation"] == "PASS" for a in result["areas"]),
        "package_fail": sum(a["package_validation"] == "FAIL" for a in result["areas"]),
        "monster_placements": total_manifest,
        "passive_placements": total_passive,
        "projectile_placements": total_projectile,
        "area06_created": False,
        "overall": "PASS" if not result["errors"] else "FAIL",
    })
    return result


def write_validation(result: dict) -> None:
    (OUT / "INPUT_V2_2_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    lines = [
        "# INPUT V2.2 VALIDATION", "",
        f"- overall: **{result['overall']}**",
        f"- package validation: {result['package_pass']}/{result['target_areas']} PASS",
        f"- monster placements: {result['monster_placements']}",
        f"- passive placements: {result['passive_placements']}",
        f"- projectile placements: {result['projectile_placements']}",
        "- RUNTIME_VALIDATION: NOT_RUN (area_20 DEF conflict is UNRESOLVED)",
        "- ART_APPROVAL: NOT_REVIEWED", "",
        "| Area | PACKAGE_VALIDATION | GENERATION_READY | RUNTIME_VALIDATION | ART_APPROVAL | errors |",
        "|---|---|---|---|---|---|",
    ]
    for area in result["areas"]:
        lines.append(f"| {area['area_id']} | {area['package_validation']} | {area['generation_ready']} | {area['runtime_validation']} | {area['art_approval']} | {'; '.join(area['errors']) or '-'} |")
    if result["errors"]:
        lines += ["", "## Errors", ""] + [f"- {error}" for error in result["errors"]]
    (OUT / "INPUT_V2_2_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    index_path = OUT / "ALL_AREAS_INPUT_V2_2_INDEX.md"
    index = index_path.read_text(encoding="utf-8").replace("PENDING_INDEPENDENT", "PASS" if result["overall"] == "PASS" else "FAIL")
    index_path.write_text(index, encoding="utf-8", newline="\n")


def finalize_evidence(result: dict) -> None:
    regression_json = OUT / "INPUT_V2_2_REGRESSION_RESULTS.json"
    regression_md = OUT / "INPUT_V2_2_REGRESSION_RESULTS.md"
    if not regression_json.is_file() or not regression_md.is_file():
        raise RuntimeError("run test_area_images_input_v2_2_validator.py before --finalize")
    regression = json.loads(regression_json.read_text(encoding="utf-8"))
    if regression.get("overall") != "PASS":
        raise RuntimeError("regression tests did not pass")

    with tempfile.TemporaryDirectory(prefix="input_v2_2_evidence_") as td:
        evidence = Path(td) / "INPUT_V2_2_EVIDENCE"
        evidence.mkdir()
        shutil.copy2(CROSSCHECK, evidence / CROSSCHECK.name)
        reports = evidence / "reports"
        reports.mkdir()
        report_names = [
            "ALL_AREAS_INPUT_V2_2_INDEX.md", "INPUT_V2_2_CHANGELOG.md",
            "INPUT_V2_2_CHANGE_MATRIX.md",
            "INPUT_V2_2_ADDITIONAL_FINDINGS.md", "INPUT_V2_2_BEFORE_AFTER_EVIDENCE.csv",
            "INPUT_V2_2_BEFORE_AFTER_EVIDENCE.md", "INPUT_V2_2_REMAINING_DECISIONS.md",
            "PROJECTILE_SCOPE_REVIEW_V2_2.md", "ASSET_BINDING_PLAN_V2_2.csv",
            "INPUT_V2_2_VALIDATION.json", "INPUT_V2_2_VALIDATION.md",
            "INPUT_V2_2_REGRESSION_RESULTS.json", "INPUT_V2_2_REGRESSION_RESULTS.md",
            "BUILD_RESULT.json",
        ]
        for name in report_names:
            shutil.copy2(OUT / name, reports / name)

        scripts = evidence / "repro_scripts"
        scripts.mkdir()
        for name in ("build-area-images-input-v2_2.py", "verify_area_images_input_v2_2.py", "test_area_images_input_v2_2_validator.py"):
            shutil.copy2(ROOT / "docs/tools" / name, scripts / name)

        project = evidence / "project_evidence"
        evidence_paths = [
            "RootDesk/MyDesk/Combat/SkillProjectile.mlua",
            "RootDesk/MyDesk/Models/Effects/SkillProjectile.model",
            "RootDesk/MyDesk/Combat/SkillEffect.mlua",
            "RootDesk/MyDesk/PlayerAttack.mlua",
            "RootDesk/MyDesk/MonsterAttack.mlua",
            "RootDesk/MyDesk/Player/PlayerStats.mlua",
            "RootDesk/MyDesk/GameData/GameDataVerify.mlua",
            "RootDesk/MyDesk/GameData/GameBalance.csv",
        ]
        for rel in evidence_paths:
            target = project / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        baseline_dir = evidence / "baseline_commit"
        baseline_dir.mkdir()
        (baseline_dir / "SkillTable.csv").write_bytes(git_bytes(baseline["git_head"], "RootDesk/MyDesk/GameData/SkillTable.csv"))
        shutil.copy2(BASELINE, baseline_dir / "SOURCE_BASELINE.json")

        manifest_rows = []
        for path in sorted(evidence.rglob("*")):
            if path.is_file() and path.name != "EVIDENCE_MANIFEST.csv":
                manifest_rows.append({"path": path.relative_to(evidence).as_posix(), "sha256": sha_file(path), "bytes": path.stat().st_size})
        write_csv(evidence / "EVIDENCE_MANIFEST.csv", manifest_rows, ["path", "sha256", "bytes"])
        evidence_zip = OUT / "INPUT_V2_2_EVIDENCE.zip"
        with zipfile.ZipFile(evidence_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(evidence.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(evidence.parent).as_posix())

    hash_rows = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "INPUT_V2_2_HASHES.csv":
            hash_rows.append({"file": path.name, "sha256": sha_file(path), "bytes": path.stat().st_size})
    write_csv(OUT / "INPUT_V2_2_HASHES.csv", hash_rows, ["file", "sha256", "bytes"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    result = validate_all()
    write_validation(result)
    if result["overall"] != "PASS":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    if args.finalize:
        finalize_evidence(result)
    print(json.dumps({"overall": result["overall"], "areas": result["target_areas"], "monsters": result["monster_placements"], "finalized": args.finalize}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
