from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "docs/art/output_audit/runs/20260912_145815_content_style"
PREVIOUS = ROOT / "docs/art/output_audit/runs/20260912_143540"
WORK = ROOT / "docs/art/output_audit_work/20260912_143540"


OBSERVED_VISUALS = {
    "m_snail": "초록 이슬방울이 낮은 점액 띠로 길어졌다가 밝은 튐 뒤 작은 방울로 사라짐",
    "m_blue_snail": "푸른 껍질형 반구가 시전자 둘레에서 닫히고 반사광이 돈 뒤 얇은 물고리로 소멸",
    "m_mushroom": "베이지색 포자 덩어리 셋이 둥글게 부풀고 점 입자를 남기며 흩어짐",
    "m_mushmom": "주황 포자핵이 지면에서 버섯갓형 충격파로 크게 솟고 굵은 포자 파편으로 해체",
    "m_horny_mushroom": "상아색 뿔과 짙은 갓 곡선이 반사광과 함께 커졌다가 원형 모티브로 복귀",
    "m_stone_golem": "갈색 암석판이 원형 방패로 맞물리고 틈의 금빛 균열광이 밝아졌다가 풀림",
    "m_axe_stump": "도끼날형 갈색 초승달이 전방을 긁고 나무 파편을 튄 뒤 가는 궤적으로 소멸",
    "m_dark_axe_stump": "검보라 나무 가시와 뿌리형 기운이 중앙에서 솟아 방패 덩어리로 굳었다가 가라앉음",
    "m_wild_boar": "갈색 흙먼지가 낮게 압축되어 전방 충돌광과 파편을 만들고 잔흙으로 흩어짐",
    "m_iron_hog": "회색 철갑판과 금빛 충격선이 겹쳐 단단한 방어 모티브를 만들고 짧게 맥동",
    "m_skeleton_commander": "뼛조각과 긴 뼈가 지면에서 솟아 군집 충격을 만든 뒤 분진과 함께 내려앉음",
    "m_fire_boar": "주황 불꽃 혀가 낮은 전방 파동으로 커지고 불티를 뿌린 뒤 작은 불씨로 소멸",
    "m_stumpy": "가시 박힌 초록 나이테 탄이 네 프레임 동안 국소 광택과 덩굴 맥동만 바꾸며 유지",
    "m_slime": "연두 점액방울이 바닥을 미끄러지며 길게 늘고 충돌 튐 뒤 낮은 점액 자국으로 사라짐",
    "m_dark_stump": "짧은 뿌리가 붙은 갈색 나이테 원판이 닫혀 방패가 되고 중심 반사광 뒤 풀림",
    "m_bubbling": "푸른 물방울들이 투명 구체를 감싸며 부풀고 밝은 막을 만든 뒤 작은 거품으로 감소",
    "m_fairy": "금빛 잎과 별 입자가 연녹색 마력 소용돌이를 만들고 중심광 뒤 가볍게 흩어짐",
    "m_faust": "보라 저주띠와 작은 인형이 마법진 중심에 모여 폭발하고, 투사체는 인형핵 형태로 맥동",
    "m_octopus": "짙은 남보라 먹물방울이 중앙에서 넓은 얼룩으로 터지고 작은 방울로 분해",
    "m_stirge": "붉은 감지점 주위에 남보라 동심 파동이 벌어졌다 줄어드는 저밀도 탐지 표현",
    "m_jr_wraith": "반투명 푸른 손자국이 냉기 원과 함께 선명해지고 가시형 충격 뒤 흐릿해짐",
    "m_wraith": "청록 혼불 꼬리와 작은 불씨가 한 덩어리로 숨 쉬듯 커졌다가 잔불로 줄어듦",
    "m_shade": "검보라 장막 원이 층을 이루며 커져 밝은 심연 중심을 만들고 조각·연기로 해체",
    "m_ribbon_pig": "붉은 리본 매듭에서 분홍 전방 잔상이 터지고 꽃잎형 조각으로 사라짐",
    "m_blue_pig": "푸른 리본 매듭이 둥근 보호 고리와 반사광을 만들며 짧게 수축·팽창",
    "m_starfish": "금빛 별이 청록 물고리 속에서 회전·확대되고 별조각과 물방울로 흩어짐",
    "m_jellyfish": "푸른 젤리 돔이 늘어나고 얼음성 물결과 별조각을 만든 뒤 납작하게 복귀",
    "m_king_clang": "붉은 집게 형상 둘과 푸른 파도가 왕관형 충격 고리를 만들고 거품으로 소멸",
    "m_zombie_mushroom": "갈색 죽은 포자핵에서 탁한 연두 연기와 잎조각이 피었다가 다시 말라든 핵으로 수축",
    "m_copper_drake": "청록 바람선이 청동 비늘 묶음을 감싸고 중심 반사광 뒤 비늘 모티브로 안정",
    "m_drake": "주황 불길이 원형 용염 덩어리로 치솟고 검은 연기와 불티를 남기며 가라앉음",
    "m_wild_kargo": "검보라 그림자 발톱과 가시가 지면에서 전방으로 솟고 먹빛 잔상으로 흐려짐",
    "m_jr_balrog": "붉은 뿔형 화염 고리가 커져 중앙 폭발을 만들고 불씨 원으로 갈라져 소멸",
    "m_tauromacis": "푸른 번개가 금속성 원형 문양에 내려꽂혀 밝은 낙뢰 절정을 만든 뒤 얇은 고리로 잔류",
    "m_star_pixie": "금빛 별과 짧은 청백 꼬리가 CAST에서 형성되고, 투사체는 별핵의 국소 반짝임만 변화",
    "m_jr_cellion": "붉은 별불꽃이 둥글게 부풀고 밝은 적색 코어 뒤 작은 불꽃으로 되돌아감",
    "m_lunar_pixie": "연보라 달조각이 구체를 감싸며 커지고, 투사체는 달구슬 중심의 국소 광택만 맥동",
    "m_luster_pixie": "금빛 태양핵과 날개형 광선이 펼쳐졌다 중심으로 수축하는 비전투 잔상",
    "m_eliza": "초록 잎과 금빛 정원 소용돌이가 넓게 회전해 중심 폭풍광을 만들고 잎조각으로 해체",
    "m_jr_yeti": "주황 온기핵 주위의 푸른 눈송이가 녹듯 줄어드는 짧은 비전투 호흡",
    "m_dark_jr_yeti": "검회색 설분이 낮은 소용돌이로 뭉쳤다가 가는 눈가루 흔적으로 흐려짐",
    "m_hector": "회청색 세 갈래 발톱바람이 전방에서 솟아 굵어지고 짧은 눈가루 궤적으로 소멸",
    "m_white_fang": "푸른 얼음 송곳니 둘이 교차해 결정형 충격을 만들고 작은 파편으로 분리",
    "m_snow_witch": "청백색 굽은 설풍 고리가 여러 층의 눈보라 원통으로 커졌다 눈결정과 함께 꺼짐",
    "m_bubble_fish": "청록 물막이 둥근 거품막으로 닫히고 내부 물방울이 밝아졌다 얇은 막으로 복귀",
    "m_mask_fish": "푸른 가면 눈매와 수면 파문이 나타났다 감지점만 남기고 투명하게 사라짐",
    "m_squid": "검남색 먹물 구름이 여러 방울로 부풀어 중앙을 덮고 회색 먹방울로 분산",
    "m_shark": "물회오리가 이빨 달린 푸른 수류탄을 형성해 튀기며, 투사체는 물방울 광택만 변화",
    "m_pianus": "청록 심해 광선핵이 수면 왕관처럼 솟아 가로 집중광 절정을 만들고 물방울로 감소",
    "m_ratz": "황동 태엽과 은색 끝날이 회전하며 짧은 전방 속도선과 먼지를 남김",
    "m_drumming_bunny": "붉은 북심을 중심으로 금빛 동심 충격륜이 확대됐다 작은 박자점으로 소멸",
    "m_bloctopus": "보라 블록이 청록 격자막 속에서 선명해졌다 반투명 큐브 잔상으로 흐려짐",
    "m_king_bloctopus": "왕관·눈·포신을 가진 분홍 블록퍼스형 탄이 CAST와 PROJECTILE에 반복되고 보라 광선이 부착",
    "m_rombot": "보라 기계핵 주위로 혼돈 고리와 수직 충격선이 겹쳐 커졌다 파편·얇은 원으로 감소",
    "m_brown_teddy": "갈색 봉제 쿠션이 눌려 납작해졌다 탄성 화살표와 솜먼지를 내며 복원",
    "m_toy_trojan": "바퀴·태엽과 눈 달린 목마 머리 조각이 전방 충돌광을 만들고 속도선·별조각으로 해체",
    "m_master_robo": "회색 기어 여러 개가 청록 회로광과 함께 맞물려 돌고 원형 기계핵으로 안정",
    "m_chronos": "검푸른 시간 구체와 시계 파편이 충돌광으로 벌어졌다 작은 파편 궤도로 줄어듦",
    "m_timer": "금빛 시계핵과 청백 시간살이 방사형으로 펼쳐졌다 고리·작은 시계점으로 수축",
    "m_white_sand_rabbit": "밝은 모래 고리가 지면에서 원뿔 송곳으로 솟고 갈색 알갱이와 함께 무너짐",
    "m_scarf_plead": "주황·적갈 목도리 조각이 바람 초승달을 따라 흔들렸다 원래 곡선으로 복귀",
    "m_meercat": "낮은 모래 둔덕이 전방 원뿔로 솟고 큰 모래 파편 뒤 얕은 고리로 가라앉음",
    "m_sand_dwarf": "주황 망치 머리와 붉은 체력광이 짧게 밝아졌다 모래 궤적 속에서 안정",
    "m_deo": "초록 선인장 방패가 모래가시 폭발 중심에서 솟고 금빛 파편 고리로 해체",
    "m_cube_slime": "청록 큐브핵 둘레에 각진 방벽과 작은 큐브 입자가 닫히고 반사광 뒤 유지",
    "m_mithril_mutae": "청회색 미스릴 육각판이 구형 껍질로 맞물리고 청록 코어가 밝아졌다 안정",
    "m_homun": "금속 플라스크가 보라 독무와 거품에 잠겼다가 탁한 연기·방울로 분해",
    "m_roid": "청록 기계 코어가 포신형 광선을 형성하고, 투사체는 금속 탄체의 내부광만 변화",
    "m_chimera": "연두 산성 소용돌이가 밝은 독성 충격으로 터지고, 투사체는 점액 구체의 국소 회전만 변화",
    "m_straw_dummy": "묶인 볏짚 매듭이 금빛 균형 고리 안에서 작게 회전·맥동하는 비전투 표현",
    "m_wooden_dummy": "나무 원통 둘이 갈색 회전 궤적을 만들고 금빛 충격륜 뒤 파편으로 풀림",
    "m_peach_monkey": "분홍 복숭아핵이 잎과 꽃빛 속에서 터지고, 투사체는 복숭아 구체의 국소 광택만 변화",
    "m_blue_flower_serpent": "푸른 꽃비늘 묶음이 물방울과 함께 감겨 커졌다 원래 비늘 코일로 줄어듦",
    "m_tae_roon": "청록 쌍권풍이 서로 감겨 밝은 충돌광을 만들고, 투사체는 두 바람핵의 국소 맥동만 변화",
    "m_harp": "푸른 깃털 한 장과 청백 바람 꼬리가 짧게 부풀었다 가는 깃결로 복귀",
    "m_blood_harp": "붉은 깃털과 원형 문양이 겹쳐 진홍 폭발핵을 만들고 작은 깃조각으로 소멸",
    "m_blue_wyvern": "청백 얼음 숨결과 뾰족한 빙편이 전방에서 폭발하고 눈가루로 감소",
    "m_dark_wyvern": "검은 비늘 조각에 붉은 근맥광이 번졌다 원래 비늘 덩어리로 수축",
    "m_manon": "주황 용화염이 뿔처럼 솟아 큰 불꽃 덩어리를 만들고 불씨·연기로 사라짐",
    "m_memory_monk": "베이지 염주알이 원형 묵상 고리로 모였다 빛알을 남기며 다시 풀림",
    "m_memory_monk_trainee": "금청 기도문양과 날개형 광선이 방사형으로 펼쳐졌다 작은 빛점으로 소멸",
    "m_memory_guardian": "금청 방패 조각이 중앙 문장에 맞물려 닫히고 반사광 뒤 분리",
    "m_chief_memory_guardian": "금청 시간 수호 문양이 네 방향으로 회전·확대됐다 얇은 시간 고리로 사라짐",
    "m_dodo": "검정·금빛 기억 조각이 큰 소용돌이로 합쳐 폭발하고, 투사체는 기억핵의 국소 회전만 변화",
    "m_mateon": "연두 외계 광선핵이 고리와 함께 압축·발광하고, 투사체는 중심 광택과 고리만 맥동",
    "m_plateon": "회색 외계 장갑판이 연두 코어 주위에 구형으로 닫히고 짧게 회전·안정",
    "m_mecateon": "분홍 기계 렌즈가 가로 레이저를 충전·발사하고 작은 금속 조각으로 해체",
    "m_chief_gray": "보라 정신노드와 작은 위성점이 규칙적 원형망으로 커졌다 중심 구체로 복귀",
    "m_zeno": "검보라 중력 고리들이 입체적으로 겹쳐 밝은 보라 핵을 만들고 얇은 궤도로 수축",
    "m_official_knight_c": "청백 전격 두 줄이 연속 발차기 초승달처럼 겹쳐 충돌광 뒤 물결형 잔상으로 소멸",
    "m_official_knight_d": "민트 바람잎과 조준 십자선이 저밀도 고리로 모였다 작은 깃조각으로 풀림",
    "m_advanced_knight_a": "검보라 그림자 손톱 여러 겹이 민첩한 횡방향 잔상으로 커졌다 흐릿해짐",
    "m_advanced_knight_b": "붉은 화염 문장이 바닥 불꽃혀와 함께 솟고 주황 불씨로 가라앉음",
    "m_cygnus": "보라 왕관·날개형 정령불꽃이 크게 피어 검은 파편과 보라 잔광으로 소멸",
    "m_mutant_dark_stump": "뒤틀린 검갈 나무껍질이 닫힌 고치 방패로 커졌다 흰 파편과 함께 풀림",
    "m_mutant_iron_hog": "철갑과 갈색 흙덩이가 전방 압축탄처럼 말려 충돌 파편을 만들고 먼지로 감소",
    "m_mutant_stone_mask": "갈색 석면 조각이 둥근 가면판으로 맞물리고 표면 반사광 뒤 다시 분리",
    "m_ancient_dark_golem": "검갈 암석가시가 지면 균열에서 솟아 큰 산형 충격을 만들고 분진으로 가라앉음",
    "m_mutant_stumpy": "검보라 뿌리와 가시가 무덤형 덩어리로 자라 절정을 만든 뒤 낮은 뿌리 흔적으로 사라짐",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def role_phrase(roles: str) -> str:
    parts = roles.split("|")
    labels = {
        "ICON": "ICON 1장",
        "CAST_VFX": "CAST 전 프레임",
        "PROJECTILE": "PROJECTILE 전 프레임",
        "REFERENCE_VFX": "비전투 REFERENCE 전 프레임",
    }
    return ", ".join(labels.get(p, p) for p in parts)


def trim(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def preview_path(area_id: str) -> Path:
    n = area_id[-2:]
    return WORK / f"AREA_{n}_IMAGES_OUTPUT/AREA_{n}_IMAGES_OUTPUT/AREA_OVERVIEW_PREVIEW.png"


def make_preview_review_copies() -> dict[str, str]:
    out = RUN / "preview_checks"
    out.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}
    for area_id in ("area_17", "area_20"):
        src = preview_path(area_id)
        with Image.open(src) as im:
            im.load()
            copy = im.convert("RGBA")
            copy.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            dst = out / f"{area_id.upper()}_OUTPUT_OVERVIEW_REVIEW_COPY.png"
            copy.save(dst, "PNG")
            result[area_id] = dst.relative_to(ROOT).as_posix()
    return result


def make_issue_crop(area: str, row_index: int, name: str) -> str:
    src = RUN / "area_full_frame_boards" / f"{area.upper()}_ALL_FRAMES.png"
    with Image.open(src) as im:
        im.load()
        # The generated board has a fixed 86 px header and 360 px per monster row.
        top = 86 + row_index * 360
        crop = im.crop((0, top, im.width, min(im.height, top + 360))).convert("RGB")
        crop.thumbnail((2400, 700), Image.Resampling.LANCZOS)
        dst = RUN / "issue_comparisons" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        crop.save(dst, "PNG")
    return dst.relative_to(ROOT).as_posix()


def main() -> None:
    state = json.loads((RUN / "REVIEW_STATE.json").read_text(encoding="utf-8"))
    rows = read_csv(RUN / "CONTENT_STYLE_REVIEW.csv")
    prior_actions = read_csv(PREVIOUS / "ACTION_ITEMS.csv")
    prior_areas = read_csv(PREVIOUS / "AREA_STATUS.csv")
    reused = read_csv(RUN / "REUSED_FILE_CHECKS.csv")

    if len(rows) != 99:
        raise SystemExit(f"expected 99 review rows, got {len(rows)}")
    missing_observations = sorted({r["monster_id"] for r in rows} - OBSERVED_VISUALS.keys())
    extra_observations = sorted(OBSERVED_VISUALS.keys() - {r["monster_id"] for r in rows})
    if missing_observations or extra_observations:
        raise SystemExit(
            f"observation map mismatch: missing={missing_observations}, extra={extra_observations}"
        )
    if not reused or any(
        r.get("reuse_status") != "REUSED_UNCHANGED_HASH" for r in reused
    ):
        raise SystemExit("mechanical audit reuse is unsafe: output hashes changed")

    preview_copies = make_preview_review_copies()
    issue_images = {
        "king": make_issue_crop(
            "AREA_11", 3, "AREA_11_m_king_bloctopus_CAST_PROJECTILE.png"
        ),
        "trojan": make_issue_crop(
            "AREA_12", 1, "AREA_12_m_toy_trojan_CAST.png"
        ),
    }

    reviewed: list[dict[str, str]] = []
    for row in rows:
        area = row["area_id"]
        monster = row["monster_id"]
        role_set = row["roles"]
        material = trim(row["input_core_material"], 180)
        role_contract = trim(row["input_role_contract"], 160)
        actual = row["actual_files"].split("|")
        first_actual = actual[0] if actual else ""
        last_actual = actual[-1] if actual else ""

        row["review_scope"] = (
            f"실제 {role_phrase(role_set)} + INPUT 핵심 소재/역할/흐름 + OUTPUT Area Preview"
        )
        row["observed_visual_sequence"] = OBSERVED_VISUALS[monster]
        row["source_evidence"] = (
            f"{first_actual} .. {last_actual}; "
            f"area_full_frame_boards/{area.upper()}_ALL_FRAMES.png"
        )
        row["issue_roles"] = ""
        row["spec_fit_status"] = "NO_OBVIOUS_ISSUE"
        row["spec_fit_basis"] = (
            f"실제 관찰: {OBSERVED_VISUALS[monster]}. INPUT 핵심 소재 '{material}' 및 "
            f"{role_contract or '역할별 납품 범위'}와 대응하며, 역할 전환·무관한 공격 소재·별도 생물 삽입은 확인되지 않았다."
        )
        row["style_status"] = "CONSISTENT_WITH_REFERENCE"
        row["style_basis"] = (
            f"'{row['skill_name']}'의 {role_phrase(role_set)}에서 어두운 외곽/중간톤/밝은 코어, "
            "단계형 하이라이트와 알파 감쇠가 유지됐다. 역할·체급에 따른 크기와 입자량 차이를 제외하면 "
            "AREA 00 승인본 및 유사 역할군과 표현 문법이 이어진다."
        )
        row["preview_match"] = "MATCHES_DELIVERED_ASSETS"
        row["preview_basis"] = (
            f"{preview_path(area).as_posix()}의 역할별 썸네일을 실제 납품 프레임의 형상·순서·ICON과 대조함."
        )
        row["packaging_action"] = "REPACK_ONLY"
        row["art_action"] = "NONE"
        row["recommended_action"] = "REPACK_ONLY"
        row["original_art_change_candidate"] = "NO"
        row["user_approved"] = "NO"

        if area == "area_09":
            row["preview_match"] = "IMAGES_MATCH_LABEL_RENDERING_ISSUE"
            row["preview_basis"] += (
                " 이미지 배열은 일치하지만 한글 라벨이 네모 글리프로 렌더링되어 식별 문구를 읽을 수 없다."
            )

        if area == "area_17":
            row["preview_basis"] += (
                f" 원본은 유효한 2240x3568 RGBA PNG이며 검수용 축소본 {preview_copies[area]}에서도 동일함."
            )
        if area == "area_20":
            row["preview_basis"] += (
                f" 원본은 유효한 2440x5640 RGBA PNG이며 검수용 축소본 {preview_copies[area]}에서도 동일함."
            )

        if area == "area_11" and monster == "m_king_bloctopus":
            row["issue_roles"] = "CAST_VFX|PROJECTILE"
            row["spec_fit_status"] = "SPEC_MISMATCH"
            row["spec_fit_basis"] = (
                "INPUT은 '왕관 블록이 회전하며 각진 에너지 조각을 발사하는 탄'을 요구하고 "
                "몬스터 본체·얼굴·완전한 실루엣을 VFX에 넣지 말라고 명시한다. 그러나 실제 CAST와 "
                "PROJECTILE에는 눈·포신·왕관이 결합된 분홍 블록퍼스 축소 본체가 반복된다. "
                "ICON의 왕관 블록 모티브는 허용 범위이므로 ICON은 이 판정에서 제외한다."
            )
            row["art_action"] = "REGENERATE_CANDIDATE"
            row["recommended_action"] = "REGENERATE_CANDIDATE"
            row["original_art_change_candidate"] = "YES"
            row["source_evidence"] += f"; {issue_images['king']}"

        if area == "area_12" and monster == "m_toy_trojan":
            row["issue_roles"] = "CAST_VFX"
            row["spec_fit_status"] = "NEEDS_USER_REVIEW"
            row["spec_fit_basis"] = (
                "INPUT CAST 핵심은 목마 휠·태엽 스프링·전방 압축선이며 본체/얼굴 삽입을 금지한다. "
                "실제 CAST는 바퀴·태엽과 함께 눈이 있는 목마 머리/몸통 조각을 전면 형상으로 쓴다. "
                "ICON에는 목마 머리가 명시적으로 허용되어 있어, CAST의 형상이 허용된 모티브 확장인지 "
                "금지된 본체 삽입인지 해석 경계가 남는다."
            )
            row["art_action"] = "USER_REVIEW"
            row["recommended_action"] = "USER_REVIEW"
            row["original_art_change_candidate"] = "PENDING"
            row["source_evidence"] += f"; {issue_images['trojan']}"

        reviewed.append(row)

    fields = list(rows[0].keys())
    additions = [
        "review_scope",
        "observed_visual_sequence",
        "source_evidence",
        "issue_roles",
        "preview_basis",
        "packaging_action",
        "art_action",
        "original_art_change_candidate",
    ]
    for field in additions:
        if field not in fields:
            fields.append(field)
    write_csv(RUN / "CONTENT_STYLE_REVIEW.csv", reviewed, fields)

    actions: list[dict[str, str]] = []
    for old in prior_actions:
        actions.append(
            {
                "area_id": old.get("area_id", ""),
                "monster_id": old.get("monster_id", ""),
                "skill_id": old.get("skill_id", ""),
                "role": old.get("role", ""),
                "source": "PREVIOUS_MECHANICAL_AUDIT_REUSED",
                "relative_path": old.get("relative_path", ""),
                "issue": old.get("observed", ""),
                "content_status": "NOT_APPLICABLE",
                "style_status": "NOT_APPLICABLE",
                "required_action": "REPACK_ONLY" if old.get("action") == "REPACK" else old.get("action", ""),
                "reason": (
                    "현재 OUTPUT ZIP SHA-256이 직전 감사와 같아 파일/구조 판정을 재사용. "
                    + old.get("basis", "")
                ),
                "changes_original_art": "NO",
            }
        )

    actions.extend(
        [
            {
                "area_id": "area_09",
                "monster_id": "",
                "skill_id": "",
                "role": "PREVIEW",
                "source": "SUPPLEMENTAL_VISUAL_REVIEW",
                "relative_path": "AREA_OVERVIEW_PREVIEW.png",
                "issue": "한글 몬스터명·스킬명 라벨이 네모 글리프로 렌더링됨; 실제 ICON/VFX 배열은 납품 파일과 일치",
                "content_status": "NO_OBVIOUS_ISSUE",
                "style_status": "CONSISTENT_WITH_REFERENCE",
                "required_action": "REPACK_ONLY",
                "reason": "원화가 아니라 Preview 합성 글꼴/라벨 렌더링 문제",
                "changes_original_art": "NO",
            },
            {
                "area_id": "area_11",
                "monster_id": "m_king_bloctopus",
                "skill_id": "s_mon_king_bloctopus",
                "role": "CAST_VFX|PROJECTILE",
                "source": "SUPPLEMENTAL_CONTENT_REVIEW",
                "relative_path": issue_images["king"],
                "issue": "본체·얼굴 금지 명세와 달리 왕관/눈/포신을 가진 블록퍼스 축소 본체가 CAST와 PROJECTILE에 반복됨",
                "content_status": "SPEC_MISMATCH",
                "style_status": "CONSISTENT_WITH_REFERENCE",
                "required_action": "REGENERATE_CANDIDATE",
                "reason": "원화 마감보다 WHAT/금지요소 충돌. ICON은 제외하고 두 역할만 후보",
                "changes_original_art": "YES_IF_APPROVED",
            },
            {
                "area_id": "area_12",
                "monster_id": "m_toy_trojan",
                "skill_id": "s_mon_toy_trojan",
                "role": "CAST_VFX",
                "source": "SUPPLEMENTAL_CONTENT_REVIEW",
                "relative_path": issue_images["trojan"],
                "issue": "CAST의 눈 달린 목마 머리/몸통 조각이 허용된 목마 모티브인지 금지된 본체 삽입인지 해석 경계",
                "content_status": "NEEDS_USER_REVIEW",
                "style_status": "CONSISTENT_WITH_REFERENCE",
                "required_action": "USER_REVIEW",
                "reason": "ICON에는 목마 머리가 허용되지만 CAST 금지요소와의 경계는 INPUT만으로 단정 불가",
                "changes_original_art": "NO_UNTIL_DECISION",
            },
        ]
    )
    action_fields = [
        "area_id",
        "monster_id",
        "skill_id",
        "role",
        "source",
        "relative_path",
        "issue",
        "content_status",
        "style_status",
        "required_action",
        "reason",
        "changes_original_art",
    ]
    write_csv(RUN / "ACTION_ITEMS_UPDATED.csv", actions, action_fields)

    board_readme = """# CROSS_AREA_STYLE_BOARD

- `page_01.png` ~ `page_05.png`: AREA 00 승인본 5종을 고정 열로 두고 AREA 01~20(예약 결번 06 제외)의 대표 ICON/VFX를 역할·체급 순서로 비교한다.
- 대표 보드는 지역 간 마감 비교용이며, 개별 설정 판정은 `area_full_frame_boards/AREA_XX_ALL_FRAMES.png`의 실제 전 프레임과 INPUT V2.4 문구를 함께 확인했다.
- 비교 기준: 외곽선, 명암 단계, 재질/하이라이트, 발광/알파 가장자리, 입자/잔상, 프레임 전개, ICON 축소 가독성.
- 지역 팔레트·스킬 위력·보스 체급 차이는 스타일 오류로 취급하지 않았다.
- 이 검토는 `USER_APPROVED`를 의미하지 않는다.
"""
    (RUN / "CROSS_AREA_STYLE_BOARD/README.md").write_text(board_readme, encoding="utf-8")

    spec_counts = Counter(r["spec_fit_status"] for r in reviewed)
    style_counts = Counter(r["style_status"] for r in reviewed)
    preview_counts = Counter(r["preview_match"] for r in reviewed)
    all_repack_areas = sorted({r["area_id"] for r in prior_areas if r.get("file_status") == "FAIL"})

    summary = f"""# Monster Skill OUTPUT Content & Cross-Area Style Review

## 범위와 재사용 근거

- 검수 대상: AREA 01~20 실제 19개(예약 결번 AREA 06 제외), 몬스터/스킬 99쌍.
- 기준: 고정 `BASELINE_INDEX.csv`, `AUDIT_RULES.md`, 승인 INPUT V2.4, AREA 00 승인본.
- 직전 기계 검사는 OUTPUT 19개 ZIP의 SHA-256이 모두 동일한 경우만 재사용했다. 상세는 `REUSED_FILE_CHECKS.csv`.
- 직전 `VISUAL_REVIEW.csv`의 동일 반복 문구는 근거로 재사용하지 않았다. 실제 ICON과 역할별 VFX 전 프레임을 `area_full_frame_boards`로 다시 열고, OUTPUT Area Preview 및 INPUT 핵심 소재·역할·흐름과 대조했다.
- 신규 아트 생성, 알파/크롭 수정, 원본 ZIP 변경, 게임 반입은 수행하지 않았다.

## 판정 집계

| 구분 | 결과 | 수 |
|---|---:|---:|
| 설정 적합성 | NO_OBVIOUS_ISSUE | {spec_counts['NO_OBVIOUS_ISSUE']} |
| 설정 적합성 | SPEC_MISMATCH | {spec_counts['SPEC_MISMATCH']} |
| 설정 적합성 | NEEDS_USER_REVIEW | {spec_counts['NEEDS_USER_REVIEW']} |
| 스타일 | CONSISTENT_WITH_REFERENCE | {style_counts['CONSISTENT_WITH_REFERENCE']} |
| 스타일 | STYLE_OUTLIER | {style_counts['STYLE_OUTLIER']} |
| Preview | 실제 납품 이미지 일치 | {preview_counts['MATCHES_DELIVERED_ASSETS']} |
| Preview | 이미지 일치·라벨 렌더링 문제 | {preview_counts['IMAGES_MATCH_LABEL_RENDERING_ISSUE']}개 몬스터 행(AREA 09 Preview 1개) |

`NO_OBVIOUS_ISSUE`와 `CONSISTENT_WITH_REFERENCE`는 사용자 승인이 아니다.

## 설정 불일치 — 원화 수정 후보

| Area | 몬스터 / 스킬 | 역할 | 판정 | 이유 | 조치 |
|---|---|---|---|---|---|
| AREA 11 | 킹 블록퍼스 / 왕관 블록탄 | CAST_VFX, PROJECTILE | SPEC_MISMATCH | INPUT은 왕관 블록·각진 에너지 조각을 요구하며 본체/얼굴을 금지하지만, 실제 프레임은 왕관·눈·포신이 붙은 축소 몬스터 본체를 반복한다. ICON은 허용 모티브라 제외한다. | REGENERATE_CANDIDATE |

비교 이미지: `{issue_images['king']}`

## 사용자 판단 필요

| Area | 몬스터 / 스킬 | 역할 | 이유 | 조치 |
|---|---|---|---|---|
| AREA 12 | 장난감 목마 / 태엽 목마 돌진 | CAST_VFX | 휠·태엽은 명세와 맞지만 눈 달린 목마 머리/몸통 조각이 CAST의 금지된 본체 삽입인지, ICON에 허용된 목마 모티브의 확장인지 INPUT만으로 단정하기 어렵다. | USER_REVIEW |

비교 이미지: `{issue_images['trojan']}`

## Area 간 스타일 일관성

- 확정 `STYLE_OUTLIER`는 0건이다.
- AREA 00의 저레벨 크기를 고레벨·보스에 강제하지 않고, 비슷한 역할끼리 외곽선·명암·재질·발광·알파 가장자리·입자·소멸·ICON 가독성을 비교했다.
- 99쌍 모두 마감 문법은 AREA 00 승인본과 이어진다. 위 AREA 11 문제는 마감 스타일이 아니라 명세의 WHAT/금지요소 충돌이다.
- AREA 04 스티지, AREA 19 정식기사 D처럼 선형·저밀도인 패시브 REFERENCE_VFX도 역할상 공격 절정을 요구하지 않으며, ICON 및 알파 감쇠는 공통 문법을 유지해 STYLE_OUTLIER로 판정하지 않았다.

전체 비교: `CROSS_AREA_STYLE_BOARD/page_01.png` ~ `page_05.png`  
Area별 전 프레임: `area_full_frame_boards/AREA_XX_ALL_FRAMES.png`

## REPACK_ONLY와 원화 조치의 분리

- 직전 기계 감사에서 19개 Area 모두 파일/Manifest/RESULT_INFO/Preview 구조 중 하나 이상이 실패했으므로 패키지 정리는 모두 `REPACK_ONLY` 대상이다: {', '.join(all_repack_areas)}.
- AREA 09의 `AREA_OVERVIEW_PREVIEW.png`는 실제 ICON/VFX 배열은 일치하지만 한글 라벨이 네모 글리프로 깨진다. Preview 합성만 고칠 `REPACK_ONLY` 항목이며 원화 재생성 사유가 아니다.
- AREA 11 킹 블록퍼스의 CAST_VFX/PROJECTILE만 `REGENERATE_CANDIDATE`다. 사용자 확인 전에는 수정하지 않는다.
- AREA 12 장난감 목마 CAST_VFX는 `USER_REVIEW`이며 재생성 확정이 아니다.
- 그 밖의 원화는 이번 추가 검수에서 재생성 후보로 올리지 않았다.

## 증빙 위치

- 상세 판정: `CONTENT_STYLE_REVIEW.csv`
- 갱신 조치: `ACTION_ITEMS_UPDATED.csv`
- 비교 보드: `CROSS_AREA_STYLE_BOARD/`
- 문제 확대: `issue_comparisons/`
- 긴 Preview 검수용 축소본(원본 무변경): `preview_checks/`
"""
    (RUN / "CONTENT_STYLE_SUMMARY.md").write_text(summary, encoding="utf-8")

    state.update(
        {
            "status": "COMPLETE",
            "visual_review_method": "actual ICON + all delivered role frames + INPUT V2.4 + OUTPUT overview + cross-area boards",
            "spec_counts": dict(spec_counts),
            "style_counts": dict(style_counts),
            "preview_counts": dict(preview_counts),
            "issue_comparisons": issue_images,
            "original_files_modified": False,
            "user_approved": False,
        }
    )
    (RUN / "REVIEW_STATE.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    latest = (
        "# Latest OUTPUT Audit Report\n\n"
        "- Supplemental content/style review: "
        f"[{RUN.name}/CONTENT_STYLE_SUMMARY.md](runs/{RUN.name}/CONTENT_STYLE_SUMMARY.md)\n"
        "- Mechanical baseline audit: "
        f"[{PREVIOUS.name}/AUDIT_SUMMARY.md](runs/{PREVIOUS.name}/AUDIT_SUMMARY.md)\n"
    )
    (ROOT / "docs/art/output_audit/LATEST_REPORT.md").write_text(latest, encoding="utf-8")

    print(f"completed: {RUN}")
    print(f"records: {len(reviewed)}")
    print(f"spec: {dict(spec_counts)}")
    print(f"style: {dict(style_counts)}")
    print(f"actions: {len(actions)}")


if __name__ == "__main__":
    main()
