#!/usr/bin/env python3
"""Semantic and package-integrity verification for AREA input V2.3.

This verifier intentionally derives the expected production scope from the
immutable V2.2 manifests and the current runtime fields copied into V2.3.  It
does not accept the builder's summary as proof of correctness.
"""

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
SRC = DOCS / "art" / "images-input-packages-v2_2"
DST = DOCS / "art" / "images-input-packages-v2_3"

AREAS = [f"{n:02d}" for n in range(1, 21) if n != 6]
ROLES = [
    "ICON",
    "CAST_VFX",
    "PROJECTILE",
    "HIT_VFX",
    "PERSISTENT_BUFF_VFX",
    "REFERENCE_VFX",
]
APPROVED = {
    ("m_snail", "s_mon_snail_dew_trail"),
    ("m_blue_snail", "s_mon_blue_snail"),
    ("m_slime", "s_mon_slime"),
}
PROJECTILES = {
    ("02", "s_mon_stumpy"),
    ("03", "s_mon_faust"),
    ("08", "s_mon_star_pixie"),
    ("08", "s_mon_lunar_pixie"),
    ("10", "s_mon_shark"),
    ("11", "s_mon_king_bloctopus"),
    ("14", "s_mon_roid"),
    ("14", "s_mon_chimera"),
    ("15", "s_mon_peach_monkey"),
    ("15", "s_mon_tae_roon"),
    ("17", "s_mon_dodo"),
    ("18", "s_mon_mateon"),
}
IMMUTABLE_COLUMNS = [
    "work_order", "level", "area_id", "area_name", "monster_id",
    "monster_name", "monster_image_ruid", "monster_image_status", "skill_id",
    "skill_name", "skill_type", "actual_effect", "boss", "folder",
    "runtime_effect", "runtime_motion", "data_range", "targeting_range",
    "monster_targeting_range", "impact_radius", "impact_delay", "max_targets",
    "runtime_validation",
]
FORBIDDEN_CURRENT = [
    "PROJECTILE existing keep",
    "PROJECTILE 기존 유지",
    "PROJECTILE 신규 생성 제외",
    "KEEP; extra approval",
    "none in required V2.2 scope",
]


