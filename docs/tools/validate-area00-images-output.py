#!/usr/bin/env python3
"""Validate and stage the user-supplied Area 00 Images output ZIP.

The PNG files are copied byte-for-byte.  No resize, crop, recenter, colour, or
alpha operation is performed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from PIL import Image


REPO = Path(__file__).resolve().parents[2]
SOURCE_ZIP = Path(r"C:/Users/dddd/Downloads/AREA_00_IMAGES_OUTPUT.zip")
STAGE = REPO / "docs" / "art" / "area00-images-output"
ORIGINAL = STAGE / "AREA_00_IMAGES_OUTPUT_ORIGINAL.zip"
EXTRACTED = STAGE / "AREA_00_IMAGES_OUTPUT"
REPORT_JSON = STAGE / "AREA_00_OUTPUT_VALIDATION.json"
REPORT_MD = STAGE / "AREA_00_OUTPUT_VALIDATION.md"

EXPECTED = {
    "m_snail": ("달팽이", "s_mon_snail_dew_trail", "이슬 미끄럼길", "액티브", 8),
    "m_blue_snail": ("파란 달팽이", "s_mon_blue_snail", "푸른 껍질", "버프", 8),
    "m_red_snail": ("빨간 달팽이", "s_mon_red_snail", "붉은 껍질 돌진", "액티브", 8),
    "m_mano": ("마노", "s_mon_mano", "마노의 무지개 파동", "액티브", 12),
    "m_slime": ("슬라임", "s_mon_slime", "끈적한 몸통", "액티브", 8),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_extract(zf: zipfile.ZipFile, dest: Path) -> None:
    root = dest.resolve()
    for info in zf.infolist():
        rel = PurePosixPath(info.filename)
        if rel.is_absolute() or ".." in rel.parts:
            raise RuntimeError(f"Unsafe ZIP member: {info.filename}")
        target = (dest / Path(*rel.parts)).resolve()
        if root not in target.parents and target != root:
            raise RuntimeError(f"ZIP member escapes target: {info.filename}")
    zf.extractall(dest)


def read_project_rows() -> tuple[dict, dict]:
    with (REPO / "RootDesk/MyDesk/GameData/MonsterTable.csv").open("r", encoding="utf-8-sig", newline="") as fp:
        monsters = {r["id"]: r for r in csv.DictReader(fp)}
    with (REPO / "RootDesk/MyDesk/GameData/SkillTable.csv").open("r", encoding="utf-8-sig", newline="") as fp:
        skills = {r["id"]: r for r in csv.DictReader(fp)}
    return monsters, skills


def inspect_png(path: Path) -> dict:
    with Image.open(path) as image:
        image.load()
        mode = image.mode
        size = list(image.size)
        if mode != "RGBA":
            return {"file": path.name, "mode": mode, "size": size, "valid": False, "error": "not RGBA"}
        alpha = image.getchannel("A")
        alpha_min, alpha_max = alpha.getextrema()
        bbox = alpha.getbbox()
        return {
            "file": path.name,
            "mode": mode,
            "size": size,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "alpha_bbox": list(bbox) if bbox else None,
            "has_transparency": alpha_min < 255,
            "has_visible_pixels": alpha_max > 0,
            "sha256": digest(path),
            "bytes": path.stat().st_size,
            "valid": alpha_min < 255 and alpha_max > 0,
        }


def main() -> None:
    if not SOURCE_ZIP.is_file():
        raise SystemExit(f"Missing source ZIP: {SOURCE_ZIP}")
    STAGE.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE_ZIP, ORIGINAL)
    if EXTRACTED.exists():
        shutil.rmtree(EXTRACTED)
    temp = STAGE / "_extract"
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir()
    with zipfile.ZipFile(ORIGINAL) as zf:
        safe_extract(zf, temp)
    source_root = temp / "AREA_00_IMAGES_OUTPUT"
    if not source_root.is_dir():
        raise RuntimeError("Expected AREA_00_IMAGES_OUTPUT root folder")
    # Windows can reject an in-place directory rename here while Maker or an
    # antivirus scanner still has a handle open.  A mechanical recursive copy
    # preserves every input byte and is safe to rerun.
    shutil.copytree(source_root, EXTRACTED)
    shutil.rmtree(temp)

    with (EXTRACTED / "OUTPUT_MANIFEST.csv").open("r", encoding="utf-8-sig", newline="") as fp:
        manifest = list(csv.DictReader(fp))
    monsters, skills = read_project_rows()
    errors: list[str] = []
    results: list[dict] = []
    seen = set()
    for row in manifest:
        mid = row["monster_id"]
        seen.add(mid)
        if mid not in EXPECTED:
            errors.append(f"Unexpected monster_id: {mid}")
            continue
        exp_name, exp_sid, exp_skill_name, exp_type, exp_count = EXPECTED[mid]
        checks = {
            "manifest_monster_name": row["monster_name"] == exp_name,
            "manifest_skill_id": row["skill_id"] == exp_sid,
            "manifest_skill_name": row["skill_name"] == exp_skill_name,
            "manifest_skill_type": row["skill_type"] == exp_type,
            "manifest_frame_count": int(row["vfx_frame_count"]) == exp_count,
            "project_monster_exists": mid in monsters,
            "project_skill_exists": exp_sid in skills,
            "project_monster_name": monsters.get(mid, {}).get("name") == exp_name,
            "project_skill_name": skills.get(exp_sid, {}).get("name") == exp_skill_name,
            "drop_skill_link": monsters.get(mid, {}).get("drop_skill_id") == exp_sid,
            "monster_slot": skills.get(exp_sid, {}).get("slot_type") == "monster",
        }
        for key, ok in checks.items():
            if not ok:
                errors.append(f"{mid}: {key} failed")
        folder = EXTRACTED / row["folder"]
        result_info = folder / "RESULT_INFO.md"
        if not result_info.is_file():
            errors.append(f"{mid}: RESULT_INFO.md missing")
        prefix = f"{row['work_order']}_{mid}_{exp_sid}_F"
        frame_paths = sorted((folder / "VFX").glob(f"{prefix}*.png"))
        expected_names = [f"{prefix}{i:02d}.png" for i in range(exp_count)]
        actual_names = [p.name for p in frame_paths]
        if actual_names != expected_names:
            errors.append(f"{mid}: frame order/names mismatch: {actual_names}")
        frames = [inspect_png(p) for p in frame_paths]
        if any(not f["valid"] for f in frames):
            errors.append(f"{mid}: invalid RGBA/alpha frame")
        frame_sizes = {tuple(f["size"]) for f in frames}
        if len(frame_sizes) != 1:
            errors.append(f"{mid}: frame canvas mismatch: {sorted(frame_sizes)}")
        icon_path = EXTRACTED / row["icon_file"]
        if not icon_path.is_file():
            errors.append(f"{mid}: icon missing: {row['icon_file']}")
            icon = None
        else:
            icon = inspect_png(icon_path)
            if not icon["valid"]:
                errors.append(f"{mid}: invalid icon RGBA/alpha")
        results.append({
            "work_order": row["work_order"],
            "monster_id": mid,
            "monster_name": exp_name,
            "skill_id": exp_sid,
            "skill_name": exp_skill_name,
            "skill_type": exp_type,
            "expected_frames": exp_count,
            "frame_canvas": list(next(iter(frame_sizes))) if len(frame_sizes) == 1 else None,
            "frames": frames,
            "icon": icon,
            "project_checks": checks,
        })
    if seen != set(EXPECTED):
        errors.append(f"Monster set mismatch: got {sorted(seen)}, expected {sorted(EXPECTED)}")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_zip": str(SOURCE_ZIP),
        "preserved_zip": str(ORIGINAL),
        "source_zip_bytes": SOURCE_ZIP.stat().st_size,
        "source_zip_sha256": digest(SOURCE_ZIP),
        "preserved_zip_sha256": digest(ORIGINAL),
        "byte_identical_original_copy": digest(SOURCE_ZIP) == digest(ORIGINAL),
        "manifest_rows": len(manifest),
        "monsters": results,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
        "mechanical_processing": "byte-for-byte copy and safe extraction only; no image transform",
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# AREA 00 Images Output Validation",
        "",
        f"- 판정: **{report['verdict']}**",
        f"- 원본 SHA-256: `{report['source_zip_sha256']}`",
        f"- 원본 보존 복사본 동일: {report['byte_identical_original_copy']}",
        f"- 대상: {len(results)}종",
        f"- 오류: {len(errors)}건",
        "- 이미지 처리: 바이트 복사와 안전한 압축 해제만 수행. 리사이즈·분할·크롭·재중앙화·알파 변경 없음.",
        "",
        "| monster_id | skill_id | frames | canvas | frame RGBA/alpha | ICON RGBA/alpha | project match |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for item in results:
        frame_ok = len(item["frames"]) == item["expected_frames"] and all(f["valid"] for f in item["frames"])
        icon_ok = bool(item["icon"] and item["icon"]["valid"])
        project_ok = all(item["project_checks"].values())
        canvas = "×".join(map(str, item["frame_canvas"])) if item["frame_canvas"] else "불일치"
        lines.append(f"| `{item['monster_id']}` | `{item['skill_id']}` | {len(item['frames'])}/{item['expected_frames']} | {canvas} | {'PASS' if frame_ok else 'FAIL'} | {'PASS' if icon_ok else 'FAIL'} | {'PASS' if project_ok else 'FAIL'} |")
    lines += ["", "## Errors", ""] + ([f"- {e}" for e in errors] if errors else ["- 없음"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "monsters"}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
