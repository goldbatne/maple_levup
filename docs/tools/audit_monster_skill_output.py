#!/usr/bin/env python3
"""Audit monster-skill art OUTPUT ZIPs against frozen INPUT V2.4 baselines.

This tool is intentionally read-only for INPUT/OUTPUT archives and game data.
It extracts copies into output_audit_work, writes reports, and mechanically
composes comparison sheets. It never generates or modifies artwork.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import stat
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath

from PIL import Image, ImageDraw, ImageFont


DOCS_ART = Path(__file__).resolve().parents[1] / "art"
OUTPUT_DIR = DOCS_ART / "output"
AUDIT_DIR = DOCS_ART / "output_audit"
RUNS_DIR = AUDIT_DIR / "runs"
WORK_DIR = DOCS_ART / "output_audit_work"
V24_DIR = DOCS_ART / "images-input-packages-v2_4"
AREA00_INPUT = DOCS_ART / "images-input-packages" / "AREA_00_IMAGES_INPUT.zip"
AREA00_OUTPUT = DOCS_ART / "area00-images-output" / "AREA_00_IMAGES_OUTPUT_ORIGINAL.zip"
AREA00_MAP = DOCS_ART / "area00-images-output" / "AREA_00_IMAGES_RESOURCE_MAP.csv"
AREA00_IMPORT_REPORT = DOCS_ART / "area00-images-output" / "AREA_00_IMAGES_IMPORT_REPORT.md"
RULES = AUDIT_DIR / "AUDIT_RULES.md"
BASELINE_INDEX = AUDIT_DIR / "BASELINE_INDEX.csv"

AREAS = [f"{n:02d}" for n in range(1, 21) if n != 6]
ROLE_OUT = {"ICON": "ICON", "CAST_VFX": "CAST", "PROJECTILE": "PROJECTILE", "REFERENCE_VFX": "REFERENCE"}
ROLE_DIR = {"ICON": "ICON", "CAST_VFX": "CAST", "PROJECTILE": "PROJECTILE", "REFERENCE_VFX": "REFERENCE"}
OUT_TO_INPUT_ROLE = {"ICON": "ICON", "CAST": "CAST_VFX", "CAST_VFX": "CAST_VFX", "PROJECTILE": "PROJECTILE", "REFERENCE": "REFERENCE_VFX", "REFERENCE_VFX": "REFERENCE_VFX"}
FILE_STATUS = {"PASS", "FAIL", "NOT_CHECKED"}
VISUAL_STATUS = {"NO_OBVIOUS_ISSUE", "ISSUE_FOUND", "NEEDS_USER_REVIEW", "NOT_CHECKED"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def csv_rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def zip_member(zf: zipfile.ZipFile, suffix: str) -> str:
    hits = [n for n in zf.namelist() if n.replace("\\", "/").endswith(suffix)]
    if len(hits) != 1:
        raise ValueError(f"expected one {suffix}, found {hits}")
    return hits[0]


def relative_map(zf: zipfile.ZipFile) -> tuple[str, dict[str, str]]:
    files = [n.replace("\\", "/") for n in zf.namelist() if not n.endswith("/")]
    roots = {n.split("/", 1)[0] for n in files}
    if len(roots) != 1:
        raise ValueError(f"archive must have one root, found {sorted(roots)}")
    root = next(iter(roots))
    return root, {n[len(root) + 1:]: orig for n, orig in zip(files, [x for x in zf.namelist() if not x.endswith("/")])}


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def baseline_candidates() -> list[dict[str, str]]:
    result = []
    for area in AREAS:
        path = (V24_DIR / f"AREA_{area}_IMAGES_INPUT_V2_4.zip").resolve()
        with zipfile.ZipFile(path) as zf:
            revision_member = zip_member(zf, "/PACKAGE_REVISION_V2_4.md")
            revision_text = zf.read(revision_member).decode("utf-8-sig")
            if "V2.4" not in revision_text:
                raise RuntimeError(f"internal revision mismatch: {path}")
        result.append({
            "kind": "AREA_INPUT", "area_id": f"area_{area}", "revision": "V2.4",
            "approval_status": "GENERATION_READY", "path": str(path), "sha256": sha_file(path),
            "identity_evidence": "internal PACKAGE_REVISION_V2_4.md",
        })
    for kind, area_id, revision, status, path, evidence in (
        ("AREA00_INPUT", "area_00", "approved pilot input", "APPROVED_BASELINE", AREA00_INPUT, "internal Area 00 manifest/runbook"),
        ("AREA00_OUTPUT", "area_00", "approved original output", "APPROVED_BASELINE", AREA00_OUTPUT, "approved output archive + import report"),
        ("AREA00_RESOURCE_MAP", "area_00", "current approved map", "APPROVED_BASELINE", AREA00_MAP, "icon/AnimationClip/frame RUID mapping"),
        ("AREA00_IMPORT_REPORT", "area_00", "approved import report", "APPROVED_BASELINE", AREA00_IMPORT_REPORT, "recorded Area 00 approval/import evidence"),
        ("V24_VALIDATION", "all", "V2.4", "PASS", V24_DIR / "INPUT_V2_4_VALIDATION.md", "independent package validation"),
    ):
        resolved = path.resolve()
        if not resolved.exists():
            raise RuntimeError(f"baseline file missing: {resolved}")
        result.append({
            "kind": kind, "area_id": area_id, "revision": revision,
            "approval_status": status, "path": str(resolved), "sha256": sha_file(resolved),
            "identity_evidence": evidence,
        })
    return result


def ensure_baseline() -> tuple[list[dict[str, str]], list[str]]:
    current = baseline_candidates()
    errors = []
    fields = ["kind", "area_id", "revision", "approval_status", "path", "sha256", "identity_evidence"]
    if not BASELINE_INDEX.exists():
        write_csv(BASELINE_INDEX, current, fields)
        return current, errors
    with BASELINE_INDEX.open(encoding="utf-8-sig", newline="") as f:
        frozen = list(csv.DictReader(f))
    old = {(r["kind"], r["area_id"]): r for r in frozen}
    new = {(r["kind"], r["area_id"]): r for r in current}
    if old.keys() != new.keys():
        errors.append("BASELINE_INDEX candidate set differs; baseline was not changed")
    for key in old.keys() & new.keys():
        if old[key]["path"] != new[key]["path"] or old[key]["sha256"] != new[key]["sha256"]:
            errors.append(f"frozen baseline mismatch for {key}; baseline was not changed")
    return frozen, errors


def safe_zip_issues(zf: zipfile.ZipFile) -> list[str]:
    issues = []
    seen = set()
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        key = name.casefold()
        if key in seen:
            issues.append(f"duplicate entry: {name}")
        seen.add(key)
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts or re.match(r"^[A-Za-z]:", name):
            issues.append(f"unsafe path: {name}")
        mode = (info.external_attr >> 16) & 0xFFFF
        if stat.S_ISLNK(mode):
            issues.append(f"symlink entry: {name}")
    bad = zf.testzip()
    if bad:
        issues.append(f"CRC failure: {bad}")
    return issues


def safe_extract(zf: zipfile.ZipFile, destination: Path) -> None:
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        if name.endswith("/"):
            continue
        target = destination.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zf.read(info))


def parse_canvas(value: str) -> tuple[int, int] | None:
    match = re.search(r"(\d+)x(\d+)", value or "")
    return (int(match.group(1)), int(match.group(2))) if match else None


def expected_paths(scope: dict[str, str], manifest: dict[str, str]) -> list[str]:
    role = scope["effect_role"]
    if scope["production_decision"] == "AREA00_APPROVED_REUSE":
        values = []
        for path in scope["output_path"].split("|"):
            parts = path.replace("\\", "/").split("/", 1)
            values.append(parts[1] if len(parts) == 2 else path)
        return values
    count = int(float(scope["frame_count"]))
    work = f"{int(manifest['work_order']):03d}"
    prefix = f"{work}_{manifest['monster_id']}_{manifest['skill_id']}"
    directory = ROLE_DIR[role]
    if role == "ICON":
        return [f"{directory}/{prefix}_ICON.png"]
    return [f"{directory}/{prefix}_{directory}_F{i:02d}.png" for i in range(count)]


def split_manifest_paths(value: str) -> list[str]:
    """Expand either a per-file path or a role-level pipe/newline list."""
    return [p.strip().replace("\\", "/") for p in re.split(r"\s*[|;\n]\s*", value or "") if p.strip()]


def normalize_output_manifest(
    rows: list[dict[str, str]], area: str,
) -> tuple[list[dict[str, str]], list[str]]:
    """Normalize known submitted manifest dialects without changing the ZIP.

    The INPUT V2.4 contract still requires the canonical per-file schema.  This
    compatibility layer exists only so the auditor can inspect the actual art
    and report one precise REPACK issue instead of misclassifying every image as
    absent.
    """
    if not rows:
        return [], []
    canonical = {
        "area_id", "area_name", "work_order", "monster_id", "monster_name",
        "skill_id", "skill_name", "skill_type", "effect_role",
        "production_decision", "runtime_use", "relative_path", "frame_index",
        "frame_count", "canvas", "frame_seconds", "playback_mode", "sha256",
        "user_art_approval",
    }
    columns = set(rows[0])
    schema_notes = []
    missing = sorted(canonical - columns)
    if missing:
        schema_notes.append("canonical per-file columns missing: " + ", ".join(missing))
    path_fields = (
        "relative_path", "output_rel_path", "relative_file_path",
        "file_relative_path", "rel_path", "file_rel_path", "output_relpath",
        "output_files", "relative_paths", "files", "output_path",
    )
    normalized: list[dict[str, str]] = []
    for raw in rows:
        path_value = next((raw.get(k, "") for k in path_fields if raw.get(k, "").strip()), "")
        paths = split_manifest_paths(path_value)
        if not paths:
            schema_notes.append(
                f"row has no usable output path: {raw.get('monster_id', '')}/{raw.get('skill_id', '')}/{raw.get('effect_role') or raw.get('role', '')}"
            )
            continue
        raw_role = raw.get("effect_role") or raw.get("role", "")
        out_role = ROLE_OUT.get(raw_role, raw_role)
        canvas = raw.get("canvas") or raw.get("size", "")
        if not canvas and raw.get("width") and raw.get("height"):
            canvas = f"{raw['width']}x{raw['height']}"
        frame_count = (
            raw.get("frame_count") or raw.get("frame_count_total")
            or raw.get("frame_count_contract") or raw.get("frames")
            or str(len(paths))
        )
        for path in paths:
            frame_match = re.search(r"_F(\d+)\.png$", path, re.I)
            frame_index = raw.get("frame_index", "")
            if frame_match:
                frame_index = frame_match.group(1)
            elif out_role == "ICON" and not frame_index:
                frame_index = "0"
            normalized.append({
                "area_id": raw.get("area_id", ""),
                "area_name": raw.get("area_name", ""),
                "work_order": raw.get("work_order") or raw.get("monster_order", ""),
                "monster_id": raw.get("monster_id", ""),
                "monster_name": raw.get("monster_name", ""),
                "skill_id": raw.get("skill_id", ""),
                "skill_name": raw.get("skill_name", ""),
                "skill_type": raw.get("skill_type", ""),
                "effect_role": out_role,
                "production_decision": raw.get("production_decision") or raw.get("decision", ""),
                "runtime_use": raw.get("runtime_use", ""),
                "relative_path": path,
                "frame_index": frame_index,
                "frame_count": frame_count,
                "canvas": canvas,
                "frame_seconds": raw.get("frame_seconds") or raw.get("delay", ""),
                "total_seconds": raw.get("total_seconds", ""),
                "playback_mode": raw.get("playback_mode") or raw.get("playback", ""),
                "sha256": raw.get("sha256") or raw.get("hash_sha256", ""),
                "user_art_approval": raw.get("user_art_approval", ""),
            })
    return normalized, sorted(set(schema_notes))


def load_image(data: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def image_metrics(data: bytes) -> dict[str, object]:
    image = load_image(data)
    result: dict[str, object] = {"mode": image.mode, "width": image.width, "height": image.height}
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    lo, hi = alpha.getextrema()
    bbox = alpha.point(lambda x: 255 if x > 16 else 0).getbbox()
    histogram = alpha.histogram()
    opaqueish = sum(histogram[17:])
    coverage = opaqueish / (image.width * image.height)
    edges = [
        alpha.crop((0, 0, image.width, 1)), alpha.crop((0, image.height - 1, image.width, image.height)),
        alpha.crop((0, 0, 1, image.height)), alpha.crop((image.width - 1, 0, image.width, image.height)),
    ]
    edge_pixels = 0
    for edge in edges:
        edge_histogram = edge.histogram()
        edge_pixels += sum(edge_histogram[17:])
    corners = [alpha.getpixel((0, 0)), alpha.getpixel((image.width - 1, 0)), alpha.getpixel((0, image.height - 1)), alpha.getpixel((image.width - 1, image.height - 1))]
    result.update({
        "alpha_min": lo, "alpha_max": hi, "bbox": bbox, "coverage": round(coverage, 6),
        "edge_pixels": edge_pixels, "all_corners_opaque": all(x > 16 for x in corners),
    })
    return result


def add_finding(
    findings: list[dict[str, str]], area: str, monster: str, skill: str, role: str,
    path: str, requirement: str, actual: str, judgment: str, action: str,
) -> None:
    findings.append({
        "area_id": area, "monster_id": monster, "skill_id": skill, "role": role,
        "relative_path": path, "input_requirement": requirement, "observed": actual,
        "file_status": judgment, "visual_status": "NOT_CHECKED", "basis": "mechanical INPUT↔OUTPUT check",
        "action": action,
    })


def checker(size: tuple[int, int], cell: int = 12) -> Image.Image:
    out = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(x + cell - 1, size[0] - 1), min(y + cell - 1, size[1] - 1)), fill=(215, 215, 215))
    return out


def paste_asset(canvas: Image.Image, data: bytes, box: tuple[int, int, int, int]) -> None:
    image = load_image(data).convert("RGBA")
    max_w, max_h = box[2] - box[0], box[3] - box[1]
    image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    bg = checker((max_w, max_h))
    x = (max_w - image.width) // 2
    y = (max_h - image.height) // 2
    bg.paste(image, (x, y), image)
    canvas.paste(bg, (box[0], box[1]))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path(r"C:/Windows/Fonts/malgunbd.ttf" if bold else r"C:/Windows/Fonts/malgun.ttf")
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def spec_core(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("- 핵심 소재:"):
            return line.removeprefix("- 핵심 소재:").strip()
    return "핵심 소재 문구 없음"


def build_contact_sheet(
    area: str,
    area_name: str,
    input_zf: zipfile.ZipFile,
    input_rel: dict[str, str],
    output_zf: zipfile.ZipFile,
    output_rel: dict[str, str],
    manifests: list[dict[str, str]],
    expected_by_pair: dict[tuple[str, str], list[tuple[str, list[str]]]],
    target: Path,
) -> None:
    width, row_h, header = 1900, 320, 80
    canvas = Image.new("RGB", (width, header + row_h * len(manifests)), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 16), f"AREA {area} · {area_name} · INPUT monster + actual OUTPUT assets", fill="black", font=font(30, True))
    for i, m in enumerate(manifests):
        y = header + i * row_h
        draw.rectangle((0, y, width, y + row_h - 1), fill=(255, 255, 255) if i % 2 == 0 else (235, 240, 245))
        pair = (m["monster_id"], m["skill_id"])
        draw.text((20, y + 16), f"{m['work_order']}  {m['monster_name']} / {m['skill_name']}", fill=(15, 15, 15), font=font(22, True))
        draw.text((20, y + 50), f"{m['monster_id']} · {m['skill_id']} · {m['skill_type']}", fill=(70, 70, 70), font=font(16))
        spec_path = f"{m['folder'].strip('/')}/GENERATION_SPEC.md"
        core = spec_core(input_zf.read(input_rel[spec_path]).decode("utf-8-sig")) if spec_path in input_rel else "spec missing"
        if len(core) > 72:
            core = core[:72] + "…"
        draw.text((20, y + 82), "핵심 소재: " + core, fill=(55, 55, 55), font=font(15))
        monster_path = f"{m['folder'].strip('/')}/MONSTER_IMAGE.png"
        draw.text((20, y + 120), "INPUT MONSTER", fill=(40, 70, 120), font=font(14, True))
        if monster_path in input_rel:
            paste_asset(canvas, input_zf.read(input_rel[monster_path]), (20, y + 145, 190, y + 310))
        x = 220
        for role, paths in expected_by_pair.get(pair, []):
            draw.text((x, y + 120), role, fill=(95, 45, 110), font=font(14, True))
            picks = paths if len(paths) <= 4 else [paths[0], paths[len(paths) // 3], paths[(2 * len(paths)) // 3], paths[-1]]
            for path in picks:
                if path in output_rel:
                    paste_asset(canvas, output_zf.read(output_rel[path]), (x, y + 145, x + 170, y + 310))
                x += 182
            x += 22
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def audit_area(
    area: str,
    out_path: Path,
    input_path: Path,
    work_root: Path,
    visual_dir: Path,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, str]], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    items: list[dict[str, object]] = []
    output_hash = sha_file(out_path)
    with zipfile.ZipFile(out_path) as oz, zipfile.ZipFile(input_path) as iz:
        issues = safe_zip_issues(oz)
        if issues:
            for issue in issues:
                add_finding(findings, f"area_{area}", "", "", "ARCHIVE", out_path.name, "safe paths and valid CRC", issue, "FAIL", "REPACK")
            return ({"area_id": f"area_{area}", "output_zip": out_path.name, "output_sha256": output_hash, "file_status": "FAIL", "visual_status": "NOT_CHECKED", "monsters": 0, "issues": len(findings)}, items, findings, [])
        safe_extract(oz, work_root / out_path.stem)
        oroot, orel = relative_map(oz)
        iroot, irel = relative_map(iz)
        expected_root = f"AREA_{area}_IMAGES_OUTPUT"
        if oroot != expected_root:
            add_finding(findings, f"area_{area}", "", "", "ARCHIVE", oroot, expected_root, oroot, "FAIL", "REPACK")
        omanifest_path = "OUTPUT_MANIFEST.csv"
        if omanifest_path not in orel:
            add_finding(findings, f"area_{area}", "", "", "MANIFEST", omanifest_path, "required", "missing", "FAIL", "REPACK")
            omanifest = []
        else:
            raw_omanifest = csv_rows(oz.read(orel[omanifest_path]))
            omanifest, schema_notes = normalize_output_manifest(raw_omanifest, area)
            for note in schema_notes:
                add_finding(
                    findings, f"area_{area}", "", "", "MANIFEST", omanifest_path,
                    "canonical V2.4 per-file OUTPUT_MANIFEST schema", note,
                    "FAIL", "REPACK",
                )
        im = csv_rows(iz.read(irel["AREA_MANIFEST.csv"]))
        scope = csv_rows(iz.read(irel["FULL_ART_SCOPE.csv"]))
        manifest_by = {(r["monster_id"], r["skill_id"]): r for r in im}
        out_by_path = {r.get("relative_path", "").replace("\\", "/"): r for r in omanifest}
        expected_by_pair: dict[tuple[str, str], list[tuple[str, list[str]]]] = defaultdict(list)
        actual_by_pair: dict[tuple[str, str], dict[str, list[tuple[int, str]]]] = defaultdict(lambda: defaultdict(list))
        for row in omanifest:
            pair = (row.get("monster_id", ""), row.get("skill_id", ""))
            role = OUT_TO_INPUT_ROLE.get(row.get("effect_role", ""), row.get("effect_role", ""))
            raw_index = row.get("frame_index", "")
            try:
                order = int(float(raw_index)) if raw_index != "" else -1
            except ValueError:
                order = -1
            path = row.get("relative_path", "").replace("\\", "/")
            if path:
                actual_by_pair[pair][role].append((order, path))
        expected_all = set()
        alpha_warnings = 0
        for s in scope:
            if s["production_decision"] == "NO_RUNTIME_ROLE":
                continue
            role = s["effect_role"]
            if role not in ROLE_OUT:
                add_finding(findings, f"area_{area}", s["monster_id"], s["skill_id"], role, "", "known output role", "unmapped role", "FAIL", "INPUT_CONFLICT")
                continue
            pair = (s["monster_id"], s["skill_id"])
            m = manifest_by[pair]
            paths = expected_paths(s, m)
            expected_by_pair[pair].append((ROLE_OUT[role], paths))
            expected_all.update(paths)
            frame_indices = []
            for index, path in enumerate(paths):
                status = "PASS"
                observed = []
                manifest_row = out_by_path.get(path)
                if path not in orel:
                    status = "FAIL"
                    observed.append("file missing")
                    add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "required file", "missing", "FAIL", "REPACK")
                    continue
                data = oz.read(orel[path])
                try:
                    metrics = image_metrics(data)
                except Exception as exc:
                    metrics = {"decode_error": str(exc)}
                    status = "FAIL"
                    add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "decodable PNG", str(exc), "FAIL", "REEXTRACT")
                else:
                    want_canvas = parse_canvas(s["canvas"])
                    if metrics["mode"] != "RGBA":
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "PNG RGBA", f"mode={metrics['mode']}", "FAIL", "REEXTRACT")
                    if want_canvas and (metrics["width"], metrics["height"]) != want_canvas:
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, f"canvas={want_canvas}", f"canvas={(metrics['width'], metrics['height'])}", "FAIL", "REEXTRACT")
                    if metrics["alpha_min"] == 255 or metrics["coverage"] > 0.98 or metrics["all_corners_opaque"]:
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "actual transparent background", f"alpha_min={metrics['alpha_min']}; coverage={metrics['coverage']}; all_corners_opaque={metrics['all_corners_opaque']}", "FAIL", "REGENERATE")
                    if metrics["bbox"] is None or metrics["coverage"] < 0.0002:
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "nonblank frame", f"bbox={metrics['bbox']}; coverage={metrics['coverage']}", "FAIL", "REEXTRACT")
                    if metrics["edge_pixels"]:
                        alpha_warnings += 1
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "content preferably inside canvas; edge contact alone is not clipping proof", f"alpha>16 edge pixels={metrics['edge_pixels']}", "NOT_CHECKED", "USER_REVIEW")
                if manifest_row is None:
                    status = "FAIL"
                    add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "OUTPUT_MANIFEST row", "missing", "FAIL", "REPACK")
                else:
                    checks = {
                        "area_id": m["area_id"], "area_name": m["area_name"],
                        "monster_id": m["monster_id"], "monster_name": m["monster_name"],
                        "skill_id": m["skill_id"], "skill_name": m["skill_name"], "skill_type": m["skill_type"],
                        "effect_role": ROLE_OUT[role], "production_decision": s["production_decision"],
                    }
                    for field, wanted in checks.items():
                        actual_value = manifest_row.get(field, "")
                        # A missing canonical column is already reported once at
                        # archive level.  Compare populated semantic values here
                        # so dialect compatibility does not multiply one defect
                        # by every frame.
                        if actual_value and actual_value != wanted:
                            status = "FAIL"
                            add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, f"manifest {field}={wanted}", f"{actual_value}", "FAIL", "REPACK")
                    if manifest_row.get("sha256") and manifest_row.get("sha256") != sha(data):
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "manifest SHA-256 matches file", "hash mismatch", "FAIL", "REPACK")
                    if parse_canvas(manifest_row.get("canvas", "")) != parse_canvas(s["canvas"]):
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, f"manifest canvas={s['canvas']}", manifest_row.get("canvas", ""), "FAIL", "REPACK")
                    if role != "ICON":
                        try:
                            frame_indices.append(int(float(manifest_row.get("frame_index", ""))))
                        except ValueError:
                            status = "FAIL"
                if s["production_decision"] == "AREA00_APPROVED_REUSE":
                    approved_root = DOCS_ART / "area00-images-output" / "AREA_00_IMAGES_OUTPUT" / "monsters"
                    if role == "ICON":
                        pattern = f"*_{m['skill_id']}_ICON.png"
                    else:
                        frame_match = re.search(r"_F(\d\d)\.png$", path)
                        pattern = f"*_{m['skill_id']}_F{frame_match.group(1)}.png" if frame_match else "__NO_MATCH__"
                    candidates = list(approved_root.rglob(pattern))
                    if len(candidates) != 1 or sha(data) != sha(candidates[0].read_bytes()):
                        status = "FAIL"
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, path, "byte-identical Area 00 approved asset", f"candidate_count={len(candidates)}; hash_match={len(candidates)==1 and sha(data)==sha(candidates[0].read_bytes())}", "FAIL", "REPACK")
                items.append({
                    "area_id": f"area_{area}", "monster_id": m["monster_id"], "monster_name": m["monster_name"],
                    "skill_id": m["skill_id"], "skill_name": m["skill_name"], "skill_type": m["skill_type"],
                    "role": role, "production_decision": s["production_decision"], "relative_path": path,
                    "file_status": status, "visual_status": "NOT_CHECKED", "output_sha256": sha(data),
                })
            if role != "ICON" and frame_indices and sorted(frame_indices) != list(range(int(float(s["frame_count"])))):
                add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], role, "OUTPUT_MANIFEST.csv", f"continuous frames 0..{int(float(s['frame_count']))-1}", str(sorted(frame_indices)), "FAIL", "REPACK")

        actual_role_pngs = {
            p for p in orel
            if re.search(r"(^|/)((ICON)|(CAST)|(PROJECTILE)|(REFERENCE))/[^/]+\.png$", p, re.I)
        }
        for path in sorted(actual_role_pngs - expected_all):
            add_finding(findings, f"area_{area}", "", "", "UNEXPECTED", path, "no extra role PNG", "unexpected role file", "FAIL", "REPACK")
            manifest_row = out_by_path.get(path, {})
            status = "FAIL"  # wrong structure remains a failure even if pixel format is valid
            data = oz.read(orel[path])
            try:
                metrics = image_metrics(data)
            except Exception as exc:
                add_finding(findings, f"area_{area}", manifest_row.get("monster_id", ""), manifest_row.get("skill_id", ""), manifest_row.get("effect_role", "UNEXPECTED"), path, "decodable PNG", str(exc), "FAIL", "REEXTRACT")
            else:
                if metrics["mode"] != "RGBA":
                    add_finding(findings, f"area_{area}", manifest_row.get("monster_id", ""), manifest_row.get("skill_id", ""), manifest_row.get("effect_role", "UNEXPECTED"), path, "PNG RGBA", f"mode={metrics['mode']}", "FAIL", "REEXTRACT")
                if metrics["alpha_min"] == 255 or metrics["coverage"] > 0.98 or metrics["all_corners_opaque"]:
                    add_finding(findings, f"area_{area}", manifest_row.get("monster_id", ""), manifest_row.get("skill_id", ""), manifest_row.get("effect_role", "UNEXPECTED"), path, "actual transparent background", f"alpha_min={metrics['alpha_min']}; coverage={metrics['coverage']}; all_corners_opaque={metrics['all_corners_opaque']}", "FAIL", "REGENERATE")
                if metrics["bbox"] is None or metrics["coverage"] < 0.0002:
                    add_finding(findings, f"area_{area}", manifest_row.get("monster_id", ""), manifest_row.get("skill_id", ""), manifest_row.get("effect_role", "UNEXPECTED"), path, "nonblank frame", f"bbox={metrics['bbox']}; coverage={metrics['coverage']}", "FAIL", "REEXTRACT")
            items.append({
                "area_id": f"area_{area}", "monster_id": manifest_row.get("monster_id", ""), "monster_name": manifest_row.get("monster_name", ""),
                "skill_id": manifest_row.get("skill_id", ""), "skill_name": manifest_row.get("skill_name", ""), "skill_type": manifest_row.get("skill_type", ""),
                "role": OUT_TO_INPUT_ROLE.get(manifest_row.get("effect_role", ""), manifest_row.get("effect_role", "")),
                "production_decision": manifest_row.get("production_decision", ""), "relative_path": path,
                "file_status": status, "visual_status": "NOT_CHECKED", "output_sha256": sha(data),
            })

        for m in im:
            pair = (m["monster_id"], m["skill_id"])
            result = f"{m['folder'].strip('/')}/RESULT_INFO.md"
            preview = f"{m['folder'].strip('/')}/PREVIEW/labeled_preview.png"
            if result not in orel:
                add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], "RESULT_INFO", result, "required", "missing", "FAIL", "REPACK")
            else:
                text = oz.read(orel[result]).decode("utf-8-sig", errors="replace")
                for token in (m["monster_id"], m["skill_id"], m["monster_name"], m["skill_name"], "V2.4"):
                    if token not in text:
                        add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], "RESULT_INFO", result, f"contains {token}", "missing token", "FAIL", "REPACK")
            if preview not in orel:
                add_finding(findings, f"area_{area}", m["monster_id"], m["skill_id"], "PREVIEW", preview, "required labeled preview", "missing", "FAIL", "REPACK")
        if "AREA_OVERVIEW_PREVIEW.png" not in orel:
            add_finding(findings, f"area_{area}", "", "", "PREVIEW", "AREA_OVERVIEW_PREVIEW.png", "required", "missing", "FAIL", "REPACK")

        visual_assets: dict[tuple[str, str], list[tuple[str, list[str]]]] = defaultdict(list)
        for pair in manifest_by:
            if pair in actual_by_pair:
                for role, values in actual_by_pair[pair].items():
                    visual_assets[pair].append((role, [p for _, p in sorted(values)]))
            else:
                visual_assets[pair] = expected_by_pair.get(pair, [])
        build_contact_sheet(area, im[0]["area_name"], iz, irel, oz, orel, im, visual_assets, visual_dir / f"AREA_{area}_CONTACT.png")
        failed = any(f["file_status"] == "FAIL" for f in findings) or any(i["file_status"] == "FAIL" for i in items)
        area_row = {
            "area_id": f"area_{area}", "area_name": im[0]["area_name"], "output_zip": out_path.name,
            "output_sha256": output_hash, "file_status": "FAIL" if failed else "PASS",
            "visual_status": "NOT_CHECKED", "monsters": len(im), "issues": len(findings),
            "edge_touch_suspicions": alpha_warnings,
        }
        return area_row, items, findings, im


def discover_outputs() -> tuple[dict[str, list[Path]], list[dict[str, str]]]:
    by_area: dict[str, list[Path]] = defaultdict(list)
    discovery_findings = []
    for path in sorted(OUTPUT_DIR.glob("*.zip")):
        try:
            with zipfile.ZipFile(path) as zf:
                issues = safe_zip_issues(zf)
                if issues:
                    raise ValueError("; ".join(issues))
                manifest = csv_rows(zf.read(zip_member(zf, "/OUTPUT_MANIFEST.csv")))
                root, _ = relative_map(zf)
                filename_match = re.fullmatch(r"AREA_(\d{2})_IMAGES_OUTPUT\.zip", path.name)
                root_match = re.fullmatch(r"AREA_(\d{2})_IMAGES_OUTPUT", root)
                area_ids = {r.get("area_id", "") for r in manifest}
                internal = next(iter(area_ids)) if len(area_ids) == 1 else ""
                internal_match = re.fullmatch(r"area_(\d{2})", internal)
                if internal_match:
                    area = internal_match.group(1)
                elif filename_match and root_match and filename_match.group(1) == root_match.group(1):
                    area = filename_match.group(1)
                    discovery_findings.append({"area_id": f"area_{area}", "monster_id": "", "skill_id": "", "role": "MANIFEST", "relative_path": path.name, "input_requirement": f"all OUTPUT_MANIFEST area_id=area_{area}", "observed": f"invalid internal area IDs: {sorted(area_ids)}; filename/root fallback used for continued audit", "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "internal manifest/filename/root cross-check", "action": "REPACK"})
                else:
                    raise ValueError(f"invalid internal area IDs with no unambiguous filename/root fallback: {sorted(area_ids)}")
                expected_root = f"AREA_{area}_IMAGES_OUTPUT"
                if root != expected_root:
                    discovery_findings.append({"area_id": f"area_{area}", "monster_id": "", "skill_id": "", "role": "ARCHIVE", "relative_path": path.name, "input_requirement": f"root={expected_root}", "observed": f"root={root}", "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "archive identity", "action": "REPACK"})
                expected_name = f"AREA_{area}_IMAGES_OUTPUT.zip"
                if path.name != expected_name:
                    discovery_findings.append({"area_id": f"area_{area}", "monster_id": "", "skill_id": "", "role": "ARCHIVE", "relative_path": path.name, "input_requirement": expected_name, "observed": path.name, "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "filename/internal area cross-check", "action": "REPACK"})
                by_area[area].append(path)
        except Exception as exc:
            discovery_findings.append({"area_id": "UNKNOWN", "monster_id": "", "skill_id": "", "role": "ARCHIVE", "relative_path": path.name, "input_requirement": "readable safe ZIP with OUTPUT_MANIFEST", "observed": str(exc), "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "archive discovery", "action": "REPACK"})
    return by_area, discovery_findings


def write_reports(run_dir: Path, areas: list[dict[str, object]], items: list[dict[str, object]], findings: list[dict[str, str]], run_meta: dict[str, object]) -> None:
    action_items = [f for f in findings if f["file_status"] == "FAIL" or f["action"] == "USER_REVIEW"]
    area_fields = ["area_id", "area_name", "output_zip", "output_sha256", "file_status", "visual_status", "monsters", "issues", "edge_touch_suspicions"]
    item_fields = ["area_id", "monster_id", "monster_name", "skill_id", "skill_name", "skill_type", "role", "production_decision", "relative_path", "file_status", "visual_status", "output_sha256"]
    finding_fields = ["area_id", "monster_id", "skill_id", "role", "relative_path", "input_requirement", "observed", "file_status", "visual_status", "basis", "action"]
    write_csv(run_dir / "AREA_STATUS.csv", areas, area_fields)
    write_csv(run_dir / "AUDIT_SUMMARY.csv", items, item_fields)
    write_csv(run_dir / "ACTION_ITEMS.csv", action_items, finding_fields)
    (run_dir / "AUTO_AUDIT_DATA.json").write_text(json.dumps({"run": run_meta, "areas": areas, "items": items, "findings": findings}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = Counter(a["file_status"] for a in areas)
    visual_counts = Counter(a["visual_status"] for a in areas)
    lines = [
        f"# Monster Skill Art Audit — {run_meta['run_id']}", "",
        f"- Rules SHA-256: `{run_meta['rules_sha256']}`",
        f"- Baseline index SHA-256: `{run_meta['baseline_index_sha256']}`",
        f"- OUTPUT ZIPs discovered: {run_meta['output_zip_count']}",
        f"- Areas: PASS {counts['PASS']} / FAIL {counts['FAIL']} / NOT_CHECKED {counts['NOT_CHECKED']}",
        "- Visual review: " + " / ".join(f"{key} {visual_counts[key]}" for key in sorted(VISUAL_STATUS) if visual_counts[key]),
        "- USER_APPROVED: not assigned",
        "", "## Area status", "",
        "| Area | File/spec | Visual | ZIP | Issues |",
        "|---|---|---|---|---:|",
    ]
    for area in areas:
        lines.append(f"| {area['area_id']} | {area['file_status']} | {area['visual_status']} | `{area['output_zip']}` | {area['issues']} |")
    lines += ["", "## Actions", ""]
    if action_items:
        for item in action_items[:200]:
            lines.append(f"- {item['area_id']} · {item['monster_id']} · {item['skill_id']} · {item['role']} · `{item['relative_path']}` → **{item['action']}**: {item['observed']}")
    else:
        lines.append("- None from mechanical checks.")
    lines += ["", "Visual contact sheets are under `visual_review/`. These sheets mechanically compose INPUT monsters and actual OUTPUT files; they are not generated art.", ""]
    (run_dir / "AUDIT_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    for path in (OUTPUT_DIR, AUDIT_DIR, RUNS_DIR, WORK_DIR):
        path.mkdir(parents=True, exist_ok=True)
    baseline, baseline_errors = ensure_baseline()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    work_root = WORK_DIR / run_id
    visual_dir = run_dir / "visual_review"
    evidence_dir = run_dir / "evidence"
    run_dir.mkdir()
    work_root.mkdir()
    visual_dir.mkdir()
    evidence_dir.mkdir()

    by_area, findings = discover_outputs()
    baseline_inputs = {r["area_id"][-2:]: Path(r["path"]) for r in baseline if r["kind"] == "AREA_INPUT"}
    area_rows: list[dict[str, object]] = []
    item_rows: list[dict[str, object]] = []
    for area in AREAS:
        candidates = by_area.get(area, [])
        if not candidates:
            area_rows.append({"area_id": f"area_{area}", "area_name": "", "output_zip": "", "output_sha256": "", "file_status": "NOT_CHECKED", "visual_status": "NOT_CHECKED", "monsters": 0, "issues": 0, "edge_touch_suspicions": 0})
            continue
        if len(candidates) > 1:
            hashes = {sha_file(p) for p in candidates}
            for path in candidates:
                findings.append({"area_id": f"area_{area}", "monster_id": "", "skill_id": "", "role": "ARCHIVE", "relative_path": path.name, "input_requirement": "one unambiguous OUTPUT per Area", "observed": f"VERSION_CONFLICT; candidates={len(candidates)}; unique_hashes={len(hashes)}", "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "OUTPUT discovery", "action": "USER_REVIEW"})
            area_rows.append({"area_id": f"area_{area}", "area_name": "", "output_zip": "|".join(p.name for p in candidates), "output_sha256": "", "file_status": "FAIL", "visual_status": "NOT_CHECKED", "monsters": 0, "issues": len(candidates), "edge_touch_suspicions": 0})
            continue
        if area not in baseline_inputs:
            findings.append({"area_id": f"area_{area}", "monster_id": "", "skill_id": "", "role": "BASELINE", "relative_path": candidates[0].name, "input_requirement": "matching frozen INPUT", "observed": "MISSING_INPUT", "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "BASELINE_INDEX", "action": "INPUT_CONFLICT"})
            area_rows.append({"area_id": f"area_{area}", "area_name": "", "output_zip": candidates[0].name, "output_sha256": sha_file(candidates[0]), "file_status": "FAIL", "visual_status": "NOT_CHECKED", "monsters": 0, "issues": 1, "edge_touch_suspicions": 0})
            continue
        try:
            area_row, items, area_findings, _ = audit_area(area, candidates[0], baseline_inputs[area], work_root, visual_dir)
            area_rows.append(area_row)
            item_rows.extend(items)
            findings.extend(area_findings)
        except Exception as exc:
            findings.append({"area_id": f"area_{area}", "monster_id": "", "skill_id": "", "role": "AUDIT", "relative_path": candidates[0].name, "input_requirement": "complete audit", "observed": repr(exc), "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "audit exception", "action": "USER_REVIEW"})
            area_rows.append({"area_id": f"area_{area}", "area_name": "", "output_zip": candidates[0].name, "output_sha256": sha_file(candidates[0]), "file_status": "FAIL", "visual_status": "NOT_CHECKED", "monsters": 0, "issues": 1, "edge_touch_suspicions": 0})

    for error in baseline_errors:
        findings.append({"area_id": "ALL", "monster_id": "", "skill_id": "", "role": "BASELINE", "relative_path": "BASELINE_INDEX.csv", "input_requirement": "frozen baseline hash", "observed": error, "file_status": "FAIL", "visual_status": "NOT_CHECKED", "basis": "baseline lock", "action": "INPUT_CONFLICT"})
    for area_row in area_rows:
        related = [f for f in findings if f["area_id"] in {area_row["area_id"], "ALL"}]
        area_row["issues"] = len(related)
        if any(f["file_status"] == "FAIL" for f in related):
            area_row["file_status"] = "FAIL"
    run_meta = {
        "run_id": run_id, "rules_sha256": sha_file(RULES), "baseline_index_sha256": sha_file(BASELINE_INDEX),
        "output_zip_count": sum(len(v) for v in by_area.values()), "work_path": str(work_root.resolve()),
    }
    write_reports(run_dir, area_rows, item_rows, findings, run_meta)
    latest = AUDIT_DIR / "LATEST_REPORT.md"
    latest.write_text(
        f"# Latest completed output audit\n\n- run_id: `{run_id}`\n- report: `{(run_dir / 'AUDIT_SUMMARY.md').resolve()}`\n- rules_sha256: `{run_meta['rules_sha256']}`\n- baseline_index_sha256: `{run_meta['baseline_index_sha256']}`\n- visual review status: `NOT_CHECKED` until comparison sheets are actually reviewed\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"run_id": run_id, "run_dir": str(run_dir.resolve()), "areas": Counter(a["file_status"] for a in area_rows), "items": len(item_rows), "findings": len(findings), "visual_dir": str(visual_dir.resolve())}, ensure_ascii=False, indent=2, default=dict))
    return 0


if __name__ == "__main__":
    sys.exit(main())
