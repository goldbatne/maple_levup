#!/usr/bin/env python3
"""Build full-frame content/style review evidence without altering artwork."""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import textwrap
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

import audit_monster_skill_output as audit


PREVIOUS_RUN = audit.AUDIT_DIR / "runs" / "20260912_143540"
REVIEW_FIELDS = [
    "area_id", "area_name", "monster_id", "monster_name", "skill_id",
    "skill_name", "skill_type", "boss", "roles", "actual_files",
    "input_core_material", "input_role_contract", "input_motion_contract",
    "input_time_flow", "input_icon_motif", "spec_fit_status",
    "spec_fit_basis", "style_status", "style_basis", "preview_match",
    "recommended_action", "user_approved",
]


def rows(zf: zipfile.ZipFile, rel: dict[str, str], name: str) -> list[dict[str, str]]:
    return audit.csv_rows(zf.read(rel[name]))


def bullet(text: str, label: str) -> str:
    prefix = f"- {label}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def fit_text(draw: ImageDraw.ImageDraw, value: str, width_chars: int) -> str:
    return "\n".join(textwrap.wrap(value, width=width_chars, break_long_words=False)[:3])


def load_png(zf: zipfile.ZipFile, member: str) -> Image.Image:
    image = Image.open(io.BytesIO(zf.read(member)))
    image.load()
    return image.convert("RGBA")


