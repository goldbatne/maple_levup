from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import shutil
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DOCS_ART = ROOT / "docs/art"
SOURCE_DIR = DOCS_ART / "output"
RESULT_ROOT = DOCS_ART / "output_repacked"
AUDIT_ROOT = DOCS_ART / "output_audit"
STYLE_RUN = AUDIT_ROOT / "runs/20260912_145815_content_style"
WORK_ROOT = DOCS_ART / "output_audit_work"
BASELINE = AUDIT_ROOT / "BASELINE_INDEX.csv"

TARGET_AREAS = ["01", "02", "03", "04", "05", "07", "08", "09", "10", "13", "14", "15", "16", "17", "18", "19", "20"]
HELD_AREAS = ["11", "12"]

MANIFEST_FIELDS = [
    "area_id", "area_name", "work_order", "monster_id", "monster_name",
    "skill_id", "skill_name", "skill_type", "effect_role",
    "production_decision", "runtime_use", "relative_path", "frame_index",
    "frame_count", "canvas", "frame_seconds", "playback_mode", "sha256",
    "user_art_approval",
]


def load_audit_module():
    path = ROOT / "docs/tools/audit_monster_skill_output.py"
    spec = importlib.util.spec_from_file_location("output_audit_module", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit = load_audit_module()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_file(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_zip_csv(zf: zipfile.ZipFile, rel: dict[str, str], name: str) -> list[dict[str, str]]:
    return audit.csv_rows(zf.read(rel[name]))


def write_csv_file(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def unique_run_dir() -> tuple[str, Path]:
    base = datetime.now().strftime("%Y%m%d_%H%M%S") + "_v24_repack"
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    candidate = RESULT_ROOT / base
    suffix = 2
    while candidate.exists():
        candidate = RESULT_ROOT / f"{base}_{suffix:02d}"
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate.name, candidate


def source_assets(
    oz: zipfile.ZipFile, orel: dict[str, str], area: str,
) -> dict[tuple[str, str, str], list[str]]:
    raw = audit.csv_rows(oz.read(orel["OUTPUT_MANIFEST.csv"]))
    normalized, _ = audit.normalize_output_manifest(raw, area)
    found: dict[tuple[str, str, str], list[tuple[int, str]]] = defaultdict(list)
    for row in normalized:
        path = row["relative_path"].replace("\\", "/")
        if path not in orel or not path.lower().endswith(".png"):
            continue
        role = audit.OUT_TO_INPUT_ROLE.get(row["effect_role"], row["effect_role"])
        try:
            index = int(float(row.get("frame_index", "0")))
        except ValueError:
            index = 0
        found[(row["monster_id"], row["skill_id"], role)].append((index, path))
    return {key: [p for _, p in sorted(values)] for key, values in found.items()}


def checker(size: tuple[int, int], cell: int = 12) -> Image.Image:
    canvas = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(canvas)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(x + cell, size[0]), min(y + cell, size[1])), fill=(226, 226, 226))
    return canvas


def paste_contain(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    base = checker((x1 - x0, y1 - y0))
    rgba = image.convert("RGBA")
    rgba.thumbnail((x1 - x0 - 10, y1 - y0 - 10), Image.Resampling.LANCZOS)
    x = (base.width - rgba.width) // 2
    y = (base.height - rgba.height) // 2
    base.paste(rgba, (x, y), rgba)
    canvas.paste(base, (x0, y0))


def load_image_bytes(data: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(data))
    image.load()
    return image.convert("RGBA")


def build_labeled_preview(
    stage_root: Path,
    monster: dict[str, str],
    input_monster_bytes: bytes,
    roles: list[tuple[str, list[str]]],
    destination: Path,
) -> None:
    width = 2200
    role_height = 235
    height = 175 + max(1, len(roles)) * role_height
    canvas = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, 125), fill=(28, 39, 55))
    draw.text((24, 16), f"{int(monster['work_order']):03d}  {monster['monster_name']} ({monster['monster_id']})", fill="white", font=audit.font(32, True))
    draw.text((24, 66), f"{monster['skill_name']} ({monster['skill_id']}) · {monster['skill_type']} · USER_ART_APPROVAL=PENDING", fill=(220, 230, 242), font=audit.font(23))
    paste_contain(canvas, load_image_bytes(input_monster_bytes), (24, 145, 244, min(height - 20, 365)))
    draw.text((24, min(height - 48, 370)), "INPUT MONSTER_IMAGE", fill=(50, 70, 100), font=audit.font(15, True))
    y = 145
    for role, paths in roles:
        draw.text((285, y), role, fill=(80, 45, 110), font=audit.font(19, True))
        x = 285
        for path in paths:
            image = Image.open(stage_root / Path(path))
            image.load()
            paste_contain(canvas, image, (x, y + 34, x + 185, y + 214))
            frame = re.search(r"_F(\d+)\.png$", path, re.I)
            draw.text((x + 5, y + 190), f"F{frame.group(1)}" if frame else "ICON", fill=(55, 55, 55), font=audit.font(13))
            x += 195
        y += role_height
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, "PNG")


