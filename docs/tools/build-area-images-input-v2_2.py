#!/usr/bin/env python3
"""Build targeted AREA 01~20 INPUT V2.2 packages from immutable V2.1 ZIPs.

This revision changes documentation and validation contracts only. It does not
edit game data/code, Area 00, prior INPUT/OUTPUT packages, or generate art.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "art" / "images-input-packages-v2_1"
OUT = ROOT / "docs" / "art" / "images-input-packages-v2_2"
CROSSCHECK = Path(r"C:/Users/dddd/Downloads/V2_1_EVIDENCE_CROSSCHECK_20260912.zip")
BASELINE = ROOT / "docs" / "art" / "images-input-packages-v2" / "SOURCE_BASELINE.json"
AREA00_RESOURCE_MAP = ROOT / "docs" / "art" / "area00-images-output" / "AREA_00_IMAGES_RESOURCE_MAP.csv"
MISLOCATED_SKILLS = ROOT / "Mislocated" / "MyDesk" / "GameData" / "SkillTable.csv"
TARGET_IDS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]

PROJECTILE_SECONDS = 0.35
PROJECTILE_HIT_RADIUS = 0.8
BOSS_RANGE_MULTIPLIER = 0.667
STUMPY_ID = "s_mon_stumpy"
STONE_MASK_ID = "s_mon_mutant_stone_mask"

PROJECTILE_CODE = "RootDesk/MyDesk/Combat/SkillProjectile.mlua"
PROJECTILE_MODEL = "RootDesk/MyDesk/Models/Effects/SkillProjectile.model"
SKILL_EFFECT_CODE = "RootDesk/MyDesk/Combat/SkillEffect.mlua"
PLAYER_ATTACK_CODE = "RootDesk/MyDesk/PlayerAttack.mlua"
MONSTER_ATTACK_CODE = "RootDesk/MyDesk/MonsterAttack.mlua"
PLAYER_STATS_CODE = "RootDesk/MyDesk/Player/PlayerStats.mlua"
VERIFY_CODE = "RootDesk/MyDesk/GameData/GameDataVerify.mlua"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(data: bytes | str) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: str | float | int | None) -> str:
    if value is None or value == "":
        return "0"
    try:
        number = float(value)
        return str(int(number)) if number.is_integer() else str(number)
    except (TypeError, ValueError):
        return str(value)


def split(raw: str | None) -> list[str]:
    return [] if not raw else raw.split("|")


def layers(skill: dict[str, str]) -> list[dict[str, str]]:
    ruids = split(skill.get("layer_ruids"))
    columns = {
        "type": split(skill.get("layer_types")),
        "style": split(skill.get("layer_styles")),
        "delay": split(skill.get("layer_delays")),
        "duration": split(skill.get("layer_durations")),
        "scale": split(skill.get("layer_scales")),
        "offset_x": split(skill.get("layer_offsets_x")),
        "offset_y": split(skill.get("layer_offsets_y")),
        "drift_x": split(skill.get("layer_drifts_x")),
        "drift_y": split(skill.get("layer_drifts_y")),
    }
    defaults = {"type": "sprite", "style": "burst", "delay": "0", "duration": "0.4", "scale": "1", "offset_x": "0", "offset_y": "0", "drift_x": "0", "drift_y": "0"}
    result = []
    for i, ruid in enumerate(ruids):
        row = {"ruid": ruid}
        for key, values in columns.items():
            row[key] = values[i] if i < len(values) and values[i] else defaults[key]
        result.append(row)
    return result


def skill_type(skill: dict[str, str]) -> str:
    if skill.get("skill_kind") == "passive":
        return "패시브"
    if skill.get("skill_kind") == "defense":
        return "버프"
    return "액티브"


def git_bytes(commit: str, rel: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{rel}"], cwd=ROOT)


def remove_section(text: str, title: str) -> str:
    pattern = re.compile(rf"(?ms)^## {re.escape(title)}\n.*?(?=^## |\Z)")
    return pattern.sub("", text).rstrip() + "\n"


def replace_section(text: str, title: str, body: str) -> str:
    text = remove_section(text, title)
    return text.rstrip() + f"\n\n## {title}\n\n{body.strip()}\n"


def zip_tree(root: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(root.parent).as_posix())


def extract_source(aid: str, parent: Path) -> Path:
    source_zip = SOURCE / f"{aid.upper()}_IMAGES_INPUT_V2_1.zip"
    with zipfile.ZipFile(source_zip) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"CRC failure in {source_zip.name}: {bad}")
        archive.extractall(parent)
    old = parent / f"{aid.upper()}_IMAGES_INPUT_V2_1"
    new = parent / f"{aid.upper()}_IMAGES_INPUT_V2_2"
    old.rename(new)
    return new


def parse_profile(spec: str) -> tuple[int, int, str]:
    match = re.search(r"(?:VFX|REFERENCE_VFX|PROJECTILE):\s*(\d+) frames, 각 (\d+)×(\d+) RGBA PNG, (?:약 |정확히 )?([0-9.]+) sec/frame", spec)
    if not match:
        raise RuntimeError("missing VFX output profile")
    if match.group(2) != match.group(3):
        raise RuntimeError("non-square VFX profile")
    return int(match.group(1)), int(match.group(2)), match.group(4)


def current_runtime_motion(skill: dict[str, str], balance: dict[str, float]) -> str:
    typ = skill_type(skill)
    if typ == "패시브":
        return "CAST 호출 없음. PlayerStats가 보유 수량을 읽어 스탯을 계산한다. REFERENCE_VFX는 제작 검수용이며 runtime_use=false다."
    layer_list = layers(skill)
    layer_text = "CAST 레이어 없음" if not layer_list else "; ".join(
        f"L{i + 1} delay={x['delay']}s duration={x['duration']}s offset=({x['offset_x']},{x['offset_y']})wu drift=({x['drift_x']},{x['drift_y']})wu/s"
        for i, x in enumerate(layer_list)
    )
    if skill.get("projectile_ruid"):
        range_value = float(skill.get("range") or 0)
        monster_range = range_value * balance["boss_skill_range_multiplier"]
        return (
            f"skill.range={fmt(range_value)}wu는 플레이어 조준 거리이며 몬스터 사용 시 {fmt(monster_range)}wu로 대상 탐색한다. "
            f"projectile_ruid {skill['projectile_ruid']}를 시전자+h에서 목표+h로 {fmt(balance['projectile_seconds'])}초 동안 이동·Z회전시킨 뒤, "
            f"착탄점 반경 {fmt(balance['projectile_hit_radius'])}wu에서 최대 {('제한 없음' if float(skill.get('max_targets') or 0) <= 0 else fmt(skill['max_targets']) + '대상')} 피해를 판정한다. {layer_text}."
        )
    if float(skill.get("dash_distance") or 0) > 0:
        return (
            f"플레이어는 8방향으로 {fmt(skill['dash_distance'])}wu를 {fmt(balance['skill_dash_seconds'])}초 이동하고 계산 도착점에서 피해를 판정한다. "
            "PlayCast는 직후 서버가 보는 시전자 위치를 사용하므로 CAST 위치와 계산 피해점의 일치는 보장되지 않는다. "
            f"몬스터는 dash 분기 없이 시전자 중심 원형 판정 후 명중 시 CAST한다. {layer_text}."
        )
    if typ == "버프":
        return f"플레이어/몬스터 모두 자기 효과 적용 성공 후 시전자 위치에서 방향 반전 없이 CAST한다. {layer_text}."
    return (
        "플레이어는 즉시 시전자 중심 원형 피해 판정 뒤 CAST한다. 몬스터는 축소 반경 판정이 실제 명중한 경우 CAST한다. "
        f"지연 레이어는 SpawnLayer 실행 시점의 시전자 좌표를 읽고, 스폰 뒤에는 맵 엔티티로 drift가 적용된다. {layer_text}."
    )


def runtime_effect(skill: dict[str, str], balance: dict[str, float]) -> str:
    if skill_type(skill) == "패시브":
        stat = skill.get("passive_stat") or "(빈 값)"
        return f"보유 수량 기반 {stat} 컬렉션 포인트 계산 후보. GameDataVerify/PlayerStats 지원 여부는 별도 런타임 상태를 따른다."
    if skill.get("projectile_ruid"):
        max_targets = float(skill.get("max_targets") or 0)
        target_text = "제한 없음" if max_targets <= 0 else f"최대 {fmt(max_targets)}대상"
        return (
            f"{skill.get('scaling_stat')} 계수 {fmt(skill.get('coefficient'))}; skill.range={fmt(skill.get('range'))}wu는 조준/탐색 거리; "
            f"{fmt(balance['projectile_seconds'])}초 뒤 착탄점 반경 {fmt(balance['projectile_hit_radius'])}wu에서 {target_text} 피해 판정."
        )
    return "AREA_MANIFEST의 확정 기획 효과와 현행 비투사체 실행 경로를 따른다."


def contract_fields(skill: dict[str, str], approved: bool, balance: dict[str, float]) -> dict[str, str]:
    typ = skill_type(skill)
    if approved:
        return {
            "required_roles": "APPROVED_REUSE",
            "replacement_target_fields": "none",
            "runtime_use": "approved_existing",
            "generation_ready": "READY_REUSE",
        }
    if typ == "패시브":
        return {
            "required_roles": "REFERENCE_VFX|ICON",
            "replacement_target_fields": "none|icon_ruid",
            "runtime_use": "false|ui",
            "generation_ready": "READY",
        }
    if skill.get("id") == STUMPY_ID:
        return {
            "required_roles": "PROJECTILE|ICON",
            "replacement_target_fields": "projectile_ruid|icon_ruid",
            "runtime_use": "true|ui",
            "generation_ready": "READY",
        }
    return {
        "required_roles": "CAST_VFX|ICON",
        "replacement_target_fields": ("layer_ruids" if layers(skill) else "effect_ruid") + "|icon_ruid",
        "runtime_use": "true|ui",
        "generation_ready": "READY",
    }


def role_contract(skill: dict[str, str], spec: str, balance: dict[str, float], approved: bool) -> tuple[str, list[dict]]:
    frames, canvas, frame_seconds = parse_profile(spec)
    if skill.get("id") == STUMPY_ID:
        frames, canvas, frame_seconds = 4, 512, "0.08"
    fields = contract_fields(skill, approved, balance)
    typ = skill_type(skill)
    rows = []
    if approved:
        body = """- 역할: AREA 00 승인 VFX/ICON 바이트 재사용
