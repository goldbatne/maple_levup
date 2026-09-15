from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "images-input-packages"
COMMAND_VALIDATION = ROOT / "docs" / "art" / "skill_reference_collection" / "ALL_AREA_COMMAND_SYSTEM_VALIDATION.json"


def rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


index = list(csv.DictReader((OUT / "ALL_AREAS_INDEX.csv").open("r", encoding="utf-8-sig", newline="")))
results = []
all_errors = []
all_monsters = set()
placement_count = 0

if COMMAND_VALIDATION.exists():
    command_validation = json.loads(COMMAND_VALIDATION.read_text(encoding="utf-8"))
    expected_zip_hashes = {row["area"]: row["zip_sha256"] for row in command_validation["areas"]}
else:
    expected_zip_hashes = {}
    all_errors.append(f"current command validation missing: {COMMAND_VALIDATION.relative_to(ROOT)}")

for entry in index:
    num = entry["area_num"]
    package = f"AREA_{num}_IMAGES_INPUT"
    zip_path = OUT / entry["zip_file"]
    prompt_path = OUT / entry["prompt_file"]
    errors = []
    if not zip_path.exists():
        errors.append("ZIP missing")
        results.append({"area_num": num, "area_id": entry["area_id"], "status": "FAIL", "errors": errors})
        all_errors.extend(f"AREA {num}: {error}" for error in errors)
        continue
    zip_digest = sha(zip_path.read_bytes())
    if expected_zip_hashes.get(num) != zip_digest:
        errors.append("ZIP differs from current command-system validation")
    with zipfile.ZipFile(zip_path) as z:
        root = package + "/"
        names = set(z.namelist())
        bad = z.testzip()
        if bad:
            errors.append(f"CRC failed: {bad}")
        required = [
            "README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md", "AREA_MANIFEST.md", "AREA_MANIFEST.csv",
            "OUTPUT_NAMING_SPEC.md", "OUTPUT_FORMAT_SPEC.md", "QUALITY_GATE.md", "SOURCE_STATE_CURRENT.md",
            "INPUT_FILE_HASHES.csv", "global_skill_style_library/STYLE_INDEX.md",
            "global_skill_style_library/STYLE_INDEX.csv", "global_skill_style_library/summary/STYLE_ATLAS.md",
            "global_skill_style_library/RESOURCE_API_SNAPSHOT.json",
            "global_skill_style_library/CURRENTNESS_EXCLUSIONS.md",
            "global_skill_style_library/area00_finish_baseline/AREA_OVERVIEW_PREVIEW.png",
            "global_skill_style_library/area00_finish_baseline/STYLE_BASELINE_CANDIDATE.md",
        ]
        for rel in required:
            if root + rel not in names:
                errors.append("missing: " + rel)

        manifest_member = root + "AREA_MANIFEST.csv"
        manifest = rows(z.read(manifest_member).decode("utf-8-sig")) if manifest_member in names else []
        placement_count += len(manifest)
        if len(manifest) != int(entry["monster_count"]):
            errors.append(f"manifest count {len(manifest)} != index {entry['monster_count']}")
        mids = [m["monster_id"] for m in manifest]
        sids = [m["skill_id"] for m in manifest]
        if len(mids) != len(set(mids)):
            errors.append("duplicate monster_id in Area")
        if len(sids) != len(set(sids)):
            errors.append("duplicate skill_id in Area")
        all_monsters.update(mids)

        for m in manifest:
            folder = m["folder"].rstrip("/") + "/"
            for rel in [
                "MONSTER_IMAGE.png",
                "GENERATION_SPEC.md",
                "MONSTER_INFO.md",
                "RUNTIME_ROLE_MAP.md",
                "SOURCE_PROVENANCE.md",
                "DESIGN_REFERENCE_BRIEF.md",
            ]:
                if root + folder + rel not in names:
                    errors.append(f"{m['monster_id']} missing {rel}")
            image_member = root + folder + "MONSTER_IMAGE.png"
            if image_member in names:
                data = z.read(image_member)
                try:
                    with Image.open(io.BytesIO(data)) as im:
                        rgba = im.convert("RGBA")
                        lo, hi = rgba.getchannel("A").getextrema()
                        if im.format != "PNG" or hi == 0 or lo == 255:
                            errors.append(f"{m['monster_id']} invalid PNG/alpha: {im.format} {lo}~{hi}")
                except Exception as exc:
                    errors.append(f"{m['monster_id']} unreadable PNG: {exc}")
            spec_member = root + folder + "GENERATION_SPEC.md"
            if spec_member in names:
                spec = z.read(spec_member).decode("utf-8-sig")
                if "## 스킬별 확정 디자인 참조" not in spec:
                    errors.append(f"{m['monster_id']} missing current design-reference section")
                if "ultimate_psychic_shot_vi_historical" in spec:
                    errors.append(f"{m['monster_id']} uses historical negative as positive assignment")

        style_member = root + "global_skill_style_library/STYLE_INDEX.csv"
        styles = rows(z.read(style_member).decode("utf-8-sig")) if style_member in names else []
        if len(styles) != 6:
            errors.append(f"curated style count {len(styles)} != 6")
        for style in styles:
            folder = f"global_skill_style_library/{int(style['order']):02d}_{style['key']}/"
            for rel in ["info.md", "ruid.txt", "icon_preview.png", "animation_preview.gif"]:
                if root + folder + rel not in names:
                    errors.append(f"missing reference file {folder}{rel}")

        prompt_member = root + "CHATGPT_IMAGES_MASTER_PROMPT.md"
        if prompt_member in names:
            prompt = z.read(prompt_member).decode("utf-8-sig")
            external_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
            normalized_zip_prompt = prompt.replace("\r\n", "\n").replace("\r", "\n")
            if not prompt_path.exists() or external_prompt != normalized_zip_prompt:
                errors.append("external production prompt differs from ZIP prompt")
            for phrase in [
                "native image generation/editing — version/model unverified",
                "준비→성장→절정→해체→fade",
                f"AREA_{num}_IMAGES_OUTPUT",
            ]:
                if phrase not in prompt:
                    errors.append(f"prompt missing phrase: {phrase}")

        hash_member = root + "INPUT_FILE_HASHES.csv"
        if hash_member in names:
            hashes = rows(z.read(hash_member).decode("utf-8-sig"))
            for record in hashes:
                member = root + record["path"]
                if member not in names:
                    errors.append(f"hash manifest missing target {record['path']}")
                elif sha(z.read(member)) != record["sha256"]:
                    errors.append(f"hash mismatch {record['path']}")

    status = "PASS" if not errors else "FAIL"
    result = {
        "area_num": num,
        "area_id": entry["area_id"],
        "status": status,
        "monster_count": int(entry["monster_count"]),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": zip_digest,
        "errors": errors,
    }
    results.append(result)
    all_errors.extend(f"AREA {num}: {error}" for error in errors)

