#!/usr/bin/env python3
"""Build the limited INPUT V2.4 correction from V2.3.

Scope is deliberately narrow: current projectile wording, role-specific motion
guidance, and the three Area 00 approved-reuse contracts. No image bytes,
gameplay data, game code, or MSW resources are changed.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DOCS = Path(__file__).resolve().parents[1]
SRC = DOCS / "art" / "images-input-packages-v2_3"
DST = DOCS / "art" / "images-input-packages-v2_4"
REVIEW_ZIP = Path(r"C:/Users/dddd/Downloads/INPUT_V2_3_REVIEW_RESULTS.zip")
AREA00_MAP = DOCS / "art" / "area00-images-output" / "AREA_00_IMAGES_RESOURCE_MAP.csv"
V22 = DOCS / "art" / "images-input-packages-v2_2"

AREAS = [f"{n:02d}" for n in range(1, 21) if n != 6]
APPROVED = {
    ("m_snail", "s_mon_snail_dew_trail"),
    ("m_blue_snail", "s_mon_blue_snail"),
    ("m_slime", "s_mon_slime"),
}
PROJECTILES = {
    "s_mon_stumpy",
    "s_mon_faust",
    "s_mon_star_pixie",
    "s_mon_lunar_pixie",
    "s_mon_shark",
    "s_mon_king_bloctopus",
    "s_mon_roid",
    "s_mon_chimera",
    "s_mon_peach_monkey",
    "s_mon_tae_roon",
    "s_mon_dodo",
    "s_mon_mateon",
}

# Existing motifs are retained and divided by runtime role.  The local-motion
# sentence says what may animate inside the fixed projectile canvas; it never
# replaces the engine translation/ZRotation contract.
PROJECTILE_VISUALS = {
    "s_mon_faust": (
        "실로 묶인 인형 표식과 자주색 저주 침이 시전자 원점에서 응축된 뒤 방출되는 준비광",
        "작은 인형 표식 핵에 저주 침과 짧은 실 자락이 붙은 방향 중립 비행체",
        "실 자락의 떨림과 저주 입자의 국소 맥동만 허용하며 전체 스프라이트 회전은 원화에 굽지 않는다",
    ),
    "s_mon_star_pixie": (
        "작은 별핵이 시전자 원점에서 점등되고 꼬리별 잔상을 만들며 방출되는 섬광",
        "별핵과 짧은 꼬리별 잔상을 고정 중심에 둔 방향 중립 비행체",
        "별핵 밝기와 꼬리 입자의 국소 흔들림만 애니메이션하며 캔버스 전체 이동·회전은 넣지 않는다",
    ),
    "s_mon_lunar_pixie": (
        "초승달 테두리와 은빛 궤도가 시전자 원점에서 월광 구슬을 응축해 내보내는 준비 연출",
        "월광 구슬을 중심으로 초승달 조각과 은빛 궤도가 둘린 방향 중립 비행체",
        "구슬 주변 궤도와 작은 월광 입자의 상대 회전만 허용하며 전체 스프라이트 회전은 넣지 않는다",
    ),
    "s_mon_shark": (
        "압축 수류와 이빨 톱니 윤곽이 시전자 원점에서 수류탄 형태로 뭉쳐 방출되는 연출",
        "이빨 톱니가 둘린 압축 수류탄과 짧은 기포 꼬리를 고정 중심에 둔 방향 중립 비행체",
        "내부 수류와 기포의 국소 순환·맥동만 허용하며 전체 수류탄의 이동·회전은 엔진에 맡긴다",
    ),
    "s_mon_king_bloctopus": (
        "왕관 블록과 각진 에너지 조각이 시전자 원점에서 조립되어 발사되는 준비 연출",
        "왕관 블록 핵과 소수의 각진 에너지 조각으로 이루어진 방향 중립 비행체",
        "왕관 블록 중심부와 주변 조각의 상대 회전만 표현하고 캔버스 전체 회전은 원화에 넣지 않는다",
    ),
    "s_mon_roid": (
        "알카드노 금속 코어가 시전자 원점에서 직선 에너지를 압축한 뒤 방출하는 점화광",
        "금속 코어와 압축 에너지 외곽으로 구성된 방향 중립 비행체",
        "코어 내부 광량과 작은 전기 입자의 국소 맥동만 허용하며 전체 스프라이트 회전은 넣지 않는다",
    ),
    "s_mon_chimera": (
        "서로 다른 두 산성액 줄기가 시전자 원점에서 합쳐져 포격탄으로 응축되는 준비 연출",
        "두 산성액이 합쳐진 핵과 짧은 액체 꼬리를 가진 방향 중립 비행체",
        "핵 내부 두 액체의 국소 소용돌이와 방울 변형만 허용하며 캔버스 전체 이동·회전은 넣지 않는다",
    ),
    "s_mon_peach_monkey": (
        "천도 복숭아와 잎사귀 바람이 시전자 원점에서 모여 투척 직전 반짝이는 준비 연출",
        "천도 복숭아와 짧은 잎사귀 꼬리를 고정 중심에 둔 방향 중립 비행체",
        "잎사귀 꼬리의 국소 펄럭임과 표면 반짝임만 표현하고 포물선 이동·전체 회전은 엔진에 맡긴다",
    ),
    "s_mon_tae_roon": (
        "두 권격이 시전자 원점에서 마주쳐 쌍둥이 바람 소용돌이를 압축·방출하는 연출",
        "서로 마주 보는 두 권격풍과 중앙 바람핵으로 구성된 방향 중립 비행체",
        "두 권격풍의 중심 기준 상대 역회전은 유지하되 캔버스 전체 회전은 원화에 굽지 않는다",
    ),
    "s_mon_dodo": (
        "빛바랜 기억 조각이 시전자 원점의 검은 포식구로 빨려 들어가며 방출되는 준비 연출",
        "검은 포식구와 안쪽으로 말려드는 기억 조각을 고정 중심에 둔 방향 중립 비행체",
        "기억 조각의 중심향 국소 나선과 포식구 맥동만 허용하며 전체 스프라이트 회전은 넣지 않는다",
    ),
    "s_mon_mateon": (
        "외계 수정핵이 시전자 원점에서 황록 광선을 응축해 둥근 탄으로 방출하는 점화 연출",
        "외계 수정핵과 얇은 황록 광륜으로 구성된 방향 중립 비행체",
        "수정핵 밝기와 광륜 입자의 국소 궤도만 표현하고 전체 스프라이트 이동·회전은 엔진에 맡긴다",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha256(path.read_bytes())


def read_csv_path(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_zip(zf: zipfile.ZipFile, member: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(zf.read(member).decode("utf-8-sig"))))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def zip_tree(root: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, f"{root.name}/{path.relative_to(root).as_posix()}")


def append_fields(rows: list[dict[str, str]], fields: list[str]) -> None:
    for row in rows:
        for field in fields:
            row.setdefault(field, "n/a")


def load_review_csv(name: str) -> list[dict[str, str]]:
    with zipfile.ZipFile(REVIEW_ZIP) as zf:
        member = f"V2_3_REVIEW/{name}"
        return read_csv_zip(zf, member)


def load_v22_approved() -> dict[tuple[str, str], tuple[str, str]]:
    result: dict[tuple[str, str], tuple[str, str]] = {}
    for area in ("01", "03"):
        path = V22 / f"AREA_{area}_IMAGES_INPUT_V2_2.zip"
        with zipfile.ZipFile(path) as zf:
            member = next(n for n in zf.namelist() if n.endswith("/ASSET_BINDING_PLAN.csv"))
            for row in read_csv_zip(zf, member):
                if row.get("decision") != "APPROVED_REUSE":
                    continue
                clip, icon = row["current_ruid"].split("|", 1)
                result[(row["monster_id"], row["skill_id"])] = (icon, clip)
    return result


def load_approved() -> dict[tuple[str, str], dict[str, str]]:
    official = {(r["monster_id"], r["skill_id"]): r for r in read_csv_path(AREA00_MAP)}
    review = {(r["monster_id"], r["skill_id"]): r for r in load_review_csv("AREA00_APPROVAL_SOURCE.csv")}
    v22 = load_v22_approved()
    selected: dict[tuple[str, str], dict[str, str]] = {}
    for key in APPROVED:
        if key not in official or key not in review or key not in v22:
            raise RuntimeError(f"approval evidence missing for {key}")
        row = official[key]
        if row["icon_ruid"] != review[key]["icon_ruid"] or row["animationclip_ruid"] != review[key]["animationclip_ruid"]:
            raise RuntimeError(f"review/Area00 approval mismatch for {key}")
        if (row["icon_ruid"], row["animationclip_ruid"]) != v22[key]:
            raise RuntimeError(f"V2.2/Area00 approval mismatch for {key}")
        selected[key] = row
    return selected


def member_relative(stage: Path, path: Path) -> str:
    return path.relative_to(stage).as_posix()


def approved_paths(stage: Path, row: dict[str, str], role: str) -> tuple[list[str], list[str]]:
    old = [p for p in row["required_file_set"].split("|") if p and p != "none"]
    root = None
    for p in old:
        if "/ICON/" in p or "/VFX/" in p:
            root = p.rsplit("/", 2)[0]
            break
    if root is None:
        raise RuntimeError(f"cannot locate approved reuse root for {row['monster_id']}")
    folder = stage / root
    if role == "ICON":
        files = sorted(member_relative(stage, p) for p in (folder / "ICON").glob("*.png"))
    elif role == "CAST_VFX":
        files = sorted(member_relative(stage, p) for p in (folder / "VFX").glob("*_F??.png"))
    else:
        raise AssertionError(role)
    previews = sorted(member_relative(stage, p) for p in (folder / "PREVIEW").glob("*.png"))
    return files, previews


def output_paths(manifest: dict[str, str], role: str, frame_count: int) -> list[str]:
    work_order = str(manifest["work_order"]).strip()
    work_order = f"{int(work_order):03d}" if work_order.isdigit() else work_order
    prefix = f"{work_order}_{manifest['monster_id']}_{manifest['skill_id']}"
    folder = manifest["folder"].strip("/")
    if role == "ICON":
        return [f"AREA_{manifest['area_id'][-2:]}_IMAGES_OUTPUT/{folder}/ICON/{prefix}_ICON.png"]
    return [
        f"AREA_{manifest['area_id'][-2:]}_IMAGES_OUTPUT/{folder}/CAST/{prefix}_CAST_F{i:02d}.png"
        for i in range(frame_count)
    ]


EVIDENCE_FIELDS = [
    "baseline_current_evidence",
    "approved_target_ruid",
    "approved_frame_sprite_ruids",
    "source_path",
    "output_path",
    "preview_reference_files",
    "approval_evidence",
    "approval_status",
]


def patch_scope(
    stage: Path,
    scope: list[dict[str, str]],
    manifests: dict[tuple[str, str], dict[str, str]],
    approved: dict[tuple[str, str], dict[str, str]],
) -> None:
    append_fields(scope, EVIDENCE_FIELDS)
    for row in scope:
        key = (row["monster_id"], row["skill_id"])
        if row["production_decision"] != "AREA00_APPROVED_REUSE":
            continue
        if key not in approved or row["effect_role"] not in {"ICON", "CAST_VFX"}:
            raise RuntimeError(f"unexpected approved reuse row {key} {row['effect_role']}")
        role = row["effect_role"]
        files, previews = approved_paths(stage, row, role)
        expected = 1 if role == "ICON" else 8
        if len(files) != expected:
            raise RuntimeError(f"{key} {role}: expected {expected} approved files, got {len(files)}")
        evidence = approved[key]
        approved_ruid = evidence["icon_ruid"] if role == "ICON" else evidence["animationclip_ruid"]
        row["baseline_current_evidence"] = row["current_resource"]
        row["approved_target_ruid"] = approved_ruid
        row["approved_frame_sprite_ruids"] = evidence["frame_sprite_ruids"] if role == "CAST_VFX" else "n/a"
        row["source_path"] = "|".join(files)
        row["required_file_set"] = "|".join(files)
        row["output_path"] = "|".join(output_paths(manifests[key], role, expected))
        row["preview_reference_files"] = "|".join(previews)
        row["approval_evidence"] = "AREA_00_IMAGES_RESOURCE_MAP.csv + V2.2 ASSET_BINDING_PLAN.csv + INPUT_V2_3_REVIEW_RESULTS"
        row["approval_status"] = "CONFIRMED_MATCH"
        if role == "ICON":
            row["future_target"] = f"icon_ruid -> approved_icon_ruid={approved_ruid}"
        else:
            row["future_target"] = f"layer_ruids -> approved_animationclip_ruid={approved_ruid}"


def sync_rows(scope: list[dict[str, str]], target: list[dict[str, str]]) -> None:
    by_key = {(r["monster_id"], r["skill_id"], r["effect_role"]): r for r in scope}
    append_fields(target, EVIDENCE_FIELDS)
    for row in target:
        source = by_key[(row["monster_id"], row["skill_id"], row["effect_role"])]
        for field in EVIDENCE_FIELDS + ["required_file_set", "future_target"]:
            row[field] = source[field]
        if "production_decision" in row:
            row["production_decision"] = source["production_decision"]
        if "decision" in row:
            row["decision"] = source["production_decision"]


def patch_runtime_conflicts(old_text: str) -> str:
    text = old_text.replace("V2.3", "V2.4")
    replacement = """## Projectile scope