- generation_required: false
- runtime_use: approved_existing
- 새 그림 생성·교체 금지. approved_reuse/AREA_00의 파일과 해시를 유지한다.
- RUNTIME_VALIDATION과 ART_APPROVAL은 AREA 00 승인 기록을 인용하며 V2.2에서 재실행하지 않는다."""
        return body, rows
    if typ == "패시브":
        body = f"""- 역할: REFERENCE_VFX + ICON
- runtime_use: false (REFERENCE_VFX) / ui (ICON)
- REFERENCE_VFX 필요 파일: `VFX/F00...F{frames - 1:02d}.png`, {frames}장 × {canvas}×{canvas} RGBA, {frame_seconds}s/frame
- ICON 필요 파일: `ICON/icon.png`, 256×256 RGBA
- REFERENCE_VFX는 labeled preview에서만 one-shot으로 재생해 소재·리듬을 검수한다. SkillTable CAST/effect/layer 필드에 자동 연결하지 않는다.
- 보유 효과는 PlayerStats 계산 경로이며 그림 재생과 분리한다.
- 반복/좌표/FlipX: 런타임 미사용이므로 적용하지 않는다. Preview 안에서만 동일 캔버스·중심축을 유지한다."""
        return body, rows
    if skill.get("id") == STUMPY_ID:
        body = f"""- 역할: PROJECTILE + ICON. CAST_VFX는 만들지 않는다.
- current fields: effect_ruid 비어 있음 / layer_ruids 비어 있음 / projectile_ruid=`{skill['projectile_ruid']}`
- PROJECTILE 교체 대상: `projectile_ruid`
- PROJECTILE 필요 파일: `PROJECTILE/F00.png`~`PROJECTILE/F03.png`, 4장 × 512×512 RGBA, 0.08s/frame
- 재생 계약: non-loop one-shot 4×0.08=0.32초를 0.35초 엔티티 수명 안에 완전 재생한다. 0.03초는 프레임/삭제 경계 여유이며 비행시간·피해시점은 변경하지 않는다.
- 실제 모델/코드는 AnimationClip 재생속도·Loop·FlipX를 설정하지 않는다. 반입 시 AnimationClip 자체를 0.08s/frame non-loop로 구성해야 하며 이는 RUNTIME_VALIDATION 대상이다.
- 엔진 동작: 시전자+h→목표+h 위치 보간과 ZRotation만 수행한다. 진행 방향 자동 정렬과 FlipX는 없다.
- 원화 동작: 캔버스 중심에서 형태 변화·맥동만 표현하고 캔버스 안 좌→우 이동이나 방향 자동 정렬을 가정하지 않는다.
- 착탄: {fmt(balance['projectile_seconds'])}초 뒤 반경 {fmt(balance['projectile_hit_radius'])}wu 판정. 전용 IMPACT 파일/필드는 없다.
- ICON 필요 파일: `ICON/icon.png`, 256×256 RGBA."""
        return body, rows
    role = "SELF_BUFF_CAST_VFX" if typ == "버프" else "CAST_VFX"
    body = f"""- 역할: {role} + ICON