expected = [f"{n:02d}" for n in range(21) if n != 6]
actual = [row["area_num"] for row in index]
if actual != expected:
    all_errors.append(f"Area order/set mismatch: {actual}")
if len(list(OUT.glob("AREA_[0-9][0-9]_IMAGES_INPUT.zip"))) != 20:
    all_errors.append("canonical ZIP count is not 20")
if len(list(OUT.glob("AREA_[0-9][0-9]_CHATGPT_PRODUCTION_PROMPT.txt"))) != 20:
    all_errors.append("external prompt count is not 20")
if placement_count != 104:
    all_errors.append(f"skill placement count {placement_count} != 104")
if len(all_monsters) != 101:
    all_errors.append(f"unique monster count {len(all_monsters)} != 101")

summary = {
    "area_count": len(index),
    "zip_count": len(list(OUT.glob("AREA_[0-9][0-9]_IMAGES_INPUT.zip"))),
    "prompt_count": len(list(OUT.glob("AREA_[0-9][0-9]_CHATGPT_PRODUCTION_PROMPT.txt"))),
    "skill_placements": placement_count,
    "unique_monsters": len(all_monsters),
    "pass": sum(r["status"] == "PASS" for r in results),
    "fail": sum(r["status"] != "PASS" for r in results),
    "total_zip_bytes": sum(r["zip_bytes"] for r in results),
    "errors": all_errors,
}
(OUT / "PACKAGE_VALIDATION_REPORT.json").write_text(
    json.dumps({"summary": summary, "areas": results}, ensure_ascii=False, indent=2), encoding="utf-8"
)
(OUT / "PACKAGE_VALIDATION_REPORT.md").write_text(
    "# Area Images Input Package Verification\n\n"
    f"- Area/ZIP/prompt: {summary['area_count']}/{summary['zip_count']}/{summary['prompt_count']}\n"
    f"- Skill placements / unique monsters: {summary['skill_placements']}/{summary['unique_monsters']}\n"
    f"- PASS/FAIL: {summary['pass']}/{summary['fail']}\n"
    f"- Total ZIP bytes: {summary['total_zip_bytes']}\n"
    f"- Errors: {', '.join(all_errors) if all_errors else '없음'}\n\n"
    "검사: 최종 command-system 검증 해시, ZIP CRC, 필수 문서, manifest/내부 hash, MONSTER_IMAGE PNG/alpha, 6개 선별 reference, "
    "역사적 negative reference 미할당, 외부/내부 프롬프트 일치, 핵심 품질 문구, 내부 hash manifest, Area 집합.\n",
    encoding="utf-8",
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
raise SystemExit(0 if not all_errors and summary["fail"] == 0 else 1)
