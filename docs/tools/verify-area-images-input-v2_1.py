#!/usr/bin/env python3
"""Independent verifier for generated AREA INPUT V2.1 ZIPs and evidence ZIP."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import tempfile
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "images-input-packages-v2_1"
V2 = ROOT / "docs" / "art" / "images-input-packages-v2"
AREA00 = ROOT / "docs" / "art" / "area00-images-output"
TARGET_IDS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]
REQUIRED_ROOT = [
    "AREA_MANIFEST.csv", "AREA_MANIFEST.md", "README_START_HERE.md",
    "CHATGPT_IMAGES_MASTER_PROMPT.md", "OUTPUT_NAMING_SPEC.md",
    "OUTPUT_FORMAT_SPEC.md", "ASSET_BINDING_PLAN.csv", "ASSET_BINDING_PLAN.md",
    "DATA_SOURCE_RESOLUTION.md", "PROJECTILE_SCOPE_REVIEW.md",
    "PACKAGE_REVISION_V2_1.md", "runtime_evidence/RUNTIME_CODE_EVIDENCE.md",
    "global_skill_style_library/STYLE_INDEX.csv",
    "global_skill_style_library/STYLE_INDEX.md",
    "global_skill_style_library/summary/STYLE_ATLAS.md",
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(data: bytes | str) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return list(csv.DictReader(io.StringIO(text)))


def exact_white(data: bytes) -> bool:
    with Image.open(io.BytesIO(data)) as im:
        rgba = im.convert("RGBA")
        return all(a > 0 and r == 255 and g == 255 and b == 255 for r, g, b, a in rgba.getdata())


def safe_text(z: zipfile.ZipFile, name: str) -> str:
    return z.read(name).decode("utf-8-sig")


def main() -> None:
    errors: list[str] = []
    area_results = []
    common_style_hashes = set()
    v2_frozen_before = {p.name: sha_file(p) for p in sorted(V2.glob("AREA_*_IMAGES_INPUT_V2.zip"))}
    baseline = json.loads((V2 / "SOURCE_BASELINE.json").read_text(encoding="utf-8"))
    area00_hashes = {
        "input_zip": sha_file(ROOT / "docs" / "art" / "images-input-packages" / "AREA_00_IMAGES_INPUT.zip"),
        "output_manifest": sha_file(AREA00 / "AREA_00_IMAGES_OUTPUT" / "OUTPUT_MANIFEST.md"),
        "resource_map": sha_file(AREA00 / "AREA_00_IMAGES_RESOURCE_MAP.csv"),
        "import_report": sha_file(AREA00 / "AREA_00_IMAGES_IMPORT_REPORT.md"),
    }
    if area00_hashes != baseline["area00_frozen_sha256"]:
        errors.append("AREA 00 frozen hashes changed")

    zips = sorted(OUT.glob("AREA_*_IMAGES_INPUT_V2_1.zip"))
    if len(zips) != 19:
        errors.append(f"expected 19 area zips, got {len(zips)}")
    if (OUT / "AREA_06_IMAGES_INPUT_V2_1.zip").exists():
        errors.append("reserved AREA 06 exists")

    total_monsters = 0
    total_specs = 0
    total_white = None
    total_binding_monsters = 0
    for aid in TARGET_IDS:
        path = OUT / f"{aid.upper()}_IMAGES_INPUT_V2_1.zip"
        local_errors = []
        if not path.exists() or not zipfile.is_zipfile(path):
            local_errors.append("missing/not zip")
            area_results.append({"area_id": aid, "status": "FAIL", "errors": local_errors})
            errors.extend(f"{aid}: {e}" for e in local_errors)
            continue
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad:
                local_errors.append(f"CRC {bad}")
            root = f"{aid.upper()}_IMAGES_INPUT_V2_1/"
            names = set(z.namelist())
            for rel in REQUIRED_ROOT:
                if root + rel not in names:
                    local_errors.append(f"missing {rel}")

            try:
                manifest = rows(z.read(root + "AREA_MANIFEST.csv"))
                binding = rows(z.read(root + "ASSET_BINDING_PLAN.csv"))
            except KeyError as exc:
                local_errors.append(f"manifest/binding missing {exc}")
                manifest, binding = [], []
            total_monsters += len(manifest)
            total_binding_monsters += len({(r.get("monster_id"), r.get("skill_id")) for r in binding})

            # Identity fields must equal immutable V2 manifest; only actual_motion may change.
            with zipfile.ZipFile(V2 / f"{aid.upper()}_IMAGES_INPUT_V2.zip") as old:
                old_manifest = rows(old.read(f"{aid.upper()}_IMAGES_INPUT_V2/AREA_MANIFEST.csv"))
            fixed = ["work_order", "level", "area_id", "area_name", "monster_id", "monster_name",
                     "monster_image_ruid", "skill_id", "skill_name", "skill_type", "actual_effect", "boss", "folder"]
            if len(old_manifest) != len(manifest):
                local_errors.append("manifest row count changed")
            else:
                for a, b in zip(old_manifest, manifest):
                    for col in fixed:
                        if a.get(col) != b.get(col):
                            local_errors.append(f"fixed field changed {a.get('monster_id')}:{col}")
                    if not b.get("actual_motion"):
                        local_errors.append(f"actual_motion empty {b.get('monster_id')}")

            for row in manifest:
                folder = root + row["folder"] + "/"
                for rel in ("MONSTER_IMAGE.png", "MONSTER_INFO.md", "SOURCE_PROVENANCE.md", "GENERATION_SPEC.md", "RUNTIME_ROLE_MAP.md"):
                    if folder + rel not in names:
                        local_errors.append(f"missing {row['monster_id']} {rel}")
                for rel in ("GENERATION_SPEC.md", "RUNTIME_ROLE_MAP.md"):
                    if folder + rel in names:
                        text = safe_text(z, folder + rel)
                        total_specs += int(rel == "GENERATION_SPEC.md")
                        for phrase in ("## V2.1 실제 동작·납품 동기화", "actual_motion:", "labeled_preview.png", "AREA_OVERVIEW_PREVIEW.png", "(0.5,0.5)"):
                            if phrase not in text:
                                local_errors.append(f"{row['monster_id']} {rel} missing {phrase}")
                if not any(r.get("monster_id") == row["monster_id"] and r.get("skill_id") == row["skill_id"] for r in binding):
                    local_errors.append(f"binding absent {row['monster_id']}")

            # Style index / info synchronization and white-preview exclusion.
            try:
                style_data = z.read(root + "global_skill_style_library/STYLE_INDEX.csv")
                common_style_hashes.add(sha_bytes(style_data))
                styles = rows(style_data)
                if len(styles) != 183:
                    local_errors.append(f"style count {len(styles)}")
                white_count = 0
                for s in styles:
                    dirs = [n for n in names if n.startswith(root + f"global_skill_style_library/skills/{int(s['index']):04d}_") and n.endswith("/preview.png")]
                    infos = [n for n in names if n.startswith(root + f"global_skill_style_library/skills/{int(s['index']):04d}_") and n.endswith("/info.md")]
                    if len(dirs) != 1 or len(infos) != 1:
                        local_errors.append(f"style files {s['index']}")
                        continue
                    white = exact_white(z.read(dirs[0]))
                    white_count += int(white)
                    expected = "false" if white else "true"
                    if s.get("preview_usable") != expected:
                        local_errors.append(f"preview usable mismatch {s['index']}")
                    if s.get("reference_role") != s.get("role_classification"):
                        local_errors.append(f"role mismatch {s['index']}")
                    info = safe_text(z, infos[0])
                    for value in (s.get("reference_role", ""), s.get("style_priority", ""), f"preview_usable: `{expected}`"):
                        if value not in info:
                            local_errors.append(f"info sync mismatch {s['index']}:{value}")
                if total_white is None:
                    total_white = white_count
                elif total_white != white_count:
                    local_errors.append("common white count differs")
            except KeyError as exc:
                local_errors.append(f"style missing {exc}")

            # Delivery contract and no absolute local dependencies.
            for rel in ("OUTPUT_NAMING_SPEC.md", "OUTPUT_FORMAT_SPEC.md", "README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md"):
                if root + rel in names:
                    t = safe_text(z, root + rel)
                    for phrase in ("labeled_preview.png", "AREA_OVERVIEW_PREVIEW.png", "AREA_XX_IMAGES_OUTPUT"):
                        if phrase not in t:
                            local_errors.append(f"{rel} missing {phrase}")
                    if re.search(r"(?:[A-Za-z]:\\|[A-Za-z]:/)", t):
                        local_errors.append(f"absolute path in {rel}")

            # Approved reuse files must remain byte-identical to Area 00 output.
            reuse_names = [n for n in names if n.startswith(root + "approved_reuse/AREA_00/") and n.endswith(".png")]
            for name in reuse_names:
                suffix = name.split("approved_reuse/AREA_00/", 1)[1]
                source = AREA00 / "AREA_00_IMAGES_OUTPUT" / "monsters" / suffix
                if not source.exists() or sha_bytes(z.read(name)) != sha_file(source):
                    local_errors.append(f"reuse mismatch {suffix}")

        status = "PASS" if not local_errors else "FAIL"
        area_results.append({"area_id": aid, "status": status, "errors": local_errors, "zip_sha256": sha_file(path)})
        errors.extend(f"{aid}: {e}" for e in local_errors)

    if total_monsters != 99:
        errors.append(f"expected 99 monster placements, got {total_monsters}")
    if total_specs != 99:
        errors.append(f"expected 99 generation specs, got {total_specs}")
    if total_white != 8:
        errors.append(f"expected 8 exact-white previews, got {total_white}")
    if len(common_style_hashes) != 1:
        errors.append(f"style library mismatch: {len(common_style_hashes)} hashes")
    if v2_frozen_before != {p.name: sha_file(p) for p in sorted(V2.glob("AREA_*_IMAGES_INPUT_V2.zip"))}:
        errors.append("V2 ZIP hashes changed during verification")

    evidence_zip = OUT / "INPUT_V2_1_EVIDENCE.zip"
    evidence_errors = []
    if not evidence_zip.exists() or not zipfile.is_zipfile(evidence_zip):
        evidence_errors.append("evidence ZIP missing/not zip")
    else:
        with zipfile.ZipFile(evidence_zip) as z:
            bad = z.testzip()
            if bad:
                evidence_errors.append(f"CRC {bad}")
            root = "INPUT_V2_1_EVIDENCE/"
            required = [
                "prior_v2_reports/INPUT_V2_ADDITIONAL_FINDINGS.md",
                "prior_v2_reports/INPUT_V2_VALIDATION.md", "prior_v2_reports/INPUT_V2_CHANGELOG.md",
                "prior_v2_reports/ALL_AREAS_INPUT_V2_INDEX.md", "prior_v2_reports/SOURCE_BASELINE.json",
                "baseline_commit/RootDesk/MyDesk/GameData/SkillTable.csv",
                "baseline_commit/RootDesk/MyDesk/GameData/SkillTable.userdataset",
                "DATA_SOURCE_RESOLUTION.md", "RUNTIME_CODE_EVIDENCE.md", "ASSET_BINDING_PLAN.csv",
                "PROJECTILE_SCOPE_REVIEW.md", "INPUT_V2_1_CHANGELOG.md",
                "INPUT_V2_1_VALIDATION.md", "INPUT_V2_1_ADDITIONAL_FINDINGS.md",
                "ALL_AREAS_INPUT_V2_1_INDEX.md", "EVIDENCE_MANIFEST.csv", "MISSING_EVIDENCE.md",
            ]
            names = set(z.namelist())
            for rel in required:
                if root + rel not in names:
                    evidence_errors.append(f"missing {rel}")
            if root + "EVIDENCE_MANIFEST.csv" in names:
                for r in rows(z.read(root + "EVIDENCE_MANIFEST.csv")):
                    name = root + r["evidence_path"]
                    if name not in names:
                        evidence_errors.append(f"manifest missing {r['evidence_path']}")
                    elif sha_bytes(z.read(name)) != r["sha256"]:
                        evidence_errors.append(f"manifest hash {r['evidence_path']}")

    errors.extend("evidence: " + x for x in evidence_errors)
    result = {
        "verified_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "target_areas": 19, "validated_zips": len(zips), "monster_placements": total_monsters,
        "generation_specs": total_specs, "pass": sum(x["status"] == "PASS" for x in area_results),
        "fail": sum(x["status"] == "FAIL" for x in area_results), "area06_absent": not (OUT / "AREA_06_IMAGES_INPUT_V2_1.zip").exists(),
        "common_style_hash_count": len(common_style_hashes), "exact_white_previews": total_white,
        "area00_frozen": area00_hashes == baseline["area00_frozen_sha256"],
        "v2_frozen": v2_frozen_before == {p.name: sha_file(p) for p in sorted(V2.glob("AREA_*_IMAGES_INPUT_V2.zip"))},
        "evidence_zip_valid": not evidence_errors, "area_results": area_results, "errors": errors,
    }

    # Put the independent result into the evidence ZIP and refresh its manifest.
    if evidence_zip.exists() and zipfile.is_zipfile(evidence_zip):
        with tempfile.TemporaryDirectory(prefix="v2_1_verify_") as td:
            temp = Path(td)
            with zipfile.ZipFile(evidence_zip) as z:
                z.extractall(temp)
            ev = temp / "INPUT_V2_1_EVIDENCE"
            report_json = ev / "INPUT_V2_1_INDEPENDENT_VALIDATION.json"
            report_md = ev / "INPUT_V2_1_INDEPENDENT_VALIDATION.md"
            report_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
            report_md.write_text(
                "# INPUT V2.1 INDEPENDENT VALIDATION\n\n"
                f"- Area ZIP: {result['pass']}/19 PASS\n- placements/specs: {total_monsters}/{total_specs}\n"
                f"- style common hash: {len(common_style_hashes)}\n- exact-white excluded: {total_white}\n"
                f"- Area00 frozen: {result['area00_frozen']}\n- V2 frozen: {result['v2_frozen']}\n"
                f"- errors: {len(errors)}\n\n이 검사는 ZIP 재개봉·CRC·고정 필드·style/info 동기화·alpha 프리뷰 판정·재사용 해시·증빙 manifest를 확인했다. 파일 검증은 사용자 아트 승인이 아니다.\n",
                encoding="utf-8", newline="\n")
            manifest_path = ev / "EVIDENCE_MANIFEST.csv"
            manifest = rows(manifest_path.read_bytes())
            manifest = [r for r in manifest if r["evidence_path"] not in {report_json.name, report_md.name}]
            for p in (report_json, report_md):
                manifest.append({"evidence_path": p.name, "source_path": "generated", "source_version": "independent verifier", "available": "true", "sha256": sha_file(p), "bytes": p.stat().st_size})
            with manifest_path.open("w", encoding="utf-8-sig", newline="") as fp:
                w = csv.DictWriter(fp, fieldnames=["evidence_path", "source_path", "source_version", "available", "sha256", "bytes"])
                w.writeheader(); w.writerows(manifest)
            rebuilt = OUT / "INPUT_V2_1_EVIDENCE.verified.tmp.zip"
            with zipfile.ZipFile(rebuilt, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for p in sorted(ev.rglob("*")):
                    if p.is_file():
                        z.write(p, p.relative_to(ev.parent).as_posix())
            rebuilt.replace(evidence_zip)

    (OUT / "INPUT_V2_1_INDEPENDENT_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    (OUT / "INPUT_V2_1_INDEPENDENT_VALIDATION.md").write_text(
        "# INPUT V2.1 INDEPENDENT VALIDATION\n\n"
        f"- Area ZIP PASS: {result['pass']}/19\n- errors: {len(errors)}\n- evidence ZIP: {'PASS' if not evidence_errors else 'FAIL'}\n",
        encoding="utf-8", newline="\n")
    build_result = OUT / "BUILD_RESULT.json"
    if build_result.exists():
        build = json.loads(build_result.read_text(encoding="utf-8"))
        build["evidence_zip_sha256_after_independent_validation"] = sha_file(evidence_zip)
        build["independent_validation"] = {"pass": result["pass"], "fail": result["fail"], "errors": len(errors)}
        build_result.write_text(json.dumps(build, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