- runtime_use: true (CAST) / ui (ICON)
- CAST 필요 파일: `VFX/F00...F{frames - 1:02d}.png`, {frames}장 × {canvas}×{canvas} RGBA, {frame_seconds}s/frame
- ICON 필요 파일: `ICON/icon.png`, 256×256 RGBA
- target_field: `{('layer_ruids' if layers(skill) else 'effect_ruid')}` (아트 승인 후 기존 visual stack을 승인된 primary clip 하나로 교체하는 계획)
- 기존 레이어와 projectile_ruid는 승인 전 KEEP한다. projectile_ruid가 있는 11종은 이번 필수 범위에서 비행체 아트를 교체하지 않는다.
- 지연 CAST 레이어는 SpawnLayer 실행 시점의 시전자 좌표를 읽고, 스폰 뒤에는 맵 엔티티로 drift를 적용한다.
- 엔진 이동(projectile/dash/drift)과 이미지 내부 연출을 중복하지 않는다."""
    return body, rows


def update_generation_spec(path: Path, row: dict[str, str], skill: dict[str, str], balance: dict[str, float], approved: bool) -> tuple[int, int, str]:
    text = path.read_text(encoding="utf-8")
    old_effect = row["actual_effect"]
    motion = current_runtime_motion(skill, balance)
    text = re.sub(r"^- 실제 현재 효과:.*$", f"- 확정 기획 효과(보존 원문): {old_effect}", text, flags=re.M)
    text = re.sub(r"^- 실제 현재 동작:.*$", f"- 확인된 런타임 효과: {runtime_effect(skill, balance)}\n- 확인된 런타임 동작: {motion}", text, flags=re.M)
    for title in ("런타임 역할·반입 계약", "V2.1 실제 동작·납품 동기화", "V2.2 현행 런타임·납품 계약"):
        text = remove_section(text, title)

    if skill.get("id") == STUMPY_ID:
        visual = """- 핵심 소재: 고목 나이테에서 싹이 돋아 응축된 생기탄. 몬스터 본체는 넣지 않는다.
- 주 색상: 고목 갈색 #75533A / 보조 색상: 생기 연두 #8ED35B.
- 효과 발생 위치: 움직이는 projectile entity의 로컬 중심.
- 진행 방향: 원화 자체는 방향 중립. 엔진은 위치 보간과 Z축 회전만 하며 FlipX·진행 방향 자동 정렬은 하지 않는다.
- 대상 표현: 타깃 캐릭터와 조준 범위를 이미지에 넣지 않는다. 전용 IMPACT VFX도 만들지 않는다.
- 화면 점유율: 핵심 소재 70%, 외곽 파편 85% 이내. 이펙트 밀도는 보스 체급이되 투사체 실루엣을 흐리지 않는다.
- 시간 흐름: F00 응축 → F01 발광 상승 → F02 절정 → F03 안정/잔광. 0.32초 안에 한 번 완결된다.
- 아이콘 핵심 모티브: 싹튼 나이테 + 작은 생기 코어. 64px에서도 두 형상이 읽혀야 한다."""
        text = replace_section(text, "시각 번역", visual)
        profile = """- profile: `BOSS_PROJECTILE_V2_2`
- PROJECTILE: 4 frames, 각 512×512 RGBA PNG, 정확히 0.08 sec/frame (총 0.32초)
- 동일 캔버스·동일 기준축·방향 중립·non-loop one-shot
- ICON: 256×256 RGBA PNG 1장
- 주 납품물은 PROJECTILE/F00...F03 개별 PNG다. contact sheet는 선택 검수물일 뿐이다."""
        text = replace_section(text, "출력 프로필", profile)
    elif skill_type(skill) == "패시브":
        frames, canvas, frame_seconds = parse_profile(text)
        profile = f"""- profile: `PASSIVE_REFERENCE_ONLY`
- REFERENCE_VFX: {frames} frames, 각 {canvas}×{canvas} RGBA PNG, 약 {frame_seconds} sec/frame
- runtime_use=false. labeled preview에서만 one-shot으로 재생한다.
- ICON: 256×256 RGBA PNG 1장
- 주 납품물은 VFX/F00... 개별 PNG와 ICON이다. CAST_VFX 납품물은 없다."""
        text = replace_section(text, "출력 프로필", profile)
        text = text.replace("현행 CAST 레이어는 one-shot", "REFERENCE_VFX는 Preview에서만 one-shot")

    body, _ = role_contract(skill, text, balance, approved)
    status = contract_fields(skill, approved, balance)
    current = f"""- actual_motion: {motion}
- runtime_effect: {runtime_effect(skill, balance)}
- required_roles: `{status['required_roles']}`
- replacement_target_fields: `{status['replacement_target_fields']}`
- generation_ready: `{status['generation_ready']}`
- 몬스터별 `PREVIEW/labeled_preview.png`와 Area 루트 `AREA_OVERVIEW_PREVIEW.png`는 필수 검수물이다.
- 별도 contact sheet는 선택 검수물이며 위 두 Preview를 대체하지 않는다.
- 동일 캔버스·중심축·실제 alpha를 유지하고 autocrop/recenter하지 않는다.

{body}"""
    text = replace_section(text, "V2.2 현행 런타임·납품 계약", current)
    path.write_text(text, encoding="utf-8", newline="\n")
    return parse_profile(text)


def write_runtime_role_map(path: Path, row: dict[str, str], skill: dict[str, str], spec: str, balance: dict[str, float], approved: bool) -> None:
    contract, _ = role_contract(skill, spec, balance, approved)
    fields = contract_fields(skill, approved, balance)
    text = f"""# Runtime Role Map — {row['monster_id']} / {row['skill_id']}

## Current V2.2 contract

- confirmed design effect (preserved): {row['actual_effect']}
- runtime_effect: {runtime_effect(skill, balance)}
- actual_motion: {current_runtime_motion(skill, balance)}
- required_roles: `{fields['required_roles']}`
- replacement_target_fields: `{fields['replacement_target_fields']}`
- generation_ready: `{fields['generation_ready']}`

{contract}

## Coordinate and timing evidence

