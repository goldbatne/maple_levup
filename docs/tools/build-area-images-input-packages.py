from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "RootDesk" / "MyDesk" / "GameData"
OUT = ROOT / "docs" / "art" / "images-input-packages"
CACHE = OUT / "_cache"
RAW = CACHE / "raw"
COMMON = CACHE / "global_skill_style_library"
STAGE = CACHE / "stage"
REVIEW_CSV = ROOT / "docs" / "design" / "monster-skill-master" / "MONSTER_SKILL_REVIEW.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def walk_json_sprite(node) -> str:
    if isinstance(node, dict):
        if node.get("Name") == "SpriteRUID" and isinstance(node.get("Value"), str) and node["Value"]:
            return node["Value"]
        for value in node.values():
            found = walk_json_sprite(value)
            if found:
                return found
    elif isinstance(node, list):
        for value in node:
            found = walk_json_sprite(value)
            if found:
                return found
    return ""


def model_ruids() -> dict[str, str]:
    result = {}
    base = ROOT / "RootDesk" / "MyDesk" / "Models" / "Monsters"
    for p in base.rglob("*.model"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        model_id = str(obj.get("EntryKey", "")).removeprefix("model://")
        if model_id and model_id not in result:
            result[model_id] = walk_json_sprite(obj)
    return result


def safe_name(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value.strip())
    value = re.sub(r"\s+", "_", value)
    return value[:80] or "unnamed"


def split_pipe(value: str) -> list[str]:
    return [v.strip() for v in str(value or "").split("|") if v.strip()]


def number(value: str, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


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
        max_count = int(balance.get("skill_stack_max", 5))
        maximum = first + extra * (max_count - 1)
        return f"보유만 해도 {skill.get('passive_stat') or skill.get('scaling_stat')} +{first:g}; 중복 1장당 +{extra:g}, {max_count}장 최대 +{maximum:g}"
    if kind == "버프":
        return f"자신에게 {number(skill.get('duration')):g}초 동안 피해 {number(skill.get('effect_value')) * 100:g}% 감소"
    target = "단일 대상"
    if skill.get("target_mode") == "area":
        target = f"반경 {number(skill.get('range')):g} 범위"
        if number(skill.get("max_targets")) > 0:
            target += f" 최대 {int(number(skill.get('max_targets')))}대상"
        else:
            target += " 대상 제한 없음"
    elif number(skill.get("max_targets")) > 1:
        target = f"최대 {int(number(skill.get('max_targets')))}대상"
    base = number(skill.get("coefficient"))
    max_scale = 1 + balance.get("skill_stack_bonus", 0.2) * (balance.get("skill_stack_max", 5) - 1)
    text = f"{skill.get('scaling_stat')} 계수 {base:g}로 {target} 피해; {number(skill.get('cooldown')):g}초 재사용"
    if max_scale > 1:
        text += f"; 5장 보유 시 계수 ×{max_scale:g}"
    if number(skill.get("dash_distance")) > 0:
        text += f"; {number(skill.get('dash_distance')):g} 거리 돌진"
    return text


def motion_summary(skill: dict[str, str]) -> str:
    if skill_type(skill) == "패시브":
        return "현행 런타임 VFX 없음; 인벤토리/스킬 UI 아이콘으로만 표시"
    layers = split_pipe(skill.get("layer_ruids", ""))
    types = split_pipe(skill.get("layer_types", ""))
    styles = split_pipe(skill.get("layer_styles", ""))
    delays = split_pipe(skill.get("layer_delays", ""))
    durations = split_pipe(skill.get("layer_durations", ""))
    text = []
    if layers:
        text.append(f"layer_ruids {len(layers)}개")
        if types:
            text.append("타입 " + "/".join(types))
        if styles:
            text.append("스타일 " + "/".join(styles))
        if delays:
            text.append("지연 " + "/".join(delays) + "초")
        if durations:
            text.append("지속 " + "/".join(durations) + "초")
    elif skill.get("effect_ruid"):
        if skill.get("effect_style"):
            text.append(f"Sprite {skill['effect_ruid']}를 {skill['effect_style']} 방식으로 재생")
        else:
            text.append(f"AnimationClip {skill['effect_ruid']}를 시전자 기준 재생")
    if skill.get("projectile_ruid"):
        text.append(f"투사체 {skill['projectile_ruid']}가 목표 방향으로 이동")
    if number(skill.get("dash_distance")) > 0:
        text.append("시전자가 목표 방향으로 돌진")
    return "; ".join(text) if text else "현행 연출 RUID 없음"


AREA_PALETTES = {
    "area_00": ("초원 연두 #79B84A", "항구 하늘색 #7CC7E8"),
    "area_01": ("숲 초록 #5FAE45", "버섯 주황 #E78A3B"),
    "area_02": ("적갈색 #A94F36", "암석 황토 #D09A55"),
    "area_03": ("엘리니아 청록 #4EC7A2", "요정 보라 #A977D6"),
    "area_04": ("커닝 남청 #394B73", "네온 청록 #39B9B0"),
    "area_05": ("바닷물 청록 #34AFC5", "모래 금색 #E6C46A"),
    "area_07": ("동굴 이끼 #597B3A", "용암 주황 #E36B32"),
    "area_08": ("하늘 파랑 #72BDEB", "별빛 금색 #F3D36A"),
    "area_09": ("빙설 하늘색 #A8DEF2", "빙정 남색 #4F79A8"),
    "area_10": ("심해 남청 #174E78", "산호 청록 #42C8C2"),
    "area_11": ("에오스 청회색 #6C86A8", "태엽 황동 #C89A48"),
    "area_12": ("장난감 빨강 #D95F61", "블록 파랑 #5C8FD8"),
    "area_13": ("사막 금색 #D8AE58", "오아시스 청록 #36AFA2"),
    "area_14": ("연금 청록 #48A58C", "시약 자주 #A95B95"),
    "area_15": ("천도 분홍 #E990A7", "무릉 옥색 #64A982"),
    "area_16": ("미나르 수풀 #3F8956", "용족 청색 #547CC3"),
    "area_17": ("기억 청색 #668DB8", "시간 금색 #D6B65F"),
    "area_18": ("기지 강철 #687782", "외계 보라 #8C6BC0"),
    "area_19": ("타락 자주 #5D3A72", "여제 청색 #3F73A8"),
    "area_20": ("황혼 주황 #B75C38", "잿빛 흑색 #4A4748"),
}


def visual_motif(skill_name: str) -> str:
    rules = [
        (("화염", "용염", "불", "이프리트"), "불꽃 혀, 뜨거운 코어, 재와 불티"),
        (("빙", "눈", "설", "차가운"), "서리 결정, 얼음 파편, 차가운 김"),
        (("물", "파도", "기포", "먹물", "심해"), "유체 곡선, 물방울, 흰 포말"),
        (("포자", "버섯"), "둥근 포자 입자와 탄성 있는 구름 덩어리"),
        (("뿌리", "고목", "밑동", "목인", "짚"), "나뭇결, 뿌리 갈래, 마른 섬유 파편"),
        (("암석", "돌", "골렘", "지진", "석"), "각진 암석 조각, 분진, 지면 균열"),
        (("뼈", "망령", "원혼", "어둠", "그림자", "심연"), "검은 외곽, 보랏빛 중간톤, 창백한 영혼 코어"),
        (("별", "월광", "태양", "여신"), "별가루, 초승달/광륜, 밝은 중심광"),
        (("태엽", "시간", "크로노스", "타이머", "회로"), "시계 눈금, 기어 파편, 시간 잔상"),
        (("모래", "사막", "선인장"), "모래 띠, 사암 파편, 건조한 바람 꼬리"),
        (("연금", "플라스크", "산성", "미스릴", "융합"), "시약 방울, 연금 문양, 금속/유리 파편"),
        (("광선", "레이저", "중력", "에너지", "외계", "기계"), "정돈된 에너지 링, 광선 코어, 전자 파편"),
        (("기사", "여제", "뇌전", "바람"), "기사단 문양을 직접 복제하지 않은 속성 궤적과 날카로운 타격광"),
    ]
    for keys, text in rules:
        if any(k in skill_name for k in keys):
            return text
    return f"확정 스킬명 ‘{skill_name}’의 핵심 명사를 추상 VFX 소재로 번역; 몬스터 본체는 넣지 않음"


def profile_for(level: int, kind: str, boss: bool, target_mode: str) -> dict[str, str | int | float]:
    if kind == "패시브":
        return {"id": "PASSIVE_ICON_MOTIF", "frames": 6, "size": 256, "fps": 10, "occupancy": "작음(캐릭터 몸통의 0.5~0.8배)", "density": "낮음"}
    if kind == "버프":
        return {"id": "BUFF_SELF", "frames": 8, "size": 256, "fps": 10, "occupancy": "중소형(캐릭터 중심 0.8~1.2배)", "density": "낮음~중간"}
    if boss:
        return {"id": "BOSS_ACTIVE", "frames": 12, "size": 512, "fps": 12.5, "occupancy": "큼(캐릭터 2~3배, 화면을 가리지 않음)", "density": "높음"}
    if level <= 40 and target_mode != "area":
        return {"id": "LOW_ACTIVE", "frames": 8, "size": 256, "fps": 10, "occupancy": "작음(캐릭터 0.7~1.1배)", "density": "낮음"}
    return {"id": "MID_AREA_ACTIVE", "frames": 8, "size": 384, "fps": 10, "occupancy": "중간(캐릭터 1.2~2배)", "density": "중간" if level < 150 else "중간~높음"}


def representative_png(src: Path, dst: Path, remove_solid_edge_background: bool = False) -> dict:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        frames = []
        n = getattr(im, "n_frames", 1)
        for i in range(n):
            im.seek(i)
            rgba = im.convert("RGBA")
            alpha = rgba.getchannel("A")
            bbox = alpha.getbbox()
            score = 0 if bbox is None else (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) + i / max(1, n)
            frames.append((score, i, rgba.copy()))
        _, selected, rgba = max(frames, key=lambda x: x[0])
        if remove_solid_edge_background and rgba.getchannel("A").getextrema() == (255, 255):
            corners = [(0, 0), (rgba.width - 1, 0), (0, rgba.height - 1), (rgba.width - 1, rgba.height - 1)]
            corner_colors = [rgba.getpixel(p) for p in corners]
            base = corner_colors[0]
            if all(max(abs(c[i] - base[i]) for i in range(3)) <= 12 for c in corner_colors):
                for point, color in zip(corners, corner_colors):
                    ImageDraw.floodfill(rgba, point, (color[0], color[1], color[2], 0), thresh=18)
        rgba.save(dst, "PNG", optimize=True)
        a = rgba.getchannel("A")
        lo, hi = a.getextrema()
        bbox = a.getbbox()
        return {"width": rgba.width, "height": rgba.height, "frames": n, "selected_frame": selected, "alpha_min": lo, "alpha_max": hi, "alpha_bbox": bbox}


LOCAL_FALLBACKS = {
    "518cc119c1c04b8797090175d9f015f2": "skill-snail-tackle.svg",
    "73c1bdafcb7e42bc8db0041883226449": "skill-blueshell-guard.svg",
    "6923ce8064e4445d8e63176645943fb1": "skill-spore-spray.svg",
    "0b09a6a325c54caca2282859ae624b22": "skill-mushmom-stomp.svg",
    "cba9471e009f46ee9c786f31d29c3848": "skill-rock-throw.svg",
    "0928f98bbd114efc935696c1200c9d39": "skill-horn-gore.svg",
    "b03001aaa4cf4dfe82d34a48c58cb342": "skill-axe-swing.svg",
    "0fbbe12552664c5f87944ff56a630178": "skill-dark-root.svg",
    "b656b6744e204375a345782b5119aea2": "skill-boar-charge.svg",
    "da712fe9654b4ea2940cee669043bceb": "skill-iron-hide.svg",
    "637abac61bd14f788b157d6aaf1fa08f": "skill-bone-grave.svg",
    "f960bb921fb44bea91c95ea6b95f1d85": "skill-fire-burst.svg",
    "383249b0f9254764aa758b1bcc9bfee9": "skill-earth-rend.svg",
    "72d1dd0939714240bddc0b6865eb93ce": "skill-slime-body.svg",
    "5f5ebe88b8f2426195c793b3440012e4": "skill-fairy-dust.svg",
    "8061aa7a332b4e7ba783b3cd582ebb4b": "skill-stump-bark.svg",
    "572a7a12dcb449bcb0582fc2ccf5be07": "skill-bubble-burst.svg",
    "c07ed26000af460a8438a3486e16f3ec": "skill-dark-grip.svg",
}


def ensure_local_fallback(ruid: str, dst: Path) -> bool:
    if ruid == "74cd5784067849bf865c80b2f2ebf795":
        src = ROOT / "docs" / "art" / "pilot-snail-images25" / "output" / "frames" / "snail_dew_trail_f04.png"
        if src.exists():
            shutil.copy2(src, dst)
            return True
        return False
    name = LOCAL_FALLBACKS.get(ruid)
    if not name:
        return False
    src = ROOT / "docs" / "art" / "skill-icons" / name
    rasterizer = ROOT / "docs" / "art" / "skill-icons" / "rasterize.py"
    if not src.exists() or not rasterizer.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(rasterizer), str(src), str(dst), "2"], check=True, capture_output=True, text=True)
    return dst.exists()