def build_area_overview(area_name: str, previews: list[Path], destination: Path) -> None:
    width = 2200
    thumb_h = 520
    height = 115 + len(previews) * thumb_h
    canvas = Image.new("RGB", (width, height), (238, 241, 246))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, 90), fill=(30, 42, 58))
    area_no = destination.parent.name[5:7]
    draw.text((24, 18), f"AREA {area_no} · {area_name} · V2.4 REPACK PREVIEW", fill="white", font=audit.font(32, True))
    y = 105
    for preview in previews:
        with Image.open(preview) as im:
            im.load()
            copy = im.convert("RGB")
            copy.thumbnail((width - 30, thumb_h - 15), Image.Resampling.LANCZOS)
            canvas.paste(copy, (15, y))
        y += thumb_h
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, "PNG")


def result_info(monster: dict[str, str], roles: list[tuple[str, list[str]]]) -> str:
    role_lines = []
    for role, paths in roles:
        role_lines.append(f"- {role}: {len(paths)} file(s)")
        for path in paths:
            role_lines.append(f"  - `{path}`")
    return "\n".join(
        [
            "# RESULT_INFO — V2.4 REPACK",
            "",
            f"- area_id: {monster['area_id']}",
            f"- area_name: {monster['area_name']}",
            f"- work_order: {int(monster['work_order']):03d}",
            f"- monster_id: {monster['monster_id']}",
            f"- monster_name: {monster['monster_name']}",
            f"- skill_id: {monster['skill_id']}",
            f"- skill_name: {monster['skill_name']}",
            f"- skill_type: {monster['skill_type']}",
            "- input_contract: approved INPUT V2.4",
            "- user_art_approval: PENDING",
            "- runtime_validation: NOT_RUN",
            "- original_role_png_bytes: PRESERVED",
            "",
            "## Delivered roles",
            "",
            *role_lines,
            "",
            "Preview와 문서만 재구성했으며 VFX/PROJECTILE/REFERENCE/ICON PNG는 원본 ZIP의 바이트를 그대로 복사했다.",
            "",
        ]
    )