- CAST delay가 0보다 크면 Timer가 끝난 뒤 SpawnLayer가 그 순간의 caster.WorldPosition을 읽는다 (`SkillEffect.mlua:55-60,83-94`).
- 스폰된 CAST는 맵 엔티티이며 이후 SkillCastEffect가 drift를 적용한다. 시전자 추적 부착물이 아니다.
- PROJECTILE은 `SkillProjectile`이 위치 보간과 ZRotation을 수행한다. PROJECTILE 경로에는 FlipX 또는 진행 방향 자동 정렬 코드가 없다.
- `skill.range`는 targeting 거리이고 투사체 착탄 피해 반경은 GameBalance `projectile_hit_radius={fmt(balance['projectile_hit_radius'])}`다.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def update_style_library(stage: Path) -> tuple[Counter, int]:
    library = stage / "global_skill_style_library"
    rows = csv_rows((library / "STYLE_INDEX.csv").read_bytes())
    priorities = Counter(row["style_priority"] for row in rows)
    exclude_count = 0
    for row in rows:
        if row["style_priority"] != "EXCLUDE_STYLE":
            continue
        exclude_count += 1
        prefix = f"{int(row['index']):04d}_"
        matches = list((library / "skills").glob(prefix + "*/info.md"))
        if len(matches) != 1:
            raise RuntimeError(f"style info lookup failed: {row['index']}")
        old = matches[0].read_text(encoding="utf-8")
        old_priority_match = re.search(r"^- 스타일 우선순위: \*\*([^*]+)\*\*", old, re.M)
        old_family_match = re.search(r"^- 효과 계열: (.+)$", old, re.M)
        old_priority = old_priority_match.group(1) if old_priority_match else "미확인"
        old_family = old_family_match.group(1) if old_family_match else "미확인"
        text = f"""# {row['skill_resource_name']}

## 현행 분류 — V2.2

- RUID: `{row['RUID']}`
- 출처: {row['source']}
- reference_role: `{row['reference_role']}`
- style_priority: `EXCLUDE_STYLE`
- role_basis: {row['role_basis']}
- preview_usable: `{row['preview_usable']}`
- 사용 규칙: 본체·캐릭터·장면이 주 형상이므로 신규 VFX의 렌더링 우선 레퍼런스에서 제외한다. RUID와 이미지는 대조 이력으로만 보존한다.

## 변경 이력 — 현행 지시 아님

- V2.1 이전 상단 표기 style_priority: `{old_priority}`
- V2.1 이전 상단 표기 effect_family: `{old_family}`
- 변경 이유: STYLE_INDEX.csv의 시각 검수 분류와 상충해 V2.2에서 현행 값을 단일화했다.
"""
        matches[0].write_text(text, encoding="utf-8", newline="\n")

    index_lines = [
        "# Global Skill Style Library Index — V2.2", "",
        "현행 분류의 단일 원장은 `STYLE_INDEX.csv`다. 개별 info.md의 `현행 분류 — V2.2`와 동일해야 한다.",
        "이 183개는 프로젝트 확보 수집본이지 메이플 전체 스킬 전수 자료가 아니다.",
        "RECENT_PRIMARY는 검증된 시기 근거가 있을 때만 최신 우선이다. RECENT_SECONDARY를 자동 승격하지 않는다.",
        "UNKNOWN/LEGACY_REFERENCE는 보조 비교, EXCLUDE_STYLE은 분류 이력 보존용이다.", "",
        "| index | name | RUID | reference_role | style_priority | preview_usable | reason |",
        "|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        index_lines.append(f"| {int(row['index'])} | {row['skill_resource_name']} | `{row['RUID']}` | {row['reference_role']} | {row['style_priority']} | {row['preview_usable']} | {row['role_basis']} |")
    (library / "STYLE_INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8", newline="\n")

    roles = Counter(row["reference_role"] for row in rows)
    unusable = sum(row["preview_usable"].lower() != "true" for row in rows)
    atlas = f"""# STYLE ATLAS — V2.2

- 전체 수집본: {len(rows)}
- 역할: """ + " / ".join(f"{key} {value}" for key, value in sorted(roles.items())) + f"""
- 우선순위: """ + " / ".join(f"{key} {value}" for key, value in sorted(priorities.items())) + f"""
- preview_usable=false: {unusable}
- 현행 분류 원장: `../STYLE_INDEX.csv`
- RECENT_PRIMARY만 검증된 시기 근거가 있을 때 최신 우선으로 쓴다. RECENT_SECONDARY는 자동 대체 세트가 아니다.
- UNKNOWN/LEGACY_REFERENCE는 보조 비교이고 EXCLUDE_STYLE은 최종 렌더링 레퍼런스에서 제외한다.
- 몬스터·캐릭터 본체와 장면 실루엣은 신규 VFX 외형으로 복제하지 않는다.
"""
    (library / "summary" / "STYLE_ATLAS.md").write_text(atlas, encoding="utf-8", newline="\n")
    return priorities, exclude_count


def update_binding(stage: Path, skills: dict[str, dict], balance: dict[str, float]) -> list[dict]:
    path = stage / "ASSET_BINDING_PLAN.csv"
    rows = csv_rows(path.read_bytes())
    extra = ["generation_required", "runtime_use", "targeting_range", "monster_targeting_range", "impact_radius", "impact_delay", "max_targets", "contract_status"]
    for row in rows:
        skill = skills[row["skill_id"]]
        role = row["effect_role"]
        required = row.get("decision") in {"REPLACE_PLANNED", "REFERENCE_ONLY"} or role == "ICON"
        row["generation_required"] = str(required).lower()
        row["runtime_use"] = "false" if role == "REFERENCE_VFX" else ("ui" if role == "ICON" else "true")
        if skill.get("projectile_ruid"):
            target = float(skill.get("range") or 0)
            row["targeting_range"] = fmt(target)
            row["monster_targeting_range"] = fmt(target * balance["boss_skill_range_multiplier"])
            row["impact_radius"] = fmt(balance["projectile_hit_radius"])
            row["impact_delay"] = fmt(balance["projectile_seconds"])
            row["max_targets"] = "unlimited" if float(skill.get("max_targets") or 0) <= 0 else fmt(skill["max_targets"])
        else:
            for field in ("targeting_range", "monster_targeting_range", "impact_radius", "impact_delay", "max_targets"):
                row[field] = "n/a"
        row["contract_status"] = "READY"
        if skill["id"] == STUMPY_ID and role == "PROJECTILE":
            row.update({
                "decision": "REPLACE_PLANNED",
                "new_file_set": "PROJECTILE/F00.png...F03.png -> accepted AnimationClip",
                "target_field": "projectile_ruid",
                "target_layer": "SkillProjectile SpriteRenderer",
                "attach_to": "moving projectile entity",
                "duration_seconds": "0.35 entity lifetime; 0.32 art playback",
                "loop": "false",
                "frame_timing": "4 frames × 0.08s = 0.32s one-shot; 0.03s lifetime margin",
                "direction": "engine translation + ZRotation only; art direction-neutral",
                "flip_x": "none in actual PROJECTILE path",
                "image_internal_vs_engine": "frames animate local form only; engine owns translation and ZRotation",
                "notes": "CAST fields absent; PROJECTILE+ICON only. Import must author non-loop clip at 0.08s/frame; runtime not run in V2.2.",
            })
        elif skill.get("projectile_ruid") and role == "PROJECTILE":
            row["direction"] = "engine translation + ZRotation only"
            row["flip_x"] = "none in actual PROJECTILE path"
            row["notes"] = "KEEP: existing projectile art remains outside required V2.2 generation scope; additional approval required to replace"
        if role == "CURRENT_CAST_LAYER" and float(row.get("delay_seconds") or 0) > 0:
            row["attach_to"] = "map entity spawned at caster position sampled when delayed SpawnLayer executes"
            row["image_internal_vs_engine"] = "position sampled at execution; after spawn map entity applies configured drift and does not follow caster"
    columns = list(rows[0])
    for field in extra:
        if field not in columns:
            columns.append(field)
    write_csv(path, rows, columns)
    return rows


def output_requirements(manifest: list[dict], skills: dict[str, dict], profiles: dict[str, tuple[int, int, str]], approved_ids: set[str]) -> list[dict]:
    rows = []
    for row in manifest:
        skill = skills[row["skill_id"]]
        frames, canvas, frame_seconds = profiles[row["skill_id"]]
        approved = row["skill_id"] in approved_ids
        fields = contract_fields(skill, approved, {})
        if approved:
            rows.append({"work_order": row["work_order"], "monster_id": row["monster_id"], "skill_id": row["skill_id"], "role": "APPROVED_REUSE", "required": "true", "target_field": "none", "files": "approved_reuse/AREA_00/*", "frames": "existing", "canvas": "existing", "frame_seconds": "existing", "runtime_use": "approved_existing"})
            continue
        primary = "REFERENCE_VFX" if skill_type(skill) == "패시브" else ("PROJECTILE" if skill["id"] == STUMPY_ID else "CAST_VFX")
        folder = "PROJECTILE" if primary == "PROJECTILE" else "VFX"
        rows.append({"work_order": row["work_order"], "monster_id": row["monster_id"], "skill_id": row["skill_id"], "role": primary, "required": "true", "target_field": fields["replacement_target_fields"].split("|")[0], "files": f"{folder}/F00.png...F{frames - 1:02d}.png", "frames": str(frames), "canvas": f"{canvas}x{canvas} RGBA", "frame_seconds": frame_seconds, "runtime_use": "false" if primary == "REFERENCE_VFX" else "true"})
        rows.append({"work_order": row["work_order"], "monster_id": row["monster_id"], "skill_id": row["skill_id"], "role": "ICON", "required": "true", "target_field": "icon_ruid", "files": "ICON/icon.png", "frames": "1", "canvas": "256x256 RGBA", "frame_seconds": "static", "runtime_use": "ui"})
    return rows


def write_output_docs(stage: Path, aid: str) -> None:
    upper = aid.upper()
    naming = f"""# Output Naming Spec — V2.2

출력 루트: `{upper}_IMAGES_OUTPUT/`

## 필수 구조

```text
{upper}_IMAGES_OUTPUT/
├─ OUTPUT_MANIFEST.csv
├─ OUTPUT_MANIFEST.md
├─ AREA_OVERVIEW_PREVIEW.png        # 필수
├─ SOURCE_SHEET/                    # 원본 시트가 있을 때만
├─ SHEET_SPLIT_MANIFEST.csv         # 시트를 분할했을 때만
└─ monsters/
   └─ NNN_[monster_id]_[name]/
      ├─ VFX/                       # CAST_VFX 또는 REFERENCE_VFX
      ├─ PROJECTILE/                # OUTPUT_REQUIREMENTS가 요구할 때만
      ├─ ICON/icon.png
      ├─ PREVIEW/labeled_preview.png # 필수
      ├─ CONTACT_PREVIEW.png        # 선택 검수물
      └─ RESULT_INFO.md
```

- `PREVIEW/labeled_preview.png`와 `AREA_OVERVIEW_PREVIEW.png`는 필수다.
- 별도 contact sheet는 선택 검수물이며 필수 Preview를 대체하지 않는다.
- 주 게임용 납품물은 역할별 F00... 개별 RGBA PNG다. sprite/contact sheet는 주 납품물이 아니다.
- 정확한 역할·프레임 수·target_field는 `OUTPUT_REQUIREMENTS.csv`를 단일 원장으로 따른다.
- 원본 시트가 있으면 분할 좌표와 시트 원본을 보존한다. autocrop/recenter 금지.
"""
    format_doc = f"""# Output Format Spec — V2.2

- 출력 루트: `{upper}_IMAGES_OUTPUT/`
- 모든 VFX/PROJECTILE 프레임은 frame-separated RGBA PNG이며 같은 역할 안에서 캔버스·피봇·스케일이 같아야 한다.
- ICON은 256×256 RGBA 1장이다.
- 실제 alpha, 빈 프레임, 잘림, 다른 셀 조각, 프레임 누락을 검사한다.
- `skill.range`를 이미지상의 피해 반경으로 그리지 않는다. 투사체의 targeting_range와 impact_radius는 별도다.
- 엔진 이동(projectile 위치 보간·ZRotation, dash, layer drift)을 이미지 안의 캔버스 이동으로 중복하지 않는다.
- 패시브 REFERENCE_VFX는 runtime_use=false이며 Preview 전용이다. CAST 납품물로 취급하지 않는다.
- 스텀피는 PROJECTILE 4프레임+ICON만 요구하며 CAST_VFX를 요구하지 않는다.
- 몬스터별 `PREVIEW/labeled_preview.png`와 Area 루트 `AREA_OVERVIEW_PREVIEW.png`는 필수다. 별도 contact sheet는 선택이다.
- 파일 검사, 제작 준비, Maker 런타임, 사용자 아트 승인은 서로 다른 상태로 기록한다.
"""
    (stage / "OUTPUT_NAMING_SPEC.md").write_text(naming, encoding="utf-8", newline="\n")
    (stage / "OUTPUT_FORMAT_SPEC.md").write_text(format_doc, encoding="utf-8", newline="\n")


def update_prompt_docs(stage: Path, aid: str, area_name: str) -> None:
    contract = f"""- 출력 루트: `{aid.upper()}_IMAGES_OUTPUT/`
- `OUTPUT_REQUIREMENTS.csv`가 역할·파일 수·target_field의 단일 원장이다.
- 스텀피는 PROJECTILE+ICON만 제작하고 CAST_VFX를 만들지 않는다.
- 패시브 REFERENCE_VFX는 runtime_use=false이며 labeled preview에서만 재생한다.
- 투사체의 targeting_range와 impact_radius를 혼동하지 않는다. 조준 거리만큼 피해가 퍼지는 그림을 만들지 않는다.
- PROJECTILE 원화는 엔진 위치 이동·ZRotation을 중복하지 않는다. 실제 코드에 없는 FlipX/방향 자동 정렬을 가정하지 않는다.
- 몬스터별 `PREVIEW/labeled_preview.png`와 루트 `AREA_OVERVIEW_PREVIEW.png`는 필수다. 별도 contact sheet는 선택이다.
- PACKAGE_VALIDATION, GENERATION_READY, RUNTIME_VALIDATION, ART_APPROVAL을 분리한다. Maker를 실행하지 않았으면 RUNTIME_VALIDATION은 NOT_RUN이다."""
    for filename in ("CHATGPT_IMAGES_MASTER_PROMPT.md", "README_START_HERE.md"):
        path = stage / filename
        text = path.read_text(encoding="utf-8")
        text = text.replace("V2.1", "V2.2")
        text = remove_section(text, "V2.1 mandatory delivery contract")
        text = remove_section(text, "V2.2 current delivery contract")
        text = replace_section(text, "V2.2 current delivery contract", contract)
        path.write_text(text, encoding="utf-8", newline="\n")


def manifest_markdown(manifest: list[dict]) -> str:
    lines = [
        "# AREA MANIFEST — V2.2", "",
        "`actual_effect`는 V2.1의 확정 기획/CSV 설명을 바이트 의미상 보존한 값이며 런타임 반경 설명이 아니다. 실제 실행은 `runtime_effect`, `targeting_range`, `impact_radius`, `impact_delay`, `max_targets` 열을 따른다.", "",
        "| order | monster_id | skill_id | type | required roles | target fields | generation | runtime |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in manifest:
        lines.append(f"| {row['work_order']} | `{row['monster_id']}` | `{row['skill_id']}` | {row['skill_type']} | {row['required_roles']} | {row['replacement_target_fields']} | {row['generation_ready']} | {row['runtime_validation']} |")
    lines += ["", "## Projectile runtime fields", "", "| monster_id | skill_id | data range | player targeting | monster targeting | impact radius | delay | max targets |", "|---|---|---:|---:|---:|---:|---:|---|" ]
    for row in manifest:
        if row["targeting_range"] != "n/a":
            lines.append(f"| `{row['monster_id']}` | `{row['skill_id']}` | {row['data_range']} | {row['targeting_range']} | {row['monster_targeting_range']} | {row['impact_radius']} | {row['impact_delay']} | {row['max_targets']} |")
    return "\n".join(lines) + "\n"


def projectile_review(projectiles: list[dict], balance: dict[str, float]) -> str:
    lines = [
        "# PROJECTILE SCOPE REVIEW — V2.2", "",
        "12개 몬스터 투사체의 현행 역할을 코드 기준으로 분리했다. `range`는 targeting, 착탄 피해는 공통 `projectile_hit_radius`다.", "",
        "| Area | monster | skill | data range | player targeting | monster targeting | impact radius | delay | max targets | required art | existing projectile |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for item in projectiles:
        skill = item["skill"]
        target = float(skill.get("range") or 0)
        max_targets = "unlimited" if float(skill.get("max_targets") or 0) <= 0 else fmt(skill["max_targets"])
        required = "PROJECTILE+ICON replace" if skill["id"] == STUMPY_ID else "CAST_VFX+ICON"
        keep = "replace planned" if skill["id"] == STUMPY_ID else "KEEP; extra approval needed"
        lines.append(f"| {item['area_id']} | `{item['monster_id']}` | `{skill['id']}` | {fmt(target)} | {fmt(target)} | {fmt(target * balance['boss_skill_range_multiplier'])} | {fmt(balance['projectile_hit_radius'])} | {fmt(balance['projectile_seconds'])} | {max_targets} | {required} | {keep} |")
    lines += ["", "- PlayerAttack.ThrowSkill은 skill.range 안에서 조준 대상을 고른다 (`PlayerAttack.mlua:277-323`).", "- MonsterAttack.CastSkill은 skill.range×boss_skill_range_multiplier로 대상을 탐색한다 (`MonsterAttack.mlua:383-402,469-485`).", "- 양쪽 ResolveThrowHit은 projectile_hit_radius를 착탄점 CircleShape에 쓴다 (`PlayerAttack.mlua:483-504`, `MonsterAttack.mlua:506-529`).", "- 원래 actual_effect 문구의 큰 반경 숫자는 확정 기획/데이터 값으로 보존했으며 현행 착탄 피해 반경으로 단정하지 않는다."]
    return "\n".join(lines) + "\n"


def runtime_conflicts(balance: dict[str, float]) -> str:
    return f"""# Runtime and design conflicts — V2.2

## AREA 20 / s_mon_mutant_stone_mask

- 확정 데이터: passive_stat=DEF (변경하지 않음).
- GameDataVerify는 STR/DEX/INT/LUK만 허용해 DEF를 오류로 기록한다 (`GameDataVerify.mlua:188-200`).
- PlayerStats.GetCollectionPoints는 전달받은 이름과 passive_stat이 같은 항목을 합산하지만, GetCollectionBonus("DEF")는 DEX 포인트만 사용한다 (`PlayerStats.mlua:527-576`). DEF collection point를 파생 방어력에 더하는 호출은 확인되지 않았다.
- 결론: 현행 계산에서 스킬 passive_stat=DEF는 방어력 보너스로 소비되지 않는 기획/실행 충돌이다. 게임 데이터·검증·계산 코드는 V2.2에서 변경하지 않았다.
- GENERATION_READY는 아트 입력 기준 READY, RUNTIME_VALIDATION은 UNRESOLVED다.

## Current Maker SkillTable

- 정상 경로 SkillTable 파일은 삭제 상태이며 Mislocated 후보가 있다. `_DataService:GetTable("SkillTable")` 이름 조회만으로 현재 Maker 등록 EntryKey를 식별할 수 없다.
- V2.2는 기준 커밋 데이터와 V2.1 확정 패키지를 사용하지만 현재 Maker 등록 테이블과 같다고 단정하지 않는다. RUNTIME_VALIDATION=NOT_RUN.

## Six dash skills

- 플레이어 피해점은 계산 도착점, PlayCast는 호출 뒤 서버가 보는 caster 위치를 사용하므로 일치가 보장되지 않는다.
- 지연 CAST는 Timer 후 SpawnLayer 실행 시점의 caster 좌표를 읽고, 스폰 뒤 맵 엔티티에 drift가 적용된다.
- 몬스터 공통 CastSkill에는 dash_distance 이동 분기가 없다. 경고를 유지하며 이번에 코드를 바꾸지 않는다.

## Projectile scope

- 비행/피해 지연 {fmt(balance['projectile_seconds'])}초와 착탄 반경 {fmt(balance['projectile_hit_radius'])}wu는 유지했다.
- 스텀피만 PROJECTILE+ICON 교체 계획이다. 나머지 11종 projectile_ruid는 KEEP이며 추가 승인 없이 비행체 아트 범위를 늘리지 않았다.
"""


def package_status(aid: str, generation_status: str, runtime_status: str) -> str:
    return f"""# Package status — {aid} / V2.2

| Axis | Status | Meaning |
|---|---|---|
| PACKAGE_VALIDATION | PASS_BUILD | 빌더가 파일·경로·내부 CRC 후보를 검사함. 독립 검증 결과는 루트 INPUT_V2_2_VALIDATION 참조 |
| GENERATION_READY | {generation_status} | 제작 역할·원본·프레임 계약 기준 |
| RUNTIME_VALIDATION | {runtime_status} | Maker/게임은 이번 작업에서 실행하지 않음 |
| ART_APPROVAL | NOT_REVIEWED | V2.2는 입력 패키지이며 생성 아트 승인이 아님 |
"""


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"destination exists: {OUT}")
    if not CROSSCHECK.exists():
        raise RuntimeError(f"missing user evidence: {CROSSCHECK}")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    commit = baseline["git_head"]
    skill_rows = csv_rows(git_bytes(commit, "RootDesk/MyDesk/GameData/SkillTable.csv"))
    skills = {row["id"]: row for row in skill_rows}
    if MISLOCATED_SKILLS.exists():
        for row in csv_rows(MISLOCATED_SKILLS.read_bytes()):
            skills.setdefault(row["id"], row)
    approved_skill_ids = {row["skill_id"] for row in csv_rows(AREA00_RESOURCE_MAP.read_bytes())}
    balance_rows = csv_rows((ROOT / "RootDesk/MyDesk/GameData/GameBalance.csv").read_bytes())
    balance = {row["key"]: float(row["value"]) for row in balance_rows}
    if balance["projectile_seconds"] != PROJECTILE_SECONDS or balance["projectile_hit_radius"] != PROJECTILE_HIT_RADIUS:
        raise RuntimeError("runtime projectile constants changed; re-audit required")

    all_projectiles = []
    for aid in TARGET_IDS:
        with zipfile.ZipFile(SOURCE / f"{aid.upper()}_IMAGES_INPUT_V2_1.zip") as archive:
            source_root = f"{aid.upper()}_IMAGES_INPUT_V2_1/"
            source_manifest = csv_rows(archive.read(source_root + "AREA_MANIFEST.csv"))
        for row in source_manifest:
            skill = skills.get(row["skill_id"])
            if skill and skill.get("projectile_ruid"):
                all_projectiles.append({"area_id": aid, "monster_id": row["monster_id"], "skill": skill})
    projectiles_doc = projectile_review(all_projectiles, balance)

    with tempfile.TemporaryDirectory(prefix="input_v2_2_build_") as td:
        temp = Path(td)
        final = temp / "final"
        final.mkdir()
        all_binding = []
        before_after = []
        area_results = []
        style_counts = None
        exclude_count = 0
        total_monsters = 0
        passive_count = 0

        for aid in TARGET_IDS:
            work = temp / aid
            work.mkdir()
            stage = extract_source(aid, work)
            manifest_path = stage / "AREA_MANIFEST.csv"
            manifest = csv_rows(manifest_path.read_bytes())
            total_monsters += len(manifest)
            approved_ids = {row["skill_id"] for row in manifest if row["skill_id"] in approved_skill_ids}
            profiles = {}
            area_runtime = "NOT_RUN"

            for row in manifest:
                skill = skills.get(row["skill_id"])
                if not skill:
                    raise RuntimeError(f"baseline skill missing: {row['skill_id']}")
                approved = row["skill_id"] in approved_ids
                if skill_type(skill) == "패시브":
                    passive_count += 1
                old_motion = row.get("actual_motion", "")
                profile = update_generation_spec(stage / row["folder"] / "GENERATION_SPEC.md", row, skill, balance, approved)
                profiles[row["skill_id"]] = profile
                spec = (stage / row["folder"] / "GENERATION_SPEC.md").read_text(encoding="utf-8")
                write_runtime_role_map(stage / row["folder"] / "RUNTIME_ROLE_MAP.md", row, skill, spec, balance, approved)
                current = current_runtime_motion(skill, balance)
                fields = contract_fields(skill, approved, balance)
                row.update({
                    "runtime_effect": runtime_effect(skill, balance),
                    "runtime_motion": current,
                    "required_roles": fields["required_roles"],
                    "replacement_target_fields": fields["replacement_target_fields"],
                    "runtime_use": fields["runtime_use"],
                    "generation_ready": fields["generation_ready"],
                    "runtime_validation": "UNRESOLVED" if skill["id"] == STONE_MASK_ID else ("AREA00_APPROVED_NOT_RERUN" if approved else "NOT_RUN"),
                    "data_range": fmt(skill.get("range")) if skill.get("projectile_ruid") else "n/a",
                    "targeting_range": fmt(skill.get("range")) if skill.get("projectile_ruid") else "n/a",
                    "monster_targeting_range": fmt(float(skill.get("range") or 0) * balance["boss_skill_range_multiplier"]) if skill.get("projectile_ruid") else "n/a",
                    "impact_radius": fmt(balance["projectile_hit_radius"]) if skill.get("projectile_ruid") else "n/a",
                    "impact_delay": fmt(balance["projectile_seconds"]) if skill.get("projectile_ruid") else "n/a",
                    "max_targets": ("unlimited" if float(skill.get("max_targets") or 0) <= 0 else fmt(skill["max_targets"])) if skill.get("projectile_ruid") else "n/a",
                })
                if old_motion != current:
                    before_after.append({
                        "area_id": aid,
                        "monster_id": row["monster_id"],
                        "skill_id": row["skill_id"],
                        "before": old_motion,
                        "after": current,
                        "evidence": "PlayerAttack.mlua:277-323,483-504; MonsterAttack.mlua:383-402,450-529; SkillEffect.mlua:55-60,83-117,149-194",
                        "impact": "documentation/runtime-role contract only; game data/code unchanged",
                    })
                if skill["id"] == STONE_MASK_ID:
                    area_runtime = "UNRESOLVED"

            write_csv(manifest_path, manifest, list(manifest[0]))
            (stage / "AREA_MANIFEST.md").write_text(manifest_markdown(manifest), encoding="utf-8", newline="\n")
            binding = update_binding(stage, skills, balance)
            all_binding.extend(binding)
            requirements = output_requirements(manifest, skills, profiles, approved_ids)
            write_csv(stage / "OUTPUT_REQUIREMENTS.csv", requirements, list(requirements[0]))
            write_output_docs(stage, aid)
            update_prompt_docs(stage, aid, manifest[0]["area_name"])
            priorities, excludes = update_style_library(stage)
            if style_counts is None:
                style_counts, exclude_count = priorities, excludes
            elif priorities != style_counts or excludes != exclude_count:
                raise RuntimeError("style library diverged across areas")

            (stage / "PROJECTILE_SCOPE_REVIEW.md").write_text(projectiles_doc, encoding="utf-8", newline="\n")
            (stage / "RUNTIME_CONFLICTS_V2_2.md").write_text(runtime_conflicts(balance), encoding="utf-8", newline="\n")
            (stage / "PACKAGE_STATUS_V2_2.md").write_text(package_status(aid, "READY", area_runtime), encoding="utf-8", newline="\n")
            revision = f"""# PACKAGE REVISION — V2.2

- source: `{aid.upper()}_IMAGES_INPUT_V2_1.zip`
- source_sha256: `{sha_file(SOURCE / f'{aid.upper()}_IMAGES_INPUT_V2_1.zip')}`
- built_utc: `{datetime.now(timezone.utc).isoformat()}`
- game data/code changed: `false`
- Area 00 changed: `false`
- art generated: `false`
- scope: V2.1 evidence crosscheck confirmed corrections only
"""
            (stage / "PACKAGE_REVISION_V2_2.md").write_text(revision, encoding="utf-8", newline="\n")
            old_revision = stage / "PACKAGE_REVISION_V2_1.md"
            if old_revision.exists():
                history = stage / "history"
                history.mkdir(exist_ok=True)
                old_revision.rename(history / old_revision.name)

            zip_path = final / f"{aid.upper()}_IMAGES_INPUT_V2_2.zip"
            zip_tree(stage, zip_path)
            area_results.append({"area_id": aid, "area_name": manifest[0]["area_name"], "monsters": len(manifest), "package_validation": "PENDING_INDEPENDENT", "generation_ready": "READY", "runtime_validation": area_runtime, "art_approval": "NOT_REVIEWED", "zip": zip_path.name, "sha256": sha_file(zip_path)})

        # The final 12-projectile matrix is copied beside the packages and later into evidence.
        (final / "PROJECTILE_SCOPE_REVIEW_V2_2.md").write_text(projectiles_doc, encoding="utf-8", newline="\n")
        conflicts_doc = runtime_conflicts(balance)
        (final / "INPUT_V2_2_REMAINING_DECISIONS.md").write_text(conflicts_doc, encoding="utf-8", newline="\n")
        write_csv(final / "ASSET_BINDING_PLAN_V2_2.csv", all_binding, list(all_binding[0]))
        write_csv(final / "INPUT_V2_2_BEFORE_AFTER_EVIDENCE.csv", before_after, list(before_after[0]))

        table = ["# V2.2 before/after and evidence", "", "| Area | monster | skill | before | after | evidence |", "|---|---|---|---|---|---|"]
        for row in before_after:
            table.append(f"| {row['area_id']} | `{row['monster_id']}` | `{row['skill_id']}` | {row['before'].replace('|', '/')} | {row['after'].replace('|', '/')} | {row['evidence']} |")
        (final / "INPUT_V2_2_BEFORE_AFTER_EVIDENCE.md").write_text("\n".join(table) + "\n", encoding="utf-8", newline="\n")

        changelog = f"""# INPUT V2.2 CHANGELOG

- Source: immutable 19 V2.1 ZIPs. Area 00, prior INPUT/OUTPUT, game data/code unchanged.
- Stumpy: removed current CAST generation contract; PROJECTILE+ICON only. 4×0.08=0.32s non-loop frame contract fits the unchanged 0.35s projectile lifetime.
- 12 monster projectile skills: separated data range, player/monster targeting_range, impact_radius={fmt(balance['projectile_hit_radius'])}, impact_delay={fmt(balance['projectile_seconds'])}, max_targets.
- Existing 11 non-Stumpy projectile assets remain KEEP and outside required art scope.
- 15 EXCLUDE_STYLE info files: current classification moved to one top section; previous values retained only as history.
- {passive_count} passive specs/maps: REFERENCE_VFX preview-only, runtime_use=false; no CAST delivery instruction.
- 19 OUTPUT examples: labeled/overview previews mandatory; separate contact sheet optional.
- AREA 20 DEF passive and six dash execution warnings recorded without game changes.
- Status axes split: PACKAGE_VALIDATION / GENERATION_READY / RUNTIME_VALIDATION / ART_APPROVAL.
"""
        (final / "INPUT_V2_2_CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="\n")
        change_matrix = """# INPUT V2.2 change matrix

| Change | Before in V2.1 | Current V2.2 | Project evidence | Affected Area | Game change |
|---|---|---|---|---|---|
| Stumpy delivery role | Spec/runtime map said CAST_VFX 12f and projectile KEEP while binding plan said PROJECTILE replace | PROJECTILE 4f + ICON, target projectile_ruid; no CAST delivery | SkillTable baseline row s_mon_stumpy; SkillEffect.mlua:149-194; SkillProjectile.mlua:39-81; SkillProjectile.model:20-68 | 02 | none |
| Stumpy playback period | 12×0.08=0.96s vs 0.35s entity life | non-loop 4×0.08=0.32s complete playback, 0.03s margin | GameBalance.csv:21; SkillProjectile.mlua:39-59; model has no playback speed/loop property | 02 | none |
| Projectile range semantics | Five actual-effect sentences could be read as range-sized impact radius | immutable planning text retained; runtime fields split into targeting_range / impact_radius=0.8 / impact_delay=0.35 / max_targets | PlayerAttack.mlua:277-323,483-504; MonsterAttack.mlua:383-402,450-529; GameBalance.csv:21,24 | 02,03,08,10,11,14,15,17,18 | none |
| Existing projectile scope | ambiguous optional redraw wording | Stumpy replace only; other 11 projectile_ruid rows KEEP pending approval | SkillTable baseline projectile_ruid fields; ASSET_BINDING_PLAN_V2_2.csv | 03,08,10,11,14,15,17,18 | none |
| EXCLUDE_STYLE info | old UNKNOWN/LEGACY and layered-VFX header coexisted with V2.1 synchronized block | one `현행 분류 — V2.2`; old values history-only | STYLE_INDEX.csv + 183 preview classification; 15 EXCLUDE_STYLE rows | all 19 | none |
| Preview obligation | tree example called PREVIEW optional while lower contract required labeled/overview | labeled_preview + AREA_OVERVIEW mandatory; separate contact sheet optional | OUTPUT_NAMING_SPEC.md / OUTPUT_FORMAT_SPEC.md | all 19 | none |
| Passive VFX role | runtime-none statement coexisted with generic CAST one-shot template | REFERENCE_VFX preview-only, runtime_use=false; ICON UI role | GameData.mlua passive load; PlayerStats.mlua:527-576; no passive PlayCast call | all 19 / 35 placements | none |
| Delayed CAST position | attachment timing was underspecified | caster position sampled when delayed SpawnLayer executes; map entity drifts afterward | SkillEffect.mlua:55-60,83-117; SkillCastEffect.mlua | all Areas with delayed layers | none |
| Dash visual vs hit point | calculated destination could be mistaken for CAST origin | six-skill warning retained: calculated hit point vs server-observed caster position | PlayerAttack.mlua:386-479; SkillEffect.mlua:83-117; MonsterAttack.mlua:354-443 | 02,05,07,09,12,20 | none |
| Stone-mask DEF passive | package described DEF passive without exposing verifier/calculation conflict | generation READY; runtime UNRESOLVED | GameDataVerify.mlua:188-200; PlayerStats.mlua:527-576 | 20 | none |
| Status wording | READY/PASS could combine package, runtime, and art meanings | four axes recorded independently | PACKAGE_STATUS_V2_2.md; validator | all 19 | none |

The attached V2.1 crosscheck ZIP was treated as a candidate review. The project evidence column is the applied basis.
"""
        (final / "INPUT_V2_2_CHANGE_MATRIX.md").write_text(change_matrix, encoding="utf-8", newline="\n")
        findings = f"""# INPUT V2.2 ADDITIONAL FINDINGS

## Corrected input errors

- Stumpy had a PROJECTILE replacement plan but CAST output text; unified to PROJECTILE+ICON.
- Stumpy 12×0.08=0.96s could not complete within the 0.35s entity life. The image contract is now 4×0.08=0.32s non-loop, with no gameplay timing change.
- Five projectile descriptions treated skill.range as damage radius. The immutable planning text remains in `actual_effect`; current execution is separately recorded as targeting_range vs impact_radius.
- EXCLUDE_STYLE, Preview, and passive REFERENCE_VFX instructions were duplicated/conflicting; current instructions are now single-source.

## Runtime/design conflicts left unchanged

- `{STONE_MASK_ID}` passive_stat=DEF is rejected by GameDataVerify and is not consumed by PlayerStats.GetCollectionBonus("DEF").
- Current Maker-registered SkillTable is unresolved; filename candidates are not treated as proof.
- Six dash skills retain calculated-hit-point vs CAST-caster-position warning.
- Eleven existing projectile artworks remain KEEP pending separate scope approval.

## Evidence distinction

- Attached crosscheck ZIP is a review input, not an instruction source. Every applied item was rechecked against the project files listed in the evidence table.
- RUNTIME_VALIDATION is NOT_RUN/UNRESOLVED because Maker execution was prohibited.
"""
        (final / "INPUT_V2_2_ADDITIONAL_FINDINGS.md").write_text(findings, encoding="utf-8", newline="\n")

        index = [
            "# ALL AREAS INPUT V2.2 INDEX", "",
            f"- 대상: {len(area_results)} Area / {total_monsters} monster placements",
            "- area_06: 예약 결번, 생성하지 않음",
            "- Area 00: 변경하지 않음", "",
            "| Area | name | monsters | PACKAGE_VALIDATION | GENERATION_READY | RUNTIME_VALIDATION | ART_APPROVAL | ZIP | SHA-256 |",
            "|---|---|---:|---|---|---|---|---|---|",
        ]
        for row in area_results:
            index.append(f"| {row['area_id']} | {row['area_name']} | {row['monsters']} | {row['package_validation']} | {row['generation_ready']} | {row['runtime_validation']} | {row['art_approval']} | `{row['zip']}` | `{row['sha256']}` |")
        (final / "ALL_AREAS_INPUT_V2_2_INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
        build_result = {
            "built_utc": datetime.now(timezone.utc).isoformat(),
            "source_revision": "V2.1",
            "target_revision": "V2.2",
            "areas": len(area_results),
            "monster_placements": total_monsters,
            "passives": passive_count,
            "monster_projectiles": len(all_projectiles),
            "exclude_style": exclude_count,
            "style_priority_counts": dict(style_counts or {}),
            "area06_created": False,
            "art_generated": False,
            "runtime_run": False,
            "areas_detail": area_results,
        }
        (final / "BUILD_RESULT.json").write_text(json.dumps(build_result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        shutil.move(str(final), str(OUT))

    print(json.dumps({"out": str(OUT), "areas": 19, "monsters": total_monsters, "passives": passive_count, "projectiles": len(all_projectiles)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