def resource_preview(ruid: str, metadata: dict, dst: Path, transparent_monster_background: bool = False) -> tuple[bool, dict, str]:
    item = metadata.get(ruid, {})
    dl = item.get("_download", {})
    rel = dl.get("file")
    if rel:
        src = CACHE / rel
        if src.exists():
            try:
                info = representative_png(src, dst, transparent_monster_background)
                return True, info, "MSW 공식 리소스 검색 API thumbnail"
            except Exception as e:
                return False, {"error": str(e)}, "MSW thumbnail 변환 실패"
    if ensure_local_fallback(ruid, dst):
        with Image.open(dst) as im:
            rgba = im.convert("RGBA")
            rgba.save(dst, "PNG", optimize=True)
            a = rgba.getchannel("A")
            return True, {"width": rgba.width, "height": rgba.height, "frames": 1, "selected_frame": 0, "alpha_min": a.getextrema()[0], "alpha_max": a.getextrema()[1], "alpha_bbox": a.getbbox()}, "프로젝트 보존 원본/반입 프레임"
    return False, {}, "미확보"


def style_priority(uses: list[dict], ruid: str) -> tuple[str, str, str]:
    search_notes = " ".join(u.get("skill_name", "") for u in uses if u.get("field") == "supplementary_search")
    if "6차" in search_notes or "HEXA" in search_notes:
        return "RECENT_SECONDARY", "6차/HEXA 의미 검색 후보; 정확한 스킬명·출시일 미확인", "LOW"
    skill_ids = {u.get("skill_id", "") for u in uses}
    if any(x.startswith("s_hero_") or x.startswith("s_bow_") for x in skill_ids):
        return "LEGACY_REFERENCE", "프로젝트 T16-3a의 모험가 계보 자료; 자산 자체 개정일 미확인", "MEDIUM"
    if ruid in LOCAL_FALLBACKS:
        return "LEGACY_REFERENCE", "프로젝트 T20/T32/T37 직접 제작 아이콘 기록", "HIGH_PROJECT_ONLY"
    return "UNKNOWN", "리소스 API에 출시 시기 메타데이터 없음", "NONE"