- 실제 PROJECTILE 역할 12종은 모두 `NEW_ART`다. 기존 `projectile_ruid`는 현재 연결과 출처를 확인하기 위한 baseline evidence일 뿐 기존 비행체 아트를 유지하라는 지시가 아니다.
- 스텀피를 포함한 12종 모두 4프레임 × 0.08초 = 0.32초 non-loop로 제작하고, 0.35초 엔티티 수명 안에서 완주한다.
- `skill.range`는 targeting_range이며 착탄 피해 반경은 현재 코드의 `projectile_hit_radius=0.8wu`다. 두 값을 이미지 범위로 합치지 않는다.
- PROJECTILE 원화는 로컬 중심·방향 중립이다. 엔진이 시전자+h에서 목표+h까지 이동시키고 ZRotation을 적용하므로 캔버스 전체 이동·전체 스프라이트 회전을 프레임에 중복하지 않는다. PROJECTILE FlipX나 진행 방향 자동 정렬은 현재 경로에 없다.
- 이번 revision은 문서·재사용 계약 보완이다. 게임의 실제 RUID 연결은 변경하지 않는다.
"""
    text = re.sub(r"## Projectile scope\s*.*?(?=\n## |\Z)", replacement.rstrip(), text, flags=re.S)
    return text.rstrip() + "\n"


def patch_readme(text: str, area: str) -> str:
    text = text.replace("V2.3", "V2.4").replace(" V2\n", " V2.4\n")
    text = text.replace(
        "1. PACKAGE_REVISION과 AREA_MANIFEST에서 범위와 보류를 확인한다.",
        "1. `PACKAGE_REVISION_V2_4.md`와 `FULL_ART_SCOPE.csv`를 현행 revision/scope의 첫 기준으로 읽고, AREA_MANIFEST에서 고정 데이터를 확인한다.",
    )
    text = text.replace("PACKAGE_REVISION.md", "PACKAGE_REVISION_V2_4.md")
    return text


def patch_master(text: str) -> str:
    text = text.replace("V2.3", "V2.4")
    text = text.replace(
        "1. `PACKAGE_REVISION.md`, `AREA_MANIFEST`, 모든 `GENERATION_SPEC.md`, `RUNTIME_ROLE_MAP.md`, `SOURCE_PROVENANCE.md`를 먼저 읽으세요.",
        "1. `PACKAGE_REVISION_V2_4.md`와 `FULL_ART_SCOPE.csv`를 현행 revision/scope의 첫 기준으로 읽고, 이어서 `AREA_MANIFEST`, 모든 `GENERATION_SPEC.md`, `RUNTIME_ROLE_MAP.md`, `SOURCE_PROVENANCE.md`를 읽으세요.",
    )
    text = text.replace("PACKAGE_REVISION.md", "PACKAGE_REVISION_V2_4.md")
    return text


def binding_plan_doc() -> str:
    return """# ASSET BINDING PLAN — V2.4