def zip_directory(stage: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            zf.write(path, path.relative_to(stage.parent).as_posix())


def create_area_package(
    area: str,
    input_path: Path,
    source_path: Path,
    run_dir: Path,
    stage_parent: Path,
) -> tuple[Path | None, list[dict[str, str]], list[str]]:
    area_id = f"area_{area}"
    errors: list[str] = []
    mappings: list[dict[str, str]] = []
    stage_root = stage_parent / f"AREA_{area}_IMAGES_OUTPUT"
    stage_root.mkdir(parents=True)

    with zipfile.ZipFile(input_path) as iz, zipfile.ZipFile(source_path) as oz:
        _, irel = audit.relative_map(iz)
        _, orel = audit.relative_map(oz)
        manifest = read_zip_csv(iz, irel, "AREA_MANIFEST.csv")
        scope = read_zip_csv(iz, irel, "FULL_ART_SCOPE.csv")
        manifest_by = {(m["monster_id"], m["skill_id"]): m for m in manifest}
        source_by = source_assets(oz, orel, area)
        manifest_rows: list[dict[str, str]] = []
        delivered_by_pair: dict[tuple[str, str], list[tuple[str, list[str]]]] = defaultdict(list)

        for s in scope:
            if s["production_decision"] == "NO_RUNTIME_ROLE":
                continue
            pair = (s["monster_id"], s["skill_id"])
            monster = manifest_by.get(pair)
            if not monster:
                errors.append(f"{pair}: missing AREA_MANIFEST row")
                continue
            role = s["effect_role"]
            expected = audit.expected_paths(s, monster)
            sources = source_by.get((pair[0], pair[1], role), [])
            if len(sources) != len(expected):
                errors.append(
                    f"{pair}/{role}: source count {len(sources)} != expected {len(expected)}"
                )
                continue
            delivered_by_pair[pair].append((role, expected))
            for index, (src_rel, dst_rel) in enumerate(zip(sources, expected)):
                if src_rel not in orel:
                    errors.append(f"{pair}/{role}: source path missing {src_rel}")
                    continue
                data = oz.read(orel[src_rel])
                destination = stage_root / Path(dst_rel)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                digest = sha_bytes(data)
                mappings.append(
                    {
                        "area_id": area_id,
                        "monster_id": pair[0],
                        "skill_id": pair[1],
                        "role": role,
                        "frame_index": "0" if role == "ICON" else str(index),
                        "source_zip": source_path.name,
                        "source_path": src_rel,
                        "output_path": dst_rel,
                        "source_sha256": digest,
                        "output_sha256": digest,
                        "byte_preserved": "PASS",
                    }
                )
                manifest_rows.append(
                    {
                        "area_id": monster["area_id"],
                        "area_name": monster["area_name"],
                        "work_order": f"{int(monster['work_order']):03d}",
                        "monster_id": monster["monster_id"],
                        "monster_name": monster["monster_name"],
                        "skill_id": monster["skill_id"],
                        "skill_name": monster["skill_name"],
                        "skill_type": monster["skill_type"],
                        "effect_role": audit.ROLE_OUT[role],
                        "production_decision": s["production_decision"],
                        "runtime_use": s["runtime_use"],
                        "relative_path": dst_rel,
                        "frame_index": "0" if role == "ICON" else str(index),
                        "frame_count": str(int(float(s["frame_count"]))),
                        "canvas": s["canvas"],
                        "frame_seconds": s["frame_seconds"],
                        "playback_mode": s["playback_mode"],
                        "sha256": digest,
                        "user_art_approval": "PENDING",
                    }
                )

        if errors:
            shutil.rmtree(stage_root)
            return None, mappings, errors

        preview_paths = []
        for monster in manifest:
            pair = (monster["monster_id"], monster["skill_id"])
            roles = delivered_by_pair[pair]
            monster_image = f"{monster['folder'].strip('/')}/MONSTER_IMAGE.png"
            if monster_image not in irel:
                errors.append(f"{pair}: missing INPUT MONSTER_IMAGE {monster_image}")
                continue
            result_path = stage_root / monster["folder"] / "RESULT_INFO.md"
            result_path.parent.mkdir(parents=True, exist_ok=True)
            result_path.write_text(result_info(monster, roles), encoding="utf-8")
            preview_path = stage_root / monster["folder"] / "PREVIEW/labeled_preview.png"
            build_labeled_preview(
                stage_root, monster, iz.read(irel[monster_image]), roles, preview_path
            )
            preview_paths.append(preview_path)

        if errors:
            shutil.rmtree(stage_root)
            return None, mappings, errors

        build_area_overview(
            manifest[0]["area_name"], preview_paths, stage_root / "AREA_OVERVIEW_PREVIEW.png"
        )
        write_csv_file(stage_root / "OUTPUT_MANIFEST.csv", manifest_rows, MANIFEST_FIELDS)
        md_lines = [
            f"# AREA {area} OUTPUT MANIFEST — V2.4 REPACK",
            "",
            f"- area_id: {area_id}",
            f"- area_name: {manifest[0]['area_name']}",
            f"- input_revision: V2.4",
            f"- source_output_sha256: {sha_file(source_path)}",
            f"- role_png_count: {len(manifest_rows)}",
            "- original_role_png_bytes: PRESERVED",
            "- user_art_approval: PENDING",
            "- runtime_validation: NOT_RUN",
            "",
            "세부 파일별 매핑과 SHA-256은 `OUTPUT_MANIFEST.csv` 및 실행 폴더의 `PNG_BYTE_PRESERVATION.csv`를 따른다.",
            "",
        ]
        (stage_root / "OUTPUT_MANIFEST.md").write_text("\n".join(md_lines), encoding="utf-8")
        (stage_root / "REPACK_INFO.md").write_text(
            "\n".join(
                [
                    "# REPACK_INFO",
                    "",
                    "이 패키지는 승인 INPUT V2.4 구조에 맞춘 원화 무변경 REPACK이다.",
                    "VFX·PROJECTILE·REFERENCE·ICON PNG는 원본 OUTPUT 바이트를 그대로 사용했다.",
                    "Preview와 문서만 다시 만들었으며 사용자 아트 승인이나 런타임 통과를 의미하지 않는다.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    target = run_dir / f"AREA_{area}_IMAGES_OUTPUT.zip"
    zip_directory(stage_root, target)
    return target, mappings, errors


def hold_report(content_rows: list[dict[str, str]], run_dir: Path) -> None:
    lookup = {(r["area_id"], r["monster_id"]): r for r in content_rows}
    king = lookup[("area_11", "m_king_bloctopus")]
    trojan = lookup[("area_12", "m_toy_trojan")]
    evidence_dir = run_dir / "HOLD_EVIDENCE"
    evidence_dir.mkdir(parents=True)
    copies = []
    for source_name in (
        "AREA_11_m_king_bloctopus_CAST_PROJECTILE.png",
        "AREA_12_m_toy_trojan_CAST.png",
    ):
        src = STYLE_RUN / "issue_comparisons" / source_name
        dst = evidence_dir / source_name
        shutil.copyfile(src, dst)
        copies.append(dst.name)
    text = f"""# AREA 11·12 REPACK HOLD

## AREA 11 — 킹 블록퍼스 / 왕관 블록탄

- 상태: `REGENERATE_CANDIDATE`, 이번 실행에서 ZIP 미생성.
- 보류 역할: `CAST_VFX`, `PROJECTILE`.
- 정확한 핵심 소재: {king['input_core_material']}
- 정확한 역할 계약: {king['input_role_contract']}
- 정확한 진행/엔진 계약: {king['input_motion_contract']}
- ICON 모티브: {king['input_icon_motif']}
- 판정 근거: {king['spec_fit_basis']}
- 비교 이미지: `HOLD_EVIDENCE/{copies[0]}`
- ICON과 다른 몬스터 에셋은 원본 OUTPUT에 그대로 보존되어 있으며, 이번 보류로 수정·삭제하지 않았다.

## AREA 12 — 장난감 목마 / 태엽 목마 돌진

- 상태: `USER_REVIEW`, 이번 실행에서 ZIP 미생성.
- 판단 대기 역할: `CAST_VFX`.
- 정확한 핵심 소재: {trojan['input_core_material']}
- 정확한 역할 계약: {trojan['input_role_contract']}
- 정확한 진행/엔진 계약: {trojan['input_motion_contract']}
- ICON 모티브: {trojan['input_icon_motif']}
- 판정 근거: {trojan['spec_fit_basis']}
- 비교 이미지: `HOLD_EVIDENCE/{copies[1]}`
- 판단 질문: CAST의 눈 달린 목마 머리/몸통 조각을 ICON에 허용된 '목마 머리 + 바퀴 속도선'의 확장으로 볼지, VFX 금지사항인 몬스터 본체·얼굴 삽입으로 볼지 결정이 필요하다.

두 Area 모두 원화 재생성, 알파 수정, 크롭, 게임 반입을 수행하지 않았다.
"""
    (run_dir / "HOLD_AREA_11_12.md").write_text(text, encoding="utf-8")


def revalidate(
    area: str,
    package: Path,
    input_path: Path,
    mapping_rows: list[dict[str, str]],
    run_id: str,
) -> tuple[str, list[str]]:
    errors: list[str] = []
    extraction = WORK_ROOT / run_id / f"AREA_{area}_REEXTRACTED"
    extraction.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package) as zf:
        bad = zf.testzip()
        if bad:
            errors.append(f"CRC failure: {bad}")
        safe = audit.safe_zip_issues(zf)
        errors.extend(safe)
        audit.safe_extract(zf, extraction)
    visual_dir = WORK_ROOT / run_id / "REVALIDATION_CONTACTS"
    area_row, _, findings, _ = audit.audit_area(
        area, package, input_path, extraction / "audit_area", visual_dir
    )
    errors.extend(
        f"{f['role']} {f['relative_path']}: {f['observed']}"
        for f in findings
        if f["file_status"] == "FAIL"
    )
    root = extraction / f"AREA_{area}_IMAGES_OUTPUT"
    for row in mapping_rows:
        target = root / Path(row["output_path"])
        if not target.exists():
            errors.append(f"re-extracted PNG missing: {row['output_path']}")
            continue
        if sha_file(target) != row["source_sha256"]:
            errors.append(f"re-extracted hash mismatch: {row['output_path']}")
    if area_row.get("file_status") != "PASS":
        errors.append("canonical V2.4 audit did not return PASS")
    return ("PASS" if not errors else "FAIL"), sorted(set(errors))


def main() -> int:
    content_rows = read_csv_file(STYLE_RUN / "CONTENT_STYLE_REVIEW.csv")
    action_rows = read_csv_file(STYLE_RUN / "ACTION_ITEMS_UPDATED.csv")
    baseline_rows = read_csv_file(BASELINE)
    baseline = {(r["kind"], r["area_id"]): r for r in baseline_rows}
    reuse_rows = read_csv_file(STYLE_RUN / "REUSED_FILE_CHECKS.csv")
    source_hashes = {r["area_id"]: r["output_sha256"] for r in reuse_rows}

    review_areas = {r["area_id"] for r in content_rows if r["packaging_action"] == "REPACK_ONLY"}
    if review_areas != {f"area_{n}" for n in TARGET_AREAS + HELD_AREAS}:
        raise SystemExit("CONTENT_STYLE_REVIEW area scope changed")
    hold_actions = {
        (r["area_id"], r["monster_id"], r["art_action"])
        for r in content_rows if r["art_action"] != "NONE"
    }
    expected_holds = {
        ("area_11", "m_king_bloctopus", "REGENERATE_CANDIDATE"),
        ("area_12", "m_toy_trojan", "USER_REVIEW"),
    }
    if hold_actions != expected_holds:
        raise SystemExit(f"unexpected art hold set: {hold_actions}")
    if not action_rows:
        raise SystemExit("ACTION_ITEMS_UPDATED.csv is empty")

    run_id, run_dir = unique_run_dir()
    stage_parent = WORK_ROOT / run_id / "STAGING"
    stage_parent.mkdir(parents=True, exist_ok=True)
    hold_report(content_rows, run_dir)

    all_mappings: list[dict[str, str]] = []
    status_rows: list[dict[str, str]] = []
    packages: dict[str, Path] = {}
    inputs: dict[str, Path] = {}

    for area in TARGET_AREAS:
        area_id = f"area_{area}"
        input_row = baseline[("AREA_INPUT", area_id)]
        input_path = Path(input_row["path"])
        source_path = SOURCE_DIR / f"AREA_{area}_IMAGES_OUTPUT.zip"
        inputs[area] = input_path
        pre_errors = []
        if sha_file(input_path) != input_row["sha256"]:
            pre_errors.append("baseline INPUT V2.4 hash mismatch")
        if sha_file(source_path) != source_hashes[area_id]:
            pre_errors.append("source OUTPUT hash changed since content/style review")
        if pre_errors:
            status_rows.append(
                {
                    "area_id": area_id,
                    "repack_status": "UNRESOLVED",
                    "revalidation_status": "NOT_RUN",
                    "zip_path": "",
                    "png_count": "0",
                    "png_bytes_changed": "0",
                    "issues": " | ".join(pre_errors),
                }
            )
            continue
        package, mappings, errors = create_area_package(
            area, input_path, source_path, run_dir, stage_parent
        )
        all_mappings.extend(mappings)
        if package is None:
            status_rows.append(
                {
                    "area_id": area_id,
                    "repack_status": "UNRESOLVED",
                    "revalidation_status": "NOT_RUN",
                    "zip_path": "",
                    "png_count": str(len(mappings)),
                    "png_bytes_changed": str(sum(r["byte_preserved"] != "PASS" for r in mappings)),
                    "issues": " | ".join(errors),
                }
            )
            continue
        packages[area] = package
        status_rows.append(
            {
                "area_id": area_id,
                "repack_status": "COMPLETE",
                "revalidation_status": "PENDING",
                "zip_path": str(package.resolve()),
                "png_count": str(len(mappings)),
                "png_bytes_changed": str(sum(r["byte_preserved"] != "PASS" for r in mappings)),
                "issues": "",
            }
        )

    mapping_by_area: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_mappings:
        mapping_by_area[row["area_id"][-2:]].append(row)
    status_by_area = {r["area_id"][-2:]: r for r in status_rows}
    for area, package in packages.items():
        result, errors = revalidate(
            area, package, inputs[area], mapping_by_area[area], run_id
        )
        status_by_area[area]["revalidation_status"] = result
        status_by_area[area]["issues"] = " | ".join(errors)

    status_rows.extend(
        [
            {
                "area_id": "area_11",
                "repack_status": "HELD",
                "revalidation_status": "UNRESOLVED",
                "zip_path": "",
                "png_count": "0",
                "png_bytes_changed": "0",
                "issues": "m_king_bloctopus CAST_VFX|PROJECTILE REGENERATE_CANDIDATE; see HOLD_AREA_11_12.md",
            },
            {
                "area_id": "area_12",
                "repack_status": "HELD",
                "revalidation_status": "UNRESOLVED",
                "zip_path": "",
                "png_count": "0",
                "png_bytes_changed": "0",
                "issues": "m_toy_trojan CAST_VFX USER_REVIEW; see HOLD_AREA_11_12.md",
            },
        ]
    )
    status_rows.sort(key=lambda r: int(r["area_id"][-2:]))

    write_csv_file(
        run_dir / "PNG_BYTE_PRESERVATION.csv",
        all_mappings,
        [
            "area_id", "monster_id", "skill_id", "role", "frame_index",
            "source_zip", "source_path", "output_path", "source_sha256",
            "output_sha256", "byte_preserved",
        ],
    )
    write_csv_file(
        run_dir / "REPACK_AREA_STATUS.csv",
        status_rows,
        [
            "area_id", "repack_status", "revalidation_status", "zip_path",
            "png_count", "png_bytes_changed", "issues",
        ],
    )
    write_csv_file(
        run_dir / "REVALIDATION.csv",
        [
            {
                "area_id": r["area_id"],
                "status": r["revalidation_status"],
                "zip_path": r["zip_path"],
                "issues": r["issues"],
            }
            for r in status_rows
        ],
        ["area_id", "status", "zip_path", "issues"],
    )

    counts = Counter(r["revalidation_status"] for r in status_rows)
    changed = sum(r["byte_preserved"] != "PASS" for r in all_mappings)
    completed = [r for r in status_rows if r["revalidation_status"] == "PASS"]
    unresolved = [r for r in status_rows if r["revalidation_status"] == "UNRESOLVED"]
    failures = [r for r in status_rows if r["revalidation_status"] == "FAIL"]
    zip_lines = "\n".join(f"- {r['area_id']}: `{r['zip_path']}`" for r in completed)
    unresolved_lines = "\n".join(f"- {r['area_id']}: {r['issues']}" for r in unresolved + failures) or "- 없음"
    summary = f"""# V2.4 OUTPUT REPACK REPORT

## 결과

- 실행: `{run_id}`
- REPACK 완료/재검증 PASS: {len(completed)} Area
- 재검증 FAIL: {len(failures)} Area
- 미확인/보류: {len(unresolved)} Area
- 복사한 역할 PNG: {len(all_mappings)}개
- 원화 PNG 바이트 변경: {changed}개
- 사용자 아트 승인: 기록하지 않음 (`PENDING` 유지)
- 런타임 검증: `NOT_RUN`

## 완료 ZIP

{zip_lines or '- 없음'}

## 보류·미해결

{unresolved_lines}

## 원화 보존

`PNG_BYTE_PRESERVATION.csv`에서 원본 ZIP 상대경로 → 새 V2.4 경로와 양쪽 SHA-256을 기록했다. 새 ZIP을 다시 추출한 뒤에도 같은 해시를 확인했다. VFX·PROJECTILE·REFERENCE·ICON에는 리사이즈, 재인코딩, 알파 수정, 크롭, 재중앙화, 재생성을 수행하지 않았다.

## AREA 09 Preview

Malgun Gothic으로 Preview만 다시 합성했다. 실제 역할 PNG는 다른 Area와 동일하게 바이트 복사했다.

## AREA 11·12

정확한 INPUT 문구와 기존 확대 비교 이미지는 `HOLD_AREA_11_12.md`와 `HOLD_EVIDENCE/`에 보존했다. 두 Area ZIP은 생성하지 않았고 원본 OUTPUT도 변경하지 않았다.

REPACK PASS는 패키지/해시/구조 검증 결과이며 사용자 아트 승인 또는 Maker·런타임 통과가 아니다.
"""
    (run_dir / "REPACK_SUMMARY.md").write_text(summary, encoding="utf-8")
    (run_dir / "RUN_STATE.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "source_dir": str(SOURCE_DIR.resolve()),
                "baseline_index": str(BASELINE.resolve()),
                "content_style_run": str(STYLE_RUN.resolve()),
                "target_areas": TARGET_AREAS,
                "held_areas": HELD_AREAS,
                "revalidation_counts": dict(counts),
                "role_png_count": len(all_mappings),
                "role_png_bytes_changed": changed,
                "user_art_approval": "PENDING",
                "runtime_validation": "NOT_RUN",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (RESULT_ROOT / "LATEST_REPACK.md").write_text(
        f"# Latest V2.4 OUTPUT REPACK\n\n- [{run_id}/REPACK_SUMMARY.md]({run_id}/REPACK_SUMMARY.md)\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "run_dir": str(run_dir.resolve()),
        "pass": len(completed),
        "fail": len(failures),
        "unresolved": len(unresolved),
        "role_pngs": len(all_mappings),
        "role_png_bytes_changed": changed,
    }, ensure_ascii=False, indent=2))
    return 0 if not failures and len(completed) == len(TARGET_AREAS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