def analyze_png(path: Path) -> dict:
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        pixels = list(rgba.getdata())
        visible = [p for p in pixels if p[3] > 16]
        if not visible:
            return {"dominant": "미확보", "coverage": 0, "dark": 0, "mid": 0, "bright": 0}
        coverage = len(visible) / len(pixels)
        # Objective color estimate: average of saturated/visible pixels.
        sat = sorted(visible, key=lambda p: max(p[:3]) - min(p[:3]), reverse=True)[: max(1, len(visible) // 3)]
        r = round(sum(p[0] for p in sat) / len(sat)); g = round(sum(p[1] for p in sat) / len(sat)); b = round(sum(p[2] for p in sat) / len(sat))
        lum = [(p[0] * 0.2126 + p[1] * 0.7152 + p[2] * 0.0722) for p in visible]
        return {
            "dominant": f"#{r:02X}{g:02X}{b:02X}", "coverage": coverage,
            "dark": sum(v < 85 for v in lum) / len(lum),
            "mid": sum(85 <= v < 190 for v in lum) / len(lum),
            "bright": sum(v >= 190 for v in lum) / len(lum),
        }


def effect_family(uses: list[dict]) -> str:
    fields = {u.get("field", "") for u in uses}
    if fields == {"icon_ruid"}:
        return "icon"
    names = " ".join(u.get("skill_name", "") for u in uses)
    for keys, family in [
        (("돌진", "맹진"), "dash"), (("광선", "레이저"), "beam"), (("폭발", "충격", "지진"), "impact/explosion"),
        (("파동", "폭풍", "눈보라"), "wave/area"), (("탄환", "구슬", "투척", "포격", "숨결"), "projectile"),
        (("피부", "껍질", "외피", "갑주", "완충"), "buff/passive"),
    ]:
        if any(k in names for k in keys):
            return family
    if "projectile_ruid" in fields:
        return "projectile"
    if "layer_ruids" in fields or "effect_ruid" in fields:
        return "layered VFX"
    return "mixed/unknown"


def build_style_library(metadata: dict, uses_map: dict) -> tuple[list[dict], Counter]:
    if COMMON.exists():
        shutil.rmtree(COMMON)
    (COMMON / "skills").mkdir(parents=True, exist_ok=True)
    (COMMON / "summary").mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, ruid in enumerate(sorted(uses_map), 1):
        uses = [u for u in uses_map[ruid] if u.get("kind") == "style"]
        if not uses:
            continue
        item = metadata.get(ruid, {})
        names = item.get("names") or {}
        display = (names.get("ko") or names.get("en") or [item.get("dname") or uses[0].get("skill_name") or ruid])[0]
        folder = COMMON / "skills" / f"{len(rows)+1:04d}_{safe_name(display)}"
        folder.mkdir(parents=True, exist_ok=True)
        ok, png_info, source = resource_preview(ruid, metadata, folder / "preview.png")
        priority, era, confidence = style_priority(uses, ruid)
        analysis = analyze_png(folder / "preview.png") if ok else {"dominant": "미확보", "coverage": 0, "dark": 0, "mid": 0, "bright": 0}
        width = png_info.get("width", number((item.get("payload") or {}).get("width")))
        height = png_info.get("height", number((item.get("payload") or {}).get("height")))
        occupancy = "small" if max(width or 0, height or 0) <= 128 else "medium" if max(width or 0, height or 0) <= 512 else "large"
        density = "low" if analysis["coverage"] < 0.18 else "medium" if analysis["coverage"] < 0.45 else "high"
        frame_count = len((item.get("payload") or {}).get("frames") or []) or png_info.get("frames", 1)
        row = {
            "index": len(rows) + 1,
            "skill_resource_name": display,
            "RUID": ruid,
            "source": source,
            "known_era_version_date": era,
            "chronology_confidence": confidence,
            "style_priority": priority,
            "effect_family": effect_family(uses),
            "visual_density": density,
            "screen_occupancy": occupancy,
            "color_structure": f"대표색 {analysis['dominant']}; dark {analysis['dark']:.0%}/mid {analysis['mid']:.0%}/bright {analysis['bright']:.0%}",
            "hit_treatment": "개별 프리뷰에서 확인; 기능 복제 금지",
            "trail_treatment": "개별 프리뷰에서 확인; 미표현일 수 있음",
            "fragment_treatment": "개별 프리뷰에서 확인; 미표현일 수 있음",
            "animation_rhythm": f"메타데이터 프레임 {frame_count}개; 실제 지연값 미확보",
            "icon_usefulness": "높음" if all(u.get("field") == "icon_ruid" for u in uses) else "보조",
            "preview_status": "확보" if ok else "미확보",
            "notes": "; ".join(sorted({f"{u.get('skill_id') or '-'}:{u.get('skill_name')}:{u.get('field')}" for u in uses})),
        }
        rows.append(row)
        (folder / "ruid.txt").write_text(ruid + "\n", encoding="utf-8")
        (folder / "info.md").write_text(
            f"# {display}\n\n- RUID: `{ruid}`\n- 출처: {source}\n- 스타일 우선순위: **{priority}**\n- 시기 근거: {era}\n- 시기 확신도: {confidence}\n- 효과 계열: {row['effect_family']}\n- 프리뷰: {'확보' if ok else '미확보'}\n- 사용 연결: {row['notes']}\n\n이 자료는 **시각 문법 분석용**이며 기능·무기·실루엣 복제용이 아니다.\n",
            encoding="utf-8",
        )

    columns = list(rows[0].keys())
    write_csv(COMMON / "STYLE_INDEX.csv", rows, columns)
    table = "\n".join("| " + " | ".join(str(r[c]).replace("|", "\\|") for c in columns) + " |" for r in rows)
    (COMMON / "STYLE_INDEX.md").write_text(
        "# Global Skill Style Library Index\n\n"
        "현재 SkillTable이 참조하는 모든 고유 시각 RUID와 공식 MSW 검색 보조 후보를 합친 코퍼스다. 시기 메타데이터가 없으면 UNKNOWN으로 유지했다.\n\n"
        "| " + " | ".join(columns) + " |\n| " + " | ".join("---" for _ in columns) + " |\n" + table + "\n",
        encoding="utf-8",
    )
    counts = Counter(r["style_priority"] for r in rows)
    (COMMON / "summary" / "STYLE_ATLAS.md").write_text(
        f"""# 최신 문법 우선 Global Style Atlas

## 코퍼스 범위

- 총 {len(rows)}개 고유 RUID. 현재 SkillTable의 icon/effect/projectile/layer RUID 전체와 공식 검색 보조 후보를 포함한다.
- RECENT_PRIMARY {counts['RECENT_PRIMARY']} / RECENT_SECONDARY {counts['RECENT_SECONDARY']} / LEGACY_REFERENCE {counts['LEGACY_REFERENCE']} / UNKNOWN {counts['UNKNOWN']} / EXCLUDE_STYLE {counts['EXCLUDE_STYLE']}.
- 정확한 출시일이 없는 리소스를 최신이라고 단정하지 않았다. `RECENT_SECONDARY`는 6차/HEXA 의미 검색으로 찾은 후보이며 확신도가 낮다. `RECENT_PRIMARY`는 정확한 근거가 없어 비워 두었다.

## 적용 우선순위

1. WHAT은 각 몬스터 GENERATION_SPEC의 확정 이름·타입·효과·동작이다.
2. HOW는 코퍼스 전체를 보되 RECENT_PRIMARY → RECENT_SECONDARY → UNKNOWN → LEGACY_REFERENCE 순으로 비교한다.
3. 최신 후보에서 어두운 외곽, 중간톤 형상, 밝은 코어, 발광·반투명 층, 절정 타격광, 자연스러운 fade를 참고한다.
4. 레거시는 저레벨 규모, 단순 실루엣, 한눈에 읽히는 고전 모티브에만 참고한다.
5. 기존 무기·캐릭터·메커니즘·실루엣을 직접 복제하지 않는다.

## 프레임 리듬

- 준비 10~20%: 작은 씨앗/윤곽. 빈 프레임 금지.
- 상승 30~40%: 주형 확대, 잔상과 보조 입자 증가.
- 절정 20~30%: 가장 밝은 코어와 타격 플래시. 한 프레임에만 과밀하게 몰지 않는다.
- 소멸 20~30%: 형상 분해, 파편 감속, 알파 fade. 갑작스러운 삭제 금지.

## 레벨·체급별 스케일

- 저레벨 일반몹: 현대적 명암 구조를 쓰되 작은 점유율, 1개 핵심 형상, 제한된 파편.
- 중레벨: 실루엣을 유지하면서 타격 플래시·잔상·보조 입자를 분명히 한다.
- 고레벨: 절정 프레임과 반투명 보조층을 강화하되 플레이 공간을 가리지 않는다.
- 보스: 가장 높은 점유율과 레이어 밀도를 허용하되 몬스터 본체나 플레이어 직업 스킬을 복제하지 않는다.
- 버프: 시전자 중심의 닫힌 형상, 외곽→코어→소멸 순서.
- 패시브: 아이콘이 주 결과다. 별도 VFX는 런타임 미적용 참고 모티브로만 만든다.

## 아이콘 문법

- 256×256 RGBA, 투명 배경, 한 개의 강한 실루엣, 작은 크기에서도 구별되는 명암.
- 외곽은 어둡게, 핵심 모티브는 중간톤, 효과의 정체를 밝은 코어로 고정한다.
- 글자·숫자·UI 프레임·몬스터 본체·체커보드 배경을 넣지 않는다.
""",
        encoding="utf-8",
    )
    return rows, counts


def area_ref(area_id: str, dst: Path) -> str:
    sources = {
        "area_00": ROOT / "docs/art/pilot-snail-images25/input/REF_05_AREA00_BACKGROUND.png",
        "area_04": ROOT / "docs/art/tiles/kerning",
        "area_05": ROOT / "docs/art/tiles/nautilus",
        "area_07": ROOT / "docs/art/tiles/t64/sleepywood",
        "area_08": ROOT / "docs/art/tiles/t64/orbis",
        "area_09": ROOT / "docs/art/tiles/t64/elnath",
        "area_10": ROOT / "docs/art/tiles/t64/aqua",
        "area_11": ROOT / "docs/art/tiles/t65/luduslake",
        "area_12": ROOT / "docs/art/tiles/t65/ludibrium",
        "area_13": ROOT / "docs/art/tiles/t65/nihal",
        "area_14": ROOT / "docs/art/tiles/t65/magatia",
        "area_15": ROOT / "docs/art/tiles/t67/mulung",
        "area_16": ROOT / "docs/art/tiles/t67/minar",
        "area_17": ROOT / "docs/art/tiles/t67/temple",
        "area_18": ROOT / "docs/art/tiles/t67/omega",
        "area_19": ROOT / "docs/art/tiles/t68/future",
        "area_20": ROOT / "docs/art/tiles/t68/twilight",
    }
    src = sources.get(area_id)
    dst.mkdir(parents=True, exist_ok=True)
    if src is None or not src.exists():
        (dst / "AREA_REF_STATUS.md").write_text("# Area 분위기 자료\n\n- 상태: **미확보**\n- 몬스터 원본과 Area 팔레트/설명만 사용한다. 이 누락 때문에 전체 생성을 중단하지 않는다.\n", encoding="utf-8")
        return "미확보"
    if src.is_file():
        shutil.copy2(src, dst / "AREA_REFERENCE.png")
        (dst / "AREA_REF_STATUS.md").write_text(f"# Area 분위기 자료\n\n- 상태: 확보\n- 프로젝트 원본: `{src.relative_to(ROOT).as_posix()}`\n- 용도: 색감·배경 대비 참고만 사용. 배경 자체를 VFX에 그리지 않는다.\n", encoding="utf-8")
        return "확보"
    images = sorted(src.glob("*.png"))
    if not images:
        (dst / "AREA_REF_STATUS.md").write_text("# Area 분위기 자료\n\n- 상태: **미확보**\n", encoding="utf-8")
        return "미확보"
    thumbs = []
    for p in images[:8]:
        with Image.open(p) as im:
            rgba = im.convert("RGBA")
            rgba.thumbnail((192, 192), Image.Resampling.NEAREST)
            thumbs.append((p.name, rgba.copy()))
    cols = min(4, len(thumbs)); rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGBA", (cols * 192, rows * 192), (0, 0, 0, 0))
    for i, (_, im) in enumerate(thumbs):
        x = (i % cols) * 192 + (192 - im.width) // 2; y = (i // cols) * 192 + (192 - im.height) // 2
        sheet.alpha_composite(im, (x, y))
    sheet.save(dst / "AREA_REFERENCE.png", "PNG", optimize=True)
    names = ", ".join(p.name for p in images[:8])
    (dst / "AREA_REF_STATUS.md").write_text(f"# Area 분위기 자료\n\n- 상태: 확보\n- 프로젝트 타일 원본: `{src.relative_to(ROOT).as_posix()}`\n- 합성 대상: {names}\n- 용도: 색감·바닥 대비 참고만 사용. 타일을 VFX에 직접 복제하지 않는다.\n", encoding="utf-8")
    return "확보"


def build_monster_docs(folder: Path, seq: int, monster: dict, skill: dict, area: dict, boss: bool, review: dict, balance: dict, image_status: str, image_info: dict) -> None:
    kind = skill_type(skill)
    level = int(number(monster.get("level")))
    profile = profile_for(level, kind, boss, skill.get("target_mode", ""))
    primary, secondary = AREA_PALETTES.get(area["id"], ("몬스터 원본 대표색", "지역 보조색"))
    origin = "시전자 중심"
    direction = "중앙에서 바깥으로"
    targeting = "자기 자신"
    if kind == "패시브":
        origin, direction, targeting = "아이콘 중심", "고정 실루엣", "런타임 대상 없음"
    elif skill.get("target_mode") == "single":
        origin, direction, targeting = "시전자 앞쪽", "오른쪽 기준 진행(FlipX 고려)", "단일 대상"
    elif skill.get("target_mode") == "area":
        origin, direction = "시전자 또는 충돌점 중심", "중앙에서 방사/전방 확산"
        targeting = "범위" if not number(skill.get("max_targets")) else f"다중 대상 최대 {int(number(skill.get('max_targets')))}"
    if skill.get("projectile_ruid"):
        origin, direction = "시전자 앞쪽", "오른쪽으로 투사체 이동(FlipX 고려)"
    effect = actual_effect(skill, balance)
    motion = motion_summary(skill)
    lore = review.get("원작 몬스터/지역 설정과의 연결 근거", "현재 Area/MonsterTable 배치와 확정 이름을 기준으로 함")
    cautions = ["확정 스킬명·타입·효과·동작을 바꾸지 않는다.", "몬스터 본체를 VFX 안에 직접 그리지 않는다.", "기존 플레이어 스킬의 무기·캐릭터·실루엣을 복제하지 않는다."]
    if "수류탄" in skill.get("name", ""):
        cautions.append("‘수류탄’은 압축된 물의 흐름(水流) 탄환 의미로 해석하고 현대식 손폭탄을 그리지 않는다.")
    if "석면" in skill.get("name", ""):
        cautions.append("‘석면’은 현재 확정 문자열을 유지하되 asbestos 섬유를 그리지 말고 스톤마스크/발굴지의 돌 표면 모티브만 사용한다.")
    if kind == "패시브":
        cautions.append("현행 패시브에는 런타임 VFX가 없다. VFX 결과는 비전투 참고 모티브로 표시하고 자동 반입하지 않는다.")
    stages = "준비(핵심 형상 출현) → 상승(형상 확대·보조 입자) → 절정(밝은 코어/타격광) → 소멸(형상 분해·알파 fade)"
    spec = f"""# GENERATION SPEC — {monster['name']} / {skill['name']}

## 확정 데이터

- 작업 순번: {seq:03d}
- 레벨: {level}
- Area: `{area['id']}` / {area['name']}
- monster_id: `{monster['id']}`
- 몬스터 이름: {monster['name']}
- monster image RUID: `{monster['image_ruid']}`
- skill_id: `{skill['id']}`
- 최종 스킬 이름: **{skill['name']}**
- 스킬 타입: **{kind}**
- 보스 여부: {'보스' if boss else '일반 몬스터'}
- 실제 현재 효과: {effect}
- 실제 현재 동작: {motion}

## 원작/지역 연결

{lore}

## 시각 번역

- 핵심 소재: {visual_motif(skill['name'])}
- 주 색상: {primary}; 반드시 MONSTER_IMAGE의 실제 대표색과 조화시킬 것
- 보조 색상: {secondary}; 어떤 배경에서도 읽히도록 밝은 코어와 어두운 외곽을 함께 둘 것
- 효과 발생 위치: {origin}
- 진행 방향: {direction}
- 대상 표현: {targeting}
- 화면 점유율: {profile['occupancy']}
- 이펙트 밀도: {profile['density']}
- 시간 흐름: {stages}
- 아이콘 핵심 모티브: 스킬명 ‘{skill['name']}’에서 가장 구별되는 명사 한 개를 중심 실루엣으로 사용

## 출력 프로필

- profile: `{profile['id']}`
- VFX: {profile['frames']} frames, 각 {profile['size']}×{profile['size']} RGBA PNG, 약 {1/float(profile['fps']):.2f} sec/frame
- 동일 캔버스·동일 기준축·우측 기준·one-shot
- ICON: 256×256 RGBA PNG 1장

## 해석 주의

""" + "\n".join(f"- {x}" for x in cautions) + "\n"
    (folder / "GENERATION_SPEC.md").write_text(spec, encoding="utf-8")
    (folder / "MONSTER_INFO.md").write_text(
        f"""# Monster Reference — {monster['name']}

- 작업 순번: {seq:03d}
- level: {level}
- Area: `{area['id']}` / {area['name']}
- monster_id: `{monster['id']}`
- model_id: `{monster['model_id']}`
- image RUID: `{monster['image_ruid']}`
- image status: **{image_status}**
- image format: {image_info.get('width', '미확보')}×{image_info.get('height', '미확보')} RGBA PNG
- alpha range: {image_info.get('alpha_min', '미확보')}~{image_info.get('alpha_max', '미확보')}
- skill_id: `{skill['id']}`
- skill name/type: {skill['name']} / {kind}

MONSTER_IMAGE는 외형·색상·실루엣·부위 특징을 이해하기 위한 레퍼런스다. 최종 VFX에 몬스터 본체를 그대로 넣지 않는다.
""",
        encoding="utf-8",
    )


def master_prompt(area: dict, count: int) -> str:
    return f"""# ChatGPT Images Master Prompt — {area['id']} {area['name']}

첨부된 ZIP 전체를 먼저 분석하세요. 이 ZIP은 `{area['id']}` / **{area['name']}**의 몬스터 {count}종에 대한 확정 입력 패키지입니다.

1. `AREA_MANIFEST`와 모든 `monsters/*/GENERATION_SPEC.md`를 읽으세요.
2. `global_skill_style_library`의 **전체** STYLE_INDEX, STYLE_ATLAS, skills/*/preview.png를 분석하세요. 옛 자료도 제외하지 않되, `RECENT_PRIMARY`를 최우선, `RECENT_SECONDARY`를 다음 우선으로 시각 문법에 반영하세요. UNKNOWN은 보조 비교, LEGACY_REFERENCE는 저레벨 규모와 고전 실루엣 참고에 사용하세요.
3. WHAT(몬스터, 스킬명, 타입, 효과, 동작)은 이미 확정되었습니다. 바꾸거나 재설계하지 마세요. HOW만 메이플스토리/MSW풍 시각 언어로 제작하세요.
4. 최신 스타일에서 어두운 외곽→중간톤 형상→밝은 코어, 발광, 반투명 레이어, 타격 플래시, 잔상, 파편, 에너지 흐름, 준비→상승→절정→소멸, 자연스러운 fade, 프레임 간 형태 변화를 우선 참고하세요.
5. 화면 점유율과 밀도는 각 GENERATION_SPEC의 레벨·체급·보스 여부·출력 프로필을 따르세요. 저레벨 일반몹을 고레벨 플레이어 스킬처럼 과장하지 마세요.
6. 기존 스킬의 무기, 캐릭터, 메커니즘, 고유 실루엣을 직접 복제하지 마세요. 스타일 문법만 참고하세요.
7. 각 몬스터에 대해 VFX 프레임과 ICON을 모두 생성하세요. 패시브 VFX는 현행 런타임 미적용 참고 모티브이며 기능을 추가하지 않습니다.
8. PNG, 실제 alpha 투명 배경, 체커보드 금지, 빈 프레임 금지, 프레임 누락 금지, 동일 캔버스·동일 중심축, 임의 크롭 금지, 우측 기준(FlipX 가능)을 지키세요.
9. VFX에 몬스터 본체, 글자, 숫자, UI, 워터마크를 넣지 마세요.
10. `OUTPUT_NAMING_SPEC.md`와 `OUTPUT_FORMAT_SPEC.md`를 정확히 따르고 가능하면 전체 결과를 `AREA_{area['id'].split('_')[-1]}_IMAGES_OUTPUT.zip`으로 반환하세요.

먼저 누락 파일을 점검한 뒤, 미확보 자료는 해당 GENERATION_SPEC와 확보된 자료로 계속 진행하고 임의의 공식 설정을 만들어내지 마세요.
"""


def output_specs(area_id: str) -> tuple[str, str]:
    num = area_id.split("_")[-1]
    naming = f"""# Output Naming Spec

출력 루트: `AREA_{num}_IMAGES_OUTPUT/`

- 시트형 VFX: `NNN_[monster_id]_[skill_id]_VFX.png`
- 프레임 분리형: `NNN_[monster_id]_[skill_id]_F00.png`, `F01.png` ...
- 아이콘: `NNN_[monster_id]_[skill_id]_ICON.png`
- NNN은 AREA_MANIFEST의 작업 순번 3자리다.
- monster_id와 skill_id를 축약하거나 번역하지 않는다.

구조:

```text
AREA_{num}_IMAGES_OUTPUT/
├─ OUTPUT_MANIFEST.md
├─ OUTPUT_MANIFEST.csv
└─ monsters/
   ├─ 001_[monster_id]_[name]/
   │  ├─ VFX/
   │  ├─ ICON/
   │  └─ RESULT_INFO.md
   └─ ...
```
"""
    fmt = """# Output Format Spec

## 공통

- PNG, RGBA, 실제 alpha 투명 배경. 흰색/검정/체커보드 배경 금지.
- 프레임마다 동일 캔버스, 동일 기준축, 동일 스케일. 임의 크롭/재중앙화 금지.
- 우측 진행 기준으로 제작하고 런타임 FlipX를 고려한다.
- one-shot. 빈 프레임과 누락 프레임 금지.
- ICON은 256×256 RGBA PNG 1장, 글자·숫자·UI 프레임·몬스터 본체 금지.

## 표준 규격군

| Profile | VFX frames | Canvas/frame | Timing | 용도 |
|---|---:|---:|---:|---|
| LOW_ACTIVE | 8 | 256×256 | 0.10s | 저레벨 단일 액티브 |
| MID_AREA_ACTIVE | 8 | 384×384 | 0.10s | 중·고레벨 범위/다중 액티브 |
| BOSS_ACTIVE | 12 | 512×512 | 0.08s | 보스급 액티브 |
| BUFF_SELF | 8 | 256×256 | 0.10s | 자기 중심 버프 |
| PASSIVE_ICON_MOTIF | 6 | 256×256 | 0.10s | 현행 런타임 미적용 참고 모티브 + 아이콘 |

달팽이 파일럿의 8 frames / 0.1 sec / Offset X64 Y0은 LOW_ACTIVE 참고값이다. 모든 스킬에 같은 오프셋을 강제하지 않으며, 각 프레임 내부의 공통 피봇은 반드시 유지한다.
"""
    return naming, fmt


def zip_add_tree(z: zipfile.ZipFile, source: Path, arc_root: str = "") -> None:
    for p in sorted(source.rglob("*")):
        if p.is_file():
            rel = p.relative_to(source).as_posix()
            z.write(p, f"{arc_root}/{rel}".strip("/"))


def main() -> None:
    monsters = read_csv(DATA / "MonsterTable.csv")
    skills = read_csv(DATA / "SkillTable.csv")
    areas = sorted(read_csv(DATA / "AreaTable.csv"), key=lambda x: number(x.get("sort_order")))
    rooms = read_csv(DATA / "RoomTable.csv")
    balance_rows = read_csv(DATA / "GameBalance.csv")
    balance = {r["key"]: number(r.get("value")) for r in balance_rows}
    skill_by_id = {s["id"]: s for s in skills}
    monster_by_id = {m["id"]: m for m in monsters if m.get("drop_skill_id") and number(m.get("level")) <= 200}
    models = model_ruids()
    review = {r["monster_id"]: r for r in read_csv(REVIEW_CSV)} if REVIEW_CSV.exists() else {}
    metadata = json.loads((CACHE / "resource_metadata.json").read_text(encoding="utf-8"))
    uses_map = json.loads((CACHE / "resource_uses.json").read_text(encoding="utf-8"))

    for m in monster_by_id.values():
        m["image_ruid"] = models.get(m.get("model_id", ""), "")

    area_monster_ids = defaultdict(list)
    boss_pairs = set()
    for room in rooms:
        mid = room.get("monster_id", "")
        aid = room.get("area_id", "")
        if aid and mid in monster_by_id and mid not in area_monster_ids[aid]:
            area_monster_ids[aid].append(mid)
        if room.get("room_type") == "boss" and mid:
            boss_pairs.add((aid, mid))
    for aid in area_monster_ids:
        area_monster_ids[aid].sort(key=lambda mid: (number(monster_by_id[mid].get("level")), mid))

    style_rows, style_counts = build_style_library(metadata, uses_map)
    style_missing = sum(r["preview_status"] != "확보" for r in style_rows)

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("AREA_*_IMAGES_INPUT.zip"):
        old.unlink()
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    index_rows = []
    unique_monsters = set()
    total_placements = 0
    total_missing = style_missing

    for order, area in enumerate(areas, 1):
        ids = area_monster_ids.get(area["id"], [])
        unique_monsters.update(ids); total_placements += len(ids)
        levels = [int(number(monster_by_id[mid]["level"])) for mid in ids]
        level_range = f"Lv{min(levels)}~{max(levels)}" if levels else "미확보"
        package_name = f"{area['id'].upper()}_IMAGES_INPUT"
        stage = STAGE / package_name
        monsters_dir = stage / "monsters"
        monsters_dir.mkdir(parents=True)
        manifest_rows = []
        missing = []
        seen_skills = set()

        for seq, mid in enumerate(ids, 1):
            monster = monster_by_id[mid]
            skill = skill_by_id.get(monster["drop_skill_id"])
            folder_name = f"{seq:03d}_{safe_name(mid)}_{safe_name(monster['name'])}"
            folder = monsters_dir / folder_name
            folder.mkdir(parents=True)
            image_ok, image_info, image_source = resource_preview(monster["image_ruid"], metadata, folder / "MONSTER_IMAGE.png", True)
            numbered = f"{seq:03d}_{int(number(monster['level']))}_{safe_name(mid)}_{safe_name(monster['name'])}.png"
            if image_ok:
                shutil.copy2(folder / "MONSTER_IMAGE.png", folder / numbered)
            else:
                missing.append(f"monster image: {mid} / {monster['image_ruid']}")
                (folder / "MONSTER_IMAGE_MISSING.md").write_text(f"# 몬스터 이미지 미확보\n\n- monster_id: `{mid}`\n- RUID: `{monster['image_ruid']}`\n- 후속 작업은 나머지 확정 데이터로 계속한다.\n", encoding="utf-8")
            if skill is None:
                missing.append(f"skill row: {monster['drop_skill_id']}")
                continue
            if skill["id"] in seen_skills:
                missing.append(f"duplicate skill_id in area: {skill['id']}")
            seen_skills.add(skill["id"])
            boss = (area["id"], mid) in boss_pairs
            build_monster_docs(folder, seq, monster, skill, area, boss, review.get(mid, {}), balance, "확보" if image_ok else "미확보", image_info)
            manifest_rows.append({
                "work_order": seq, "level": int(number(monster["level"])), "area_id": area["id"], "area_name": area["name"],
                "monster_id": mid, "monster_name": monster["name"], "monster_image_ruid": monster["image_ruid"],
                "monster_image_status": "확보" if image_ok else "미확보", "skill_id": skill["id"], "skill_name": skill["name"],
                "skill_type": skill_type(skill), "actual_effect": actual_effect(skill, balance), "actual_motion": motion_summary(skill),
                "boss": "Y" if boss else "N", "folder": f"monsters/{folder_name}",
            })

        columns = list(manifest_rows[0].keys()) if manifest_rows else ["work_order","level","area_id","area_name","monster_id","monster_name","monster_image_ruid","monster_image_status","skill_id","skill_name","skill_type","actual_effect","actual_motion","boss","folder"]
        write_csv(stage / "AREA_MANIFEST.csv", manifest_rows, columns)
        md_table = "\n".join("| " + " | ".join(str(r[c]).replace("|", "\\|") for c in columns) + " |" for r in manifest_rows)
        (stage / "AREA_MANIFEST.md").write_text(
            f"# {area['id']} {area['name']} Manifest\n\n- 처리 순서: {order}\n- 레벨 범위: {level_range}\n- 포획 가능 몬스터: {len(ids)}종\n- 자료 누락: {len(missing)}건\n\n| " + " | ".join(columns) + " |\n| " + " | ".join("---" for _ in columns) + " |\n" + md_table + "\n",
            encoding="utf-8",
        )
        naming, fmt = output_specs(area["id"])
        (stage / "OUTPUT_NAMING_SPEC.md").write_text(naming, encoding="utf-8")
        (stage / "OUTPUT_FORMAT_SPEC.md").write_text(fmt, encoding="utf-8")
        (stage / "CHATGPT_IMAGES_MASTER_PROMPT.md").write_text(master_prompt(area, len(ids)), encoding="utf-8")
        (stage / "README_START_HERE.md").write_text(
            f"""# START HERE — {area['id']} {area['name']}

이 ZIP은 신규 이미지를 직접 포함한 결과물이 아니라 ChatGPT Images에 전달할 **입력 패키지**다.

1. `AREA_MANIFEST.md`에서 대상 {len(ids)}종과 확정 효과를 확인한다.
2. `global_skill_style_library/summary/STYLE_ATLAS.md`와 전체 STYLE_INDEX/preview를 분석한다.
3. `monsters/*/GENERATION_SPEC.md`의 WHAT을 변경하지 않는다.
4. `CHATGPT_IMAGES_MASTER_PROMPT.md`를 그대로 사용한다.
5. 결과는 OUTPUT_NAMING_SPEC/OUTPUT_FORMAT_SPEC를 따른다.

금지: SkillTable 변경, 기능 재설계, Resource Storage 업로드, AnimationClip 생성, 기존 스킬 직접 복제.

누락 목록: {', '.join(missing) if missing else '없음'}
""",
            encoding="utf-8",
        )
        ref_status = area_ref(area["id"], stage / "area_refs")
        total_missing += len(missing) + (1 if ref_status == "미확보" else 0)
        zip_path = OUT / f"{package_name}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
            zip_add_tree(z, stage, package_name)
            zip_add_tree(z, COMMON, f"{package_name}/global_skill_style_library")
        with zipfile.ZipFile(zip_path, "r") as z:
            bad = z.testzip()
            names = set(z.namelist())
            required = {f"{package_name}/README_START_HERE.md", f"{package_name}/CHATGPT_IMAGES_MASTER_PROMPT.md", f"{package_name}/AREA_MANIFEST.md", f"{package_name}/AREA_MANIFEST.csv", f"{package_name}/OUTPUT_NAMING_SPEC.md", f"{package_name}/OUTPUT_FORMAT_SPEC.md", f"{package_name}/global_skill_style_library/STYLE_INDEX.md", f"{package_name}/global_skill_style_library/STYLE_INDEX.csv", f"{package_name}/global_skill_style_library/summary/STYLE_ATLAS.md"}
            validation = "PASS" if bad is None and required.issubset(names) and len(manifest_rows) == len(ids) else "WARN"
            if bad:
                missing.append(f"zip CRC: {bad}")
            if not required.issubset(names):
                missing.append("required file missing")
        index_rows.append({
            "area_order": order, "area_id": area["id"], "area_name": area["name"], "level_range": level_range,
            "monster_count": len(ids), "zip_path": zip_path.relative_to(ROOT).as_posix(), "zip_bytes": zip_path.stat().st_size,
            "missing_materials": len(missing) + (1 if ref_status == "미확보" else 0), "area_ref_status": ref_status, "validation": validation,
        })
        shutil.rmtree(stage)

    index_cols = list(index_rows[0].keys())
    write_csv(OUT / "ALL_AREAS_INDEX.csv", index_rows, index_cols)
    index_table = "\n".join("| " + " | ".join(str(r[c]).replace("|", "\\|") for c in index_cols) + " |" for r in index_rows)
    (OUT / "ALL_AREAS_INDEX.md").write_text(
        f"""# All Areas ChatGPT Images Input Packages

- 기준 데이터: 현재 MonsterTable / SkillTable / AreaTable / RoomTable
- Area: {len(areas)}개
- 생성 ZIP: {len(index_rows)}개
- 고유 포획 가능 몬스터: {len(unique_monsters)}종
- Area 배치 합계(중복 지역 배치 포함): {total_placements}건
- 스타일 라이브러리: {len(style_rows)}개 고유 RUID
- RECENT_PRIMARY {style_counts['RECENT_PRIMARY']} / RECENT_SECONDARY {style_counts['RECENT_SECONDARY']} / LEGACY_REFERENCE {style_counts['LEGACY_REFERENCE']} / UNKNOWN {style_counts['UNKNOWN']} / EXCLUDE_STYLE {style_counts['EXCLUDE_STYLE']}
- 미확보/경고 자료: {total_missing}건

| """ + " | ".join(index_cols) + " |\n| " + " | ".join("---" for _ in index_cols) + " |\n" + index_table + "\n",
        encoding="utf-8",
    )
    summary = {
        "areas": len(areas), "zips": len(index_rows), "unique_monsters": len(unique_monsters), "monster_placements": total_placements,
        "style_resources": len(style_rows), "style_priority": dict(style_counts), "missing_materials": total_missing,
        "validation_pass": sum(r["validation"] == "PASS" for r in index_rows), "validation_warn": sum(r["validation"] != "PASS" for r in index_rows),
    }
    (OUT / "BUILD_VALIDATION_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
