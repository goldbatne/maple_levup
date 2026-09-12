#!/usr/bin/env python3
"""Independent semantic, byte, and archive verification for INPUT V2.4."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


DOCS = Path(__file__).resolve().parents[1]
SRC = DOCS / "art" / "images-input-packages-v2_3"
DST = DOCS / "art" / "images-input-packages-v2_4"
AREA00 = DOCS / "art" / "area00-images-output" / "AREA_00_IMAGES_OUTPUT" / "monsters"
AREA00_MAP = DOCS / "art" / "area00-images-output" / "AREA_00_IMAGES_RESOURCE_MAP.csv"
V22 = DOCS / "art" / "images-input-packages-v2_2"

AREAS = [f"{n:02d}" for n in range(1, 21) if n != 6]
ROLES = ["ICON", "CAST_VFX", "PROJECTILE", "HIT_VFX", "PERSISTENT_BUFF_VFX", "REFERENCE_VFX"]
APPROVED = {
    ("m_snail", "s_mon_snail_dew_trail"),
    ("m_blue_snail", "s_mon_blue_snail"),
    ("m_slime", "s_mon_slime"),
}
PROJECTILES = {
    "s_mon_stumpy", "s_mon_faust", "s_mon_star_pixie", "s_mon_lunar_pixie",
    "s_mon_shark", "s_mon_king_bloctopus", "s_mon_roid", "s_mon_chimera",
    "s_mon_peach_monkey", "s_mon_tae_roon", "s_mon_dodo", "s_mon_mateon",
}
EXPANDED_PROJECTILES = PROJECTILES - {"s_mon_stumpy"}
IMMUTABLE = [
    "work_order", "level", "area_id", "area_name", "monster_id", "monster_name",
    "monster_image_ruid", "monster_image_status", "skill_id", "skill_name", "skill_type",
    "actual_effect", "boss", "folder", "runtime_effect", "runtime_motion", "data_range",
    "targeting_range", "monster_targeting_range", "impact_radius", "impact_delay",
    "max_targets", "runtime_validation",
]
SYNC_FIELDS = [
    "required_file_set", "future_target", "baseline_current_evidence", "approved_target_ruid",
    "approved_frame_sprite_ruids", "source_path", "output_path", "preview_reference_files",
    "approval_evidence", "approval_status",
]
FORBIDDEN_CURRENT = [
    "나머지 11종 projectile_ruid는 keep",
    "스텀피만 projectile+icon 교체 계획",
    "keep은 승인 전 현행 보존",
    "우측 기준 제작 후 flipx. projectile",
    "projectile은 동일 중심축에서 자체 회전/맥동",
]


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks: Counter[str] = Counter()

    def ok(self, key: str) -> None:
        self.checks[key] += 1

    def fail(self, message: str) -> None:
        self.errors.append(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def path_rows(path: Path) -> list[dict[str, str]]:
    return rows(path.read_bytes())


def member(zf: zipfile.ZipFile, suffix: str) -> str:
    matches = [n for n in zf.namelist() if n.replace("\\", "/").endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"expected one {suffix}, got {matches}")
    return matches[0]


def relative_members(zf: zipfile.ZipFile) -> dict[str, str]:
    root = zf.namelist()[0].split("/", 1)[0] + "/"
    return {n[len(root):]: n for n in zf.namelist() if n.startswith(root) and not n.endswith("/")}


def load_approved() -> dict[tuple[str, str], dict[str, str]]:
    return {(r["monster_id"], r["skill_id"]): r for r in path_rows(AREA00_MAP)}


def load_v22() -> dict[tuple[str, str], tuple[str, str]]:
    result = {}
    for area in ("01", "03"):
        with zipfile.ZipFile(V22 / f"AREA_{area}_IMAGES_INPUT_V2_2.zip") as zf:
            plan = rows(zf.read(member(zf, "/ASSET_BINDING_PLAN.csv")))
            for row in plan:
                if row.get("decision") == "APPROVED_REUSE":
                    clip, icon = row["current_ruid"].split("|", 1)
                    result[(row["monster_id"], row["skill_id"])] = (icon, clip)
    return result


def verify_manifest(audit: Audit, area: str, old: list[dict[str, str]], new: list[dict[str, str]]) -> None:
    ob = {(r["monster_id"], r["skill_id"]): r for r in old}
    nb = {(r["monster_id"], r["skill_id"]): r for r in new}
    if ob.keys() != nb.keys():
        audit.fail(f"AREA {area}: manifest pair set changed")
        return
    for key in ob:
        for field in IMMUTABLE:
            if ob[key].get(field, "") != nb[key].get(field, ""):
                audit.fail(f"AREA {area} {key}: immutable {field} changed")
    audit.ok("immutable_manifest")


def verify_tables(
    audit: Audit,
    area: str,
    scope: list[dict[str, str]],
    output: list[dict[str, str]],
    binding: list[dict[str, str]],
) -> None:
    keyed = {(r["monster_id"], r["skill_id"], r["effect_role"]): r for r in scope}
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in scope:
        grouped[(row["monster_id"], row["skill_id"])].append(row)
    for key, group in grouped.items():
        if len(group) != 6 or {r["effect_role"] for r in group} != set(ROLES):
            audit.fail(f"AREA {area} {key}: canonical six-role inventory broken")
    for label, target in (("OUTPUT_REQUIREMENTS", output), ("ASSET_BINDING_PLAN", binding)):
        other = {(r["monster_id"], r["skill_id"], r["effect_role"]): r for r in target}
        if other.keys() != keyed.keys():
            audit.fail(f"AREA {area}: {label} role keys differ")
            continue
        for key, base in keyed.items():
            row = other[key]
            decision = row.get("production_decision", row.get("decision", ""))
            if decision != base["production_decision"]:
                audit.fail(f"AREA {area} {key}: {label} decision mismatch")
            for field in SYNC_FIELDS:
                if row.get(field, "") != base.get(field, ""):
                    audit.fail(f"AREA {area} {key}: {label} {field} mismatch")
    audit.ok("table_sync")


def check_reuse(
    audit: Audit,
    area: str,
    scope: list[dict[str, str]],
    names: dict[str, str],
    zf: zipfile.ZipFile,
    approved: dict[tuple[str, str], dict[str, str]],
    v22: dict[tuple[str, str], tuple[str, str]],
) -> int:
    count = 0
    for row in scope:
        if row["production_decision"] != "AREA00_APPROVED_REUSE":
            continue
        key = (row["monster_id"], row["skill_id"])
        if key not in APPROVED or key not in approved or key not in v22:
            audit.fail(f"AREA {area} {key}: unverified approved reuse")
            continue
        role = row["effect_role"]
        files = row["required_file_set"].split("|")
        want = 1 if role == "ICON" else 8
        if len(files) != want:
            audit.fail(f"AREA {area} {key} {role}: required files {len(files)} != {want}")
        if role == "ICON" and any("/ICON/" not in p or "/PREVIEW/" in p or "/VFX/" in p for p in files):
            audit.fail(f"AREA {area} {key}: ICON role contains non-icon files")
        if role == "CAST_VFX" and any("/VFX/" not in p or not re.search(r"_F\d\d\.png$", p) for p in files):
            audit.fail(f"AREA {area} {key}: CAST role contains non-frame files")
        previews = [p for p in row["preview_reference_files"].split("|") if p and p != "n/a"]
        if len(previews) != 2 or any("/PREVIEW/" not in p for p in previews):
            audit.fail(f"AREA {area} {key} {role}: preview references not separated")
        if set(files) & set(previews):
            audit.fail(f"AREA {area} {key} {role}: preview leaked into required files")
        if row["source_path"] != row["required_file_set"]:
            audit.fail(f"AREA {area} {key} {role}: source_path differs from approved required files")
        if any(p not in names for p in files + previews):
            audit.fail(f"AREA {area} {key} {role}: package reference missing")
            continue
        target = approved[key]["icon_ruid"] if role == "ICON" else approved[key]["animationclip_ruid"]
        v22_target = v22[key][0] if role == "ICON" else v22[key][1]
        if target != v22_target or row["approved_target_ruid"] != target or target not in row["future_target"]:
            audit.fail(f"AREA {area} {key} {role}: approved RUID mismatch")
        if row["baseline_current_evidence"] != row["current_resource"]:
            audit.fail(f"AREA {area} {key} {role}: baseline evidence not preserved separately")
        if row["approval_status"] != "CONFIRMED_MATCH":
            audit.fail(f"AREA {area} {key} {role}: approval not confirmed")
        if role == "CAST_VFX" and row["approved_frame_sprite_ruids"] != approved[key]["frame_sprite_ruids"]:
            audit.fail(f"AREA {area} {key}: approved frame RUID list mismatch")
        outputs = row["output_path"].split("|")
        if len(outputs) != want or any("_IMAGES_OUTPUT/" not in p for p in outputs):
            audit.fail(f"AREA {area} {key} {role}: output path contract invalid")
        if any(not re.match(r"\d{3}_", Path(p).name) for p in outputs):
            audit.fail(f"AREA {area} {key} {role}: output filename work_order is not three digits")
        if role == "ICON" and any("/ICON/" not in p for p in outputs):
            audit.fail(f"AREA {area} {key}: icon output path invalid")
        if role == "CAST_VFX" and any("/CAST/" not in p or "_CAST_F" not in p for p in outputs):
            audit.fail(f"AREA {area} {key}: CAST output path invalid")

        for p in files:
            data = zf.read(names[p])
            basename = Path(p).name
            candidates = list(AREA00.rglob(basename))
            if len(candidates) != 1 or sha(data) != sha(candidates[0].read_bytes()):
                audit.fail(f"AREA {area} {key}: approved PNG differs from Area 00 source: {basename}")
            count += 1
    return count


def verify_projectiles(audit: Audit, area: str, scope: list[dict[str, str]], zf: zipfile.ZipFile) -> None:
    projectile_rows = [r for r in scope if r["effect_role"] == "PROJECTILE" and r["production_decision"] == "NEW_ART"]
    for row in projectile_rows:
        if row["skill_id"] not in PROJECTILES:
            audit.fail(f"AREA {area}: unexpected projectile {row['skill_id']}")
        contract = " ".join(row.get(k, "") for k in (
            "frame_count", "frame_seconds", "total_seconds", "playback_mode",
            "direction_and_engine_motion", "impact_radius",
        )).lower()
        for token in ("4", "0.08", "0.32", "0.35", "0.8"):
            if token not in contract:
                audit.fail(f"AREA {area} {row['skill_id']}: projectile contract missing {token}")

    names = relative_members(zf)
    specs = [n for n in names if n.endswith("/GENERATION_SPEC.md")]
    for spec in specs:
        text = zf.read(names[spec]).decode("utf-8-sig")
        skill_match = re.search(r"- skill_id: `([^`]+)`", text)
        if not skill_match:
            continue
        skill = skill_match.group(1)
        if skill in EXPANDED_PROJECTILES:
            for marker in ("- CAST 방향/표현:", "- PROJECTILE 방향/표현:", "- PROJECTILE 국소 애니메이션:"):
                if marker not in text:
                    audit.fail(f"AREA {area} {skill}: missing role-specific marker {marker}")
            if "4×0.08=0.32초" not in text or "0.35초 수명" not in text or "0.8wu" not in text:
                audit.fail(f"AREA {area} {skill}: spec lost timing/radius contract")
        if skill == "s_mon_stumpy":
            if "CAST_VFX는 현재 실행 역할이 없다" not in text:
                audit.fail("AREA 02 Stumpy: missing no-CAST clarification")
            if "4×0.08=0.32초" not in text or "0.35초 수명" not in text or "0.8wu" not in text:
                audit.fail("AREA 02 Stumpy: spec lost timing/radius contract")
    audit.ok("projectile_contract")


def verify_current_docs(audit: Audit, area: str, zf: zipfile.ZipFile) -> None:
    names = relative_members(zf)
    required = [
        "README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md", "ASSET_BINDING_PLAN.md",
        "RUNTIME_CONFLICTS_V2_4.md", "PACKAGE_REVISION_V2_4.md", "PACKAGE_STATUS_V2_4.md",
    ]
    for path in required:
        if path not in names:
            audit.fail(f"AREA {area}: missing {path}")
    if "RUNTIME_CONFLICTS_V2_3.md" in names:
        audit.fail(f"AREA {area}: V2.3 conflicts document remains current")
    current_texts = {
        p: zf.read(n).decode("utf-8-sig", errors="replace")
        for p, n in names.items()
        if p.lower().endswith((".md", ".txt", ".csv")) and not p.lower().startswith("history/")
    }
    for path, text in current_texts.items():
        lower = text.lower()
        for phrase in FORBIDDEN_CURRENT:
            if phrase in lower:
                audit.fail(f"AREA {area}: stale/ambiguous phrase in {path}: {phrase}")
    for path in ("README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md"):
        text = current_texts.get(path, "")
        if "PACKAGE_REVISION_V2_4.md" not in text or "FULL_ART_SCOPE.csv" not in text:
            audit.fail(f"AREA {area}: {path} does not start from current revision/scope")
        if "`PACKAGE_REVISION.md`" in text:
            audit.fail(f"AREA {area}: {path} retains generic V2 revision entry")
    plan = current_texts.get("ASSET_BINDING_PLAN.md", "")
    for decision in ("NEW_ART", "AREA00_APPROVED_REUSE", "NO_RUNTIME_ROLE"):
        if decision not in plan:
            audit.fail(f"AREA {area}: binding plan missing {decision}")
    conflicts = current_texts.get("RUNTIME_CONFLICTS_V2_4.md", "")
    for marker in ("12종", "NEW_ART", "baseline evidence", "0.35초", "0.8wu", "PROJECTILE FlipX"):
        if marker not in conflicts:
            audit.fail(f"AREA {area}: runtime conflicts missing current projectile marker {marker}")
    audit.ok("current_documents")


def compare_pngs(audit: Audit, area: str, old: zipfile.ZipFile, new: zipfile.ZipFile) -> tuple[int, int]:
    om = relative_members(old)
    nm = relative_members(new)
    monster_count = 0
    approved_png_count = 0
    for rel, old_name in om.items():
        if not rel.lower().endswith(".png"):
            continue
        if "/monsters/" in ("/" + rel.lower()) and rel.endswith("/MONSTER_IMAGE.png"):
            monster_count += 1
            if rel not in nm or sha(old.read(old_name)) != sha(new.read(nm[rel])):
                audit.fail(f"AREA {area}: MONSTER_IMAGE changed: {rel}")
        if rel.startswith("approved_reuse/"):
            if rel not in nm or sha(old.read(old_name)) != sha(new.read(nm[rel])):
                audit.fail(f"AREA {area}: approved reuse PNG changed: {rel}")
            if "/ICON/" in rel or ("/VFX/" in rel and re.search(r"_F\d\d\.png$", rel)):
                approved_png_count += 1
    return monster_count, approved_png_count


def write_reports(audit: Audit, summary: dict) -> None:
    payload = {"overall": "PASS" if not audit.errors else "FAIL", "errors": audit.errors, "warnings": audit.warnings, "checks": dict(audit.checks), **summary}
    (DST / "INPUT_V2_4_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# INPUT V2.4 검증 보고서", "",
        f"- 종합: **{payload['overall']}**",
        f"- 패키지: {summary['packages']} / 19",
        f"- 몬스터/스킬 쌍: {summary['pairs']}",
        f"- 역할 행: {summary['scope_rows']}",
        f"- NEW_ART: {summary['new_art_sets']}",
        f"- Area 00 승인 재사용: {summary['reuse_sets']} / 승인 PNG {summary['approved_pngs']}장",
        f"- V2.3과 동일한 몬스터 원본: {summary['monster_images']}장",
        "", "## 상태", "",
        f"- PACKAGE_VALIDATION: {'PASS' if not audit.errors else 'FAIL'}",
        f"- GENERATION_READY: {'READY (19/19)' if not audit.errors else 'BLOCKED'}",
        "- IMPORT_VALIDATION: NOT_READY_ASSETS_NOT_GENERATED",
        "- RUNTIME_VALIDATION: NOT_RUN (Area 20 기존 충돌은 UNRESOLVED)",
        "- ART_APPROVAL: NOT_REVIEWED",
        "", "## 확인 사항", "",
        "- 현행 11종 KEEP 문구 제거 및 실제 PROJECTILE 12종 NEW_ART 계약 확인",
        "- 11종 CAST/PROJECTILE 방향·국소 회전·엔진 ZRotation 분리 확인",
        "- 스텀피 ICON+PROJECTILE 전용 및 4×0.08=0.32초/0.35초/0.8wu 유지 확인",
        "- 재사용 ICON 1개·CAST 8프레임·Preview 분리 및 승인 RUID 교차 대조",
        "- V2.3 확정 스킬/런타임 필드, 승인 PNG, 몬스터 원본 이미지 불변 확인",
        "- ZIP CRC와 내부 참조 경로 확인",
        "", "## 오류", "",
    ]
    lines += [f"- {e}" for e in audit.errors] or ["- 없음"]
    (DST / "INPUT_V2_4_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hashes() -> None:
    names = [
        "ALL_AREAS_INPUT_V2_4_INDEX.md", "FULL_ART_SCOPE.csv", "INPUT_V2_4_CHANGELOG.md",
        "INPUT_V2_4_VALIDATION.md", "INPUT_V2_4_VALIDATION.json", "BUILD_RESULT.json",
    ]
    paths = sorted(DST.glob("AREA_*_IMAGES_INPUT_V2_4.zip")) + [DST / n for n in names]
    with (DST / "INPUT_V2_4_HASHES.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "bytes", "sha256"])
        writer.writeheader()
        for path in paths:
            writer.writerow({"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())})


def main() -> int:
    audit = Audit()
    approved = load_approved()
    v22 = load_v22()
    all_scope = []
    pairs = set()
    package_count = 0
    monster_images = 0
    approved_pngs = 0
    reuse_required_files = 0
    for area in AREAS:
        old_path = SRC / f"AREA_{area}_IMAGES_INPUT_V2_3.zip"
        new_path = DST / f"AREA_{area}_IMAGES_INPUT_V2_4.zip"
        if not old_path.exists() or not new_path.exists():
            audit.fail(f"AREA {area}: source or V2.4 ZIP missing")
            continue
        package_count += 1
        with zipfile.ZipFile(old_path) as old, zipfile.ZipFile(new_path) as new:
            bad = new.testzip()
            if bad:
                audit.fail(f"AREA {area}: CRC failure at {bad}")
            else:
                audit.ok("zip_crc")
            om = rows(old.read(member(old, "/AREA_MANIFEST.csv")))
            nm = rows(new.read(member(new, "/AREA_MANIFEST.csv")))
            verify_manifest(audit, area, om, nm)
            scope = rows(new.read(member(new, "/FULL_ART_SCOPE.csv")))
            output = rows(new.read(member(new, "/OUTPUT_REQUIREMENTS.csv")))
            binding = rows(new.read(member(new, "/ASSET_BINDING_PLAN.csv")))
            verify_tables(audit, area, scope, output, binding)
            verify_projectiles(audit, area, scope, new)
            verify_current_docs(audit, area, new)
            rel = relative_members(new)
            reuse_required_files += check_reuse(audit, area, scope, rel, new, approved, v22)
            mi, ap = compare_pngs(audit, area, old, new)
            monster_images += mi
            approved_pngs += ap
            all_scope.extend(scope)
            pairs.update((r["monster_id"], r["skill_id"]) for r in nm)

    if (DST / "AREA_06_IMAGES_INPUT_V2_4.zip").exists():
        audit.fail("reserved AREA 06 was created")
    counts = Counter(r["effect_role"] for r in all_scope if r["production_decision"] == "NEW_ART")
    reuse = Counter(r["effect_role"] for r in all_scope if r["production_decision"] == "AREA00_APPROVED_REUSE")
    if counts != Counter({"ICON": 96, "CAST_VFX": 60, "PROJECTILE": 12, "REFERENCE_VFX": 35}):
        audit.fail(f"NEW_ART scope changed: {dict(counts)}")
    if reuse != Counter({"ICON": 3, "CAST_VFX": 3}):
        audit.fail(f"approved reuse scope changed: {dict(reuse)}")
    if len(pairs) != 99 or len(all_scope) != 594:
        audit.fail(f"cardinality mismatch pairs={len(pairs)} rows={len(all_scope)}")
    if monster_images != 99:
        audit.fail(f"MONSTER_IMAGE count {monster_images} != 99")
    if approved_pngs != 27 or reuse_required_files != 27:
        audit.fail(f"approved PNG counts archive={approved_pngs}, contract={reuse_required_files}, expected=27")

    summary = {
        "packages": package_count,
        "areas": AREAS,
        "pairs": len(pairs),
        "scope_rows": len(all_scope),
        "new_art_sets": dict(sorted(counts.items())),
        "reuse_sets": dict(sorted(reuse.items())),
        "monster_images": monster_images,
        "approved_pngs": approved_pngs,
    }
    write_reports(audit, summary)
    if not audit.errors:
        index = DST / "ALL_AREAS_INPUT_V2_4_INDEX.md"
        index.write_text(index.read_text(encoding="utf-8-sig").replace("PENDING_INDEPENDENT", "PASS"), encoding="utf-8", newline="\n")
    write_hashes()
    print(json.dumps({"overall": "PASS" if not audit.errors else "FAIL", "errors": audit.errors[:30], **summary}, ensure_ascii=False, indent=2))
    return 0 if not audit.errors else 1


if __name__ == "__main__":
    sys.exit(main())