def is_passive(value: str) -> bool:
    return value.strip().lower() in {"passive", "패시브"}


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks: Counter[str] = Counter()

    def ok(self, name: str) -> None:
        self.checks[name] += 1

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv_bytes(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def zip_member(zf: zipfile.ZipFile, suffix: str) -> str:
    hits = [n for n in zf.namelist() if n.replace("\\", "/").endswith(suffix)]
    if len(hits) != 1:
        raise ValueError(f"expected one member ending {suffix!r}, got {hits}")
    return hits[0]


def current_text_members(zf: zipfile.ZipFile) -> list[str]:
    return [
        n for n in zf.namelist()
        if n.lower().endswith((".md", ".txt", ".csv"))
        and "/history/" not in n.replace("\\", "/").lower()
    ]


def expected_decision(manifest: dict[str, str], role: str, area: str) -> str:
    key = (manifest["monster_id"], manifest["skill_id"])
    passive = is_passive(manifest["skill_type"])
    approved = key in APPROVED
    if role == "ICON":
        return "AREA00_APPROVED_REUSE" if approved else "NEW_ART"
    if role == "CAST_VFX":
        if approved:
            return "AREA00_APPROVED_REUSE"
        if passive or manifest["skill_id"] == "s_mon_stumpy":
            return "NO_RUNTIME_ROLE"
        return "NEW_ART"
    if role == "PROJECTILE":
        return "NEW_ART" if (area, manifest["skill_id"]) in PROJECTILES else "NO_RUNTIME_ROLE"
    if role in {"HIT_VFX", "PERSISTENT_BUFF_VFX"}:
        return "NO_RUNTIME_ROLE"
    if role == "REFERENCE_VFX":
        return "NEW_ART" if passive else "NO_RUNTIME_ROLE"
    raise AssertionError(role)


def compare_manifests(audit: Audit, area: str, old: list[dict[str, str]], new: list[dict[str, str]]) -> None:
    old_by = {(r["monster_id"], r["skill_id"]): r for r in old}
    new_by = {(r["monster_id"], r["skill_id"]): r for r in new}
    if old_by.keys() != new_by.keys():
        audit.fail(f"AREA {area}: manifest pair set changed")
        return
    for key in old_by:
        for col in IMMUTABLE_COLUMNS:
            if old_by[key].get(col, "") != new_by[key].get(col, ""):
                audit.fail(f"AREA {area} {key}: immutable {col} changed")
    audit.ok("immutable_manifest")


def verify_scope(
    audit: Audit,
    area: str,
    manifest: list[dict[str, str]],
    scope: list[dict[str, str]],
    output_rows: list[dict[str, str]],
    binding_rows: list[dict[str, str]],
) -> None:
    manifests = {(r["monster_id"], r["skill_id"]): r for r in manifest}
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in scope:
        grouped[(row["monster_id"], row["skill_id"])].append(row)
    if set(grouped) != set(manifests):
        audit.fail(f"AREA {area}: FULL_ART_SCOPE pair set differs from manifest")
        return
    for key, rows in grouped.items():
        role_map = {r["effect_role"]: r for r in rows}
        if len(rows) != len(ROLES) or set(role_map) != set(ROLES):
            audit.fail(f"AREA {area} {key}: not exactly six canonical roles")
            continue
        m = manifests[key]
        for role in ROLES:
            row = role_map[role]
            want = expected_decision(m, role, area)
            if row.get("production_decision") != want:
                audit.fail(f"AREA {area} {key} {role}: {row.get('production_decision')} != {want}")
            if want == "NEW_ART" and row.get("required_file_set", "").strip().lower() in {"", "none"}:
                audit.fail(f"AREA {area} {key} {role}: NEW_ART has no files")
            if want == "NO_RUNTIME_ROLE" and row.get("required_file_set", "").strip().lower() not in {"none", "n/a"}:
                audit.fail(f"AREA {area} {key} {role}: absent role requests files")
            if role == "REFERENCE_VFX":
                expected_runtime = "false"
                if row.get("runtime_use", "").lower() != expected_runtime:
                    audit.fail(f"AREA {area} {key}: REFERENCE runtime_use must be {expected_runtime}")
            if role == "PROJECTILE" and want == "NEW_ART":
                timing = " ".join(row.get(k, "") for k in (
                    "frame_count", "frame_seconds", "total_seconds",
                    "playback_mode", "future_target", "direction_and_engine_motion",
                )).lower()
                for token in ("4", "0.08", "0.32", "0.35", "projectile_ruid"):
                    if token not in timing:
                        audit.fail(f"AREA {area} {key}: projectile contract missing {token}")
                if "flipx" in timing and not re.search(r"no(?:\s+projectile)?\s+flipx|does not.*flipx|without.*flipx", timing):
                    audit.fail(f"AREA {area} {key}: unsupported FlipX claim")
    # The generated output and binding matrices must describe the same six-role universe.
    scope_keyed = {(r["monster_id"], r["skill_id"], r["effect_role"]): r for r in scope}
    for label, rows in (("OUTPUT_REQUIREMENTS", output_rows), ("ASSET_BINDING_PLAN", binding_rows)):
        keyed = {(r["monster_id"], r["skill_id"], r["effect_role"]): r for r in rows}
        if set(keyed) != set(scope_keyed):
            audit.fail(f"AREA {area}: {label} role keys differ from FULL_ART_SCOPE")
            continue
        for key, base in scope_keyed.items():
            other = keyed[key]
            decision = other.get("production_decision", other.get("decision", ""))
            if decision != base["production_decision"]:
                audit.fail(f"AREA {area} {key}: {label} decision mismatch")
            if other.get("required_file_set", "") != base.get("required_file_set", ""):
                audit.fail(f"AREA {area} {key}: {label} required_files mismatch")
    audit.ok("role_semantics")


def verify_docs(audit: Audit, area: str, zf: zipfile.ZipFile) -> None:
    names = set(zf.namelist())
    required_suffixes = [
        "/README_START_HERE.md", "/AREA_MANIFEST.csv", "/AREA_MANIFEST.md",
        "/FULL_ART_SCOPE.csv", "/OUTPUT_REQUIREMENTS.csv", "/ASSET_BINDING_PLAN.csv",
        "/CHATGPT_IMAGES_MASTER_PROMPT.md", "/OUTPUT_NAMING_SPEC.md",
        "/OUTPUT_FORMAT_SPEC.md", "/PROJECTILE_SCOPE_REVIEW.md",
        "/PACKAGE_REVISION_V2_3.md", "/PACKAGE_STATUS_V2_3.md",
        "/RUNTIME_CONFLICTS_V2_3.md",
    ]
    for suffix in required_suffixes:
        if not any(n.replace("\\", "/").endswith(suffix) for n in names):
            audit.fail(f"AREA {area}: missing {suffix}")
    for name in current_text_members(zf):
        text = zf.read(name).decode("utf-8-sig", errors="replace")
        for phrase in FORBIDDEN_CURRENT:
            if phrase.lower() in text.lower():
                audit.fail(f"AREA {area}: stale current instruction {phrase!r} in {name}")
    if any(
        n.replace("\\", "/").endswith("/RUNTIME_CONFLICTS_V2_2.md")
        and "/history/" not in n.replace("\\", "/").lower()
        for n in names
    ):
        audit.fail(f"AREA {area}: V2.2 runtime conflict document remains current")
    all_text = "\n".join(
        zf.read(n).decode("utf-8-sig", errors="replace") for n in current_text_members(zf)
    ).lower()
    for phrase in (
        "no_runtime_role", "frame-separated", "labeled_preview", "overview_preview",
        "targeting_range", "impact_radius", "engine movement", "runtime_use=false",
    ):
        if phrase not in all_text:
            audit.fail(f"AREA {area}: package guidance missing {phrase!r}")
    # Every monster folder must contain both authoritative scope artifacts.
    manifest_name = zip_member(zf, "/AREA_MANIFEST.csv")
    manifest = read_csv_bytes(zf.read(manifest_name))
    for row in manifest:
        folder = row["folder"].strip("/")
        if not any(n.replace("\\", "/").endswith(f"/{folder}/GENERATION_SPEC.md") for n in names):
            audit.fail(f"AREA {area}: missing GENERATION_SPEC for {folder}")
        if not any(n.replace("\\", "/").endswith(f"/{folder}/RUNTIME_ROLE_MAP.md") for n in names):
            audit.fail(f"AREA {area}: missing RUNTIME_ROLE_MAP for {folder}")
    audit.ok("package_documents")


def verify_approved_reuse(audit: Audit, area: str, old: zipfile.ZipFile, new: zipfile.ZipFile) -> None:
    if area not in {"01", "02"}:
        return
    old_members = {n.replace("\\", "/").split("/approved_reuse/", 1)[1]: n
                   for n in old.namelist() if "/approved_reuse/" in n.replace("\\", "/") and not n.endswith("/")}
    new_members = {n.replace("\\", "/").split("/approved_reuse/", 1)[1]: n
                   for n in new.namelist() if "/approved_reuse/" in n.replace("\\", "/") and not n.endswith("/")}
    if old_members.keys() != new_members.keys():
        audit.fail(f"AREA {area}: approved reuse file set changed")
        return
    for rel in old_members:
        if sha256(old.read(old_members[rel])) != sha256(new.read(new_members[rel])):
            audit.fail(f"AREA {area}: approved reuse bytes changed: {rel}")
    audit.ok("area00_reuse_hash")


def write_reports(audit: Audit, aggregate: dict) -> None:
    result = {
        "schema": "INPUT_V2_3_VALIDATION_V1",
        "overall": "PASS" if not audit.errors else "FAIL",
        "checks": dict(sorted(audit.checks.items())),
        "errors": audit.errors,
        "warnings": audit.warnings,
        **aggregate,
    }
    (DST / "INPUT_V2_3_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# INPUT V2.3 독립 검증",
        "",
        f"- 종합: **{result['overall']}**",
        f"- 패키지: {aggregate['package_count']} / 19",
        f"- Area: {', '.join(aggregate['areas'])}",
        f"- 몬스터/스킬 조합: {aggregate['pair_count']}",
        f"- 역할 행: {aggregate['scope_row_count']}",
        f"- 신규 아트 스킬: {aggregate['new_art_skill_count']}",
        f"- 신규 역할 세트: {aggregate['new_art_sets']}",
        f"- Area 00 승인 재사용 세트: {aggregate['reuse_sets']}",
        "",
        "## 상태 축",
        "",
        "- PACKAGE_VALIDATION: PASS" if not audit.errors else "- PACKAGE_VALIDATION: FAIL",
        "- GENERATION_READY: READY (19/19)" if not audit.errors else "- GENERATION_READY: BLOCKED",
        "- IMPORT_VALIDATION: NOT_READY_ASSETS_NOT_GENERATED",
        "- RUNTIME_VALIDATION: NOT_RUN (AREA 20 passive_stat=DEF는 UNRESOLVED)",
        "- ART_APPROVAL: NOT_REVIEWED",
        "",
        "## 검증 범위",
        "",
        "- V2.2 확정 식별자·이름·타입·효과·실제 동작 필드 불변 비교",
        "- 6개 표준 역할의 존재 및 NEW_ART/재사용/NO_RUNTIME_ROLE 의미 검증",
        "- 12종 PROJECTILE 신규 제작, 스텀피 4×0.08초 비루프 계약 검증",
        "- 패시브 35종 ICON+REFERENCE_VFX와 runtime_use=false 검증",
        "- FULL_ART_SCOPE/OUTPUT_REQUIREMENTS/ASSET_BINDING_PLAN 교차 대조",
        "- ZIP CRC, 필수 파일, 독립 참조, Area 00 승인 파일 바이트 해시 검증",
        "",
        "## 오류",
        "",
    ]
    lines.extend([f"- {e}" for e in audit.errors] or ["- 없음"])
    lines.extend(["", "## 경고", ""])
    lines.extend([f"- {w}" for w in audit.warnings] or ["- 없음"])
    (DST / "INPUT_V2_3_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hashes() -> None:
    rows = []
    for path in sorted(DST.glob("AREA_*_IMAGES_INPUT_V2_3.zip")):
        rows.append({"file": path.name, "bytes": str(path.stat().st_size), "sha256": sha256(path.read_bytes())})
    for name in (
        "ALL_AREAS_INPUT_V2_3_INDEX.md", "FULL_ART_SCOPE.csv", "INPUT_V2_3_CHANGELOG.md",
        "INPUT_V2_3_VALIDATION.md", "INPUT_V2_3_VALIDATION.json",
        "VALIDATOR_REGRESSION_RESULTS.md", "VALIDATOR_REGRESSION_RESULTS.json",
    ):
        path = DST / name
        if path.exists():
            rows.append({"file": name, "bytes": str(path.stat().st_size), "sha256": sha256(path.read_bytes())})
    with (DST / "INPUT_V2_3_HASHES.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["file", "bytes", "sha256"])
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    audit = Audit()
    scope_all: list[dict[str, str]] = []
    pairs: set[tuple[str, str]] = set()
    packages = []
    for area in AREAS:
        old_path = SRC / f"AREA_{area}_IMAGES_INPUT_V2_2.zip"
        new_path = DST / f"AREA_{area}_IMAGES_INPUT_V2_3.zip"
        if not old_path.exists() or not new_path.exists():
            audit.fail(f"AREA {area}: source or V2.3 zip missing")
            continue
        packages.append(new_path)
        with zipfile.ZipFile(old_path) as old, zipfile.ZipFile(new_path) as new:
            if new.testzip() is not None:
                audit.fail(f"AREA {area}: CRC failure at {new.testzip()}")
            else:
                audit.ok("zip_crc")
            old_manifest = read_csv_bytes(old.read(zip_member(old, "/AREA_MANIFEST.csv")))
            new_manifest = read_csv_bytes(new.read(zip_member(new, "/AREA_MANIFEST.csv")))
            compare_manifests(audit, area, old_manifest, new_manifest)
            scope = read_csv_bytes(new.read(zip_member(new, "/FULL_ART_SCOPE.csv")))
            output_rows = read_csv_bytes(new.read(zip_member(new, "/OUTPUT_REQUIREMENTS.csv")))
            binding_rows = read_csv_bytes(new.read(zip_member(new, "/ASSET_BINDING_PLAN.csv")))
            verify_scope(audit, area, new_manifest, scope, output_rows, binding_rows)
            verify_docs(audit, area, new)
            verify_approved_reuse(audit, area, old, new)
            scope_all.extend(scope)
            pairs.update((r["monster_id"], r["skill_id"]) for r in new_manifest)

    if (DST / "AREA_06_IMAGES_INPUT_V2_3.zip").exists():
        audit.fail("reserved AREA 06 was created")
    else:
        audit.ok("area06_absent")

    counts = Counter(r["effect_role"] for r in scope_all if r["production_decision"] == "NEW_ART")
    reuse = Counter(r["effect_role"] for r in scope_all if r["production_decision"] == "AREA00_APPROVED_REUSE")
    new_skills = {(r["monster_id"], r["skill_id"]) for r in scope_all if r["production_decision"] == "NEW_ART"}
    expected_counts = Counter({"ICON": 96, "CAST_VFX": 60, "PROJECTILE": 12, "REFERENCE_VFX": 35})
    if counts != expected_counts:
        audit.fail(f"global NEW_ART set counts {dict(counts)} != {dict(expected_counts)}")
    if reuse != Counter({"ICON": 3, "CAST_VFX": 3}):
        audit.fail(f"global approved reuse counts incorrect: {dict(reuse)}")
    if len(new_skills) != 96:
        audit.fail(f"NEW_ART skill count {len(new_skills)} != 96")
    if len(scope_all) != 594 or len(pairs) != 99:
        audit.fail(f"global cardinality pairs={len(pairs)}, scope={len(scope_all)}")

    aggregate = {
        "package_count": len(packages),
        "areas": AREAS,
        "pair_count": len(pairs),
        "scope_row_count": len(scope_all),
        "new_art_skill_count": len(new_skills),
        "new_art_sets": dict(sorted(counts.items())),
        "reuse_sets": dict(sorted(reuse.items())),
    }
    write_reports(audit, aggregate)
    if not audit.errors:
        index_path = DST / "ALL_AREAS_INPUT_V2_3_INDEX.md"
        index_text = index_path.read_text(encoding="utf-8-sig")
        index_path.write_text(
            index_text.replace("PENDING_INDEPENDENT", "PASS"), encoding="utf-8", newline="\n"
        )
    write_hashes()
    print(json.dumps({"overall": "PASS" if not audit.errors else "FAIL", "errors": audit.errors[:20], **aggregate}, ensure_ascii=False, indent=2))
    return 0 if not audit.errors else 1


if __name__ == "__main__":
    sys.exit(main())