`ASSET_BINDING_PLAN.csv`가 현행 연결 계획 원장이다. decision 값은 다음 세 가지만 사용한다.

- `NEW_ART`: 해당 역할의 새 아트를 제작한다. 현재 RUID는 baseline/current evidence일 뿐 유지 지시가 아니다.
- `AREA00_APPROVED_REUSE`: 정확히 확인된 Area 00 승인 파일과 승인 RUID를 재사용한다. `baseline_current_evidence`와 `approved_target_ruid`를 구분해서 읽는다.
- `NO_RUNTIME_ROLE`: 현재 실행 경로에 해당 시각 역할이 없으므로 파일을 만들거나 연결하지 않는다.

`source_path`는 INPUT에 포함된 원본 또는 승인 재사용 파일이고 `output_path`는 향후 OUTPUT에 둘 최종 경로다. Preview는 `preview_reference_files`에만 기록하며 게임 반입 원본과 `required_file_set`에 섞지 않는다.

이 문서는 제작·향후 연결 계획이며 실제 리소스 업로드, AnimationClip 생성, SkillTable RUID 변경이 완료됐다는 뜻이 아니다.
"""


def role_map_doc(manifest: dict[str, str], rows: list[dict[str, str]]) -> str:
    lines = [
        f"# Runtime Role Map — {manifest['monster_id']} / {manifest['skill_id']} — V2.4",
        "",
        "| role | current | production | files | timing | baseline/current evidence | approved target | future target | unresolved |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        timing = f"{row['frame_count']}f / {row['canvas']} / {row['frame_seconds']} / {row['playback_mode']}"
        lines.append(
            f"| {row['effect_role']} | {row['current_use']} · {row['current_field_or_layer']} | {row['production_decision']} | "
            f"`{row['required_file_set']}` | {timing} | `{row['baseline_current_evidence']}` | "
            f"`{row['approved_target_ruid']}` | `{row['future_target']}` | {row['unresolved']} |"
        )
    required = [r for r in rows if r["production_decision"] != "NO_RUNTIME_ROLE"]
    lines += [
        "", "## Authoritative contract", "",
        f"- required_roles: `{'|'.join(r['effect_role'] for r in required)}`",
        f"- production_decisions: `{'|'.join(r['production_decision'] for r in required)}`",
        f"- future_targets: `{'|'.join(r['future_target'] for r in required)}`",
        f"- confirmed design effect preserved: {manifest['actual_effect']}",
        f"- runtime_effect preserved: {manifest['runtime_effect']}",
        f"- runtime_motion preserved: {manifest['runtime_motion']}",
        f"- targeting_range={manifest['targeting_range']} / impact_radius={manifest['impact_radius']} / impact_delay={manifest['impact_delay']} / max_targets={manifest['max_targets']}",
        "",
    ]
    approved_rows = [r for r in rows if r["production_decision"] == "AREA00_APPROVED_REUSE"]
    if approved_rows:
        lines += ["## Area 00 approved reuse", ""]
        for row in approved_rows:
            lines += [
                f"- {row['effect_role']} baseline/current evidence: `{row['baseline_current_evidence']}`",
                f"- {row['effect_role']} approved target RUID: `{row['approved_target_ruid']}`",
                f"- source_path: `{row['source_path']}`",
                f"- output_path: `{row['output_path']}`",
                f"- preview_reference_files: `{row['preview_reference_files']}`",
            ]
        lines.append("")
    lines.append("No role marked `NO_RUNTIME_ROLE` may be generated merely because it appears in the inventory. Runtime import remains separate from production readiness.")
    return "\n".join(lines) + "\n"


def replace_line(text: str, prefix: str, replacement: list[str]) -> str:
    lines = text.splitlines()
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.startswith(prefix):
            out.extend(replacement)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        raise RuntimeError(f"line not found: {prefix}")
    return "\n".join(out) + "\n"


def replace_first_line(text: str, prefix: str, replacement: list[str]) -> str:
    lines = text.splitlines()
    out: list[str] = []
    replaced = False
    for line in lines:
        if not replaced and line.startswith(prefix):
            out.extend(replacement)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        raise RuntimeError(f"line not found: {prefix}")
    return "\n".join(out) + "\n"


def patch_projectile_spec(text: str, skill_id: str) -> str:
    if skill_id == "s_mon_stumpy":
        marker = "- PROJECTILE 역할 구분: CAST_VFX는 현재 실행 역할이 없다. 생기탄 중심의 나이테·새싹·입자만 로컬에서 맥동하며, 캔버스 전체 이동·전체 스프라이트 회전은 엔진 이동/ZRotation과 중복하지 않는다."
        if marker not in text:
            text = text.replace("- 진행 방향:", marker + "\n- 진행 방향:")
        return text
    cast, projectile, local = PROJECTILE_VISUALS[skill_id]
    old_line = next(line for line in text.splitlines() if line.startswith("- 진행 방향·엔진 이동:"))
    drift = ""
    if "layer drift는 엔진 적용:" in old_line:
        drift = " 기존 CAST layer drift는 엔진 적용:" + old_line.split("layer drift는 엔진 적용:", 1)[1]
    text = replace_line(text, "- 진행 방향·엔진 이동:", [
        f"- CAST 방향/표현: 우측 기준 제작 후 FlipX는 CAST_VFX에만 적용한다. {cast}.{drift}",
        f"- PROJECTILE 방향/표현: 로컬 중심·방향 중립이며 PROJECTILE FlipX나 진행 방향 자동 정렬을 가정하지 않는다. {projectile}.",
        f"- PROJECTILE 국소 애니메이션: {local}. 엔진이 시전자+h에서 목표+h까지 이동시키고 ZRotation을 적용하므로 그 전체 이동·회전을 이미지 프레임에 중복하지 않는다.",
    ])
    text = replace_line(text, "- 시간 흐름:", [
        "- 역할별 시간 흐름: CAST는 발사 준비 → 방출 섬광 → 짧은 잔광. PROJECTILE은 F00 형성 → F01 상승 → F02 절정 → F03 안정/잔광을 동일 로컬 중심에서 완결하며 위치 이동은 엔진에 맡긴다.",
    ])
    return text


def patch_spec(text: str, manifest: dict[str, str], rows: list[dict[str, str]]) -> str:
    text = text.replace("V2.3", "V2.4")
    by_role = {r["effect_role"]: r for r in rows}
    for role in ("ICON", "CAST_VFX", "PROJECTILE", "REFERENCE_VFX"):
        row = by_role[role]
        if row["production_decision"] == "NO_RUNTIME_ROLE":
            continue
        profile = f"- {role}: {row['production_decision']} / {row['required_file_set']}"
        if role == "ICON":
            profile += " / 256x256 RGBA"
        else:
            profile += f" / {row['frame_count']} frames × {row['canvas']} / {row['frame_seconds']}s per frame / {row['playback_mode']}"
        text = replace_first_line(text, f"- {role}:", [profile])

    for role, row in by_role.items():
        prefix = f"- {role}: current="
        replacement = (
            f"- {role}: current={row['current_use']}; decision={row['production_decision']}; "
            f"field={row['current_field_or_layer']}; files={row['required_file_set']}; target={row['future_target']}"
        )
        text = replace_line(text, prefix, [replacement])

    if manifest["skill_id"] in PROJECTILES:
        text = patch_projectile_spec(text, manifest["skill_id"])
        contract = "- PROJECTILE 제작 계약: 4×0.08=0.32초 non-loop로 0.35초 수명 안에 완주한다. targeting_range와 현재 착탄 피해 반경 0.8wu를 구분하며 게임 수치는 변경하지 않는다."
        if contract not in text:
            text = text.replace("### Shared constraints\n", "### Shared constraints\n\n" + contract + "\n")

    approved_rows = [r for r in rows if r["production_decision"] == "AREA00_APPROVED_REUSE"]
    if approved_rows:
        evidence_lines = ["### Area 00 approved reuse evidence", ""]
        for row in approved_rows:
            evidence_lines += [
                f"- {row['effect_role']} baseline/current evidence: `{row['baseline_current_evidence']}`",
                f"- {row['effect_role']} approved target RUID: `{row['approved_target_ruid']}`",
                f"- {row['effect_role']} source_path: `{row['source_path']}`",
                f"- {row['effect_role']} output_path: `{row['output_path']}`",
                f"- {row['effect_role']} preview_reference_files: `{row['preview_reference_files']}`",
            ]
        evidence_lines += ["- 승인 근거: Area 00 resource map과 V2.2 approved binding 값이 일치함. 게임 RUID는 이 INPUT revision에서 변경하지 않는다.", ""]
        text = text.replace("### Shared constraints\n", "\n".join(evidence_lines) + "\n### Shared constraints\n")
    return text


def write_reuse_contract(stage: Path, scope: list[dict[str, str]]) -> None:
    rows = [r for r in scope if r["production_decision"] == "AREA00_APPROVED_REUSE"]
    if not rows:
        return
    fields = [
        "area_id", "monster_id", "skill_id", "effect_role", "baseline_current_evidence",
        "approved_target_ruid", "approved_frame_sprite_ruids", "required_file_set", "source_path",
        "output_path", "preview_reference_files", "approval_evidence", "approval_status",
    ]
    write_csv(stage / "AREA00_APPROVED_REUSE_CONTRACT_V2_4.csv", rows, fields)


def build() -> None:
    if DST.exists():
        raise RuntimeError(f"refusing to overwrite existing {DST}")
    if not REVIEW_ZIP.exists():
        raise RuntimeError(f"review ZIP missing: {REVIEW_ZIP}")
    approved = load_approved()
    DST.mkdir(parents=True)
    evidence_dir = DST / "evidence"
    evidence_dir.mkdir()
    with zipfile.ZipFile(REVIEW_ZIP) as zf:
        for name in ("AREA00_APPROVAL_SOURCE.csv", "PROJECTILE_NEW_SCOPE.csv", "SOURCE_EVIDENCE.md"):
            data = zf.read(f"V2_3_REVIEW/{name}")
            (evidence_dir / name).write_bytes(data)

    source_hashes = {p.name: sha_file(p) for p in sorted(SRC.glob("AREA_*_IMAGES_INPUT_V2_3.zip"))}
    all_scope: list[dict[str, str]] = []
    index_rows = []
    for area in AREAS:
        source_zip = SRC / f"AREA_{area}_IMAGES_INPUT_V2_3.zip"
        if not source_zip.exists():
            raise RuntimeError(f"missing source {source_zip.name}")
        with tempfile.TemporaryDirectory(prefix=f"area_{area}_v24_") as tmp:
            tmp_path = Path(tmp)
            with zipfile.ZipFile(source_zip) as zf:
                zf.extractall(tmp_path)
            old_stage = next(p for p in tmp_path.iterdir() if p.is_dir())
            stage = tmp_path / f"AREA_{area}_IMAGES_INPUT_V2_4"
            old_stage.rename(stage)

            manifest = read_csv_path(stage / "AREA_MANIFEST.csv")
            manifests = {(r["monster_id"], r["skill_id"]): r for r in manifest}
            scope = read_csv_path(stage / "FULL_ART_SCOPE.csv")
            output = read_csv_path(stage / "OUTPUT_REQUIREMENTS.csv")
            binding = read_csv_path(stage / "ASSET_BINDING_PLAN.csv")
            patch_scope(stage, scope, manifests, approved)
            sync_rows(scope, output)
            sync_rows(scope, binding)

            write_csv(stage / "FULL_ART_SCOPE.csv", scope, list(scope[0]))
            write_csv(stage / "OUTPUT_REQUIREMENTS.csv", output, list(output[0]))
            write_csv(stage / "ASSET_BINDING_PLAN.csv", binding, list(binding[0]))
            write_reuse_contract(stage, scope)

            grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
            for row in scope:
                grouped.setdefault((row["monster_id"], row["skill_id"]), []).append(row)
            for key, rows in grouped.items():
                folder = stage / manifests[key]["folder"]
                spec = folder / "GENERATION_SPEC.md"
                spec.write_text(patch_spec(spec.read_text(encoding="utf-8-sig"), manifests[key], rows), encoding="utf-8", newline="\n")
                (folder / "RUNTIME_ROLE_MAP.md").write_text(role_map_doc(manifests[key], rows), encoding="utf-8", newline="\n")

            old_conflicts = stage / "RUNTIME_CONFLICTS_V2_3.md"
            old_conflict_text = old_conflicts.read_text(encoding="utf-8-sig")
            history = stage / "history"
            history.mkdir(exist_ok=True)
            old_conflicts.rename(history / old_conflicts.name)
            (stage / "RUNTIME_CONFLICTS_V2_4.md").write_text(patch_runtime_conflicts(old_conflict_text), encoding="utf-8", newline="\n")

            for name in ("PACKAGE_REVISION_V2_3.md", "PACKAGE_STATUS_V2_3.md"):
                path = stage / name
                if path.exists():
                    path.rename(history / name)
            (stage / "PACKAGE_REVISION_V2_4.md").write_text(
                f"# PACKAGE REVISION — V2.4\n\n"
                f"- source: `{source_zip.name}`\n"
                f"- source_sha256: `{source_hashes[source_zip.name]}`\n"
                f"- review_source: `{REVIEW_ZIP.name}` / `{sha_file(REVIEW_ZIP)}`\n"
                f"- built_utc: `{datetime.now(timezone.utc).isoformat()}`\n"
                "- scope: limited current-document, projectile role wording, and Area 00 approved-reuse contract correction\n"
                "- production scope reduced: `false`\n"
                "- images/OUTPUT/resources/game files changed: `false`\n",
                encoding="utf-8", newline="\n",
            )
            (stage / "PACKAGE_STATUS_V2_4.md").write_text(
                f"# Package status — area_{area} / V2.4\n\n"
                "| Axis | Status |\n|---|---|\n"
                "| PACKAGE_VALIDATION | PASS_BUILD; see global independent validation |\n"
                "| GENERATION_READY | READY |\n"
                "| IMPORT_VALIDATION | NOT_READY_ASSETS_NOT_GENERATED |\n"
                f"| RUNTIME_VALIDATION | {'UNRESOLVED' if area == '20' else 'NOT_RUN'} |\n"
                "| ART_APPROVAL | NOT_REVIEWED |\n",
                encoding="utf-8", newline="\n",
            )
            readme = stage / "README_START_HERE.md"
            readme.write_text(patch_readme(readme.read_text(encoding="utf-8-sig"), area), encoding="utf-8", newline="\n")
            master = stage / "CHATGPT_IMAGES_MASTER_PROMPT.md"
            master.write_text(patch_master(master.read_text(encoding="utf-8-sig")), encoding="utf-8", newline="\n")
            (stage / "ASSET_BINDING_PLAN.md").write_text(binding_plan_doc(), encoding="utf-8", newline="\n")

            target = DST / f"AREA_{area}_IMAGES_INPUT_V2_4.zip"
            zip_tree(stage, target)
            all_scope.extend(scope)
            index_rows.append({
                "area": area,
                "name": manifest[0]["area_name"],
                "monsters": len(manifest),
                "zip": target.name,
                "source_sha256": source_hashes[source_zip.name],
                "sha256": sha_file(target),
            })

    write_csv(DST / "FULL_ART_SCOPE.csv", all_scope, list(all_scope[0]))
    counts = Counter(r["effect_role"] for r in all_scope if r["production_decision"] == "NEW_ART")
    reuse = Counter(r["effect_role"] for r in all_scope if r["production_decision"] == "AREA00_APPROVED_REUSE")
    index = [
        "# ALL AREAS INPUT V2.4 INDEX", "",
        "V2.4 preserves V2.3 full new-art scope and only corrects current documentation and the confirmed Area 00 reuse contract.", "",
        "| Area | Name | Monsters | Package | Package validation | Generation ready | SHA-256 |",
        "|---:|---|---:|---|---|---|---|",
    ]
    for row in index_rows:
        index.append(f"| {row['area']} | {row['name']} | {row['monsters']} | `{row['zip']}` | PENDING_INDEPENDENT | READY | `{row['sha256']}` |")
    index += ["", "- Area 06: reserved/absent; not created.", "- Import: NOT_READY_ASSETS_NOT_GENERATED.", "- Runtime: NOT_RUN (Area 20 conflict remains UNRESOLVED).", "- Art approval: NOT_REVIEWED.", ""]
    (DST / "ALL_AREAS_INPUT_V2_4_INDEX.md").write_text("\n".join(index), encoding="utf-8")
    (DST / "INPUT_V2_4_CHANGELOG.md").write_text(
        "# INPUT V2.4 CHANGELOG\n\n"
        "- Preserved V2.3 full NEW_ART scope and all fixed skill/gameplay data.\n"
        "- Removed the current 11-projectile KEEP contradiction; all 12 actual PROJECTILE roles remain NEW_ART.\n"
        "- Split CAST FlipX guidance from direction-neutral PROJECTILE art and clarified local motif motion versus engine translation/ZRotation for the 11 newly expanded projectile specs.\n"
        "- Kept Stumpy as PROJECTILE+ICON only with 4×0.08=0.32s inside the 0.35s lifetime and impact radius 0.8wu.\n"
        "- Split three Area 00 reuse pairs into ICON=1 required file and CAST_VFX=8 required frames; previews are separate references.\n"
        "- Added baseline/current evidence, approved target RUID, source path, output path, and approval-source fields.\n"
        "- Synchronized FULL_ART_SCOPE, OUTPUT_REQUIREMENTS, ASSET_BINDING_PLAN, GENERATION_SPEC, RUNTIME_ROLE_MAP, README, MASTER_PROMPT, and runtime-conflict documents.\n"
        "- No images, OUTPUT, MSW resources, RUID bindings, code, or game data were changed.\n",
        encoding="utf-8", newline="\n",
    )
    (DST / "BUILD_RESULT.json").write_text(json.dumps({
        "areas": len(index_rows), "pairs": len({(r['monster_id'], r['skill_id']) for r in all_scope}),
        "scope_rows": len(all_scope), "new_art_sets": dict(counts), "reuse_sets": dict(reuse),
        "review_zip_sha256": sha_file(REVIEW_ZIP),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(DST), "areas": len(index_rows), "new_art_sets": dict(counts), "reuse_sets": dict(reuse)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
