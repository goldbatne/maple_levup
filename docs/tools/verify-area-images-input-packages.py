from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "images-input-packages"


def csv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))


index = list(csv.DictReader((OUT / "ALL_AREAS_INDEX.csv").open("r", encoding="utf-8-sig", newline="")))
results = []
all_monsters = set()
all_errors = []

for row in index:
    area_id = row["area_id"]
    package = f"{area_id.upper()}_IMAGES_INPUT"
    zip_path = ROOT / row["zip_path"]
    errors = []
    if not zip_path.exists():
        errors.append("ZIP missing")
        results.append({"area_id": area_id, "status": "FAIL", "errors": errors})
        continue
    with zipfile.ZipFile(zip_path, "r") as z:
        bad = z.testzip()
        if bad:
            errors.append(f"CRC failed: {bad}")
        names = set(z.namelist())
        root = package + "/"
        required = [
            "README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md", "AREA_MANIFEST.md", "AREA_MANIFEST.csv",
            "OUTPUT_NAMING_SPEC.md", "OUTPUT_FORMAT_SPEC.md", "global_skill_style_library/STYLE_INDEX.md",
            "global_skill_style_library/STYLE_INDEX.csv", "global_skill_style_library/summary/STYLE_ATLAS.md",
        ]
        for rel in required:
            if root + rel not in names:
                errors.append("missing: " + rel)
        manifest = csv_rows(z.read(root + "AREA_MANIFEST.csv").decode("utf-8-sig")) if root + "AREA_MANIFEST.csv" in names else []
        if len(manifest) != int(row["monster_count"]):
            errors.append(f"manifest count {len(manifest)} != index {row['monster_count']}")
        mids = [m["monster_id"] for m in manifest]
        sids = [m["skill_id"] for m in manifest]
        if len(mids) != len(set(mids)):
            errors.append("duplicate monster_id")
        if len(sids) != len(set(sids)):
            errors.append("duplicate skill_id")
        all_monsters.update(mids)
        for m in manifest:
            folder = root + m["folder"].rstrip("/") + "/"
            for rel in ["MONSTER_IMAGE.png", "GENERATION_SPEC.md", "MONSTER_INFO.md"]:
                if folder + rel not in names:
                    errors.append(f"{m['monster_id']} missing {rel}")
            numbered_prefix = f"{int(m['work_order']):03d}_{int(m['level'])}_{m['monster_id']}_"
            if not any(n.startswith(folder + numbered_prefix) and n.endswith(".png") for n in names):
                errors.append(f"{m['monster_id']} missing numbered PNG")
            image_name = folder + "MONSTER_IMAGE.png"
            if image_name in names:
                try:
                    with Image.open(io.BytesIO(z.read(image_name))) as im:
                        rgba = im.convert("RGBA")
                        lo, hi = rgba.getchannel("A").getextrema()
                        if im.format != "PNG" or hi == 0 or lo == 255:
                            errors.append(f"{m['monster_id']} invalid PNG/alpha: format={im.format}, alpha={lo}~{hi}")
                except Exception as exc:
                    errors.append(f"{m['monster_id']} unreadable PNG: {exc}")
        style_csv = root + "global_skill_style_library/STYLE_INDEX.csv"
        styles = csv_rows(z.read(style_csv).decode("utf-8-sig")) if style_csv in names else []
        if len(styles) != 183:
            errors.append(f"style count {len(styles)} != 183")
        for s in styles:
            prefix = root + "global_skill_style_library/skills/"
            matches = [n for n in names if n.startswith(prefix) and n.endswith("/ruid.txt")]
            # Global counts are checked once below; per-RUID folder names need not be reconstructed from localized text.
        preview_count = sum(n.startswith(root + "global_skill_style_library/skills/") and n.endswith("/preview.png") for n in names)
        info_count = sum(n.startswith(root + "global_skill_style_library/skills/") and n.endswith("/info.md") for n in names)
        ruid_count = sum(n.startswith(root + "global_skill_style_library/skills/") and n.endswith("/ruid.txt") for n in names)
        if (preview_count, info_count, ruid_count) != (183, 183, 183):
            errors.append(f"style files preview/info/ruid = {preview_count}/{info_count}/{ruid_count}")
        if row["area_order"] == "1":
            for image_name in [n for n in names if n.startswith(root + "global_skill_style_library/skills/") and n.endswith("/preview.png")]:
                try:
                    with Image.open(io.BytesIO(z.read(image_name))) as im:
                        rgba = im.convert("RGBA")
                        if im.format != "PNG" or rgba.getchannel("A").getextrema()[1] == 0:
                            errors.append(f"invalid style preview: {image_name}")
                except Exception as exc:
                    errors.append(f"unreadable style preview: {image_name}: {exc}")
    status = "PASS" if not errors else "FAIL"
    results.append({"area_id": area_id, "status": status, "zip_bytes": zip_path.stat().st_size, "monster_count": len(manifest), "errors": errors})
    all_errors.extend(f"{area_id}: {e}" for e in errors)

expected_order = [int(r["area_order"]) for r in index]
if expected_order != list(range(1, len(index) + 1)):
    all_errors.append("Area order gap")
if len(index) != 20:
    all_errors.append(f"Area count {len(index)} != 20")
if len(all_monsters) != 101:
    all_errors.append(f"Unique monster count {len(all_monsters)} != 101")

summary = {
    "area_count": len(index),
    "zip_count": len(list(OUT.glob("AREA_*_IMAGES_INPUT.zip"))),
    "unique_monsters": len(all_monsters),
    "pass": sum(r["status"] == "PASS" for r in results),
    "fail": sum(r["status"] != "PASS" for r in results),
    "total_zip_bytes": sum(r.get("zip_bytes", 0) for r in results),
    "errors": all_errors,
}
(OUT / "PACKAGE_VALIDATION_REPORT.json").write_text(json.dumps({"summary": summary, "areas": results}, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "PACKAGE_VALIDATION_REPORT.md").write_text(
    "# Area Images Input Package Verification\n\n"
    f"- Area/ZIP: {summary['area_count']}/{summary['zip_count']}\n"
    f"- Unique monsters: {summary['unique_monsters']}\n"
    f"- PASS/FAIL: {summary['pass']}/{summary['fail']}\n"
    f"- Total ZIP bytes: {summary['total_zip_bytes']}\n"
    f"- Errors: {', '.join(all_errors) if all_errors else '없음'}\n\n"
    "검사 항목: ZIP CRC, 최상위 폴더, 필수 문서, Area manifest 수, monster_id/skill_id 중복, 몬스터 PNG/GENERATION_SPEC/MONSTER_INFO, 183개 style preview/info/RUID, Area 순서.\n",
    encoding="utf-8",
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
