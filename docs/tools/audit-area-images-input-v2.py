from __future__ import annotations

"""Audit and rebuild the Area 01~20 (except reserved Area 06) image-input packages.

This tool never mutates game data, Area 00 inputs/outputs, or the legacy input ZIPs.
It uses the legacy packages as immutable source bundles and writes a revisioned V2
bundle plus evidence reports under docs/art/images-input-packages-v2/.
"""

import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "RootDesk" / "MyDesk" / "GameData"
BASE = ROOT / "docs" / "art" / "images-input-packages"
OUT = ROOT / "docs" / "art" / "images-input-packages-v2"
AREA00_OUT = ROOT / "docs" / "art" / "area00-images-output" / "AREA_00_IMAGES_OUTPUT"
AREA00_MAP = ROOT / "docs" / "art" / "area00-images-output" / "AREA_00_IMAGES_RESOURCE_MAP.csv"
AREA00_REPORT = ROOT / "docs" / "art" / "area00-images-output" / "AREA_00_IMAGES_IMPORT_REPORT.md"

TARGET_IDS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]
REQUIRED_ROOT = [
    "README_START_HERE.md",
    "CHATGPT_IMAGES_MASTER_PROMPT.md",
    "AREA_MANIFEST.md",
    "AREA_MANIFEST.csv",
    "OUTPUT_NAMING_SPEC.md",
    "OUTPUT_FORMAT_SPEC.md",
    "global_skill_style_library/STYLE_INDEX.md",
    "global_skill_style_library/STYLE_INDEX.csv",
    "global_skill_style_library/summary/STYLE_ATLAS.md",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_file(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def read_csv_text(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))


def csv_text(rows: list[dict[str, str]], fields: list[str]) -> str:
    sio = io.StringIO(newline="")
    writer = csv.DictWriter(sio, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "\ufeff" + sio.getvalue()


def number(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def split_pipe(value: str | None) -> list[str]:
    return [x.strip() for x in str(value or "").split("|") if x.strip()]


def git_blob(ref_path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"HEAD:{ref_path}"], cwd=ROOT)


def walk_sprite_ruid(node) -> str:
    if isinstance(node, dict):
        if node.get("Name") == "SpriteRUID" and isinstance(node.get("Value"), str) and node["Value"]:
            return node["Value"]
        for value in node.values():
            found = walk_sprite_ruid(value)
            if found:
                return found
    elif isinstance(node, list):
        for value in node:
            found = walk_sprite_ruid(value)
            if found:
                return found
    return ""


def load_models() -> tuple[dict[str, str], dict[str, str]]:
    ruids: dict[str, str] = {}
    paths: dict[str, str] = {}
    for path in (ROOT / "RootDesk" / "MyDesk" / "Models" / "Monsters").rglob("*.model"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        model_id = str(obj.get("EntryKey", "")).removeprefix("model://")
        if model_id and model_id not in ruids:
            ruids[model_id] = walk_sprite_ruid(obj)
            paths[model_id] = path.relative_to(ROOT).as_posix()
    return ruids, paths


def load_skill_baseline() -> tuple[list[dict[str, str]], dict]:
    """Use the working file when present, otherwise the immutable HEAD blob.

    The caller records this downgrade. We do not recreate the deleted working file.
    """
    path = DATA / "SkillTable.csv"
    if path.exists():
        data = path.read_bytes()
        return read_csv_text(data.decode("utf-8-sig")), {
            "source": path.relative_to(ROOT).as_posix(),
            "state": "working_tree",
            "sha256": sha256_bytes(data),
        }
    data = git_blob("RootDesk/MyDesk/GameData/SkillTable.csv")
    return read_csv_text(data.decode("utf-8-sig")), {
        "source": "git:HEAD:RootDesk/MyDesk/GameData/SkillTable.csv",
        "state": "HEAD_fallback_working_file_missing",
        "sha256": sha256_bytes(data),
    }


def skill_type(skill: dict[str, str]) -> str:
    if skill.get("skill_kind") == "passive":
        return "패시브"
    if skill.get("skill_kind") == "defense" or skill.get("effect_type") == "shield":
        return "버프"
    return "액티브"


def actual_effect(skill: dict[str, str], balance: dict[str, float]) -> str:
    kind = skill_type(skill)
    if kind == "패시브":
        first = balance.get("collection_passive_first", 1)
        extra = balance.get("collection_passive_extra", 0.25)
        cap = int(balance.get("skill_stack_max", 5))
        maximum = first + extra * (cap - 1)
        stat = skill.get("passive_stat") or skill.get("scaling_stat") or "미확인"
        return f"보유만 해도 {stat} +{first:g}; 중복 1장당 +{extra:g}, {cap}장 최대 +{maximum:g}"
    if kind == "버프":
        return f"자신에게 {number(skill.get('duration')):g}초 동안 피해 {number(skill.get('effect_value')) * 100:g}% 감소"
    target = "단일 대상"
    if skill.get("target_mode") == "area":
        target = f"반경 {number(skill.get('range')):g} 범위"
        max_targets = int(number(skill.get("max_targets")))
        target += f" 최대 {max_targets}대상" if max_targets > 0 else " 대상 제한 없음"
    elif number(skill.get("max_targets")) > 1:
        target = f"최대 {int(number(skill.get('max_targets')))}대상"
    base = number(skill.get("coefficient"))
    cap = int(balance.get("skill_stack_max", 5))
    max_scale = 1 + balance.get("skill_stack_bonus", 0.2) * (cap - 1)
    text = f"{skill.get('scaling_stat')} 계수 {base:g}로 {target} 피해; {number(skill.get('cooldown')):g}초 재사용"
    if max_scale > 1:
        text += f"; {cap}장 보유 시 계수 ×{max_scale:g}"
    if number(skill.get("dash_distance")) > 0:
        text += f"; {number(skill.get('dash_distance')):g} 거리 돌진"
    return text


def legacy_motion_summary(skill: dict[str, str]) -> str:
    if skill_type(skill) == "패시브":
        return "현행 런타임 VFX 없음; 인벤토리/스킬 UI 아이콘으로만 표시"
    layers = split_pipe(skill.get("layer_ruids"))
    bits: list[str] = []
    if layers:
        bits.append(f"layer_ruids {len(layers)}개")
        for label, key in (("타입", "layer_types"), ("스타일", "layer_styles"), ("지연", "layer_delays"), ("지속", "layer_durations")):
            values = split_pipe(skill.get(key))
            if values:
                suffix = "초" if label in ("지연", "지속") else ""
                bits.append(label + " " + "/".join(values) + suffix)
    elif skill.get("effect_ruid"):
        if skill.get("effect_style"):
            bits.append(f"Sprite {skill['effect_ruid']}를 {skill['effect_style']} 방식으로 재생")
        else:
            bits.append(f"AnimationClip {skill['effect_ruid']}를 시전자 기준 재생")
    if skill.get("projectile_ruid"):
        bits.append(f"투사체 {skill['projectile_ruid']}가 목표 방향으로 이동")
    if number(skill.get("dash_distance")) > 0:
        bits.append("플레이어 사용 시 시전자가 조준 방향으로 돌진")
    return "; ".join(bits) if bits else "현행 연출 RUID 없음"


def runtime_contract(skill: dict[str, str], balance: dict[str, float]) -> dict[str, str]:
    kind = skill_type(skill)
    layers = split_pipe(skill.get("layer_ruids"))
    types = split_pipe(skill.get("layer_types"))
    styles = split_pipe(skill.get("layer_styles"))
    delays = split_pipe(skill.get("layer_delays"))
    durations = split_pipe(skill.get("layer_durations"))
    scales = split_pipe(skill.get("layer_scales"))
    ox = split_pipe(skill.get("layer_offsets_x"))
    oy = split_pipe(skill.get("layer_offsets_y"))
    dx = split_pipe(skill.get("layer_drifts_x"))
    dy = split_pipe(skill.get("layer_drifts_y"))
    if kind == "패시브":
        return {
            "roles": "ICON=런타임 필수; REFERENCE_VFX=기존 제작 범위에 포함된 비전투 참고 산출물(런타임 미사용·자동 반입 금지)",
            "origin": "런타임 시전자/발생점 없음. PlayerStats와 UI가 보유 수를 읽고 정액 스탯을 적용한다.",
            "timing": "피해 판정·시전·재생시간·반복 없음.",
            "direction": "방향·FlipX·엔진 이동 없음.",
            "engine_motion": "없음",
            "runtime_sources": "icon_ruid=" + (skill.get("icon_ruid") or "비어 있음"),
        }

    source_parts = []
    if layers:
        for i, ruid in enumerate(layers):
            def at(values: list[str], default: str) -> str:
                return values[i] if i < len(values) else default
            source_parts.append(
                f"L{i+1} ruid={ruid}, type={at(types,'sprite')}, style={at(styles,'burst')}, "
                f"delay={at(delays,'0')}s, duration={at(durations,'0.4')}s, scale={at(scales,'1')}, "
                f"offset=({at(ox,'0')},{at(oy,'0')}) world unit, drift=({at(dx,'0')},{at(dy,'0')}) world unit/s"
            )
    elif skill.get("effect_ruid"):
        source_parts.append(
            f"effect_ruid={skill['effect_ruid']}, effect_style={skill.get('effect_style') or 'attached AnimationClip'}"
        )
    projectile = skill.get("projectile_ruid") or ""
    dash = number(skill.get("dash_distance"))
    if kind == "버프":
        roles = "CAST_VFX=자기 몸에 붙는 버프 연출; ICON=UI 식별"
        origin = "플레이어/몬스터 시전자 원점에 붙여 재생. 방향 반전하지 않는다."
        timing = "실드 적용 성공 뒤 CAST_VFX가 시작되며, 지속 효과 시간과 VFX 수명은 별도 값이다."
        direction = "무방향. 닫힌 보호 윤곽과 자기 중심 맥동만 사용한다."
    elif projectile:
        roles = "CAST_VFX=발사/준비 연출; PROJECTILE=엔진이 이동시키는 비행체; ICON=UI 식별"
        origin = "CAST_VFX는 시전자 원점. PROJECTILE은 시전자에서 조준 위치로 이동한다. 전용 IMPACT VFX 필드는 현재 없다."
        timing = f"투사체가 {balance.get('projectile_seconds', 0.35):g}초 뒤 도착할 때 피해 판정. CAST_VFX는 발사 시점에 시작한다."
        direction = "우측 기준 제작 후 FlipX. PROJECTILE 그림 안에서 캔버스 전체를 좌→우로 이동시키지 않는다(엔진 이동과 중복 금지)."
    elif dash > 0:
        roles = "CAST_VFX=플레이어 돌진 도착점의 충돌 연출; ICON=UI 식별"
        origin = f"플레이어는 조준 8방향으로 {dash:g} world unit 이동하고 도착 예정점에서 피해·VFX 발생. 일반 몬스터 자동 시전 정책은 없음."
        timing = f"{balance.get('skill_dash_seconds', 0.2):g}초 이동 뒤 판정과 CAST_VFX가 시작된다."
        direction = "우측 기준 제작 후 FlipX. 이동 궤적 전체를 한 프레임 안에서 재현하지 않는다."
    else:
        roles = "CAST_VFX=시전자 중심 공격 연출; ICON=UI 식별"
        origin = "플레이어는 시전자 중심 원형 판정 뒤 CAST_VFX 재생. 보스 사용 시 명중한 경우에만 시전자 중심에서 재생한다."
        timing = "피해 판정 직후 CAST_VFX 시작. 별도 지연 피해나 전용 피격 VFX 필드는 현재 없다."
        direction = "자원은 우측 기준이며 대상이 왼쪽이면 FlipX. 판정 자체는 방향성 부채꼴이 아니라 시전자 중심 원형이다."
    return {
        "roles": roles,
        "origin": origin,
        "timing": timing,
        "direction": direction,
        "engine_motion": "layer drift는 엔진 적용: " + ("; ".join(source_parts) if source_parts else "현행 레이어 없음"),
        "runtime_sources": "; ".join(source_parts) + (("; projectile_ruid=" + projectile) if projectile else ""),
    }


def png_info(data: bytes) -> dict:
    with Image.open(io.BytesIO(data)) as im:
        rgba = im.convert("RGBA")
        alpha = rgba.getchannel("A")
        lo, hi = alpha.getextrema()
        bbox = alpha.getbbox()
        return {
            "format": im.format,
            "mode": im.mode,
            "width": im.width,
            "height": im.height,
            "alpha_min": lo,
            "alpha_max": hi,
            "alpha_bbox": list(bbox) if bbox else None,
            "visible_pixels": sum(1 for x in alpha.getdata() if x > 0),
        }


VISUAL_BODY_STYLE_INDEXES = {7, 20, 48, 96, 118, 141, 150, 161, 173, 182}
VISUAL_SCENE_STYLE_INDEXES = {32, 40, 55, 84, 151}


def style_role(row: dict[str, str], index: int) -> tuple[str, str, str]:
    """Classify the rendered preview, not merely the RUID's current use.

    The explicit index sets were reviewed in the generated 5x5 contact sheets.
    This avoids the earlier false positive where a model-associated animation RUID
    rendered an effect-only frame and was incorrectly treated as a body image.
    """
    ruid = row.get("RUID", "")
    notes = row.get("notes", "")
    family = row.get("effect_family", "")
    if index in VISUAL_BODY_STYLE_INDEXES:
        return "MONSTER_CHARACTER", "183개 preview contact sheet 시각 검수: 몬스터/캐릭터 본체가 주 형상", "EXCLUDE_STYLE"
    if index in VISUAL_SCENE_STYLE_INDEXES:
        return "SCENE", "183개 preview contact sheet 시각 검수: 본체/장면과 효과가 함께 있음", "EXCLUDE_STYLE"
    if family == "icon" or ("icon_ruid" in notes and not any(k in notes for k in ("layer_ruids", "effect_ruid", "projectile_ruid"))):
        return "ICON", "SkillTable icon_ruid 사용처", row.get("style_priority", "UNKNOWN")
    if family in {"dash", "beam", "impact/explosion", "wave/area", "projectile", "buff/passive", "layered VFX"}:
        return "VFX", "preview 시각 검수 + SkillTable 시각 필드 사용처", row.get("style_priority", "UNKNOWN")
    return "UNCONFIRMED", "프리뷰만으로 기능 역할을 확정할 메타데이터 부족", row.get("style_priority", "UNKNOWN")


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(?ms)^## {re.escape(heading)}\s*\n.*?(?=^## |\Z)"
    replacement = f"## {heading}\n\n{body.rstrip()}\n\n"
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text)
    return text.rstrip() + "\n\n" + replacement


def field_from_spec(text: str, label: str, default: str = "미확인") -> str:
    m = re.search(rf"(?m)^- {re.escape(label)}:\s*(.+?)\s*$", text)
    return m.group(1).strip() if m else default


def concrete_visual_section(old: str, skill: dict[str, str], contract: dict[str, str]) -> str:
    core = field_from_spec(old, "핵심 소재")
    primary = field_from_spec(old, "주 색상")
    secondary = field_from_spec(old, "보조 색상")
    occupancy = field_from_spec(old, "화면 점유율")
    density = field_from_spec(old, "이펙트 밀도")
    icon = field_from_spec(old, "아이콘 핵심 모티브")
    kind = skill_type(skill)
    if kind == "패시브":
        progression = "REFERENCE_VFX를 만들 경우 정지 모티브의 짧은 호흡만 표현한다. 공격 준비·타격광·투사체·폭발 단계는 넣지 않는다."
        target = "런타임 대상 없음. 아이콘은 보유 효과를 식별하는 UI 자산이며 몬스터 본체 전체를 넣지 않는다."
    elif kind == "버프":
        progression = "시전자 둘레 윤곽 출현 → 보호 구조 닫힘 → 반사광 절정 → 실드 지속과 혼동되지 않게 짧게 페이드."
        target = "시전자 자신만 감싼다. 다른 대상, 타격점, 공격 폭발은 표시하지 않는다."
    elif skill.get("projectile_ruid"):
        progression = "CAST는 발사 준비 → 방출 섬광 → 짧은 잔광. PROJECTILE은 동일 중심축에서 자체 회전/맥동만 하며 위치 이동은 엔진에 맡긴다."
        target = "조준 지점은 그림에 캐릭터로 표시하지 않는다. 현재 전용 IMPACT 출력은 요구하지 않는다."
    elif number(skill.get("dash_distance")) > 0:
        progression = "도착점 압축 → 충돌 절정 → 파편/잔상 소멸. 출발부터 도착까지의 전신 이동을 시트 안에서 반복하지 않는다."
        target = "도착점 주변 피격 범위만 읽히게 하고 이동 경로 전체를 범위로 오인시키지 않는다."
    else:
        progression = "핵심 형상 준비 → 시전자 중심 확장 → 피해 판정과 가까운 절정 프레임 → 잔광/파편 소멸."
        target = "시전자 중심 원형 범위를 표현한다. 데이터가 단일/최대 대상 제한이면 시각 밀도만 줄이고 허구의 부채꼴·지정 지점을 만들지 않는다."
    return (
        f"- 핵심 소재: {core}\n"
        f"- 주 색상: {primary}\n"
        f"- 보조 색상: {secondary}\n"
        f"- 런타임 역할: {contract['roles']}\n"
        f"- 효과 발생 위치: {contract['origin']}\n"
        f"- 진행 방향·엔진 이동: {contract['direction']} {contract['engine_motion']}\n"
        f"- 대상 표현: {target}\n"
        f"- 화면 점유율: {occupancy}\n"
        f"- 이펙트 밀도: {density}\n"
        f"- 시간 흐름: {progression}\n"
        f"- 판정 정렬: {contract['timing']}\n"
        f"- 아이콘 핵심 모티브: {icon}\n"
        "- 몬스터 본체 금지 범위: 몸·얼굴·전신 실루엣은 VFX에 넣지 않는다. 다만 확정 핵심 소재인 인형·손자국·가면·껍질·뿔·장비 파편은 해당 명세대로 유지한다."
    )


def output_profile_from_spec(spec: str) -> tuple[str, int, int, str]:
    profile = re.search(r"(?m)^- profile:\s*`([^`]+)`", spec)
    vfx = re.search(r"(?m)^- VFX:\s*(\d+) frames, 각 (\d+)×(\d+) RGBA PNG, 약 ([0-9.]+) sec/frame", spec)
    return (
        profile.group(1) if profile else "UNCONFIRMED",
        int(vfx.group(1)) if vfx else 0,
        int(vfx.group(2)) if vfx else 0,
        vfx.group(4) if vfx else "미확인",
    )


def build_master_prompt(area_id: str, area_name: str, count: int) -> str:
    output_root = f"{area_id.upper()}_IMAGES_OUTPUT"
    return f"""# ChatGPT Images Master Prompt — {area_id} {area_name}

첨부된 ZIP 전체를 먼저 분석하세요. 이 ZIP은 `{area_id}` / **{area_name}**의 포획 가능 몬스터 {count}종에 대한 제작 INPUT입니다. `READY`는 입력 준비 상태이며 결과 아트 승인이나 게임 반입 성공을 뜻하지 않습니다.

1. `PACKAGE_REVISION.md`, `AREA_MANIFEST`, 모든 `GENERATION_SPEC.md`, `RUNTIME_ROLE_MAP.md`, `SOURCE_PROVENANCE.md`를 먼저 읽으세요.
2. 몬스터 원본은 `MONSTER_IMAGE.png`를 그대로 참조합니다. 원본 몬스터를 재생성하거나 Preview에서 새로 그리지 말고 INPUT 이미지를 기계적으로 합성하세요.
3. WHAT(IDs, 이름, 타입, 효과, 동작)은 확정값입니다. 변경·재설계하지 말고 HOW만 제작하세요.
4. 공통 라이브러리는 프로젝트와 공식 검색에서 확보한 **183개 수집본**이며 메이플 전체 스킬 전수 자료가 아닙니다. `RECENT_PRIMARY`는 검증 가능한 시기 근거가 있을 때만 최신 우선으로 씁니다. 현재 `RECENT_SECONDARY`는 6차/HEXA 검색 후보일 뿐 시기·버전이 검증되지 않았으므로 최신으로 자동 승격하지 않습니다. `UNKNOWN`, `LEGACY_REFERENCE`도 보조 비교용이며 다운로드 시각은 아트 제작·업데이트 시각이 아닙니다.
5. `STYLE_INDEX`의 `role_classification`을 지키세요. `MONSTER_CHARACTER`, `SCENE`, `EXCLUDE_STYLE`의 본체·장면 실루엣을 신규 VFX 외형으로 가져오지 마세요. 혼합 자료는 VFX의 선·명암·알파 가장자리만 참고합니다.
6. 기존 스킬의 캐릭터, 무기, 고유 실루엣, 메커니즘을 복제하지 않습니다. 어두운 외곽→중간톤 형상→밝은 코어, 제한된 발광·반투명 층, 타격광, 잔상, 파편, 자연스러운 fade 같은 렌더링 문법만 참고합니다.
7. 각 `GENERATION_SPEC`의 역할별 산출물을 따릅니다. 엔진이 PROJECTILE 또는 layer drift를 이동시키면 이미지 안에서 캔버스 전체를 다시 이동시키지 않습니다. CAST/PROJECTILE/REFERENCE_VFX를 한 불명확한 시트로 합치지 않습니다.
8. VFX 원본 생성과 코드 후처리를 구분합니다. 원본 시트로 생성했다면 시트 원본과 정확한 분할 좌표를 보존하고, 주 납품물은 연속된 개별 RGBA PNG입니다. autocrop/recenter 금지, 동일 캔버스·피봇 유지, 빈 프레임·누락·다른 셀 조각 금지입니다.
9. RGBA라는 파일 모드만 확인하지 말고 실제 배경 alpha, 잘림, 셀 경계 침범을 검사하세요. 픽셀 검사는 아트 정합성 승인을 대신하지 않으며 `AUTO_VALIDATION`과 `USER_ART_APPROVAL`을 별도 기록합니다.
10. ICON은 256×256 RGBA 1장입니다. VFX/ICON에 텍스트·숫자·UI·워터마크·몬스터 본체 전체를 넣지 않습니다.
11. 출력 루트는 반드시 `{output_root}/`입니다. 실제 PNG 파일과 다운로드 가능한 OUTPUT ZIP이 없으면 COMPLETE/PASS로 기록하지 마세요. 도구 한도 중단 시 완료분·미완료분을 나누고 한도 해제나 무인 완주를 약속하지 마세요.

AREA 00 승인 재사용 파일이 `approved_reuse/AREA_00/`에 있으면 호환 확인된 그 자산을 그대로 재사용하며 다시 생성하지 않습니다. 다른 스킬의 모양·색을 AREA 00에서 복사하지 않습니다.
"""


def build_output_specs(area_id: str) -> tuple[str, str]:
    root = f"{area_id.upper()}_IMAGES_OUTPUT"
    fmt = f"""# Output Format Spec

## 원본 생성과 주 납품물

- 미술 원본을 시트로 생성했다면 **원본 시트와 분할 좌표 기록을 보존**한다.
- 주 납품물은 `F00`, `F01` ... 연속 번호의 **frame-separated RGBA PNG**다. contact/sprite sheet는 선택적 Preview이며 주 납품물을 대체하지 않는다.
- 각 역할(CAST_VFX, PROJECTILE, REFERENCE_VFX)은 GENERATION_SPEC의 `런타임 역할`과 `필요 파일`을 따른다. 서로 다른 역할을 한 시트에 섞지 않는다.
- 실제 배경 alpha가 있어야 한다. 흰색·검정·체커보드 배경, 빈 프레임, 셀 조각, 가장자리 잘림, 누락 프레임은 실패다.
- 동일 역할의 프레임은 캔버스·피봇·스케일이 같아야 한다. 임의 autocrop/recenter 금지.
- 우측 기준/FlipX 규칙은 GENERATION_SPEC를 따른다. 엔진 이동 PROJECTILE과 layer drift는 이미지 내부 전체 이동과 중복하지 않는다.
- ICON은 256×256 RGBA 1장이다. 글자·숫자·UI 프레임·몬스터 본체 전체 금지.
- 파일 자동검사 통과와 사용자 아트 승인은 별개다.

## 프로필 기준

기존 프로필의 프레임 수·캔버스·시간은 몬스터별 GENERATION_SPEC에 보존되어 있다. AREA 00 규격을 다른 스킬에 일괄 복사하지 않는다. 패시브 `REFERENCE_VFX`는 기존 제작 범위의 비전투 참고 산출물이며 런타임 연결 대상이 아니다.

출력 루트: `{root}/`
"""
    naming = f"""# Output Naming Spec

출력 루트: `{root}/`

## 필수 규칙

- 기본 CAST/REFERENCE VFX: `NNN_[monster_id]_[skill_id]_F00.png`, `F01.png` ...
- 별도 PROJECTILE이 필요한 경우: `NNN_[monster_id]_[skill_id]_PROJECTILE.png` 또는 명세가 다프레임으로 확정한 경우 `_PROJECTILE_F00.png` ...
- 아이콘: `NNN_[monster_id]_[skill_id]_ICON.png`
- 선택 Preview: `NNN_[monster_id]_[skill_id]_CONTACT_PREVIEW.png`
- NNN은 AREA_MANIFEST의 3자리 작업 순번이며 monster_id/skill_id를 축약·번역하지 않는다.
- 원본 생성 시트가 있으면 `SOURCE_SHEET/`에 보존하고 `SHEET_SPLIT_MANIFEST.csv`에 source_file, role, frame_index, x, y, width, height 열로 분할 좌표를 기록한다.
- 결과 manifest 열은 work_order, area_id, monster_id, monster_name, skill_id, skill_name, skill_type, role, file, width, height, mode, sha256, auto_validation, user_art_approval 순서다.

```text
{root}/
├─ OUTPUT_MANIFEST.md
├─ OUTPUT_MANIFEST.csv
├─ SOURCE_SHEET/                 # 원본 시트가 있을 때
├─ SHEET_SPLIT_MANIFEST.csv      # 분할했을 때
└─ monsters/
   └─ NNN_[monster_id]_[name]/
      ├─ VFX/
      ├─ PROJECTILE/             # 명세에 필요할 때만
      ├─ ICON/
      ├─ PREVIEW/                # 선택
      └─ RESULT_INFO.md
```
"""
    return fmt, naming


def build_style_docs(rows: list[dict[str, str]], counts: Counter) -> tuple[str, str, str]:
    columns = list(rows[0])
    lines = ["# Global Skill Style Library Index", "", "프로젝트 시각 RUID와 공식 검색 보조 후보를 합친 183개 수집본이다. 메이플 전체 스킬 전수 자료가 아니다.", "", "## 판정 규칙", "", "- RECENT_PRIMARY는 출시 시기·버전 근거가 검증된 경우만 사용한다.", "- RECENT_SECONDARY는 6차/HEXA 의미 검색 후보이지만 시기·버전이 미검증이므로 RECENT_PRIMARY의 대체 최신 세트로 자동 승격하지 않는다.", "- UNKNOWN/LEGACY_REFERENCE는 보조 비교 자료다. 다운로드 시각은 원본 아트 제작·업데이트 시각이 아니다.", "- role_classification이 MONSTER_CHARACTER/SCENE이면 본체·장면 실루엣을 신규 VFX로 가져오지 않는다. EXCLUDE_STYLE은 렌더링 스타일 판단에서 제외한다.", "", "| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "")).replace("|", "\\|").replace("\n", " ") for c in columns) + " |")
    index_md = "\n".join(lines) + "\n"
    atlas = f"""# Global Style Atlas — 검증된 역할과 시기 불확실성

## 코퍼스 범위

- 수집된 고유 RUID: {len(rows)}개. 현재 프로젝트 시각 필드와 공식 검색 보조 후보의 합집합이며 메이플 전체 스킬 전수 자료가 아니다.
- 스타일 분류: RECENT_PRIMARY {counts['RECENT_PRIMARY']} / RECENT_SECONDARY {counts['RECENT_SECONDARY']} / LEGACY_REFERENCE {counts['LEGACY_REFERENCE']} / UNKNOWN {counts['UNKNOWN']} / EXCLUDE_STYLE {counts['EXCLUDE_STYLE']}.
- 역할 분류: VFX {counts['ROLE_VFX']} / ICON {counts['ROLE_ICON']} / MONSTER_CHARACTER {counts['ROLE_MONSTER_CHARACTER']} / SCENE {counts['ROLE_SCENE']} / UNCONFIRMED {counts['ROLE_UNCONFIRMED']}.

## 사용 원칙

1. WHAT은 GENERATION_SPEC의 확정 데이터이며 변경하지 않는다.
2. RECENT_PRIMARY는 검증 가능한 출시 시기·버전 근거가 있을 때만 최신 우선으로 사용한다.
3. RECENT_SECONDARY는 6차/HEXA 검색 후보일 뿐 최신성이 검증되지 않았다. RECENT_PRIMARY가 비어도 자동 승격하지 않는다.
4. UNKNOWN/LEGACY_REFERENCE는 비교·보조용이다. 파일 다운로드 시각은 아트 제작·업데이트 시각이 아니다.
5. `role_classification=VFX`인 프리뷰에서만 효과의 선·명암·알파 가장자리·파편 밀도를 참고한다.
6. `MONSTER_CHARACTER`, `SCENE`, `EXCLUDE_STYLE`은 신규 VFX 외형 레퍼런스로 쓰지 않는다. 효과와 본체가 함께 있으면 효과 영역의 렌더링만 참고하고 캐릭터·무기·고유 실루엣은 가져오지 않는다.
7. 아이콘은 대표 실루엣 1개 + 보조 효과 1개를 작은 크기에서 읽히게 한다.

## 공통 렌더링 문법

- 어두운 외곽 → 중간톤 형상 → 제한된 밝은 코어의 단계가 읽혀야 한다.
- 발광·반투명 레이어는 형태를 지우지 않는 범위에서 사용한다.
- 프레임은 준비 → 상승 → 절정 → 소멸을 따르되, 패시브 참고 모티브에는 공격 절정을 강제하지 않는다.
- 중심축과 알파 가장자리를 안정적으로 유지한다.
"""
    csv_out = csv_text(rows, columns)
    return index_md, csv_out, atlas


def make_contact_sheets(records: list[tuple[str, str, bytes]], out_dir: Path, prefix: str, cols: int = 5, rows: int = 5) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    per = cols * rows
    for page, start in enumerate(range(0, len(records), per), 1):
        subset = records[start:start + per]
        canvas = Image.new("RGBA", (cols * 220, rows * 190), (244, 244, 244, 255))
        draw = ImageDraw.Draw(canvas)
        for j, (label, ruid, data) in enumerate(subset):
            x = (j % cols) * 220
            y = (j // cols) * 190
            with Image.open(io.BytesIO(data)) as im:
                rgba = im.convert("RGBA")
                rgba.thumbnail((190, 145), Image.Resampling.LANCZOS)
                tile = Image.new("RGBA", (200, 150), (220, 220, 220, 255))
                tile.alpha_composite(rgba, ((200 - rgba.width) // 2, (150 - rgba.height) // 2))
                canvas.alpha_composite(tile, (x + 10, y + 5))
            draw.text((x + 10, y + 157), f"{start+j+1:03d} {label[:25]}", fill=(15, 15, 15, 255), font=font)
            draw.text((x + 10, y + 172), ruid[:16], fill=(70, 70, 70, 255), font=font)
        canvas.convert("RGB").save(out_dir / f"{prefix}_{page:02d}.jpg", quality=90)


def copy_area00_reuse(stage_root: Path, manifest: list[dict[str, str]]) -> list[dict]:
    mappings = {r["monster_id"]: r for r in read_csv_file(AREA00_MAP)} if AREA00_MAP.exists() else {}
    reused = []
    for row in manifest:
        mid, sid = row["monster_id"], row["skill_id"]
        match = mappings.get(mid)
        if not match or match.get("skill_id") != sid:
            continue
        source_dirs = [p for p in (AREA00_OUT / "monsters").iterdir() if f"_{mid}_" in p.name]
        if len(source_dirs) != 1:
            continue
        source = source_dirs[0]
        target = stage_root / "approved_reuse" / "AREA_00" / source.name
        shutil.copytree(source, target)
        files = []
        for file in sorted(target.rglob("*.png")):
            files.append({"file": file.relative_to(stage_root).as_posix(), "sha256": sha256_file(file)})
        reused.append({"monster_id": mid, "skill_id": sid, "source": source.relative_to(ROOT).as_posix(), "files": files})
    if reused:
        lines = ["# AREA 00 승인 에셋 재사용", "", "아래 파일은 AREA 00 승인 OUTPUT의 바이트 복사본이다. 호환되는 동일 monster_id + skill_id에만 재사용하며 다시 생성하지 않는다.", ""]
        for r in reused:
            lines += [f"## {r['monster_id']} / {r['skill_id']}", "", f"- source: `{r['source']}`", "- files:"]
            lines += [f"  - `{x['file']}` — SHA-256 `{x['sha256']}`" for x in r["files"]]
            lines.append("")
        (stage_root / "approved_reuse" / "AREA_00_REUSE_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return reused


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base_hashes = {p.name: sha256_file(p) for p in sorted(BASE.glob("AREA_*_IMAGES_INPUT.zip"))}
    area00_hashes = {
        "input_zip": base_hashes.get("AREA_00_IMAGES_INPUT.zip", "missing"),
        "output_manifest": sha256_file(AREA00_OUT / "OUTPUT_MANIFEST.md") if (AREA00_OUT / "OUTPUT_MANIFEST.md").exists() else "missing",
        "resource_map": sha256_file(AREA00_MAP) if AREA00_MAP.exists() else "missing",
        "import_report": sha256_file(AREA00_REPORT) if AREA00_REPORT.exists() else "missing",
    }

    areas = {r["id"]: r for r in read_csv_file(DATA / "AreaTable.csv")}
    rooms = read_csv_file(DATA / "RoomTable.csv")
    monsters = {r["id"]: r for r in read_csv_file(DATA / "MonsterTable.csv")}
    skills_list, skill_source = load_skill_baseline()
    skills = {r["id"]: r for r in skills_list}
    balance_rows = read_csv_file(DATA / "GameBalance.csv")
    balance = {r["key"]: number(r["value"]) for r in balance_rows}
    model_ruids, model_paths = load_models()

    data_baseline = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "AreaTable": {"path": "RootDesk/MyDesk/GameData/AreaTable.csv", "sha256": sha256_file(DATA / "AreaTable.csv")},
        "RoomTable": {"path": "RootDesk/MyDesk/GameData/RoomTable.csv", "sha256": sha256_file(DATA / "RoomTable.csv")},
        "MonsterTable": {"path": "RootDesk/MyDesk/GameData/MonsterTable.csv", "sha256": sha256_file(DATA / "MonsterTable.csv")},
        "GameBalance": {"path": "RootDesk/MyDesk/GameData/GameBalance.csv", "sha256": sha256_file(DATA / "GameBalance.csv")},
        "SkillTable": skill_source,
        "legacy_input_zip_sha256": base_hashes,
        "area00_frozen_sha256": area00_hashes,
    }
    (OUT / "SOURCE_BASELINE.json").write_text(json.dumps(data_baseline, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    # Determine capture rosters from actual room placement. Hidden job bosses without drop_skill_id are intentionally excluded.
    area_capture: dict[str, list[str]] = defaultdict(list)
    area_non_capture: dict[str, list[str]] = defaultdict(list)
    for room in rooms:
        aid = room.get("area_id", "")
        for mid in split_pipe(room.get("monster_id")):
            mon = monsters.get(mid)
            if not mon:
                continue
            target = area_capture if mon.get("drop_skill_id") else area_non_capture
            if mid not in target[aid]:
                target[aid].append(mid)

    area00_approved = {r["monster_id"]: r for r in read_csv_file(AREA00_MAP)} if AREA00_MAP.exists() else {}
    style_template_rows: list[dict[str, str]] | None = None
    style_template_files: dict[str, bytes] = {}
    style_counts = Counter()
    area_results = []
    additional = []
    monster_contact_records: list[tuple[str, str, bytes]] = []
    monster_hash_groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    style_hashes: set[str] = set()

    # First pass gets the common style library and checks package-to-package identity.
    for aid in TARGET_IDS:
        base_zip = BASE / f"{aid.upper()}_IMAGES_INPUT.zip"
        if not base_zip.exists():
            continue
        with zipfile.ZipFile(base_zip) as z:
            root = f"{aid.upper()}_IMAGES_INPUT/"
            style_csv_name = root + "global_skill_style_library/STYLE_INDEX.csv"
            rows = read_csv_text(z.read(style_csv_name).decode("utf-8-sig"))
            if style_template_rows is None:
                style_template_rows = rows
                for name in z.namelist():
                    if name.startswith(root + "global_skill_style_library/skills/"):
                        rel = name[len(root + "global_skill_style_library/"):]
                        style_template_files[rel] = z.read(name)
                        if name.endswith("/preview.png"):
                            style_hashes.add(sha256_bytes(z.read(name)))
            else:
                if csv_text(rows, list(rows[0])) != csv_text(style_template_rows, list(style_template_rows[0])):
                    additional.append({"category": "확인된 INPUT 오류", "area_id": aid, "item": "공통 STYLE_INDEX가 다른 Area와 불일치", "action": "V2 공통 단일 버전으로 통일"})

    if style_template_rows is None:
        raise RuntimeError("No base style library")
    style_rows = []
    for style_index, raw in enumerate(style_template_rows, 1):
        row = dict(raw)
        role, reason, priority = style_role(row, style_index)
        row["role_classification"] = role
        row["role_basis"] = reason
        row["style_priority"] = priority
        if role == "MONSTER_CHARACTER":
            row["notes"] = (row.get("notes", "") + "; 본체 실루엣 신규 VFX 전용 금지").strip("; ")
        style_rows.append(row)
        style_counts[priority] += 1
        style_counts["ROLE_" + role] += 1
    style_index_md, style_index_csv, style_atlas_md = build_style_docs(style_rows, style_counts)

    with tempfile.TemporaryDirectory(prefix="area_input_v2_") as td:
        tmp = Path(td)
        for aid in TARGET_IDS:
            area = areas.get(aid)
            base_zip = BASE / f"{aid.upper()}_IMAGES_INPUT.zip"
            result = {
                "area_id": aid,
                "area_name": area.get("name", "") if area else "",
                "status": "READY",
                "changes": [],
                "findings": [],
                "monster_image_replacements": 0,
                "unresolved": [],
            }
            if not area or not base_zip.exists():
                result["status"] = "BLOCKED"
                result["unresolved"].append("AreaTable 또는 기존 INPUT ZIP 없음")
                area_results.append(result)
                continue
            stage = tmp / f"{aid.upper()}_IMAGES_INPUT_V2"
            with zipfile.ZipFile(base_zip) as z:
                legacy_root = f"{aid.upper()}_IMAGES_INPUT/"
                for name in z.namelist():
                    if not name.startswith(legacy_root) or name.endswith("/"):
                        continue
                    rel = name[len(legacy_root):]
                    target = stage / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(z.read(name))

            manifest_path = stage / "AREA_MANIFEST.csv"
            manifest = read_csv_file(manifest_path)
            manifest_ids = [r["monster_id"] for r in manifest]
            expected = area_capture.get(aid, [])
            if set(manifest_ids) != set(expected):
                result["status"] = "BLOCKED"
                result["unresolved"].append(f"포획 가능 실제 배치 {expected}와 manifest {manifest_ids} 불일치")
            hidden = area_non_capture.get(aid, [])
            if hidden:
                result["findings"].append("방 배치에는 있으나 포획 대상이 아닌 히든 직업 보스 제외: " + ", ".join(hidden))

            revised_manifest = []
            for row in manifest:
                mid, sid = row["monster_id"], row["skill_id"]
                mon = monsters.get(mid)
                if not mon:
                    result["status"] = "BLOCKED"; result["unresolved"].append(f"MonsterTable에 {mid} 없음"); revised_manifest.append(row); continue
                if mon.get("drop_skill_id") != sid:
                    result["status"] = "BLOCKED"; result["unresolved"].append(f"{mid}: MonsterTable drop_skill_id={mon.get('drop_skill_id')} / INPUT={sid}")
                skill = skills.get(sid)
                if not skill:
                    # Area 00 verified runtime is stronger evidence for the uncommitted dew-trail row, but the missing table remains explicit.
                    approved = area00_approved.get(mid)
                    if approved and approved.get("skill_id") == sid:
                        result["unresolved"].append(f"{sid}: 작업 트리 SkillTable 삭제로 행 직접 재조회 불가; AREA 00 승인 런타임/manifest와 일치하여 승인 재사용만 허용")
                    else:
                        result["status"] = "BLOCKED"; result["unresolved"].append(f"SkillTable 기준에 {sid} 없음")
                    revised_manifest.append(row)
                    continue
                expected_fields = {
                    "monster_name": mon["name"], "level": mon["level"], "skill_name": skill["name"],
                    "skill_type": skill_type(skill), "actual_effect": actual_effect(skill, balance),
                }
                for field, expected_value in expected_fields.items():
                    if row.get(field) != expected_value:
                        result["findings"].append(f"{mid} {field}: INPUT={row.get(field)!r} / 기준={expected_value!r}")
                        row[field] = expected_value
                        result["changes"].append(f"{mid} {field} 동기화")
                row["actual_motion"] = legacy_motion_summary(skill)
                revised_manifest.append(row)

            manifest_path.write_text(csv_text(revised_manifest, list(revised_manifest[0])), encoding="utf-8", newline="\n")
            # Manifest markdown is regenerated to eliminate stale templated claims.
            md_lines = [f"# {aid.upper()} Images Input Manifest — V2", "", f"- Area: `{aid}` / {area['name']}", f"- 대상: 실제 방 배치 중 drop_skill_id가 있는 포획 가능 몬스터 {len(revised_manifest)}종", f"- 제외된 비포획 방 배치: {', '.join(hidden) if hidden else '없음'}", "- READY는 제작 INPUT 준비 상태이며 아트 승인/게임 반입 성공을 뜻하지 않는다.", "", "| 순번 | Lv | monster_id | 몬스터 | skill_id | 스킬 | 타입 | 보스 |", "|---:|---:|---|---|---|---|---|:---:|"]
            for r in revised_manifest:
                md_lines.append(f"| {r['work_order']} | {r['level']} | `{r['monster_id']}` | {r['monster_name']} | `{r['skill_id']}` | {r['skill_name']} | {r['skill_type']} | {r['boss']} |")
            (stage / "AREA_MANIFEST.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8", newline="\n")

            # Replace the common library with exactly one corrected version.
            common = stage / "global_skill_style_library"
            if common.exists():
                shutil.rmtree(common)
            for rel, data in style_template_files.items():
                target = common / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            (common / "STYLE_INDEX.md").write_text(style_index_md, encoding="utf-8", newline="\n")
            (common / "STYLE_INDEX.csv").write_text(style_index_csv, encoding="utf-8", newline="\n")
            (common / "summary").mkdir(parents=True, exist_ok=True)
            (common / "summary" / "STYLE_ATLAS.md").write_text(style_atlas_md, encoding="utf-8", newline="\n")

            (stage / "CHATGPT_IMAGES_MASTER_PROMPT.md").write_text(build_master_prompt(aid, area["name"], len(revised_manifest)), encoding="utf-8", newline="\n")
            fmt, naming = build_output_specs(aid)
            (stage / "OUTPUT_FORMAT_SPEC.md").write_text(fmt, encoding="utf-8", newline="\n")
            (stage / "OUTPUT_NAMING_SPEC.md").write_text(naming, encoding="utf-8", newline="\n")
            (stage / "README_START_HERE.md").write_text(
                f"# START HERE — {aid} {area['name']} V2\n\n"
                "1. PACKAGE_REVISION과 AREA_MANIFEST에서 범위와 보류를 확인한다.\n"
                "2. 각 MONSTER_INFO/SOURCE_PROVENANCE/GENERATION_SPEC/RUNTIME_ROLE_MAP을 읽는다.\n"
                "3. MASTER_PROMPT와 OUTPUT 규격을 따른다.\n"
                "4. MONSTER_IMAGE는 재생성하지 않고 Preview에 그대로 합성한다.\n"
                "5. STYLE_INDEX의 역할/시기 불확실성을 지키며 RECENT_SECONDARY를 최신으로 자동 승격하지 않는다.\n"
                "6. 주 납품물은 역할별 개별 RGBA PNG이고 시트는 선택 Preview다.\n"
                f"7. 출력 루트는 `{aid.upper()}_IMAGES_OUTPUT/`이다.\n\n"
                "금지: 스킬 기획·게임 데이터 변경, 리소스 등록, AnimationClip 변경, 이미지 생성 완료를 파일 없이 선언.\n",
                encoding="utf-8", newline="\n")

            source_rows = []
            for row in revised_manifest:
                mid, sid = row["monster_id"], row["skill_id"]
                mon = monsters.get(mid, {})
                skill = skills.get(sid)
                folder = stage / row["folder"]
                image_path = folder / "MONSTER_IMAGE.png"
                data = image_path.read_bytes()
                info = png_info(data)
                image_hash = sha256_bytes(data)
                monster_hash_groups[image_hash].append((aid, mid, row["monster_image_ruid"]))
                if image_hash in style_hashes:
                    result["status"] = "BLOCKED"; result["unresolved"].append(f"{mid}: MONSTER_IMAGE가 style preview와 바이트 동일")
                expected_ruid = model_ruids.get(mon.get("model_id", ""), "")
                if expected_ruid != row["monster_image_ruid"]:
                    result["status"] = "BLOCKED"; result["unresolved"].append(f"{mid}: model RUID {expected_ruid} != INPUT {row['monster_image_ruid']}")
                if info["format"] != "PNG" or info["alpha_max"] == 0:
                    result["status"] = "BLOCKED"; result["unresolved"].append(f"{mid}: MONSTER_IMAGE PNG/alpha invalid")
                source = {
                    "area_id": aid, "monster_id": mid, "model_id": mon.get("model_id", ""),
                    "model_path": model_paths.get(mon.get("model_id", ""), "미확인"),
                    "model_sprite_ruid": expected_ruid, "input_image": image_path.relative_to(stage).as_posix(),
                    "sha256": image_hash, **info,
                    "source_origin": "기존 INPUT에 포함된 MSW 리소스 썸네일 대표 PNG",
                    "raw_download": "기존 _cache/raw 및 resource_metadata가 현재 보존되지 않아 원 다운로드 파일·다운로드 시각 재확인 불가",
                    "selected_frame": "기존 빌드 로직은 alpha bbox 최대 프레임을 선택했으나 개별 선택 index 기록은 패키지에 없어 미확인",
                    "crop_region": f"전체 캔버스 0,0,{info['width']},{info['height']}; autocrop/recenter 수행 기록 없음",
                    "composite_components": "모델 단일 SpriteRUID 기준; 합성 모델 여부를 증명하는 원본 메타데이터 없음",
                }
                source_rows.append(source)
                provenance = [f"# Source Provenance — {mid}", ""] + [f"- {k}: `{v}`" for k, v in source.items()]
                (folder / "SOURCE_PROVENANCE.md").write_text("\n".join(provenance) + "\n", encoding="utf-8", newline="\n")
                monster_contact_records.append((f"{aid}/{mid}", expected_ruid, data))

                if skill:
                    contract = runtime_contract(skill, balance)
                    spec_path = folder / "GENERATION_SPEC.md"
                    old_spec = spec_path.read_text(encoding="utf-8")
                    updated = replace_section(old_spec, "시각 번역", concrete_visual_section(old_spec, skill, contract))
                    updated = re.sub(r"(?m)^- 스타일 적용 우선순위:.*$", "- 스타일 적용 우선순위: 시기 근거가 검증된 RECENT_PRIMARY만 최신 우선으로 사용한다. RECENT_SECONDARY는 최신 대체 세트가 아니며 UNKNOWN/LEGACY와 함께 보조 비교로만 사용한다.", updated)
                    profile, frames, size, sec = output_profile_from_spec(updated)
                    needed = ["ICON: 256×256 RGBA 1장"]
                    if skill_type(skill) == "패시브":
                        needed.append(f"REFERENCE_VFX: 기존 명세 유지 {frames} frames × {size}×{size} RGBA; 런타임 미사용·자동 반입 금지")
                    else:
                        needed.append(f"CAST_VFX: {frames} frames × {size}×{size} RGBA, {sec}s/frame")
                        if skill.get("projectile_ruid"):
                            needed.append("PROJECTILE: 현행 projectile_ruid를 그대로 유지하며 이번 V2 신규 생성 범위에는 포함하지 않음")
                            result["findings"].append(f"{mid}: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존")
                    runtime_body = "\n".join([
                        f"- 역할: {contract['roles']}", f"- 발생 위치: {contract['origin']}", f"- 판정/재생: {contract['timing']}",
                        f"- 방향: {contract['direction']}", f"- 현재 리소스: {contract['runtime_sources'] or '없음'}",
                        "- 필요 파일:", *[f"  - {x}" for x in needed],
                        "- 좌표 단위: layer offset은 world unit, drift는 world unit/s. 픽셀 피봇/최종 Resource Storage offset은 이번 INPUT 단계에서 확정하지 않는다.",
                        "- 반복: 현행 CAST 레이어는 one-shot. 지속 버프 시간과 VFX 재생 수명은 별개.",
                    ])
                    updated = replace_section(updated, "런타임 역할·반입 계약", runtime_body)
                    spec_path.write_text(updated, encoding="utf-8", newline="\n")
                    (folder / "RUNTIME_ROLE_MAP.md").write_text(
                        f"# Runtime Role Map — {mid} / {sid}\n\n" + runtime_body + "\n",
                        encoding="utf-8", newline="\n")
                else:
                    approved = area00_approved.get(mid)
                    if approved and approved.get("skill_id") == sid:
                        runtime_body = "\n".join([
                            "- 역할: APPROVED_REUSE_CAST_VFX=AREA 00 승인 AnimationClip 재사용; ICON=AREA 00 승인 UI 아이콘 재사용",
                            "- 발생 위치: AREA 00 반입 보고서에서 플레이어 좌·우 방향 및 몬스터 시전자 재생을 검증했다. 현재 작업 트리의 SkillTable 원본 행이 삭제되어 세부 offset은 새 값으로 확정하지 않는다.",
                            f"- 판정/재생: 승인 기록 기준 {approved.get('frame_count', '8')}프레임 × {approved.get('frame_seconds', '0.1')}초, 총 {approved.get('total_seconds', '0.8')}초 one-shot. 피해 판정 시점은 현재 삭제된 SkillTable 행을 추정하지 않는다.",
                            "- 방향: 승인 런타임 기록의 좌우 재생을 그대로 재사용한다. 새 이미지 내부 이동·recenter·Flip 규칙을 추가하지 않는다.",
                            f"- 현재 승인 리소스: AnimationClip `{approved.get('animationclip_ruid', '')}` / ICON `{approved.get('icon_ruid', '')}`",
                            "- 필요 파일:",
                            "  - approved_reuse/AREA_00 아래에 포함된 승인 F00... 프레임과 ICON을 바이트 그대로 사용",
                            "  - 신규 VFX/ICON 생성 금지; AREA 00 승인 에셋과 해시가 다르면 재사용 중단",
                            "- 좌표 단위: 현재 삭제된 SkillTable 행 때문에 새 좌표·크기 값을 만들지 않는다. 승인 적용값을 유지한다.",
                            "- 반복: 승인 AnimationClip은 one-shot. 재사용 정책은 동일 monster_id + skill_id에만 적용한다.",
                        ])
                        spec_path = folder / "GENERATION_SPEC.md"
                        spec_text = spec_path.read_text(encoding="utf-8")
                        spec_text = replace_section(spec_text, "런타임 역할·반입 계약", runtime_body)
                        spec_path.write_text(spec_text, encoding="utf-8", newline="\n")
                        (folder / "RUNTIME_ROLE_MAP.md").write_text(
                            f"# Runtime Role Map — {mid} / {sid}\n\n" + runtime_body + "\n",
                            encoding="utf-8", newline="\n")
                    else:
                        (folder / "RUNTIME_ROLE_MAP.md").write_text(
                            f"# Runtime Role Map — {mid} / {sid}\n\n- 상태: BLOCKED\n- 이유: 현재 작업 트리 SkillTable이 삭제되어 행을 직접 재조회할 수 없고 승인 재사용 근거도 없다. 신규 생성 금지.\n",
                            encoding="utf-8", newline="\n")

                # Remove the superseded chronology claim even when the current SkillTable row
                # is unavailable (the approved Area 00 reuse case).
                spec_path = folder / "GENERATION_SPEC.md"
                if spec_path.exists():
                    spec_text = spec_path.read_text(encoding="utf-8")
                    spec_text = spec_text.replace(
                        "RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY를 사실상의 최신 우선 스타일 세트로 사용한다. UNKNOWN과 LEGACY_REFERENCE는 비교·보조 참고이며 최종 렌더링 우선순위가 아니다. 전체 라이브러리는 유지하되 최종 판단은 최신 메이플스토리/MSW 시각 문법을 우선함.",
                        "시기 근거가 검증된 RECENT_PRIMARY만 최신 우선으로 사용한다. RECENT_SECONDARY는 최신 대체 세트가 아니며 UNKNOWN/LEGACY와 함께 보조 비교로만 사용한다."
                    )
                    spec_path.write_text(spec_text, encoding="utf-8", newline="\n")

                # Extend MONSTER_INFO without changing its fixed identity fields.
                info_path = folder / "MONSTER_INFO.md"
                info_text = info_path.read_text(encoding="utf-8")
                info_text += (
                    "\n## V2 source check\n\n"
                    f"- model file: `{model_paths.get(mon.get('model_id',''), '미확인')}`\n"
                    f"- model SpriteRUID match: {'PASS' if expected_ruid == row['monster_image_ruid'] else 'FAIL'}\n"
                    f"- MONSTER_IMAGE SHA-256: `{image_hash}`\n"
                    f"- image: {info['width']}×{info['height']} {info['mode']} / alpha {info['alpha_min']}~{info['alpha_max']} / bbox {info['alpha_bbox']}\n"
                    "- 원 다운로드 원본/선택 프레임 메타데이터는 기존 패키지에 남아 있지 않아 미확인이다. 해시 일치만으로 몬스터 적합성을 주장하지 않는다.\n"
                )
                info_path.write_text(info_text, encoding="utf-8", newline="\n")

            # Area-level provenance inventory.
            fields = list(source_rows[0])
            (stage / "MONSTER_IMAGE_PROVENANCE.csv").write_text(csv_text(source_rows, fields), encoding="utf-8", newline="\n")
            reused = copy_area00_reuse(stage, revised_manifest)
            if reused:
                result["changes"].append(f"AREA 00 승인 재사용 자산 {len(reused)}종 포함")

            revision = {
                "revision": "V2",
                "base_zip": base_zip.relative_to(ROOT).as_posix(),
                "base_zip_sha256": base_hashes[base_zip.name],
                "area_id": aid,
                "area_name": area["name"],
                "scope": "INPUT 문서·검증·재사용 파일 보정만; 게임 데이터/아트/리소스 미변경",
                "skill_table_source": skill_source,
                "status": result["status"],
                "unresolved": result["unresolved"],
            }
            (stage / "PACKAGE_REVISION.md").write_text(
                "# Package Revision V2\n\n```json\n" + json.dumps(revision, ensure_ascii=False, indent=2) + "\n```\n",
                encoding="utf-8", newline="\n")
            (stage / "SOURCE_BASELINE.json").write_text(json.dumps(data_baseline, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

            # No absolute local path may remain inside an independent package.
            absolute_hits = []
            for file in stage.rglob("*"):
                if file.is_file() and file.suffix.lower() in {".md", ".csv", ".txt", ".json"}:
                    text = file.read_text(encoding="utf-8-sig", errors="replace")
                    if re.search(r"(?<![A-Za-z0-9])[A-Za-z]:[/\\]", text):
                        absolute_hits.append(file.relative_to(stage).as_posix())
            if absolute_hits:
                result["status"] = "BLOCKED"; result["unresolved"].append("ZIP 내부 로컬 절대경로: " + ", ".join(absolute_hits))

            # Final zip build.
            zip_path = OUT / f"{aid.upper()}_IMAGES_INPUT_V2.zip"
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for file in sorted(stage.rglob("*")):
                    if file.is_file():
                        z.write(file, f"{stage.name}/{file.relative_to(stage).as_posix()}")
            result["zip_path"] = zip_path.relative_to(ROOT).as_posix()
            result["zip_sha256"] = sha256_file(zip_path)
            result["zip_bytes"] = zip_path.stat().st_size
            result["monster_count"] = len(revised_manifest)
            result["reused_count"] = len(reused)
            result["changes"] += ["공통 스타일 시기/역할 규칙 보정", "실제 런타임 역할·엔진 이동·판정 시점 명시", "OUTPUT 루트/manifest/alpha 검증 규칙 통일", "몬스터 원본 출처·SHA-256 기록"]
            area_results.append(result)

    # Cross-package image checks.
    for digest, group in monster_hash_groups.items():
        unique_mids = {x[1] for x in group}
        if len(unique_mids) > 1:
            additional.append({"category": "확인된 INPUT 오류", "area_id": "MULTI", "item": f"서로 다른 monster_id가 동일 MONSTER_IMAGE bytes 사용: {group}", "action": "자동 교체하지 않음; 관련 패키지 BLOCKED 필요"})

    make_contact_sheets(monster_contact_records, OUT / "audit-previews" / "monsters", "MONSTER_IMAGES")
    style_contact = []
    for row in style_rows:
        ruid = row["RUID"]
        matches = [(rel, data) for rel, data in style_template_files.items() if rel.endswith("/preview.png") and ruid in style_template_files.get(rel.replace("preview.png", "ruid.txt"), b"").decode("utf-8", errors="ignore")]
        if matches:
            style_contact.append((f"{row['role_classification']}:{row['skill_resource_name']}", ruid, matches[0][1]))
    make_contact_sheets(style_contact, OUT / "audit-previews" / "styles", "STYLE_LIBRARY")

    # Independent ZIP re-open validation.
    validation_rows = []
    for result in area_results:
        errors = []
        zip_path = ROOT / result.get("zip_path", "")
        if not zip_path.exists():
            errors.append("ZIP missing")
        else:
            with zipfile.ZipFile(zip_path) as z:
                if z.testzip(): errors.append("CRC failure")
                root = f"{result['area_id'].upper()}_IMAGES_INPUT_V2/"
                names = set(z.namelist())
                for rel in REQUIRED_ROOT + ["PACKAGE_REVISION.md", "SOURCE_BASELINE.json", "MONSTER_IMAGE_PROVENANCE.csv"]:
                    if root + rel not in names: errors.append("missing " + rel)
                manifest = read_csv_text(z.read(root + "AREA_MANIFEST.csv").decode("utf-8-sig")) if root + "AREA_MANIFEST.csv" in names else []
                for row in manifest:
                    folder = root + row["folder"].rstrip("/") + "/"
                    for rel in ("MONSTER_IMAGE.png", "MONSTER_INFO.md", "SOURCE_PROVENANCE.md", "GENERATION_SPEC.md", "RUNTIME_ROLE_MAP.md"):
                        if folder + rel not in names: errors.append(f"{row['monster_id']} missing {rel}")
                docs = "\n".join(z.read(n).decode("utf-8-sig", errors="replace") for n in names if n.endswith((".md", ".txt", ".csv", ".json")))
                if "사실상의 최신 우선" in docs: errors.append("obsolete RECENT_SECONDARY promotion remains")
                if f"{result['area_id'].upper()}_IMAGES_INPUT_IMAGES_OUTPUT" in docs: errors.append("wrong output root remains")
                if re.search(r"(?<![A-Za-z0-9])[A-Za-z]:[/\\]", docs): errors.append("local absolute path remains")
                if "SHEET_SPLIT_MANIFEST.csv" not in docs: errors.append("sheet split provenance rule missing")
        validation_rows.append({"area_id": result["area_id"], "zip": result.get("zip_path", ""), "errors": errors, "validation": "PASS" if not errors else "FAIL"})
        if errors:
            result["status"] = "BLOCKED"
            result["unresolved"].extend(errors)

    # Verify frozen Area00 and game data remained byte-identical.
    post_area00 = {
        "input_zip": sha256_file(BASE / "AREA_00_IMAGES_INPUT.zip"),
        "output_manifest": sha256_file(AREA00_OUT / "OUTPUT_MANIFEST.md"),
        "resource_map": sha256_file(AREA00_MAP),
        "import_report": sha256_file(AREA00_REPORT),
    }
    area00_unchanged = post_area00 == area00_hashes
    game_post = {
        "AreaTable": sha256_file(DATA / "AreaTable.csv"), "RoomTable": sha256_file(DATA / "RoomTable.csv"),
        "MonsterTable": sha256_file(DATA / "MonsterTable.csv"), "GameBalance": sha256_file(DATA / "GameBalance.csv"),
    }
    game_unchanged = all(game_post[k] == data_baseline[k]["sha256"] for k in game_post)

    # Reports.
    index_lines = ["# ALL AREAS INPUT V2 INDEX", "", f"- 대상 Area: {len(area_results)}개 ({', '.join(TARGET_IDS)})", "- 예약 결번 area_06: 생성하지 않음", f"- 대상 몬스터 배치: {sum(r.get('monster_count',0) for r in area_results)}종", f"- AREA 00 변경 없음: {'PASS' if area00_unchanged else 'FAIL'}", f"- 게임 데이터 변경 없음: {'PASS' if game_unchanged else 'FAIL'}", "", "| Area | 이름 | 몬스터 | 재사용 | 상태 | ZIP | SHA-256 |", "|---|---|---:|---:|---|---|---|"]
    for r in area_results:
        index_lines.append(f"| {r['area_id']} | {r['area_name']} | {r.get('monster_count',0)} | {r.get('reused_count',0)} | {r['status']} | `{r.get('zip_path','')}` | `{r.get('zip_sha256','')}` |")
    (OUT / "ALL_AREAS_INPUT_V2_INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8", newline="\n")

    changelog_lines = ["# INPUT V2 CHANGELOG", "", "확정 monster/skill WHAT과 게임 파일은 변경하지 않았다. 기존 INPUT ZIP도 덮어쓰지 않았다.", "", "## 공통", "", "- RECENT_SECONDARY 자동 최신 승격 제거; 시기 근거 없으면 미확인 유지.", "- 183개 라이브러리에 role_classification/role_basis 추가, 본체 RUID를 EXCLUDE_STYLE로 분리.", "- 출력 루트를 AREA_XX_IMAGES_OUTPUT로 통일.", "- 역할별 VFX, 엔진 이동/FlipX/offset·drift 단위, 피해 판정 시점을 실제 코드 기준으로 명시.", "- 원본 시트·분할 좌표 보존, 실제 alpha/잘림/셀 조각 검사, 자동검사와 사용자 승인 분리.", "- Monster model→RUID→MONSTER_IMAGE 출처·해시 기록.", "- AREA 00 동일 ID 승인 자산을 독립 패키지에 바이트 복사하고 해시 기록.", "", "## Area별", ""]
    for r in area_results:
        changelog_lines += [f"### {r['area_id']} {r['area_name']}", "", *[f"- {x}" for x in r["changes"]], ""]
    (OUT / "INPUT_V2_CHANGELOG.md").write_text("\n".join(changelog_lines), encoding="utf-8", newline="\n")

    valid_lines = ["# INPUT V2 VALIDATION", "", f"- Area00 frozen: {'PASS' if area00_unchanged else 'FAIL'}", f"- game data frozen: {'PASS' if game_unchanged else 'FAIL'}", f"- ZIP count: {len(validation_rows)}", f"- ZIP validation PASS: {sum(x['validation']=='PASS' for x in validation_rows)}", "", "| Area | CRC/필수파일/참조/규칙 | 오류 |", "|---|---|---|"]
    for v in validation_rows:
        valid_lines.append(f"| {v['area_id']} | {v['validation']} | {'; '.join(v['errors']) or '없음'} |")
    valid_lines += ["", "검증은 ZIP을 다시 열어 CRC, 필수 문서, manifest 대상, 몬스터 이미지·출처 문서, 런타임 역할 문서, 절대경로, 구형 최신 승격 문구, 출력 루트를 확인했다. 픽셀 검사는 아트 적합성 승인을 대신하지 않는다."]
    (OUT / "INPUT_V2_VALIDATION.md").write_text("\n".join(valid_lines) + "\n", encoding="utf-8", newline="\n")

    findings = [
        ("확인된 INPUT 오류", "공통", "OUTPUT_NAMING_SPEC의 루트가 AREA_XX_IMAGES_INPUT_IMAGES_OUTPUT로 잘못됨", "전 Area에서 AREA_XX_IMAGES_OUTPUT로 수정"),
        ("확인된 INPUT 오류", "공통", "RECENT_PRIMARY가 비면 근거 없는 RECENT_SECONDARY를 최신으로 승격", "자동 승격 제거, 시기 미확인 유지"),
        ("확인된 INPUT 오류", "공통", "효과 위치/방향이 '시전자 또는 지정점', '방사 또는 수직' 템플릿으로 실제 코드와 불일치", "시전자/도착점/엔진 이동/판정 시점별 명세로 교체"),
        ("확인된 INPUT 오류", "공통", "패시브 VFX가 런타임 적용처럼 오인될 수 있음", "기존 제작 범위는 보존하되 REFERENCE_VFX·자동 반입 금지로 명시"),
        ("확인된 INPUT 오류", "공통", "Style corpus의 몬스터·캐릭터 본체/장면 RUID가 효과 레퍼런스와 같은 우선순위", f"MONSTER_CHARACTER {style_counts['ROLE_MONSTER_CHARACTER']}개와 SCENE {style_counts['ROLE_SCENE']}개를 EXCLUDE_STYLE로 분리"),
        ("확인된 사실", "AREA 01~20", "99개 MONSTER_IMAGE를 4장 contact sheet로 독립 시각 대조", "잘못된 개체·스타일 이미지 혼입 0건; 원본 교체 0건, audit-previews/monsters에 근거 보존"),
        ("기존 감사 판단 정정", "area_01/area_03", "방 배치의 히어로·보우마스터가 INPUT 누락처럼 보일 수 있음", "drop_skill_id가 없는 히든 직업 보스라 포획 스킬 아트 INPUT 대상 아님"),
        ("게임 데이터 또는 기획 판단 필요", "공통", "작업 트리에서 SkillTable.csv/.userdataset 삭제", "복구·수정하지 않고 HEAD 및 AREA00 승인 런타임 증거로 교차검증; 관련 불확실성 기록"),
        ("근거 부족", "공통", "기존 raw 다운로드/cache/selected frame 기록 부재", "RUID·모델 경로·현재 PNG SHA/캔버스/alpha는 기록, 선택 frame index는 미확인"),
        ("근거 부족", "공통", "요청에 명시된 감사 3개 파일을 프로젝트/첨부 저장소에서 찾지 못함", "감사 주장을 적용하지 않고 현재 파일·코드로 독립 감사"),
    ]
    findings += [(x["category"], x["area_id"], x["item"], x["action"]) for x in additional]
    finding_lines = ["# INPUT V2 ADDITIONAL FINDINGS", "", "| 구분 | 범위 | 발견·근거 | 영향/처리 |", "|---|---|---|---|"]
    for cat, scope, item, action in findings:
        finding_lines.append(f"| {cat} | {scope} | {item} | {action} |")
    finding_lines += ["", "## Area별 상태", "", "| Area | 수정 | 추가 발견 | 원본 교체 | 기획 변경 | 미확인·충돌 | 상태 | ZIP |", "|---|---|---|---:|---|---|---|---|"]
    for r in area_results:
        finding_lines.append(f"| {r['area_id']} | {'; '.join(r['changes'])} | {'; '.join(r['findings']) or '없음'} | {r['monster_image_replacements']} | 없음 | {'; '.join(r['unresolved']) or '없음'} | {r['status']} | `{r.get('zip_path','')}` |")
    (OUT / "INPUT_V2_ADDITIONAL_FINDINGS.md").write_text("\n".join(finding_lines) + "\n", encoding="utf-8", newline="\n")

    summary = {
        "areas": len(area_results), "monster_placements": sum(r.get("monster_count", 0) for r in area_results),
        "ready": sum(r["status"] == "READY" for r in area_results), "blocked": sum(r["status"] == "BLOCKED" for r in area_results),
        "zip_count": len(list(OUT.glob("AREA_*_IMAGES_INPUT_V2.zip"))), "area06_created": (OUT / "AREA_06_IMAGES_INPUT_V2.zip").exists(),
        "area00_unchanged": area00_unchanged, "game_data_unchanged": game_unchanged,
        "style_counts": dict(style_counts), "skill_source": skill_source,
    }
    (OUT / "INPUT_V2_VALIDATION.json").write_text(json.dumps({"summary": summary, "areas": area_results, "zip_validation": validation_rows}, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