def paste_checker(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    w, h = box[2] - box[0], box[3] - box[1]
    bg = audit.checker((w, h), 10)
    image = image.copy()
    image.thumbnail((w - 8, h - 8), Image.Resampling.LANCZOS)
    bg.paste(image, ((w - image.width) // 2, (h - image.height) // 2), image)
    canvas.paste(bg, (box[0], box[1]))


def actual_assets(
    oz: zipfile.ZipFile, orel: dict[str, str], area: str,
) -> dict[tuple[str, str], dict[str, list[str]]]:
    manifest = audit.csv_rows(oz.read(orel["OUTPUT_MANIFEST.csv"]))
    normalized, _ = audit.normalize_output_manifest(manifest, area)
    result: dict[tuple[str, str], dict[str, list[tuple[int, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in normalized:
        path = row["relative_path"]
        if path not in orel or not path.lower().endswith(".png"):
            continue
        role = audit.OUT_TO_INPUT_ROLE.get(row["effect_role"], row["effect_role"])
        try:
            order = int(row["frame_index"])
        except (ValueError, TypeError):
            order = -1
        result[(row["monster_id"], row["skill_id"])][role].append((order, path))
    return {
        pair: {role: [p for _, p in sorted(values)] for role, values in roles.items()}
        for pair, roles in result.items()
    }


def build_area_board(
    area: str, area_name: str, manifest: list[dict[str, str]], records: list[dict[str, str]],
    iz: zipfile.ZipFile, irel: dict[str, str], oz: zipfile.ZipFile,
    orel: dict[str, str], assets: dict[tuple[str, str], dict[str, list[str]]], target: Path,
) -> None:
    width, header, row_h = 3200, 86, 360
    canvas = Image.new("RGB", (width, header + row_h * len(records)), (244, 244, 244))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 18), f"AREA {area} · {area_name} · full delivered frames vs INPUT V2.4", fill="black", font=audit.font(32, True))
    by_pair = {(m["monster_id"], m["skill_id"]): m for m in manifest}
    for index, record in enumerate(records):
        y = header + index * row_h
        draw.rectangle((0, y, width, y + row_h - 1), fill=(255, 255, 255) if index % 2 == 0 else (235, 241, 246))
        pair = (record["monster_id"], record["skill_id"])
        m = by_pair[pair]
        draw.text((18, y + 12), f"{int(m['work_order']):03d} {m['monster_name']} / {m['skill_name']} · {m['skill_type']}", fill=(10, 10, 10), font=audit.font(21, True))
        core = fit_text(draw, "CORE: " + record["input_core_material"], 58)
        flow = fit_text(draw, "FLOW: " + record["input_time_flow"], 58)
        draw.multiline_text((18, y + 48), core, fill=(50, 50, 50), font=audit.font(14), spacing=3)
        draw.multiline_text((18, y + 123), flow, fill=(70, 70, 70), font=audit.font(13), spacing=3)
        monster_path = f"{m['folder'].strip('/')}/MONSTER_IMAGE.png"
        draw.text((18, y + 214), "INPUT MONSTER", fill=(45, 75, 125), font=audit.font(13, True))
        if monster_path in irel:
            paste_checker(canvas, load_png(iz, irel[monster_path]), (18, y + 238, 144, y + 352))
        x = 172
        role_order = ["ICON", "CAST_VFX", "PROJECTILE", "REFERENCE_VFX"]
        for role in role_order:
            paths = assets.get(pair, {}).get(role, [])
            if not paths:
                continue
            draw.text((x, y + 214), role, fill=(100, 45, 115), font=audit.font(13, True))
            for p in paths:
                paste_checker(canvas, load_png(oz, orel[p]), (x, y + 238, x + 116, y + 352))
                frame = re.search(r"_F(\d+)\.png$", p, re.I)
                draw.text((x + 3, y + 337), frame.group(1) if frame else "ICON", fill=(50, 50, 50), font=audit.font(10))
                x += 122
            x += 20
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def build_cross_pages(entries: list[dict[str, object]], target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    per_page, cols, tile_w, tile_h = 25, 5, 540, 400
    for page_index in range(0, len(entries), per_page):
        subset = entries[page_index:page_index + per_page]
        canvas = Image.new("RGB", (cols * tile_w, 70 + 5 * tile_h), (242, 242, 242))
        draw = ImageDraw.Draw(canvas)
        draw.text((20, 16), f"Cross-Area style board · actual files · page {page_index // per_page + 1}", fill="black", font=audit.font(28, True))
        for i, entry in enumerate(subset):
            x, y = (i % cols) * tile_w, 70 + (i // cols) * tile_h
            draw.rectangle((x, y, x + tile_w - 2, y + tile_h - 2), fill="white", outline=(185, 185, 185))
            draw.text((x + 12, y + 10), f"{entry['area_id']} · {entry['monster_name']}", fill=(20, 20, 20), font=audit.font(18, True))
            draw.text((x + 12, y + 38), str(entry["skill_name"]), fill=(60, 60, 60), font=audit.font(15))
            draw.text((x + 12, y + 66), "MONSTER", fill=(40, 75, 120), font=audit.font(11, True))
            paste_checker(canvas, entry["monster"], (x + 12, y + 86, x + 172, y + 246))
            draw.text((x + 188, y + 66), "ICON", fill=(105, 45, 115), font=audit.font(11, True))
            if entry.get("icon"):
                paste_checker(canvas, entry["icon"], (x + 188, y + 86, x + 348, y + 246))
            draw.text((x + 364, y + 66), "PEAK", fill=(105, 45, 115), font=audit.font(11, True))
            if entry.get("peak"):
                paste_checker(canvas, entry["peak"], (x + 364, y + 86, x + 524, y + 246))
            draw.text((x + 12, y + 260), fit_text(draw, str(entry["core"]), 62), fill=(55, 55, 55), font=audit.font(12))
        canvas.save(target_dir / f"page_{page_index // per_page + 1:02d}.png")


def add_area00_reference(entries: list[dict[str, object]], baseline: dict[tuple[str, str], Path]) -> None:
    path = baseline[("AREA00_OUTPUT", "area_00")]
    with zipfile.ZipFile(path) as zf:
        root, rel = audit.relative_map(zf)
        folders = sorted({p.split("/", 2)[1] for p in rel if p.startswith("monsters/") and "/ICON/" in p})
        for folder in folders:
            icon_path = next(p for p in rel if p.startswith(f"monsters/{folder}/ICON/") and p.endswith(".png"))
            vfx = sorted(p for p in rel if p.startswith(f"monsters/{folder}/VFX/") and p.endswith(".png"))
            parts = folder.split("_", 3)
            entries.append({
                "area_id": "area_00", "monster_name": parts[-1].replace("_", " "),
                "skill_name": "approved golden sample", "core": "AREA 00 approved finish reference",
                "monster": load_png(zf, rel[icon_path]), "icon": load_png(zf, rel[icon_path]),
                "peak": load_png(zf, rel[vfx[len(vfx) // 2]]) if vfx else None,
            })


def main() -> int:
    previous = json.loads((PREVIOUS_RUN / "AUTO_AUDIT_DATA.json").read_text(encoding="utf-8"))
    baseline_rows = list(csv.DictReader(audit.BASELINE_INDEX.open(encoding="utf-8-sig", newline="")))
    baseline = {(r["kind"], r["area_id"]): Path(r["path"]) for r in baseline_rows}
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_content_style"
    run_dir = audit.RUNS_DIR / run_id
    area_dir = run_dir / "area_full_frame_boards"
    cross_dir = run_dir / "CROSS_AREA_STYLE_BOARD"
    issue_dir = run_dir / "issue_comparisons"
    for path in (run_dir, area_dir, cross_dir, issue_dir):
        path.mkdir(parents=True, exist_ok=True)

    previous_outputs = {a["area_id"]: a for a in previous["areas"]}
    review_records: list[dict[str, str]] = []
    cross_entries: list[dict[str, object]] = []
    reuse_rows = []
    add_area00_reference(cross_entries, baseline)

    for area in audit.AREAS:
        area_id = f"area_{area}"
        input_path = baseline[("AREA_INPUT", area_id)]
        output_path = audit.OUTPUT_DIR / f"AREA_{area}_IMAGES_OUTPUT.zip"
        actual_output_hash = audit.sha_file(output_path)
        previous_hash = previous_outputs[area_id]["output_sha256"]
        if actual_output_hash != previous_hash:
            raise RuntimeError(f"OUTPUT changed since prior audit: {area_id}")
        reuse_rows.append({
            "area_id": area_id, "input_sha256": audit.sha_file(input_path),
            "output_sha256": actual_output_hash,
            "mechanical_check_reused_from": "20260912_143540",
            "reuse_status": "REUSED_UNCHANGED_HASH",
        })
        with zipfile.ZipFile(input_path) as iz, zipfile.ZipFile(output_path) as oz:
            _, irel = audit.relative_map(iz)
            _, orel = audit.relative_map(oz)
            manifest = rows(iz, irel, "AREA_MANIFEST.csv")
            assets = actual_assets(oz, orel, area)
            area_records = []
            for m in manifest:
                pair = (m["monster_id"], m["skill_id"])
                spec_path = f"{m['folder'].strip('/')}/GENERATION_SPEC.md"
                role_path = f"{m['folder'].strip('/')}/RUNTIME_ROLE_MAP.md"
                spec = iz.read(irel[spec_path]).decode("utf-8-sig")
                role_text = iz.read(irel[role_path]).decode("utf-8-sig")
                actual = assets.get(pair, {})
                flat_paths = [p for role in actual.values() for p in role]
                rec = {
                    "area_id": area_id, "area_name": m["area_name"],
                    "monster_id": m["monster_id"], "monster_name": m["monster_name"],
                    "skill_id": m["skill_id"], "skill_name": m["skill_name"],
                    "skill_type": m["skill_type"], "boss": m["boss"],
                    "roles": "|".join(actual.keys()), "actual_files": "|".join(flat_paths),
                    "input_core_material": bullet(spec, "핵심 소재"),
                    "input_role_contract": bullet(spec, "런타임 역할"),
                    "input_motion_contract": bullet(spec, "진행 방향·엔진 이동"),
                    "input_time_flow": bullet(spec, "시간 흐름"),
                    "input_icon_motif": bullet(spec, "아이콘 핵심 모티브"),
                    "spec_fit_status": "NOT_CHECKED", "spec_fit_basis": "",
                    "style_status": "NOT_CHECKED", "style_basis": "",
                    "preview_match": "NOT_CHECKED", "recommended_action": "",
                    "user_approved": "NO",
                }
                review_records.append(rec)
                area_records.append(rec)
                monster_path = f"{m['folder'].strip('/')}/MONSTER_IMAGE.png"
                icon_path = (actual.get("ICON") or [None])[0]
                vfx = actual.get("CAST_VFX") or actual.get("PROJECTILE") or actual.get("REFERENCE_VFX") or []
                cross_entries.append({
                    "area_id": area_id, "monster_name": m["monster_name"],
                    "skill_name": m["skill_name"], "core": rec["input_core_material"],
                    "monster": load_png(iz, irel[monster_path]),
                    "icon": load_png(oz, orel[icon_path]) if icon_path else None,
                    "peak": load_png(oz, orel[vfx[len(vfx) // 2]]) if vfx else None,
                })
            build_area_board(area, manifest[0]["area_name"], manifest, area_records, iz, irel, oz, orel, assets, area_dir / f"AREA_{area}_ALL_FRAMES.png")

    build_cross_pages(cross_entries, cross_dir)
    audit.write_csv(run_dir / "CONTENT_STYLE_REVIEW.csv", review_records, REVIEW_FIELDS)
    audit.write_csv(run_dir / "REUSED_FILE_CHECKS.csv", reuse_rows, ["area_id", "input_sha256", "output_sha256", "mechanical_check_reused_from", "reuse_status"])
    (run_dir / "REVIEW_STATE.json").write_text(json.dumps({
        "run_id": run_id, "previous_run": str(PREVIOUS_RUN.resolve()),
        "rules_sha256": audit.sha_file(audit.RULES),
        "baseline_index_sha256": audit.sha_file(audit.BASELINE_INDEX),
        "records": len(review_records), "status": "VISUAL_REVIEW_PENDING",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir.resolve()), "records": len(review_records), "area_boards": len(audit.AREAS), "cross_pages": len(list(cross_dir.glob('*.png')))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
