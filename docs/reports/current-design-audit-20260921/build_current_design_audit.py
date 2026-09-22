from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "RootDesk" / "MyDesk" / "GameData"
RUNTIME = ROOT / "docs" / "reports" / "roguelite-completion-20260921"
REWORK = ROOT / "docs" / "reports" / "roguelite-merge-20260921" / "rework-plan"
SKILL_AUDIT = ROOT / "docs" / "reports" / "skill-diversity-audit" / "skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path = OUT / name
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def num(value: str | int | float, default: float = 0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


areas = sorted(read_csv(DATA / "AreaTable.csv"), key=lambda x: int(x["sort_order"]))
rooms = read_csv(DATA / "RoomTable.csv")
monsters = {x["id"]: x for x in read_csv(DATA / "MonsterTable.csv")}
skills = {x["id"]: x for x in read_csv(DATA / "SkillTable.csv")}
balance = {x["key"]: x["value"] for x in read_csv(DATA / "GameBalance.csv")}
runtime_rows = {x["AreaID"]: x for x in read_csv(RUNTIME / "AREA_RUNTIME_RESULTS.csv")}

seed_evidence: dict[str, list[dict[str, object]]] = {}
for entry in json.loads((RUNTIME / "seed-v2-reproduction-final.json").read_text(encoding="utf-8")):
    msg = entry.get("message", "")
    m = re.search(
        r"\[AuditSeedV2\] (area_\d+) seed=(\d+) valid=(\w+) repeat=(\w+) path=([^ ]+) branches=(\d+) final=([^ ]+) attempt=(\d+)",
        msg,
    )
    if not m:
        continue
    seed_evidence.setdefault(m.group(1), []).append(
        {
            "seed": int(m.group(2)),
            "valid": m.group(3),
            "repeat": m.group(4),
            "path": m.group(5),
            "branches": int(m.group(6)),
            "final": m.group(7),
            "attempt": int(m.group(8)),
        }
    )


def area_rooms(area_id: str) -> list[dict[str, str]]:
    return sorted(
        [
            r
            for r in rooms
            if r["area_id"] == area_id
            and r["room_type"] != "town"
            and not r["id"].startswith("r_job_")
        ],
        key=lambda r: r["id"],
    )


def unique(seq: list[str]) -> list[str]:
    out: list[str] = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


area_state: list[dict[str, object]] = []
encounter_rows: list[dict[str, object]] = []
for area in areas:
    aid = area["id"]
    rr = area_rooms(aid)
    by_id = {r["id"]: r for r in rr}
    mids = unique([r["monster_id"] for r in rr])
    boss_rooms = [r for r in rr if r["room_type"] == "boss"]
    objective = "reach_exit" if aid in {"area_00", "area_01"} else "defeat_final_guardian"
    seed0 = seed_evidence.get(aid, [{}])[0]
    final_id = str(seed0.get("final", boss_rooms[0]["id"] if boss_rooms else "정보 부족"))
    final_map = by_id.get(final_id, {}).get("map_name", "정보 부족")
    order = int(area["sort_order"])
    step = order - 1
    hp = num(balance["run_monster_hp_base"]) + num(balance["run_monster_hp_area_step"]) * step
    atk = num(balance["run_monster_attack_base"]) + num(balance["run_monster_attack_area_step"]) * step
    defense = num(balance["run_monster_defense_base"]) + num(balance["run_monster_defense_area_step"]) * step
    seed_path = str(seed0.get("path", ""))
    seed_path_ids = [x for x in seed_path.split(">") if x]
    seed_species = unique([by_id[x]["monster_id"] for x in seed_path_ids if x in by_id])
    runtime = runtime_rows.get(aid, {})
    area_state.append(
        {
            "AreaID": aid,
            "SortOrder": order,
            "AreaName": area["name"],
            "Theme": area["name"],
            "RoomPoolCount": len(rr),
            "MapRoomPool": "|".join(f"{r['id']}:{r['map_name']}" for r in rr),
            "StartRoom": area["entry_room_id"],
            "StartMap": by_id.get(area["entry_room_id"], {}).get("map_name", "정보 부족"),
            "FinalRoomRule": "비보스 단말 Room" if objective == "reach_exit" else "Area의 boss Room",
            "FinalRoomExample": final_id,
            "FinalMapExample": final_map,
            "BossRoom": "|".join(r["id"] for r in boss_rooms) or "없음",
            "BossMonster": "|".join(
                f"{r['monster_id']}:{monsters.get(r['monster_id'], {}).get('name', '정보 부족')}" for r in boss_rooms
            )
            or "없음",
            "MonsterPoolCount": len(mids),
            "MonsterPool": "|".join(f"{m}:{monsters.get(m, {}).get('name', '정보 부족')}" for m in mids),
            "ObjectiveType": objective,
            "RunNormalHP1P": int(hp),
            "RunNormalATK": int(atk),
            "RunNormalDEF": int(defense),
            "RunBossHP1P": int(hp * num(balance["run_boss_hp_multiplier"])),
            "RuntimeStatus": runtime.get("Status", "NOT_RUN"),
            "RuntimeSeed": runtime.get("Seed", "정보 부족"),
            "RuntimeEvidence": runtime.get("Evidence", "정보 부족"),
            "RuntimeCaveat": runtime.get("Notes", "정보 부족"),
        }
    )
    encounter_rows.append(
        {
            "AreaID": aid,
            "AreaName": area["name"],
            "AreaPoolSpecies": len(mids),
            "AreaPoolMonsterIDs": "|".join(mids),
            "RoomPoolCount": len(rr),
            "SpeciesPerRoomStatic": 1,
            "MaxSpeciesPerRoomStatic": 1,
            "MaxSpeciesPerRoomRuntimeObserved": 1 if runtime else "NOT_RUN",
            "BaseMonsterCountRange": f"{min(int(r['monster_count']) for r in rr)}-{max(int(r['monster_count']) for r in rr)}",
            "OptionalRiskCountRule": "RoomTable.monster_count+1 (최소 1)",
            "FinalCountRule": "1",
            "MaxConcurrentMonstersByConfig": max(int(r["monster_count"]) for r in rr) + 1,
            "SpeciesSelection": "선택된 RoomTemplate의 고정 monster_id",
            "SelectionFrequency": "Run graph에서 Room 선택 시 간접 결정; Room/Spawn마다 재추첨 없음",
            "SpawnPosition": "Room별 파생 Seed로 개체마다 좌표 추첨",
            "SpawnTiming": "Room 로드/최종 Room 입장 시 1회",
            "RespawnInRun": "없음",
            "Seed2026MainPath": seed_path or "정보 부족",
            "Seed2026MainPathDistinctSpecies": len(seed_species),
            "Seed2026MainPathMonsterIDs": "|".join(seed_species),
            "Evidence": "RoomTable.csv; GameData.mlua:1456-1558; RoomSpawner.mlua:63-133,203-231,378-385",
        }
    )

write_csv(
    "AREA_CURRENT_STATE.csv",
    list(area_state[0].keys()),
    area_state,
)
write_csv(
    "MONSTER_ENCOUNTER_AUDIT.csv",
    list(encounter_rows[0].keys()),
    encounter_rows,
)

random_rows = [
    ("Map/Room Layout", "RANDOM_PER_RUN", "YES", "YES", "Seed가 기존 Room 템플릿의 연결 그래프·순서·주 경로를 결정"),
    ("Terrain/Tile Geometry", "FIXED", "NO", "NO", "각 .map 내부 타일·장식·충돌은 기존 템플릿 그대로"),
    ("Room Selection", "RANDOM_PER_RUN", "YES", "YES", "중간 Room을 Seed 기반 shuffle 후 경로/가지 후보로 선택"),
    ("Room Order", "RANDOM_PER_RUN", "YES", "YES", "연결 가능한 범위에서 주 경로 순서가 바뀜"),
    ("Branch", "RANDOM_PER_RUN", "YES", "YES", "0~run_branch_budget(2) 선택 위험 가지"),
    ("Corridor/Door Direction", "CONDITIONAL", "PARTIAL", "YES", "기존 Room 출입구 규격 중 연결 방향을 graph가 선택; 출입구 좌표 자체는 고정"),
    ("Internal Wall", "FIXED", "NO", "NO", "벽 위치를 생성하지 않음; 기존 맵 내부 collidable wall은 감사 당시 0"),
    ("Objective Type", "FIXED", "NO", "NO", "Area 00/01 reach_exit, 나머지 defeat_final_guardian"),
    ("Objective Room", "CONDITIONAL", "PARTIAL", "YES", "Area 규칙으로 고정 후보를 선택; reach_exit는 비보스 단말, defeat는 boss Room"),
    ("Monster Species", "CONDITIONAL", "PARTIAL", "YES", "Room 선택은 랜덤이나 각 Room의 species는 고정"),
    ("Monster Composition", "FIXED", "NO", "NO", "한 Room 한 species; 혼합 pack 생성 없음"),
    ("Monster Count", "CONDITIONAL", "PARTIAL", "NO", "RoomTable 고정값, optional_risk는 +1, final은 1"),
    ("Spawn Position", "RANDOM_PER_SPAWN", "YES", "YES", "Room 파생 RNG로 안전 후보 좌표를 개체마다 선택"),
    ("Spawn Timing", "FIXED", "NO", "NO", "Room 로드 또는 final entry 시 1회"),
    ("Respawn", "NONE", "NO", "NO", "Run one-shot encounter; 레거시 refill 경로는 Run에서 차단"),
    ("Rare/Strong Monster", "FIXED", "NO", "NO", "희귀 추첨 없음; optional/final Room 템플릿으로만 구분"),
    ("Skill Acquisition", "FIXED", "NO", "NO", "사용 가능한 monster skill은 처치 시 확정 제공; 확률 포획 미사용"),
    ("Skill Usage", "FIXED", "NO", "NO", "고정 5슬롯 직접 사용; 쿨다운만 적용"),
    ("Item Drop", "NONE", "NO", "NO", "Run death branch는 ItemDrop을 호출하지 않음"),
    ("Potion", "NONE", "NO", "NO", "Run에서 획득·사용 경로 모두 차단"),
    ("Boss", "FIXED", "NO", "NO", "defeat Area의 boss Room/monster는 데이터 고정; reach_exit는 보스 필수 아님"),
]
write_csv(
    "RANDOMNESS_MATRIX.csv",
    ["Element", "Classification", "Random", "SeedRelated", "CurrentImplementation"],
    [dict(zip(["Element", "Classification", "Random", "SeedRelated", "CurrentImplementation"], r)) for r in random_rows],
)

legacy_rows = [
    ("UI", "AreaSelect", "A", "로비에서 실제 노출/상호작용", "Area 선택 및 준비/시작으로 재사용", "AreaSelect.ui; AreaSelectPanel.mlua"),
    ("UI", "PlayerHud-HP", "A", "Run 스크린샷에서 HP 1000/1000 노출", "신규 Run 핵심 HUD", "PlayerHud.ui; PlayerHud.mlua"),
    ("UI", "PlayerHud-Level/EXP", "B", "UI 파일/컴포넌트는 존재, Run에서 비활성", "레거시 RPG 표시", "PlayerHud.mlua:96-110"),
    ("UI", "SkillBar", "A", "Run 스크린샷에서 5칸/단축키 노출", "고정 5슬롯·쿨다운·교체 UI", "SkillBar.ui; SkillBar.mlua"),
    ("UI", "RoomProgress", "A", "Run 스크린샷에서 Area/목표/Seed 노출", "신규 Run 목표 HUD", "RoomProgress.ui; RoomProgressHud.mlua"),
    ("UI", "WorldMap", "A", "Run 스크린샷에서 Room 그래프 패널 노출", "기존 월드맵을 Run graph로 재사용", "WorldMap.ui; WorldMapPanel.mlua"),
    ("UI", "GateNotice", "A", "조건부 toast", "능력 발견/준비/거부 안내", "GateNotice.ui; GateNotice.mlua"),
    ("UI", "EquipWindow/Collection", "A/B", "로비에서는 컬렉션 버튼, Run 중 자동 숨김", "장비창 대신 발견 컬렉션으로 재사용", "EquipPanel.mlua:157-188"),
    ("UI", "Inventory", "B", "UI/코드는 존재하나 신규 모드에서 패널·버튼 비활성", "레거시 가방", "InventoryPanel.mlua:106-111"),
    ("UI", "ItemQuickSlot", "B", "슬롯 엔티티를 신규 모드에서 비활성", "레거시 포션 단축키", "ItemQuickSlotBar.mlua:47-63"),
    ("UI", "StatGroup", "B", "패널/버튼을 신규 모드에서 비활성", "레거시 STR/DEX/INT/LUK", "StatPanel.mlua:92-100"),
    ("UI", "TraitWindow", "B", "실제 Runtime에서 창·버튼 비활성 로그 확인", "폐기된 Trait", "TraitPanel.mlua:22-29,69-74"),
    ("UI", "RebirthConfirm", "B", "닫힌 채 초기화; Run 중 Open 거부", "레거시 환생", "RebirthConfirmPanel.mlua:51-55,85-88"),
    ("UI", "GoddessWindow", "B", "닫힌 채 초기화; Run 중 Open 거부", "레거시 전직 안내", "GoddessPanel.mlua:38-42,67-69"),
    ("UI", "KeyConfig", "A", "파일/스크립트 활성, 메뉴에서 열 수 있음", "현재 스킬 키 확인/설정", "KeyConfig.ui; KeyConfigPanel.mlua"),
    ("UI", "Quest", "D", "전용 UI/실행 경로 미확인", "미사용", "ui 디렉터리 전수 목록"),
    ("UI", "Taming/Companion", "C", "일부 모델·레거시 데이터는 존재하나 신규 Run UI 없음", "신규 모드 미사용", "Models/Companions; PlayerCollection 레거시 필드"),
    ("UI", "PvP/Ranking", "D", "전용 UI/실행 경로 미확인", "미사용", "ui 디렉터리 전수 목록"),
    ("NPC", "TownGate/Portal_E", "A", "maptown에서 실제 사용", "Area 선택창을 여는 현재 진입점", "map/maptown.map; TownGate.mlua"),
    ("NPC", "RebirthNpc", "A", "maptown에 보이고 TouchEvent 등록 로그 확인", "환생은 거부 안내만 함; 잘못된 balance key 경고 존재", "map/maptown.map; RebirthNpc.mlua"),
    ("NPC", "GoddessNpc", "A", "maptown에 보이고 TouchEvent 등록 로그 확인", "전직 폐지 안내만 함; 잘못된 balance key 경고 존재", "map/maptown.map; GoddessNpc.mlua"),
    ("NPC", "HeroNpc", "B", "map04에 배치되나 신규 모드 상호작용 guard", "레거시 히어로 시험/안내", "map/map04.map; HeroNpc.mlua"),
    ("NPC", "BowmasterNpc", "B", "map29에 배치되나 신규 모드 상호작용 guard", "레거시 보우마스터 시험/안내", "map/map29.map; HeroNpc.mlua"),
]
write_csv(
    "LEGACY_UI_NPC_AUDIT.csv",
    ["Kind", "Name", "Classification", "RuntimeOrStaticState", "CurrentRole", "Evidence"],
    [dict(zip(["Kind", "Name", "Classification", "RuntimeOrStaticState", "CurrentRole", "Evidence"], r)) for r in legacy_rows],
)


def runtime_summary(filename: str) -> dict[str, object]:
    data = json.loads((RUNTIME / filename).read_text(encoding="utf-8"))
    logs = data.get("logs", [])
    msgs = [x.get("message", "") for x in logs]
    begin = next((x for x in logs if "[AuditAreaServer] BEGIN" in x.get("message", "")), None)
    end = next(
        (
            x
            for x in reversed(logs)
            if "[AuditAreaClient] COMPLETE" in x.get("message", "")
            or "[RogueRun] COMPLETE" in x.get("message", "")
        ),
        None,
    )
    duration = "정보 부족"
    if begin and end:
        duration = int((datetime.fromisoformat(end["time"]) - datetime.fromisoformat(begin["time"])).total_seconds())
    entered = []
    maps: list[tuple[str, int]] = []
    for msg in msgs:
        m = re.search(r"\[AuditAreaClient\] ENTER (\S+)", msg)
        if m:
            entered.append(m.group(1))
        m = re.search(r"\[AuditAreaServer\] MAP (\S+) monsters=(\d+)", msg)
        if m:
            maps.append((m.group(1), int(m.group(2))))
    aid = data.get("area", "")
    room_lookup = {r["map_name"]: r for r in area_rooms(str(aid))}
    species = unique([room_lookup[m]["monster_id"] for m, _ in maps if m in room_lookup])
    skill_ids = []
    for msg in msgs:
        m = re.search(r"\[RogueliteReward\] monster=\S+ skill=(\S+) offered=true", msg)
        if m:
            skill_ids.append(m.group(1))
    return {
        "AreaID": aid,
        "Seed": data.get("seed", "정보 부족"),
        "RuntimeSecondsStartToClear": duration,
        "VisitedRooms": len(unique(entered)),
        "VisitedRoomIDs": "|".join(unique(entered)),
        "InitialMonstersObserved": sum(x[1] for x in maps),
        "RoomInitialCounts": "|".join(f"{m}:{c}" for m, c in maps),
        "DistinctMonsterIDsObserved": len(species),
        "MonsterIDsObserved": "|".join(species),
        "MaxMonstersInOneRoomObserved": max([x[1] for x in maps] or [0]),
        "MaxSpeciesInOneRoomObserved": 1 if maps else "정보 부족",
        "SuccessfulSkillOffersObserved": len(skill_ids),
        "DistinctSkillsOfferedObserved": len(set(skill_ids)),
        "RecoveryByGameSystems": 0,
        "QAHpAssistance": bool(data.get("hpAssistance")),
        "BossOrFinalGuardian": "있음" if aid not in {"area_00", "area_01"} else "보스 필수 아님",
        "Clear": data.get("clear", bool(end)),
        "Errors": data.get("errors", sum(1 for x in logs if x.get("type") == "Error")),
        "Evidence": f"docs/reports/roguelite-completion-20260921/{filename}",
        "Caveat": "QA HP 보조 사용; 구조/밀도 표본이며 자연 밸런스 시간 아님",
    }


runtime_samples = [
    runtime_summary("area-03-runtime-assisted.json"),
    runtime_summary("batch-area_10-runtime-assisted.json"),
    runtime_summary("batch-area_20-runtime-assisted.json"),
]
write_csv("RUNTIME_SAMPLE_RUNS.csv", list(runtime_samples[0].keys()), runtime_samples)

active = []
for monster in monsters.values():
    skill = skills.get(monster.get("drop_skill_id", ""))
    if (
        skill
        and skill.get("source") == "monster"
        and skill.get("slot_type") == "monster"
        and skill.get("skill_kind") != "passive"
        and monster["id"] not in {"m_adv_hero", "m_adv_bowmaster"}
    ):
        active.append((monster, skill))
skill_types = Counter()
for _, skill in active:
    if skill["skill_kind"] == "defense":
        skill_types["Defense"] += 1
    elif skill["projectile_ruid"]:
        skill_types["Projectile"] += 1
    elif num(skill["dash_distance"]) > 0:
        skill_types["Dash/Rush"] += 1
    else:
        skill_types["Center/Direct"] += 1

head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
status = subprocess.check_output(
    ["git", "status", "--porcelain=v1"], cwd=ROOT, text=True, encoding="utf-8", errors="replace"
).splitlines()
key_hashes = {
    name: sha(DATA / name)
    for name in ["AreaTable.csv", "RoomTable.csv", "MonsterTable.csv", "SkillTable.csv", "GameBalance.csv"]
}
baseline_digest = hashlib.sha256("".join(key_hashes.values()).encode("utf-8")).hexdigest()[:12]
baseline_id = f"current-design-20260921-{head[:10]}-wt-{baseline_digest}"


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    def esc(x: object) -> str:
        return str(x).replace("|", "\\|").replace("\n", " ")

    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out.extend("| " + " | ".join(esc(x) for x in row) + " |" for row in rows)
    return "\n".join(out)


area_md = md_table(
    ["Area", "이름", "Room", "시작→최종 예", "목표", "Pool", "Boss", "Runtime"],
    [
        [
            x["AreaID"],
            x["AreaName"],
            x["RoomPoolCount"],
            f"{x['StartRoom']}→{x['FinalRoomExample']}",
            x["ObjectiveType"],
            x["MonsterPoolCount"],
            x["BossMonster"],
            x["RuntimeStatus"],
        ]
        for x in area_state
    ],
)

seed_md = md_table(
    ["Seed", "주 경로", "주 경로 몬스터", "가지", "동일한 것", "달라진 것"],
    [
        [2026, "r_001>r_003>r_007>r_00a", "달팽이>빨간 달팽이>슬라임>슬라임", 1, "Area/기존 map 지형/최종 r_00a", "중간 Room·순서·종 구성"],
        [893001, "r_001>r_002>r_004>r_007>r_00a", "달팽이>파란 달팽이>빨간 달팽이>슬라임>슬라임", 1, "Area/기존 map 지형/최종 r_00a", "중간 Room·순서·종 구성"],
        [41001, "r_001>r_002>r_003>r_00a", "달팽이>파란 달팽이>빨간 달팽이>슬라임", 0, "Area/기존 map 지형/최종 r_00a", "중간 Room·순서·가지"],
    ],
)

pair_rows = []
for left, right in [("area_00", "area_01"), ("area_03", "area_02"), ("area_05", "area_07"), ("area_10", "area_11"), ("area_19", "area_20")]:
    a = next(x for x in area_state if x["AreaID"] == left)
    b = next(x for x in area_state if x["AreaID"] == right)
    pair_rows.append(
        [
            f"{left}↔{right}",
            f"{a['AreaName']} ↔ {b['AreaName']}",
            f"{a['MonsterPoolCount']}↔{b['MonsterPoolCount']}",
            f"{a['RunNormalHP1P']}/{a['RunNormalATK']}/{a['RunNormalDEF']} ↔ {b['RunNormalHP1P']}/{b['RunNormalATK']}/{b['RunNormalDEF']}",
            f"{a['ObjectiveType']}↔{b['ObjectiveType']}",
            "테마·맵·몬스터 풀은 다르고 생성 규칙은 동일",
        ]
    )

runtime_md = md_table(
    ["Area", "Seed", "시간(s)", "방", "초기 몬스터", "서로 다른 종", "방 최대", "능력 제안", "회복", "주의"],
    [
        [
            x["AreaID"],
            x["Seed"],
            x["RuntimeSecondsStartToClear"],
            x["VisitedRooms"],
            x["InitialMonstersObserved"],
            x["DistinctMonsterIDsObserved"],
            x["MaxMonstersInOneRoomObserved"],
            x["SuccessfulSkillOffersObserved"],
            x["RecoveryByGameSystems"],
            "QA HP 보조",
        ]
        for x in runtime_samples
    ],
)

random_md = md_table(
    ["항목", "분류", "Seed", "실제"],
    [[a, b, d, e] for a, b, _, d, e in random_rows],
)

question_rows = [
    ("Q1", "확실한 것", "현재 핵심 랜덤은 기존 Room 템플릿의 그래프·선택·순서다. 혼합 몬스터 조합 랜덤은 충분히 구현돼 있지 않다."),
    ("Q2", "확실한 것", "아니다. 한 Room의 Run encounter는 하나의 MonsterID만 사용한다."),
    ("Q3", "확실한 것", "그렇다. RoomTable의 monster_id 하나가 해당 Room 전체 조우를 결정한다."),
    ("Q4", "확실한 것", "사용 가능한 액티브/방어 능력은 자격 참가자에게 처치 시 100% 제안된다. 확률 포획은 Run에서 사용하지 않는다."),
    ("Q5", "확실한 것", "현재 정상 Run 회복 수단은 없다. Run kill은 ItemDrop을 호출하지 않고 아이템 사용도 차단된다."),
    ("Q6", "확실한 것", "그렇다. 첫 능력은 1번 빈 슬롯에 들어가고 사용 후 유지되며 쿨다운마다 반복 사용한다."),
    ("Q7", "확실한 것", "없다. 장착·버튼 사용은 플레이어 통제이며 자동 공급/랜덤 추첨/사용권 소모가 없다."),
    ("Q8", "확실한 것", "아니다. Area 00/01은 reach_exit이며 보스 처치가 필수가 아니다. 나머지 18개는 final guardian 처치다."),
    ("Q9", "확실한 것", "표시되지 않는다. 플레이어별 누적 피해와 결과 Damage Summary 구현을 찾지 못했다."),
    ("Q10", "확실한 것", "신규 Run 전투 수치에는 실질적 의미가 없다. Area sort_order 기반 HP/ATK/DEF가 덮어쓰며 EXP는 0이다."),
    ("Q11", "확실한 것", "지역 테마·Room/Map 풀·고정 몬스터 풀·보스와 sort_order 기반 수치 단계가 핵심 차이다."),
    ("Q12", "확실한 것", "레거시 UI 파일은 다수 남아 있으나 대부분 숨김/차단됐다. 마을 Rebirth/Goddess NPC와 map04/map29 전직 NPC 모델은 배치 상태로 남아 있다."),
    ("Q13", "확실한 것", "Room 선택이 달라져 종의 순서/일부 구성은 달라지지만 각 Room은 고정 한 종이라 변화 폭은 제한적이다."),
    ("Q14", "확실한 것", "확정 능력 획득과 5칸 교체는 여러 능력을 확보할 기회를 주지만, 다양 사용을 강제하지 않는다. 이미 장착한 같은 능력을 계속 쓸 수 있다."),
    ("Q15", "확실한 것", "기존 지역 Room을 Seed로 다시 연결하고, Room별 단일 몬스터를 처치해 확정 능력을 고정 5슬롯에 구성하는 실시간 Area 돌파 로그라이트다."),
]

report = f"""# 현재 설계/구현 상태 감사 보고서

- 분석 일시: 2026-09-21 KST
- 대상: `D:/maplestory_levup`
- baseline_id: `{baseline_id}`
- Git: `{branch}` / `{head}`
- 시작 시 작업 트리: 미커밋 변경 있음 (`git status --porcelain`: {len(status)}행, tracked {sum(not x.startswith('??') for x in status)}, untracked {sum(x.startswith('??') for x in status)})
- 활성 모드: `roguelite_run_mode_enabled=1`
- 데이터 기준: `RootDesk/MyDesk/GameData`의 현재 로드 후보. 핵심 SHA-256은 부록에 기록했다.
- 판정 표기: Runtime은 실제 Maker 실행/기존 원본 로그가 있을 때만 `Runtime 확인`; 코드·데이터만 확인한 항목은 `정적 확인`; 계산할 근거가 없으면 `정보 부족`; 해석은 `추정:`으로 표시한다.
- 변경 원칙: 게임 코드·데이터·UI·밸런스는 변경하지 않았다. 이 디렉터리의 감사 산출물만 생성했다.

## 목차

1. Executive Summary
2. 현재 Game Loop
3. Area 구조
4. Procedural/Random Map 구조
5. Monster Pool / Spawn / Encounter
6. Skill Acquisition
7. Item / Potion / Recovery
8. Skill Usage
9. Boss / Clear
10. Party Damage Tracking
11. RPG Legacy UI
12. RPG Legacy NPC
13. Area Difficulty / Monster Level
14. Balance Structure
15. Runtime Content Density
16. Randomness Matrix
17. 문서와 실제 구현 불일치
18. Runtime 검증 범위
19. 정보 부족
20. 핵심 질문 15개 답변

## 1. Executive Summary

현재 게임은 **기존 메이플 지역의 고정 Room/Map 템플릿을 Seed로 재연결하고, Room별 단일 몬스터 종을 처치해 확정 획득한 능력을 고정 5슬롯에 구성하여 출구 또는 최종 수호자 목표를 해결하는 실시간 탑다운 Area 돌파 로그라이트**다.

핵심 사실:

- Area는 20개다. 예약 결번 `area_06`은 없다.
- 현재 Run 대상 Room/Map은 157개다. `RoomTable` 160행 중 `maptown` 1개와 `r_job_*` 2개를 생성 풀이 제외한다(`GameData.GetRoomsForArea`).
- 절차생성은 새 타일 지형 생성이 아니다. 기존 Room의 선택·순서·방향 연결·가지와 몬스터 스폰 좌표가 Seed로 달라진다.
- 한 Room에는 한 MonsterID만 나온다. 여러 종을 섞은 encounter pack은 없다.
- 액티브/방어 능력은 Run에서 확률 없이 처치 시 자격 참가자에게 제안된다. 막타 기준이 아니다.
- 스킬은 고정 5슬롯, 사용 후 유지, SkillTable 쿨다운 재사용이다. 랜덤 공급/슬롯 소비는 없다.
- Run kill에서는 아이템/포션/장비/재화 드랍이 실행되지 않으며, 아이템 사용도 차단된다. 현재 정상 Run 회복 수단은 확인되지 않았다.
- Area 00/01은 `reach_exit`, 나머지 18개는 `defeat_final_guardian`이다. 모든 Area가 보스 처치로 끝나는 것은 아니다.
- 실제 2~4인 독립 클라이언트 협동은 기존 감사에서도 BLOCKED이며 이번에도 NOT_RUN이다.

## 2. 현재 Game Loop

로비 `maptown`
→ `Portal_E/TownGate`로 Area 선택창 열기
→ Area를 한 번 눌러 준비, 같은 Area를 다시 눌러 시작
→ 서버가 참가자·Seed를 확정하고 InstanceRoom 생성
→ 기존 Room 템플릿으로 검증된 주 경로(4~6)와 최대 2개 가지 구성
→ 시작 Room에서 기본 공격으로 고정 한 종의 몬스터와 전투
→ 사용 가능한 몬스터 능력을 처치 즉시 확정 발견/제안
→ 빈 슬롯이면 첫 빈 칸에 자동 장착, 5칸이면 교체 또는 포기
→ 장착 스킬을 직접 버튼으로 반복 사용하고 기존 쿨다운 대기
→ Room 포탈을 따라 진행
→ Area 00/01은 최종 공간 도달, 나머지는 최종 수호자 처치
→ Clear 또는 전원 사망 Fail
→ `maptown` 복귀 및 Run HP/슬롯/쿨다운/pending/objective/layout 초기화.

## 3. Area 구조

{area_md}

상세: `AREA_CURRENT_STATE.csv`.

구조 판정:

- 기본 단위는 대체로 기존 메이플의 하나의 지역 테마를 하나의 Area로 묶은 방식이다.
- Area 안에는 해당 테마의 여러 사냥맵/보스맵이 Room 템플릿 풀로 들어간다.
- `area_00`은 이름 자체가 `메이플 아일랜드·리스항구`로 두 테마를 묶은 예외다.
- 한 Run은 Area 하나만 사용하며 서로 다른 Area를 연속 결합하지 않는다.
- Area 01/03의 `r_job_01`, `r_job_02`는 RoomTable에는 있으나 `r_job_` 필터로 현재 Run 풀에서 제외된다.

## 4. Procedural/Random Map 구조

정적 구현은 `GameData.mlua:1178-1187,1456-1680`에서 확인했다.

- 전체 지형 새 생성: **NO**
- 기존 Map 선택: **YES**
- Room 순서/Graph/Branch: **YES**
- 통로: **PARTIAL** — 기존 출입구 중 어떤 방향을 연결할지는 바뀌지만 포탈 좌표/내부 통로 지형은 고정이다.
- 내부 Wall 위치: **NO**
- 기존 Room/Map 템플릿 조합: **YES**
- Objective 위치: **PARTIAL** — Area 목표 규칙의 최종 후보는 사실상 고정이고, 그 전 경로가 바뀐다.
- Monster 종류: **PARTIAL** — 선택된 Room이 달라져 간접 변화하나 Room 내부 monster_id는 고정이다.
- Monster 조합: **NO** — 혼합 종 pack이 없다.
- 정확한 Spawn 위치: **YES**
- Boss: **NO** — Area의 boss Room과 boss monster는 고정이다.

Area 00 Seed A/B/C는 이번 감사에서 Maker `server_main`의 현행 생성기를 직접 실행하고 상태를 복구했다.

{seed_md}

플레이어 체감: 경로 길이, 방문 맵, 몬스터 종의 순서가 달라질 수 있다. 그러나 들어간 각 맵의 타일·배경·장애물과 해당 Room의 몬스터 종은 동일하므로 완전히 새 지형이나 매번 새 혼합 조우처럼 보이는 수준은 아니다.

## 5. Monster Pool / Spawn / Encounter

현재 조우 모델:

- 각 RoomTable 행은 `monster_id` 하나와 `monster_count` 하나를 가진다.
- 생성기가 Room을 선택하면 그 Room의 고정 monster_id를 그대로 `RogueEncounters`에 복사한다.
- 일반/시작 Room 수량은 RoomTable 값, `optional_risk`는 +1, final은 1이다.
- 현재 테이블의 기본 범위는 1~5이며 optional 가지의 정적 상한은 6이다.
- 스폰 좌표는 Room별 파생 Seed로 개체마다 추첨한다. 생성기 RNG와 전투 RNG는 분리된다.
- Run 조우는 Room 로드(최종은 입장 감지) 시 한 번 생성되고 `runEncounterSpawned`가 true가 되면 리필하지 않는다.
- Wave, Rare 추첨, 시간 기반 추가 Spawn, cleared Room 재Spawn은 없다.

따라서 예시의 `슬라임 4 + 주황버섯 3 + 스텀프 2` 같은 혼합 Room은 현재 불가능하다. 실제 구조는 `Room A: 슬라임 N`, `Room B: 주황버섯 N`이다.

Area별 상세는 `MONSTER_ENCOUNTER_AUDIT.csv`에 있다. Seed 2026 주 경로의 종 수도 함께 기록했다.

몬스터 전투 압박:

- 인지 범위 기본 6.0 world units.
- 공격 범위 기본 `player_attack_range(1.0) × 0.5 = 0.5` world units. 종별 `MonsterAttack.AttackRange>0`이면 오버라이드한다.
- 모델의 `AIChaseComponent`가 감지 후 이동/추적하고, 실제 공격은 별도 공격 범위 안에서 수행한다.
- 몬스터 공격 간격 기본 0.5초, 플레이어 i-frame 1.0초.
- Room 진입이 별도 잠금/웨이브를 시작하는 것은 아니며, 맵 로드로 조우가 놓이고 감지 범위에 들어가면 압박이 시작된다.
- 일반 Room은 전멸이 포탈 잠금 조건이 아니다. final guardian은 처치가 목표인 Area에서만 Clear 조건이다.

객관적 분류: **B에 가까운 C**. Room 선택 때문에 Run 전체 종 순서는 변하지만, 한 Room 안에서는 미리 정해진 한 종만 나온다.

## 6. Skill Acquisition

현재 플레이어 Run 사용 가능 범위는 MonsterTable의 실제 `drop_skill_id` 매핑 기준 66종이다. SkillTable만 세면 레거시 `s_mon_snail/몸통 박치기`가 하나 더 있어 67이지만, 현재 MonsterTable의 획득 매핑에서는 사용되지 않는다.

- 획득 확률: 사용 가능한 액티브/방어 능력은 **100% 확정 제안**.
- Monster별 확률/최초·중복 차이: Run에서는 없음.
- Party: 서버가 같은 map의 Run 참가자 중 사망 위치 12 world units 이내 참가자에게 각자 독립 판정.
- Last hit: 아님. `RoomMonster.Dead`의 killer는 Run reward 대상 선택에 쓰이지 않는다.
- 패시브 또는 플레이어용 active가 없는 몬스터: 발견 기록만 남기고 슬롯 능력은 주지 않는다.
- 빈 슬롯: 첫 빈 슬롯 자동 장착.
- 5칸 Full: pending 후보 생성. 기존 슬롯 하나와 Replace 또는 Reject.
- pending 중 추가 후보: FIFO queue. 같은 SkillID가 이미 슬롯/pending/queue에 있으면 중복 제안하지 않는다.
- Room 전환/Run 종료: 오래된 pending 정리.

한 Run의 평균 서로 다른 스킬 수는 단일 값으로 계산할 수 없다. 실제 방문 경로, optional 가지 방문, 같은 종 중복 Room, 패시브 종, 플레이어의 Replace/Reject에 좌우된다. 다만 Area 00의 이번 Seed 비교에서 주 경로의 서로 다른 MonsterID는 3~4종이었다. 이것은 전체 Area 평균이 아니다.

## 7. Item / Potion / Recovery

신규 Run의 `RoomMonster.Dead`는 `GrantRunKillRewards`만 호출하며 레거시 `ItemDrop.TrySpawnDrops`는 `elseif`의 비 Run 경로에 있다.

- Potion drop: 비활성
- Item/Equipment drop: 비활성
- Currency drop: 구현 경로 미확인
- EXP: Run monster는 0
- 인벤토리 아이템 사용: `PlayerInventory.UseItem`이 roguelite mode에서 false
- 장비 변경: `SetEquipSlot`이 roguelite mode에서 false
- 회복 스킬: 현재 66종 분류는 공격 63(센터/투사체/돌진 포함)+방어 3이며 회복 스킬은 확인되지 않았다.

**현재 Run 회복 수단 없음.** 마을 복귀 시 HP를 1000으로 회복하는 경로는 Run 중 회복이 아니다. 기존 빨간 포션 데이터(HP 300, legacy drop 15%)는 남아 있지만 신규 Run에서 획득/사용되지 않는다.

## 8. Skill Usage

- 고정 슬롯: 5칸.
- 획득: 첫 빈 슬롯부터 등록.
- 사용 후: 슬롯 유지.
- 재사용: SkillTable cooldown. 0/누락은 공통 fallback 4초.
- 자동 공급/랜덤 교체/사용권 소모: 없음.
- 동일 SkillID 중복 장착: 차단.
- 슬롯 이동: 지원하며 SkillID 기준 cooldown은 유지.
- 5칸 Full: pending Replace/Reject.
- 영구 Skill Pool이 Run 시작 스킬을 제공하는 구조: 없음. Run은 빈 슬롯으로 시작한다.

1개 획득 시 그 능력 하나를 쿨다운마다 반복 사용하고 나머지 4칸은 빈다. 2개/3개는 각각 두/세 버튼을 선택해 사용한다. 5개가 차면 새 능력은 자동 덮어쓰지 않고 교체/포기 선택을 기다린다. 특정 유형을 반드시 섞게 하는 규칙은 없다.

66종 구조 재확인:

{md_table(["유형", "수"], [[k, skill_types[k]] for k in ["Center/Direct", "Projectile", "Dash/Rush", "Defense"]])}

같은 유형을 여러 개 획득해도 각각 다른 SkillID라면 별도 슬롯·별도 쿨다운으로 공존한다. 시스템은 다양한 능력을 얻을 기회를 주지만 사용 다양성을 강제하지 않는다.

## 9. Boss / Clear

- Area 00/01: `reach_exit`. final은 비보스 단말 Room이며 보스 처치 필수 아님.
- Area 02~20(06 없음): `defeat_final_guardian`. 각 Area의 boss Room monster 1체가 final encounter.
- 보스 스폰: final Room 입장 감지, Run에서는 1회.
- 보스 HP: 해당 Area 일반 HP ×4 × 시작 인원 HP scale.
- 보스 Attack/Defense: Run용 Area ATK/DEF와 동일하며 별도 Run boss 공격 배율은 없다.
- 처치 후: final guardian 목표를 즉시 완료하고, 생존 참가자가 final Room에 모였으면 Clear 확정.
- reach_exit: final Room 도달 시 ObjectiveComplete 및 Clear.
- Result UI: 독립 결과 화면 미확인. RoomProgress HUD가 Clear 문구를 표시하고 약 3초 후 로비로 복귀.
- Loot: 없음.
- Damage Summary: 없음.

Boss 상세는 `AREA_CURRENT_STATE.csv`의 BossRoom/BossMonster 열을 참조한다.

## 10. Party Damage Tracking

현재 구현 검색 결과:

- 전체 Run 누적 Damage: 없음
- Boss 누적 Damage: 없음
- 플레이어별 Damage Meter: 없음
- Contribution 수치: 없음
- Result Screen Damage Summary: 없음
- Last Hit: `HitEvent.AttackerEntity`는 레거시 보상 경로에만 사용되며 Run 보상 자격은 거리 기반 참가자다. 누적 기록은 하지 않는다.

`RoomMonster`는 매 타격의 피해 로그를 남기지만 이를 플레이어별로 누적하는 원장은 확인되지 않았다.

## 11. RPG Legacy UI

분류 정의: A 실제 노출/상호작용, B 파일은 있으나 신규 모드에서 숨김/차단, C 코드·데이터만 잔존, D 완전 미사용 또는 전용 경로 미확인.

상세: `LEGACY_UI_NPC_AUDIT.csv`.

이번 Maker 확인:

- 로비 스크린샷: `evidence/maker_lobby_20260921.png`
- Area 00 Run 스크린샷: `evidence/maker_area00_run_20260921.png`
- 실제 Run 노출: HP, 5 빈 슬롯/단축키, Area/목표/Seed, Room graph panel.
- 실제 로비 노출: 컬렉션 버튼과 메뉴 버튼. 스탯/가방/장비성장/EXP/레벨/Trait/환생 버튼은 화면에서 확인되지 않았다.
- UI root 엔티티 자체는 여러 개가 Enable=true지만 내부 panel/button을 비활성화하는 구조가 많다. root 상태만으로 노출을 판정하지 않았다.

## 12. RPG Legacy NPC

- `maptown/RebirthNpc`: 모델·TouchReceive·스크립트가 활성. 현재 Runtime에서 `터치 대기` 로그 및 상호작용 시 환생 거부 안내 확인.
- `maptown/GoddessNpc`: 모델·TouchReceive·스크립트가 활성. Phase 3 전직 폐지 안내 경로가 남아 있다.
- `map04/HeroNpc`: Area 01의 Run pool에 포함된 map04에 모델이 남아 있으나 `HeroNpc`가 roguelite mode에서 상호작용을 반환한다.
- `map29/BowmasterNpc`: Area 03의 Run pool에 포함된 map29에 모델이 남아 있으나 같은 guard로 상호작용을 반환한다.
- 성장/장비/가방/Trait/Taming/Companion 전용 NPC는 map 파일 전수 이름·component 검색에서 추가로 찾지 못했다.

중요 불일치: `RebirthNpc`와 `GoddessNpc`는 `roguelite_run_mode_enabled`가 아니라 존재하지 않는 `roguelite_mode_enabled`를 조회한다. 현재 Runtime은 balance key 없음 경고를 내고 TouchEvent를 등록한다. 따라서 이전 Final Completion Audit의 “TouchEvent 자체를 등록하지 않는다”는 현재 코드/Runtime과 다르다. 이 감사에서는 수정하지 않았다.

## 13. Area Difficulty / Monster Level

신규 Run 난이도의 주 결정값:

- AreaTable `sort_order`
- 일반 HP = 240 + 28 × (sort_order-1)
- ATK = 24 + 3 × (sort_order-1)
- DEF = 6 + 1 × (sort_order-1)
- Boss HP = 일반 HP ×4
- Party HP = 위 HP × [1.00,1.25,1.50,1.75]
- Room monster_count 및 optional +1/final 1
- 종별 행동/보스 스킬은 Monster model/MonsterAttack의 기존 차이가 남는다.

`MonsterTable.level`은 RoomMonster가 초기 레코드를 읽을 때 로그용 level을 만들지만, Run에서는 직후 Area 기반 HP/ATK/DEF로 덮어쓰고 EXP=0으로 만든다. Spawn, Area gate, Run drop에도 level을 사용하지 않는다. Skill 고유 계수/cooldown은 SkillTable 값이며 Monster level로 스케일하지 않는다. UI의 legacy WorldMap branch에는 level 표시 코드가 남지만 roguelite branch는 확정 능력 정보만 표시한다.

대표 인접 5쌍:

{md_table(["쌍", "테마", "Pool수", "HP/ATK/DEF", "목표", "구현 차이"], pair_rows)}

20개 Area는 과거 레벨 진행의 지역 구분을 유지하지만, 현재 Run에서는 입장 gate 없이 sort_order 수치 단계와 테마/Pool 차이로 쓰인다. 생성 알고리즘과 Room당 단일 종 규칙은 공통이다.

## 14. Balance Structure

Player Run 기본값:

- HP 1000
- Attack/MagicAttack 35
- Defense 10
- MoveSpeed 2.4
- 기본 공격 interval 1.0초, range 1.0
- Level/EXP/장비/STR/DEX/INT/LUK/Trait/중복 성장 미합산

Monster:

- Area 00 일반 240/24/6 → Area 20 일반 772/81/25 (HP/ATK/DEF)
- MoveSpeed: 각 Monster model의 MovementComponent 값. 전역 단일값은 확인되지 않음.
- Awareness 6.0, 기본 Attack Range 0.5, Attack interval 0.5.

Skill:

- coefficient, cooldown, range, max_targets는 SkillTable 개별값.
- 현재 66종 cooldown은 기존 전수 감사에서 0/누락 없음, 실제 발동·즉시 재사용 차단 확인.

Boss/Party:

- Boss HP ×4, Attack/Defense는 Area 일반 공식.
- 1P 1.00 / 2P 1.25 / 3P 1.50 / 4P 1.75 HP.
- 실제 2~4인 Runtime은 NOT_RUN; 수식과 서버 simulation만 기존 감사 근거다.

## 15. Runtime Content Density

아래 3건은 기존 현행 개편본 Maker 원본 로그를 재분석했다. 모두 HP 보조 QA로 완주한 구조 검증이므로 자연 플레이 밸런스/완주 시간으로 해석하면 안 된다.

{runtime_md}

- 총 Monster 수 열은 방문 Room의 초기 배치 합이다. QA가 모든 일반 몬스터를 전멸시킨 것은 아니므로 실제 kill 수와 다르다.
- 회복 0은 게임 시스템 회복 횟수다. QA HP 보조는 별도이며 플레이 기능이 아니다.
- 같은 Area 3회 완주 밀도 측정은 NOT_RUN. 대신 Area 00에서 3 Seed 생성 결과를 현행 Maker generator로 비교했다.

## 16. Randomness Matrix

{random_md}

전체 CSV: `RANDOMNESS_MATRIX.csv`.

## 17. 문서와 실제 구현 불일치

1. **Final Completion Audit의 NPC 비활성 주장과 현재 Runtime 불일치**  
   문서는 Goddess/Rebirth NPC가 TouchEvent를 등록하지 않는다고 적지만, 현재 코드는 잘못된 balance key `roguelite_mode_enabled`를 조회한다. 실제 로그에 key 없음 경고와 `터치 대기`가 기록됐다.

2. **Implementation Report의 최종 대상 경로가 과거 상태**  
   `IMPLEMENTATION_REPORT.md:244`는 원본 프로젝트를 편집 대상으로 사용하지 않았다고 적지만, 이후 원본 병합 지시가 수행되어 현재 실제 실행 프로젝트는 `D:/maplestory_levup`이다. 보고서 시점 차이다.

3. **Implementation Report의 “Area Monster 풀/조우 구성” 표현은 실제보다 넓게 읽힐 수 있음**  
   실제 구현은 Area 풀에서 몬스터를 독립 추첨하지 않는다. Room template 선택이 간접적으로 종을 고르며 Room 내부는 한 종 고정이다.

4. **GDD와 현재 핵심 전투는 대체로 일치**  
   고정 5슬롯, 확정 능력 획득, 기존 cooldown, Seed Room graph, 레벨/장비 비합산은 코드와 Runtime 근거가 있다.

5. **Skill Diversity Audit은 의도적으로 구버전 baseline**  
   66종의 고유 효과/유형 데이터는 여전히 참고 가능하지만, 당시의 랜덤 SkillBar·확률 테이밍 사용 방식은 현재 Run과 다르다. 현재는 고정 슬롯/확정 획득/쿨다운이다.

6. **Build/Runtime 잔존 경고**  
   현행 Build Console은 Error 0, Info 3(`GetTile`, `ToCellPosition`, `waterTileName` dynamic member)와 기존 model Warning 2(마노 InputSpeed, 보우마스터 AvatarAttackPlayRate)다. Runtime에는 Legacy Trigger 경고와 maptown RectTileMap 탐색 경고가 남는다. 본 감사에서는 수정하지 않았다.

## 18. Runtime 검증 범위

이번 감사에서 직접 실행:

- Maker edit 상태와 current map `maptown` 확인.
- Build Console: Error 0, 총 5개 Info/Warning 확인.
- Maker Play 로비 스크린샷.
- Area 00 seed 41001 InstanceRoom 실제 생성 및 Run HUD 스크린샷.
- 현행 server generator로 Area 00 seed 2026/893001/41001 그래프·monster path 비교 후 상태 복구.
- 현행 Runtime 로그에서 Rebirth/Goddess NPC balance key 경고와 TouchEvent 등록 확인.

재사용한 동일 프로젝트 Runtime 증빙:

- Area 00, 02~20(06 제외) 시작/생성/이동/목표/Clear/복귀/reset.
- Area 01 transition/fail/reset.
- 전체 20 Area ×2 Seed 재현 검증.
- 66 Skill PlayerAttack 발동/VFX dispatch/cooldown 전수.
- Area 03/10/20 QA-assisted Run 로그의 밀도 재계산.

NOT_RUN:

- 실제 2P/3P/4P 독립 클라이언트 협동.
- 같은 Area를 서로 다른 3 Seed로 자연 플레이 완주한 시간/밀도 비교.
- QA HP 보조 없는 Area 02~20 자연 밸런스 완주.
- 현재 맵에 없는 내부 collidable wall과 66 Skill의 상호작용.
- 모든 UI/NPC 버튼을 이번 감사에서 하나씩 수동 클릭한 전수 검사.

## 19. 정보 부족

- 2~4인에서 실제 동시 플레이 압박, 개인 획득 UI 충돌, 재접속 체감: 정보 부족(Runtime 미실행).
- 자연 플레이 기준 Area별 평균 완주 시간/평균 획득 능력 수: 정보 부족(QA 보조 로그만 있음).
- 같은 Area 3 Seed의 통계적으로 유의한 체감 차이: 정보 부족(생성 비교만 3건).
- Monster별 실제 MovementComponent 속도의 전수 분포: 이 보고서에서는 모델 103종 전수 수치 표를 만들지 않음.
- UI root가 활성인 것과 모든 하위 Mask/Input blocker 상태의 조합: 대표 화면은 확인했으나 모든 창 전수 클릭은 NOT_RUN.
- 외부 원작 지역 의미와 현재 Area 묶음의 정합성: 이번 감사는 프로젝트 내부 구현만 기준으로 하며 외부 설정 조사는 수행하지 않음.

## 20. 핵심 질문 15개 답변

{md_table(["질문", "확실성", "답변"], [list(x) for x in question_rows])}

## 부록: 기준 파일 SHA-256

{md_table(["파일", "SHA-256"], [[name, value] for name, value in key_hashes.items()])}

## 완료 확인

- 게임 파일 변경 수: **0**
- 보고서 외 변경: **없음**
- 생성 산출물: 이 보고서, 5개 CSV, 보고서 생성 스크립트, Runtime 증빙 스크린샷 복사본
- git commit/push: 수행하지 않음
- 추가 개편: 수행하지 않음
"""

(OUT / "CURRENT_DESIGN_AUDIT.md").write_text(report, encoding="utf-8")
print(json.dumps({"baseline_id": baseline_id, "areas": len(area_state), "active_skills": len(active), "skill_types": skill_types}, ensure_ascii=False))
