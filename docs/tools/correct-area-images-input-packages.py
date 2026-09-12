#!/usr/bin/env python3
"""Patch existing AREA Images input ZIPs without rebuilding fixed game data.

Only Markdown instruction files inside each existing ZIP are rewritten.  The
AREA_MANIFEST CSV/Markdown and every binary reference asset are preserved.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / "docs" / "art" / "images-input-packages"

# Explicit art translations.  Each fixed monster/skill pairing has its own
# material, two-colour hierarchy and icon silhouette; no generic noun fallback
# is permitted.
VISUALS = {
    "m_snail": ("바닥을 얇게 타고 흐르는 이슬 점액 띠와 둥근 물방울", "맑은 이슬 청록 #7EDFD1", "연한 풀잎 연두 #B8E86A", "큰 이슬방울 + 낮게 미끄러지는 점액 꼬리"),
    "m_blue_snail": ("겹친 껍질 결을 닮은 반원형 보호막과 짧은 반사광", "푸른 껍질 청색 #4E9EDB", "물빛 백청 #C9F4FF", "푸른 껍질 아치 + 흰 반사광"),
    "m_red_snail": ("붉은 껍질 원반이 전방으로 압축되는 돌진 잔상과 충돌광", "껍질 적색 #D84D3F", "주황 충돌광 #FFB34F", "붉은 껍질 원반 + 전방 속도선"),
    "m_mushroom": ("작은 포자 구름 세 덩이와 부드럽게 흩어지는 점 입자", "버섯 베이지 #D8B679", "새싹 연두 #9BCB58", "버섯 포자구름 + 세 점 확산"),
    "m_mano": ("진주빛 껍질 고리에서 번지는 낮은 무지개 파동", "진주 백색 #F8F1D8", "무지개 청록·분홍 #80D8D0/#F29AB2", "진주 껍질 고리 + 무지개 파문"),
    "m_mushmom": ("굵은 포자 핵이 지면에 닿아 버섯갓 모양으로 터지는 충격", "황갈 포자색 #B77A3A", "황금 충격광 #FFD66B", "버섯갓 충격파 + 굵은 포자 파편"),
    "m_stone_golem": ("맞물린 암석 판 두 겹과 틈새에서 새는 흙빛 광선", "화강암 회색 #77736D", "토황색 #C3A56A", "겹친 바위판 + 균열광"),
    "m_slime": ("탄성 있는 점액 방울과 눌렸다 되튀는 젤리 테두리", "슬라임 연두 #79D56B", "투명 민트 #C7FFE0", "점액 방울 + 탄성 튐선"),
    "m_horny_mushroom": ("짙은 갓을 감싼 단단한 뿔 쐐기와 짧은 금속성 반짝임", "뿔 상아색 #D7C8A5", "갓 갈색 #7A4D35", "상아 뿔 + 버섯갓 곡선"),
    "m_dark_stump": ("검게 굳은 나이테 방패와 땅에 박힌 짧은 뿌리", "먹갈색 #4D3A33", "마른 나무 황토 #A47B52", "굵은 나이테 + 버팀 뿌리"),
    "m_bubbling": ("마력빛 큰 기포 하나와 주변을 도는 작은 거품 고리", "마력 청색 #55BEEA", "거품 백색 #D9FAFF", "큰 마력 기포 + 작은 거품 고리"),
    "m_axe_stump": ("도끼날 실루엣의 짧고 무거운 전방 궤적과 나무 부스러기", "철회색 #8B9094", "나무 갈색 #8B5A37", "도끼날 호 + 나무 파편"),
    "m_fairy": ("별가루 같은 요정 분말이 나선으로 모였다 퍼지는 빛무리", "요정 금빛 #FFE47A", "엘리니아 민트 #91E6BF", "별가루 나선 + 작은 날개빛"),
    "m_faust": ("실로 묶인 인형 표식과 아래로 떨어지는 자주색 저주 침", "저주 자주 #734B91", "인형 적갈 #A85A61", "실 묶인 인형 표식 + 저주 침"),
    "m_dark_axe_stump": ("지면을 찢고 솟는 검은 뿌리 갈퀴와 보랏빛 흙먼지", "암목 흑갈 #3A3038", "저주 보라 #80579A", "검은 뿌리 갈퀴 + 보라 흙먼지"),
    "m_wild_boar": ("멧돼지 어금니를 닮은 두 갈래 전방 압축선과 흙먼지", "황토 갈색 #9B633D", "먼지 금갈 #D6A65D", "쌍 어금니 + 돌진 흙먼지"),
    "m_iron_hog": ("철제 발굽이 지면을 찍는 반달 충격과 쇳가루", "강철 청회 #64798A", "충돌 백황 #E8D28A", "강철 발굽 + 지면 충격선"),
    "m_skeleton_commander": ("지면에서 비스듬히 솟는 뼈기둥과 묘지 흙 파편", "뼈 상아 #D9D0B3", "묘지 자갈색 #655C62", "교차한 뼈기둥 + 묘지 흙"),
    "m_octopus": ("검푸른 먹물 방울이 불규칙 꽃잎처럼 터지는 얼룩", "먹물 남색 #263B68", "물빛 보라 #7A76B9", "먹물 방울 + 방사 얼룩"),
    "m_fire_boar": ("낮게 휘는 불꽃 혀와 돌진 방향으로 흩는 불티", "화염 주황 #F06A2B", "고열 황색 #FFD15C", "불꽃 혀 + 전방 불티"),
    "m_stirge": ("박쥐 초음파 같은 얇은 야간 파문과 붉은 감지점", "야간 남보라 #3C355F", "감지 적색 #D85B66", "초음파 파문 + 붉은 감지점"),
    "m_jr_wraith": ("반투명 망령 손자국이 순간 겹치며 터지는 냉기 충격", "유령 청백 #A9D8E8", "묘지 보라 #6E668F", "망령 손자국 + 냉기 충격륜"),
    "m_wraith": ("휘어진 혼령 띠와 안쪽을 도는 작은 원혼 불씨", "원혼 청록 #62B9A9", "음영 자주 #625070", "혼령 띠 + 원혼 불씨"),
    "m_shade": ("빛을 삼키는 반투명 장막과 가장자리의 보랏빛 잔광", "심연 흑보라 #272335", "잔광 보라 #70538B", "검은 장막 초승달 + 보라 테두리"),
    "m_ribbon_pig": ("분홍 리본 매듭이 전방으로 길게 풀리는 돌진 궤적", "리본 분홍 #F38AA5", "충돌 백분홍 #FFD6DF", "분홍 리본 매듭 + 전방 잔상"),
    "m_stumpy": ("고목 나이테에서 싹이 돋아 에너지 씨앗으로 압축되는 탄", "고목 갈색 #75533A", "생기 연두 #8ED35B", "싹튼 나이테 + 생기탄"),
    "m_blue_pig": ("푸른 리본 매듭이 겹겹이 조여드는 원형 결속광", "리본 청색 #4F9FD7", "매듭 백청 #CCEFFF", "푸른 리본 매듭 + 조임 고리"),
    "m_starfish": ("별 모양 가시가 회전하며 남기는 다섯 갈래 수중 잔상", "불가사리 주황 #F39B45", "바닷물 청록 #5CC8C4", "회전 별가시 + 물결 잔상"),
    "m_jellyfish": ("차가운 젤리 방울이 늘어졌다 튀며 남기는 서리 테두리", "젤리 하늘 #67D6E8", "서리 백청 #D8FAFF", "젤리 방울 + 서리 튐"),
    "m_king_clang": ("왕게 집게 두 개가 닫히며 밀어내는 넓은 파도턱", "갑각 적주황 #C9603E", "파도 청록 #53B9C5", "왕관 집게 + 파도턱"),
    "m_zombie_mushroom": ("마른 포자 덩이가 꺼지지 않고 다시 붙는 탁한 생기", "죽은 포자 회갈 #827768", "병든 녹색 #7E9A58", "갈라진 포자핵 + 되붙는 점"),
    "m_copper_drake": ("청동 비늘 조각이 비스듬히 포개지는 방호판", "청동 갈색 #A56A3A", "녹청 산화색 #54A28D", "청동 비늘판 + 녹청 반사광"),
    "m_drake": ("동굴 입김처럼 좁게 시작해 넓어지는 붉은 용염", "용염 적주황 #E85632", "고열 황백 #FFD77A", "용의 불꽃 숨결 + 동굴 연기"),
    "m_wild_kargo": ("검은 야수 발톱 세 줄과 몸을 낮춘 전방 그림자 잔상", "그림자 남흑 #252A3B", "발톱 자주 #765378", "세 줄 발톱 + 낮은 돌진 그림자"),
    "m_jr_balrog": ("발록 뿔을 닮은 화염 고리가 전방으로 밀리는 파동", "지옥 적색 #B93632", "화염 금주황 #FF9B42", "발록 뿔 고리 + 화염 파동"),
    "m_tauromacis": ("미궁 수문 표식 위로 떨어지는 굵은 청백 낙뢰", "낙뢰 청백 #BCEBFF", "수문 석회 #777B86", "수문 문양 + 수직 번개"),
    "m_star_pixie": ("작은 별핵이 꼬리별 잔상을 달고 직선으로 날아가는 탄", "별빛 황색 #FFE46A", "하늘 청색 #81BDEB", "오각 별탄 + 꼬리별 잔상"),
    "m_jr_cellion": ("붉은 뿔 끝에서 솟는 짧은 기백 불꽃과 압력 고리", "뿔 적색 #C94C55", "기백 금빛 #F2C45B", "붉은 뿔 + 기백 고리"),
    "m_lunar_pixie": ("초승달 안에 맺힌 월광 구슬과 은빛 궤도", "월광 은청 #C9D9F4", "밤보라 #7770A9", "초승달 구슬 + 은빛 궤도"),
    "m_luster_pixie": ("작은 태양핵이 날개처럼 갈라지는 황금 잔상", "태양 금빛 #FFD45E", "하늘 백색 #FFF3C4", "태양핵 + 날개형 잔상"),
    "m_eliza": ("정원 잎과 꽃잎을 감아 올리는 여신풍 나선 폭풍", "정원 녹색 #68B86B", "신성 금빛 #F6D77B", "잎사귀 나선 + 황금 바람눈"),
    "m_jr_yeti": ("둥근 온기핵 주변에서 녹아내리는 작은 눈송이", "설원 백청 #DFF4F6", "온기 주황 #F4A45D", "온기핵 + 녹는 눈송이"),
    "m_dark_jr_yeti": ("검은 설분이 몸 둘레를 닫는 낮은 은폐 소용돌이", "설야 남회 #343A4B", "냉기 보라 #77769B", "검은 눈소용돌이 + 희미한 발자국"),
    "m_hector": ("늑대 발톱 세 갈래가 눈가루를 베어내는 전방 참격", "설원 회청 #798D9F", "눈가루 백색 #ECFAFF", "세 갈래 늑대발톱 + 눈가루"),
    "m_white_fang": ("송곳니 두 개가 얼음 능선처럼 교차하는 빙설 타격", "빙설 백청 #C9F2FF", "심빙 청색 #4E9CC8", "교차 송곳니 + 얼음 조각"),
    "m_snow_witch": ("마녀의 굽은 설풍 고리가 눈결정을 끌어당기는 폭풍", "눈보라 백청 #E2F8FF", "마녀 보라 #77638D", "굽은 설풍 고리 + 눈결정"),
    "m_bubble_fish": ("물고기 비늘광이 비치는 둥근 기포 보호막", "기포 청록 #62D4D3", "비늘 은청 #D2FAFF", "큰 기포막 + 비늘 반사광"),
    "m_mask_fish": ("가면 눈구멍 모양의 감지광과 동심 수중 파문", "가면 백회 #C9C6BA", "심해 청색 #356C91", "가면 눈구멍 + 감지 파문"),
    "m_squid": ("농도 높은 먹물핵이 물속에서 둥글게 폭발하는 검은 구름", "먹물 흑남 #202A42", "심해 자주 #625079", "먹물핵 + 둥근 심해 폭발"),
    "m_shark": ("이빨 톱니가 둘린 압축 수류탄과 기포 꼬리", "상어 청회 #4E7890", "폭발 청백 #AEEAF4", "이빨 수류탄 + 기포 꼬리"),
    "m_pianus": ("심해 왕관형 발광기관에서 뻗는 굵은 수평 광선", "심해 청자 #235D79", "광선 백청 #BDF7FF", "심해 왕관핵 + 수평 광선"),
    "m_ratz": ("작은 태엽 톱니가 빠르게 맞물리는 민첩 잔상", "태엽 황동 #B88A4A", "쥐회색 #85827F", "작은 톱니 + 두 줄 속도선"),
    "m_drumming_bunny": ("장난감 북면에서 퍼지는 둥근 진동륜과 태엽 별조각", "북 적색 #C9574C", "장난감 금색 #E9C75C", "북면 + 동심 진동륜"),
    "m_bloctopus": ("사각 블록 표면이 주변 색으로 바뀌며 흐려지는 위장막", "블록 청보라 #6675A8", "위장 반투명색 #B8D6D2", "사각 블록 + 흐림 격자"),
    "m_king_bloctopus": ("왕관 블록이 회전하며 각진 에너지 조각을 발사하는 탄", "왕관 금색 #E9C85B", "블록 자주 #765A9F", "왕관 블록 + 각진 탄 궤적"),
    "m_rombot": ("에오스 톱니 코어가 공간을 아래로 휘게 하는 중력 고리", "기계 철회 #5E6873", "중력 보라 #7654A5", "톱니 코어 + 눌린 중력 고리"),
    "m_brown_teddy": ("갈색 솜뭉치가 눌렸다 부푸는 쿠션형 완충막", "테디 갈색 #9A6B49", "솜 크림 #E6D2AF", "솜 쿠션 + 눌림 곡선"),
    "m_toy_trojan": ("목마 바퀴와 태엽이 전방으로 겹치는 장난감 돌진선", "목마 적갈 #A65E46", "태엽 금색 #DDBB58", "목마 머리 + 바퀴 속도선"),
    "m_master_robo": ("정밀 톱니 세 개와 회로선이 동심으로 맞물리는 코어", "기계 은회 #87939E", "회로 청록 #54D0C1", "세 톱니 코어 + 회로선"),
    "m_chronos": ("깨진 시계판 조각과 역회전하는 짧은 시간 궤도", "시간 청보라 #6773B5", "시계 금색 #D9BB62", "깨진 시계판 + 역회전 궤도"),
    "m_timer": ("정지한 시곗바늘에서 각진 시간 충격륜이 터지는 순간", "시계 황동 #C49B52", "정지 청백 #C5EAF3", "멈춘 시곗바늘 + 시간 충격륜"),
    "m_white_sand_rabbit": ("모래를 파고 솟는 원뿔형 굴착탄과 작은 모래알", "백사장 베이지 #DCCB9A", "햇빛 황색 #F5D66D", "모래 원뿔탄 + 굴착 궤적"),
    "m_scarf_plead": ("목도리 끝이 바람결을 읽듯 휘는 얇은 사막 감지선", "목도리 적갈 #B55E4A", "사막 황토 #CDA75F", "휘날린 목도리 + 바람 감지선"),
    "m_meercat": ("모래언덕 아래 숨었다 솟는 두 갈래 매복 흔적", "모래 황갈 #C9A260", "미요캣 갈색 #81604A", "솟는 모래봉 + 숨은 눈빛"),
    "m_sand_dwarf": ("대장장이 망치 문양과 단단히 맺힌 붉은 체력 불씨", "대장간 적갈 #A94F3B", "모래 금색 #D7B565", "망치 문양 + 붉은 체력핵"),
    "m_deo": ("선인장 가시가 원형으로 벌어지며 모래와 함께 폭발", "선인장 녹색 #568C4C", "사막 황금 #D9B45E", "선인장 가시핵 + 모래 폭발"),
    "m_cube_slime": ("투명 연금 큐브가 점액처럼 휘며 겹치는 사각 보호막", "연금 청록 #5AC6AF", "큐브 백청 #CFF8EA", "투명 큐브 + 점액 모서리"),
    "m_mithril_mutae": ("미스릴 판이 육각으로 포개지고 표면에 차가운 반사광", "미스릴 은청 #8FB3C6", "연금 청백 #D4F2F5", "육각 미스릴판 + 냉광"),
    "m_homun": ("금 간 플라스크에서 새는 자주빛 독무와 액체 방울", "독무 자주 #7E4C8F", "약액 녹색 #83B85B", "금 간 플라스크 + 독무"),
    "m_roid": ("알카드노 금속 코어가 압축한 직선 에너지탄", "알카드노 청회 #526D7F", "에너지 청록 #4DD1C0", "금속 코어 + 직선 에너지탄"),
    "m_chimera": ("서로 다른 산성액 두 줄기가 합쳐져 터지는 포격탄", "산성 녹색 #7BC34D", "연금 황색 #D9E66A", "쌍 산성관 + 포격 폭발"),
    "m_straw_dummy": ("짚 매듭이 흔들려도 중심을 되찾는 균형 고리", "짚 황금 #C9A44F", "수련 적갈 #9C5A45", "짚 매듭 + 균형 수평선"),
    "m_wooden_dummy": ("나무 팔축이 원형으로 휘두르는 회전 궤적과 톱밥", "목인 갈색 #8B613D", "충격 황토 #D1A65A", "나무 팔축 + 원형 타격선"),
    "m_peach_monkey": ("천도 복숭아가 잎사귀 꼬리를 달고 포물선으로 날아가는 탄", "천도 분홍 #F09691", "복숭아잎 녹색 #6FA45A", "복숭아 + 잎사귀 포물선"),
    "m_blue_flower_serpent": ("푸른 꽃잎 비늘이 뱀의 S자 곡선으로 포개지는 방호결", "청화 청색 #4D92C6", "꽃잎 백청 #C8E7EE", "S자 꽃비늘 + 푸른 꽃잎"),
    "m_tae_roon": ("두 권격이 마주 회전해 만드는 쌍둥이 바람 소용돌이", "권풍 청록 #53B9AA", "도원 금빛 #E3C66B", "쌍 주먹 바람눈 + 회전선"),
    "m_harp": ("하프 깃털이 부드러운 공기결을 타고 펼쳐지는 날개 잔상", "깃털 청백 #C8E3EE", "둥지 녹청 #659C92", "큰 깃털 + 바람결"),
    "m_blood_harp": ("핏빛 깃털이 음파 고리와 함께 떨리는 날카로운 울림", "핏빛 적색 #A93F52", "음파 자주 #76527C", "핏빛 깃털 + 음파 고리"),
    "m_blue_wyvern": ("용의 입김처럼 길게 뻗는 빙결 숨결과 쐐기 얼음", "빙룡 청색 #4B9FD5", "빙결 백청 #D6F6FF", "빙룡 숨결 + 얼음 쐐기"),
    "m_dark_wyvern": ("검은 비늘판 사이에서 붉은 근력맥이 점등되는 강화", "비늘 흑남 #2D3444", "근력 적자주 #9B455D", "검은 비늘 + 붉은 힘맥"),
    "m_manon": ("거대한 용뿔형 불꽃이 겹쳐지는 고열 용화염", "용염 주홍 #E74F2E", "용핵 황금 #FFD35C", "용뿔 화염 + 황금 용핵"),
    "m_memory_monk": ("빛바랜 기억 조각이 염주처럼 천천히 도는 묵상륜", "기억 황갈 #B69A6C", "신전 청백 #BFD7D8", "기억 염주 + 잔잔한 묵상륜"),
    "m_memory_monk_trainee": ("작은 기도 구슬이 모여 앞으로 번지는 파동", "기도 청백 #AFCFD4", "추억 금갈 #C3A46A", "기도 구슬 + 전방 잔파"),
    "m_memory_guardian": ("기억 석판 조각이 방패처럼 겹치는 갑주", "석판 회청 #6F7F82", "기억 금빛 #C9AD70", "기억 석판 방패 + 봉인광"),
    "m_chief_memory_guardian": ("네 방향 석판이 맞물려 완성되는 시간 수호진", "수호 청회 #566E78", "시간 금색 #D5B75E", "십자 석판진 + 시계 고리"),
    "m_dodo": ("빛바랜 기억 조각을 안쪽으로 빨아들이는 검은 포식구", "공허 남흑 #283141", "기억 황백 #D5C9A3", "검은 포식구 + 빨려드는 기억편"),
    "m_mateon": ("외계 수정핵에서 발사되는 둥근 황록 광선탄", "외계 황록 #C8DD59", "우주 청록 #55B9B0", "외계 수정핵 + 광선 꼬리"),
    "m_plateon": ("겹친 외계 장갑판과 조종 회로가 켜지는 방호 구조", "장갑 청회 #5F7182", "회로 연두 #A9D45F", "외계 장갑판 + 회로 점등"),
    "m_mecateon": ("기계 렌즈가 수평으로 조준해 뻗는 분홍 레이저", "레이저 분홍 #EF6E9B", "기계 청회 #63788A", "기계 렌즈 + 수평 레이저"),
    "m_chief_gray": ("큰 뇌파 구체와 작은 연산 노드가 규칙적으로 연결되는 정신망", "정신 보라 #7D67A7", "연산 청백 #A9D8E1", "뇌파 구체 + 연결 노드"),
    "m_zeno": ("외계 코어 주위 공간이 오목하게 접히는 다중 중력륜", "중력 자주 #62458E", "외계 청록 #58C4B8", "외계 코어 + 오목한 중력륜"),
    "m_official_knight_c": ("번개가 감긴 두 번의 연속 발차기 궤적", "뇌전 청백 #89DFF2", "기사 금색 #D8B65A", "쌍 발차기 호 + 번개 갈래"),
    "m_official_knight_d": ("바람 깃이 한 점으로 모이는 조준선과 화살표형 압축광", "바람 청록 #64C7B3", "기사 은백 #D7E4E2", "바람 깃 + 조준 십자"),
    "m_advanced_knight_a": ("그림자 망토 끝이 여러 위치로 갈라지는 민첩 잔상", "그림자 남보라 #2D2B46", "기사 자주 #755A8F", "갈라진 망토 + 세 겹 잔상"),
    "m_advanced_knight_b": ("이프리트 뿔을 닮은 화염 두 갈래와 기사 문양", "이프리트 적주황 #DD4F32", "기사 금색 #E3BF5F", "불꽃 뿔 + 기사 문양"),
    "m_cygnus": ("검게 시든 정원 꽃잎이 왕관형 소용돌이를 이루는 장막", "타락 자주 #68456E", "시든 장미 적색 #9E4555", "검은 꽃왕관 + 시든 꽃잎 소용돌이"),
    "m_mutant_dark_stump": ("뒤틀린 나이테 껍질이 겹쳐지고 검은 수액이 굳는 방호층", "변이 흑갈 #41363A", "검은 수액 자주 #70465E", "뒤틀린 나이테 + 굳은 수액"),
    "m_mutant_iron_hog": ("두꺼운 철갑 주둥이가 전방을 가르며 황야 먼지를 뿜는 돌진", "철갑 암회 #4F5B61", "황야 적갈 #A65F44", "철갑 코어 + 전방 속도선"),
    "m_mutant_stone_mask": ("깨진 석면 조각과 발굴지 문양이 겹치는 암석 방호", "석면 회갈 #777067", "발굴 황토 #B9945B", "갈라진 돌가면 + 발굴 먼지"),
    "m_ancient_dark_golem": ("고대 암석 균열이 지면을 가로지르며 검은 돌기둥을 세우는 지진", "고대 흑암 #35343B", "균열 적갈 #A55A43", "균열 지면 + 암흑 돌기둥"),
    "m_mutant_stumpy": ("검은 뿌리가 묘비처럼 솟아 서로 얽히는 묘지 형상", "묘지 흑갈 #383234", "변이 자주 #704B68", "묘비형 뿌리 + 검은 흙먼지"),
}


STYLE_RULE = (
    "RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY를 사실상의 최신 우선 스타일 세트로 "
    "사용한다. UNKNOWN과 LEGACY_REFERENCE는 비교·보조 참고이며 최종 렌더링 우선순위가 아니다."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_bullet(text: str, label: str, value: str) -> str:
    pattern = rf"(?m)^- {re.escape(label)}:.*$"
    replacement = f"- {label}: {value}"
    updated, count = re.subn(pattern, replacement, text)
    if count != 1:
        raise RuntimeError(f"Expected one bullet '{label}', found {count}")
    return updated


def fixed_value(text: str, label: str) -> str:
    match = re.search(rf"(?m)^- {re.escape(label)}:\s*(.+?)\s*$", text)
    if not match:
        raise RuntimeError(f"Missing fixed field: {label}")
    return match.group(1).strip().strip("`").strip("*")


def layout_for(skill_type: str, skill_name: str, effect: str, motion: str, material: str) -> tuple[str, str, str]:
    joined = f"{skill_name} {effect} {motion}"
    if skill_type == "패시브":
        return (
            f"‘{skill_name}’의 {material}을 시전자 몸 둘레의 닫힌 윤곽에 고정하며 실제 주 산출물은 아이콘 중심",
            f"{material}의 대표 결만 바깥으로 8~15% 맥동하고 이동 궤적은 만들지 않음",
            f"확정 효과 ‘{effect}’의 시전자 자신만 표시하며 현행 런타임에 없는 공격·투사체·새 버프 연출을 암시하지 않음",
        )
    if skill_type == "버프":
        return (
            f"시전자 발밑과 몸통 중심을 잇는 세로 피봇에서 ‘{skill_name}’의 {material}이 닫힌 강화 형상으로 발생",
            f"{material}이 아래에서 위로 감싸며 1회 맥동한 뒤 같은 중심에서 소멸하고 화면을 횡단하지 않음",
            f"확정 효과 ‘{effect}’의 시전자 자신만 감싸며 다른 몬스터·플레이어 실루엣은 넣지 않음",
        )
    if "미끄럼길" in joined:
        return (
            f"시전자 발밑 바로 앞에서 ‘{skill_name}’의 {material}이 낮은 지면 접촉선으로 시작",
            f"{material}의 긴 축이 오른쪽으로 미끄러지듯 늘어나고 끝부분 물방울만 뒤따라 소멸",
            f"확정 효과 ‘{effect}’의 반경 안 다중 대상을 낮은 점액 파문과 작은 접촉광으로 구분",
        )
    if any(k in joined for k in ("돌진", "맹진", "연각", "회전타", "휘두르기", "발톱", "송곳니")):
        return (
            f"시전자 전방 15% 지점에서 ‘{skill_name}’의 {material}이 시작되어 발밑 높이와 공격축을 맞춤",
            f"{material}이 오른쪽으로 압축·가속하고 충돌점에서 짧게 넓어진 뒤 반대 방향 파편 없이 소멸",
            f"확정 효과 ‘{effect}’의 전방 피격 대상과 최초 충돌점을 표시하고 타격광은 대상 중심을 가리지 않는 외곽 고리로 제한",
        )
    if any(k in joined for k in ("탄", "광선", "레이저", "포격", "숨결", "용염", "투척", "생기탄")):
        return (
            f"시전자 전방 발사 피봇에서 ‘{skill_name}’의 {material}이 완성되며 몬스터 본체 자리는 비워 둠",
            f"{material}이 오른쪽 한 방향으로 이동하고 꼬리·잔상은 발사점 쪽에만 남김",
            f"확정 효과 ‘{effect}’의 전방 피격 대상과 충돌점을 표시하며 발사체 실루엣과 충돌광을 서로 다른 프레임으로 분리",
        )
    if any(k in joined for k in ("폭발", "충격", "지진", "낙뢰", "폭풍", "눈보라", "파동", "진", "무덤", "묘지", "살포", "독무", "뿌리", "회전", "포식")):
        return (
            f"시전자 또는 지정 충돌점의 지면 중심에서 ‘{skill_name}’의 {material}이 먼저 식별되도록 발생",
            f"{material}이 중심에서 방사 또는 수직으로 확장하고 절정 뒤 파편은 원점으로 되감기지 않음",
            f"확정 효과 ‘{effect}’의 범위 안 대상만 표시하며 중심 타격광과 바깥 범위 경계를 분리해 다중 피격을 읽히게 함",
        )
    return (
        f"시전자 몸통 중심과 발밑 사이의 고정 피봇에서 ‘{skill_name}’의 {material}이 먼저 나타남",
        f"{material}의 고유 결을 따라 한 번 확장·수축하며 불필요한 화면 횡단은 하지 않음",
        f"확정 효과 ‘{effect}’가 지정한 대상만 표현하고 몬스터·플레이어 본체 실루엣은 넣지 않음",
    )


def patch_generation_spec(text: str) -> str:
    monster_id = fixed_value(text, "monster_id")
    monster_name = fixed_value(text, "몬스터 이름")
    skill_name = fixed_value(text, "최종 스킬 이름")
    skill_type = fixed_value(text, "스킬 타입")
    effect = fixed_value(text, "실제 현재 효과")
    motion = fixed_value(text, "실제 현재 동작")
    if monster_id not in VISUALS:
        raise RuntimeError(f"No explicit visual translation for {monster_id}")
    material, primary, secondary, icon = VISUALS[monster_id]
    origin, direction, target = layout_for(skill_type, skill_name, effect, motion, material)

    text = replace_bullet(text, "핵심 소재", f"{material}. ‘{monster_name} / {skill_name}’ 전용 소재이며 몬스터 본체는 VFX에 직접 넣지 않음")
    text = replace_bullet(text, "주 색상", f"{primary}; 핵심 실루엣의 중간톤과 어두운 외곽에 사용")
    text = replace_bullet(text, "보조 색상", f"{secondary}; 타격 코어·잔상·소수 입자에만 사용해 같은 Area의 다른 몬스터와 구분")
    text = replace_bullet(text, "효과 발생 위치", origin)
    text = replace_bullet(text, "진행 방향", direction)
    text = replace_bullet(text, "대상 표현", target)

    occupancy = fixed_value(text, "화면 점유율").split(";", 1)[0]
    density = fixed_value(text, "이펙트 밀도").split(";", 1)[0]
    text = replace_bullet(text, "화면 점유율", f"{occupancy}; 핵심 소재 전체가 캔버스 안전영역 70% 안에 들고 외곽 파편은 85%를 넘지 않음")
    text = replace_bullet(text, "이펙트 밀도", f"{density}; 대표 형상 1개, 보조 궤적/층 1~3개, 식별용 파편 3~7개만 사용")
    text = replace_bullet(text, "아이콘 핵심 모티브", f"대표 실루엣 1개는 ‘{icon.split(' + ')[0]}’, 보조 효과 1개는 ‘{icon.split(' + ')[1]}’. 64px 축소에서도 두 형상의 겹침과 방향이 읽혀야 함")

    marker = "## 출력 프로필"
    policy = (
        f"\n- 스타일 적용 우선순위: {STYLE_RULE} 전체 라이브러리는 유지하되 최종 판단은 최신 메이플스토리/MSW 시각 문법을 우선함.\n"
    )
    if "- 스타일 적용 우선순위:" not in text:
        text = text.replace(marker, policy + "\n" + marker)

    output_marker = "## 해석 주의"
    delivery = (
        "\n- 주 VFX 납품물: F00, F01, F02 ... 순서의 프레임 분리형 개별 RGBA PNG가 필수다.\n"
        "- contact sheet 또는 sprite sheet는 선택적 검수 미리보기일 뿐이며 주 납품물로 인정하지 않는다.\n"
    )
    if "- 주 VFX 납품물:" not in text:
        text = text.replace(output_marker, delivery + "\n" + output_marker)
    return text


def patch_style_atlas(text: str) -> str:
    text = re.sub(
        r"## 적용 우선순위\s+.*?## 프레임 리듬",
        "## 적용 우선순위\n\n"
        "1. WHAT은 각 몬스터 GENERATION_SPEC의 확정 이름·타입·효과·동작이며 변경하지 않는다.\n"
        "2. RECENT_PRIMARY가 1개 이상이면 RECENT_PRIMARY → RECENT_SECONDARY 순으로 최신 시각 문법을 판단한다.\n"
        "3. **RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY를 사실상의 최신 우선 스타일 세트로 간주한다.**\n"
        "4. UNKNOWN과 LEGACY_REFERENCE는 비교·보조 참고 자료이며 최종 렌더링 우선순위가 아니다.\n"
        "5. 전체 기존 스킬 라이브러리는 삭제하지 않고 유지하되, 최종 아트 판단은 최신 메이플스토리/MSW 시각 문법을 우선한다.\n"
        "6. 최신 우선 세트에서는 어두운 외곽, 중간톤 형상, 밝은 코어, 발광·반투명 층, 절정 타격광, 자연스러운 fade를 참고한다.\n"
        "7. 레거시는 저레벨 규모와 고전 실루엣 비교에만 쓰며 기존 무기·캐릭터·메커니즘·고유 실루엣을 직접 복제하지 않는다.\n\n"
        "## 프레임 리듬",
        text,
        flags=re.S,
    )
    text = text.replace(
        "- 256×256 RGBA, 투명 배경, 한 개의 강한 실루엣, 작은 크기에서도 구별되는 명암.",
        "- 256×256 RGBA, 투명 배경. 각 아이콘은 **대표 실루엣 1개 + 보조 효과 1개**로 제한하고 64px 축소에서도 구별되게 한다.",
    )
    return text


def patch_style_index(text: str) -> str:
    insertion = (
        "\n## 스타일 적용 우선 규칙\n\n"
        "- RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY를 사실상의 최신 우선 스타일 세트로 간주한다.\n"
        "- UNKNOWN과 LEGACY_REFERENCE는 비교·보조 참고 자료이며 최종 렌더링 우선순위가 아니다.\n"
        "- 전체 기존 스킬 라이브러리는 유지하지만 최종 아트 판단은 최신 메이플스토리/MSW 시각 문법을 우선한다.\n"
        "- EXCLUDE_STYLE은 최종 렌더링 스타일 판단에 사용하지 않는다.\n"
    )
    if "## 스타일 적용 우선 규칙" not in text:
        table_pos = text.find("\n| index |")
        if table_pos < 0:
            raise RuntimeError("STYLE_INDEX table not found")
        text = text[:table_pos] + insertion + text[table_pos:]
    return text


def patch_master(text: str) -> str:
    text = re.sub(
        r"(?m)^2\. .*?$",
        "2. `global_skill_style_library`의 **전체** STYLE_INDEX, STYLE_ATLAS, skills/*/preview.png를 분석하세요. RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY를 사실상의 최신 우선 스타일 세트로 사용하세요. UNKNOWN과 LEGACY_REFERENCE는 비교·보조 참고이며 최종 렌더링 우선순위가 아닙니다. 전체 라이브러리는 유지하되 최종 아트 판단은 최신 메이플스토리/MSW 시각 문법을 우선하세요.",
        text,
    )
    text = re.sub(
        r"(?m)^8\. .*?$",
        "8. VFX 주 납품물은 반드시 `F00`, `F01`, `F02` ... 형식의 **프레임 분리형 개별 PNG**여야 합니다. PNG, RGBA, 실제 alpha 투명 배경, 체커보드 금지, 빈 프레임 금지, 프레임 누락 금지, 동일 캔버스·동일 중심축, 임의 크롭 금지, 우측 기준(FlipX 가능)을 지키세요.",
        text,
    )
    text = re.sub(
        r"(?m)^10\. .*?$",
        "10. `OUTPUT_NAMING_SPEC.md`와 `OUTPUT_FORMAT_SPEC.md`를 정확히 따르세요. contact sheet 또는 sprite sheet는 선택적 검수 미리보기일 뿐이며 주 납품물이 아닙니다. 가능하면 프레임 분리형 결과 전체를 Area OUTPUT ZIP으로 반환하세요.",
        text,
    )
    return text


def patch_readme(text: str) -> str:
    needle = "5. 결과는 OUTPUT_NAMING_SPEC/OUTPUT_FORMAT_SPEC를 따른다."
    replacement = (
        "5. 결과는 OUTPUT_NAMING_SPEC/OUTPUT_FORMAT_SPEC를 따른다.\n"
        "6. VFX 주 납품물은 F00, F01, F02 ... 형식의 프레임 분리형 RGBA PNG이며 반드시 모두 제공한다.\n"
        "7. contact sheet/sprite sheet는 선택적 검수 미리보기일 뿐 주 납품물이 아니다.\n"
        "8. RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY를 사실상의 최신 우선 스타일 세트로 사용한다. UNKNOWN/LEGACY_REFERENCE는 비교·보조용이다."
    )
    if "contact sheet/sprite sheet" not in text:
        text = text.replace(needle, replacement)
    return text


def naming_spec(area_code: str) -> str:
    return f"""# Output Naming Spec

출력 루트: `{area_code}_IMAGES_OUTPUT/`

## 필수 주 납품물

- VFX는 반드시 프레임 분리형 개별 RGBA PNG로 납품한다.
- 이름: `NNN_[monster_id]_[skill_id]_F00.png`, `F01.png`, `F02.png` ...
- `F00`부터 GENERATION_SPEC의 마지막 프레임까지 번호를 끊거나 건너뛰지 않는다.
- 아이콘: `NNN_[monster_id]_[skill_id]_ICON.png`
- NNN은 AREA_MANIFEST의 작업 순번 3자리다.
- monster_id와 skill_id를 축약하거나 번역하지 않는다.

## 선택적 미리보기

- contact sheet 또는 sprite sheet는 검수 편의를 위한 선택적 preview만 허용한다.
- 선택 파일명: `NNN_[monster_id]_[skill_id]_CONTACT_PREVIEW.png`
- sheet는 주 납품물이 아니며 개별 `F00...` 파일을 대체할 수 없다.

```text
{area_code}_IMAGES_OUTPUT/
├─ OUTPUT_MANIFEST.md
├─ OUTPUT_MANIFEST.csv
└─ monsters/
   ├─ 001_[monster_id]_[name]/
   │  ├─ VFX/
   │  │  ├─ 001_[monster_id]_[skill_id]_F00.png
   │  │  ├─ 001_[monster_id]_[skill_id]_F01.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 001_[monster_id]_[skill_id]_ICON.png
   │  ├─ PREVIEW/  # 선택 사항
   │  └─ RESULT_INFO.md
   └─ ...
```
"""


FORMAT_SPEC = """# Output Format Spec

## 필수 주 납품 형식

- **frame-separated PNG files are mandatory.** VFX의 주 산출물은 `F00`, `F01`, `F02` ... 형식의 개별 RGBA PNG 프레임이다.
- **contact sheet is optional preview only. sprite sheet is not the primary deliverable.** 시트는 개별 프레임을 대체할 수 없다.
- PNG, RGBA, 실제 alpha 투명 배경. 흰색/검정/체커보드 배경 금지.
- 프레임마다 동일 캔버스, 동일 중심축/피봇, 동일 스케일. 임의 크롭·재중앙화 금지.
- 우측 진행 기준으로 제작하고 런타임 FlipX를 고려한다.
- one-shot. 빈 프레임과 누락 프레임 금지. `F00`부터 끝 프레임까지 연속 번호를 사용한다.
- ICON은 256×256 RGBA PNG 1장, 글자·숫자·UI 프레임·몬스터 본체 금지.

## 표준 규격군

| Profile | 필수 개별 VFX frames | Canvas/frame | Timing | 용도 |
|---|---:|---:|---:|---|
| LOW_ACTIVE | 8 | 256×256 | 0.10s | 저레벨 단일 액티브 |
| MID_AREA_ACTIVE | 8 | 384×384 | 0.10s | 중·고레벨 범위/다중 액티브 |
| BOSS_ACTIVE | 12 | 512×512 | 0.08s | 보스급 액티브 |
| BUFF_SELF | 8 | 256×256 | 0.10s | 자기 중심 버프 |
| PASSIVE_ICON_MOTIF | 6 | 256×256 | 0.10s | 현행 런타임 미적용 참고 모티브 + 아이콘 |

달팽이 파일럿의 8 frames / 0.1 sec / Offset X64 Y0은 LOW_ACTIVE 참고값이다. 모든 스킬에 같은 오프셋을 강제하지 않으며 각 개별 프레임 내부의 공통 피봇은 반드시 유지한다.
"""


def rewrite_zip(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path, "r") as zin:
        members = zin.namelist()
        roots = {n.split("/", 1)[0] for n in members if "/" in n}
        if len(roots) != 1:
            raise RuntimeError(f"Unexpected roots in {zip_path.name}: {roots}")
        root_name = next(iter(roots))
        csv_name = f"{root_name}/AREA_MANIFEST.csv"
        md_name = f"{root_name}/AREA_MANIFEST.md"
        before_csv = zin.read(csv_name)
        before_md = zin.read(md_name)
        before_members = set(members)

    with tempfile.TemporaryDirectory(prefix="area_images_correct_", dir=PACKAGES) as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zin:
            zin.extractall(tmp_path)
        package_root = tmp_path / root_name

        generation_specs = sorted(package_root.glob("monsters/*/GENERATION_SPEC.md"))
        if not generation_specs:
            raise RuntimeError(f"No GENERATION_SPEC in {zip_path.name}")
        for spec in generation_specs:
            original = spec.read_text(encoding="utf-8")
            spec.write_text(patch_generation_spec(original), encoding="utf-8", newline="\n")

        atlas = package_root / "global_skill_style_library" / "summary" / "STYLE_ATLAS.md"
        style_index = package_root / "global_skill_style_library" / "STYLE_INDEX.md"
        master = package_root / "CHATGPT_IMAGES_MASTER_PROMPT.md"
        readme = package_root / "README_START_HERE.md"
        atlas.write_text(patch_style_atlas(atlas.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        style_index.write_text(patch_style_index(style_index.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        master.write_text(patch_master(master.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        readme.write_text(patch_readme(readme.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        (package_root / "OUTPUT_NAMING_SPEC.md").write_text(naming_spec(root_name), encoding="utf-8", newline="\n")
        (package_root / "OUTPUT_FORMAT_SPEC.md").write_text(FORMAT_SPEC, encoding="utf-8", newline="\n")

        if (package_root / "AREA_MANIFEST.csv").read_bytes() != before_csv:
            raise RuntimeError(f"Fixed CSV changed before packaging: {zip_path.name}")
        if (package_root / "AREA_MANIFEST.md").read_bytes() != before_md:
            raise RuntimeError(f"Fixed manifest Markdown changed: {zip_path.name}")

        temp_zip = zip_path.with_suffix(".zip.corrected")
        if temp_zip.exists():
            temp_zip.unlink()
        with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
            for file in sorted(package_root.rglob("*")):
                if file.is_file():
                    arcname = f"{root_name}/{file.relative_to(package_root).as_posix()}"
                    zout.write(file, arcname)
        temp_zip.replace(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zout:
        after_members = set(zout.namelist())
        after_csv = zout.read(csv_name)
        after_md = zout.read(md_name)
        if after_csv != before_csv or after_md != before_md:
            raise RuntimeError(f"Manifest invariant failed: {zip_path.name}")
        if after_members != before_members:
            added = sorted(after_members - before_members)
            removed = sorted(before_members - after_members)
            raise RuntimeError(f"Package structure changed in {zip_path.name}: +{added} -{removed}")
    return {
        "zip": zip_path.name,
        "area_code": root_name.removesuffix("_IMAGES_INPUT"),
        "generation_specs": len(generation_specs),
        "manifest_csv_sha256": sha256(before_csv),
        "manifest_md_sha256": sha256(before_md),
        "zip_bytes": zip_path.stat().st_size,
    }


def update_indexes(results: list[dict]) -> None:
    sizes = {row["area_code"].lower().replace("area_", "area_"): row["zip_bytes"] for row in results}
    csv_path = PACKAGES / "ALL_AREAS_INDEX.csv"
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
        fieldnames = list(rows[0].keys())
    for row in rows:
        area_id = row["area_id"]
        row["zip_bytes"] = str(sizes[area_id])
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    md_path = PACKAGES / "ALL_AREAS_INDEX.md"
    text = md_path.read_text(encoding="utf-8")
    for row in rows:
        area_id = row["area_id"]
        pattern = rf"(?m)^(\|\s*\d+\s*\|\s*{re.escape(area_id)}\s*\|.*?\|\s*)\d+(\s*\|\s*\d+\s*\|)"
        text, count = re.subn(pattern, rf"\g<1>{row['zip_bytes']}\g<2>", text)
        if count != 1:
            raise RuntimeError(f"Could not update zip_bytes in index for {area_id}")
    note = (
        "\n## 패키지 보정 메모\n\n"
        "- 기존 확정 데이터와 기본 폴더 구조를 유지한 채 스타일 우선순위, 프레임 분리형 납품 규칙, 몬스터별 시각 번역과 아이콘 지시를 보정했다.\n"
        "- RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY가 사실상의 최신 우선 스타일 세트다. UNKNOWN/LEGACY_REFERENCE는 비교·보조용이다.\n"
        "- VFX 주 납품물은 F00, F01, F02 ... 개별 RGBA PNG이며 contact sheet/sprite sheet는 선택적 검수 미리보기다.\n"
        "- `area_06`은 현재 AreaTable에 존재하지 않는 예약/결번 ID다. 실제 Area 순서는 `sort_order` 1~20으로 연속이며 누락 패키지가 아니다.\n"
    )
    if "## 패키지 보정 메모" in text:
        text = re.sub(r"\n## 패키지 보정 메모\n.*\Z", note, text, flags=re.S)
    else:
        text = text.rstrip() + "\n" + note
    md_path.write_text(text, encoding="utf-8", newline="\n")


def validate(results: list[dict]) -> dict:
    zips = sorted(PACKAGES.glob("AREA_*_IMAGES_INPUT.zip"))
    errors: list[str] = []
    counts = Counter()
    unique_monsters: set[str] = set()
    specs_total = 0
    required_files = {
        "README_START_HERE.md",
        "CHATGPT_IMAGES_MASTER_PROMPT.md",
        "AREA_MANIFEST.md",
        "AREA_MANIFEST.csv",
        "OUTPUT_NAMING_SPEC.md",
        "OUTPUT_FORMAT_SPEC.md",
        "global_skill_style_library/STYLE_INDEX.md",
        "global_skill_style_library/summary/STYLE_ATLAS.md",
    }
    for zip_path in zips:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            root = names[0].split("/", 1)[0] + "/"
            for rel in required_files:
                if root + rel not in names:
                    errors.append(f"{zip_path.name}: missing {rel}")
            manifest = z.read(root + "AREA_MANIFEST.csv").decode("utf-8-sig")
            for row in csv.DictReader(manifest.splitlines()):
                unique_monsters.add(row["monster_id"])
            for rel in ("global_skill_style_library/STYLE_INDEX.md", "global_skill_style_library/summary/STYLE_ATLAS.md", "CHATGPT_IMAGES_MASTER_PROMPT.md"):
                doc = z.read(root + rel).decode("utf-8")
                if "RECENT_PRIMARY" not in doc or "RECENT_SECONDARY" not in doc:
                    errors.append(f"{zip_path.name}: style fallback missing in {rel}")
            fmt = z.read(root + "OUTPUT_FORMAT_SPEC.md").decode("utf-8")
            naming = z.read(root + "OUTPUT_NAMING_SPEC.md").decode("utf-8")
            if "frame-separated PNG files are mandatory" not in fmt:
                errors.append(f"{zip_path.name}: mandatory frame wording missing")
            if "optional preview only" not in fmt or "주 납품물이 아니" not in naming:
                errors.append(f"{zip_path.name}: optional contact sheet rule missing")
            specs = [n for n in names if n.endswith("/GENERATION_SPEC.md")]
            specs_total += len(specs)
            for n in specs:
                doc = z.read(n).decode("utf-8")
                mid = fixed_value(doc, "monster_id")
                if mid not in VISUALS:
                    errors.append(f"{zip_path.name}: unmapped {mid}")
                for label in ("핵심 소재", "주 색상", "보조 색상", "효과 발생 위치", "진행 방향", "대상 표현", "화면 점유율", "이펙트 밀도", "아이콘 핵심 모티브"):
                    if not re.search(rf"(?m)^- {re.escape(label)}:\s*\S", doc):
                        errors.append(f"{zip_path.name}: {mid} missing {label}")
                if "대표 실루엣 1개" not in doc or "보조 효과 1개" not in doc:
                    errors.append(f"{zip_path.name}: {mid} icon motif not concrete")
                if "주 VFX 납품물" not in doc or "사실상의 최신 우선 스타일 세트" not in doc:
                    errors.append(f"{zip_path.name}: {mid} policy missing")

            index_csv = z.read(root + "global_skill_style_library/STYLE_INDEX.csv").decode("utf-8-sig")
            local_counts = Counter(row["style_priority"] for row in csv.DictReader(index_csv.splitlines()))
            if not counts:
                counts.update(local_counts)
            elif counts != local_counts:
                errors.append(f"{zip_path.name}: style counts differ")

    index_csv_path = PACKAGES / "ALL_AREAS_INDEX.csv"
    with index_csv_path.open("r", encoding="utf-8-sig", newline="") as fp:
        index_rows = list(csv.DictReader(fp))
    index_ids = [r["area_id"] for r in index_rows]
    zip_ids = [r["area_code"].lower().replace("area_", "area_") for r in results]
    if set(index_ids) != set(zip_ids):
        errors.append(f"Index/ZIP Area mismatch: index={index_ids}, zips={zip_ids}")
    if len(index_rows) != 20:
        errors.append(f"Expected 20 actual Areas, got {len(index_rows)}")
    if "area_06" in index_ids:
        errors.append("area_06 unexpectedly exists despite missing AreaTable definition")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "areas": len(index_rows),
        "zips_recreated": len(zips),
        "generation_specs": specs_total,
        "unique_monsters": len(unique_monsters),
        "area_placements": specs_total,
        "area_06": "NOT_APPLICABLE_AREA_ID_NOT_IN_CURRENT_AREATABLE",
        "missing_actual_areas": [],
        "style_priority_counts": {
            "RECENT_PRIMARY": counts["RECENT_PRIMARY"],
            "RECENT_SECONDARY": counts["RECENT_SECONDARY"],
            "LEGACY_REFERENCE": counts["LEGACY_REFERENCE"],
            "UNKNOWN": counts["UNKNOWN"],
            "EXCLUDE_STYLE": counts["EXCLUDE_STYLE"],
        },
        "frame_separated_primary": True,
        "contact_sheet_optional_preview_only": True,
        "manifest_invariants": "PASS" if not errors else "FAIL",
        "errors": errors,
        "zip_total_bytes": sum(p.stat().st_size for p in zips),
    }


def main() -> None:
    zips = sorted(PACKAGES.glob("AREA_*_IMAGES_INPUT.zip"))
    if not zips:
        raise SystemExit("No existing Area input ZIPs found")
    results = [rewrite_zip(path) for path in zips]
    update_indexes(results)
    report = validate(results)
    report["packages"] = results
    report_path = PACKAGES / "PACKAGE_CORRECTION_REPORT.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# Area Images Input Package Correction Report",
        "",
        f"- Area: {report['areas']}",
        f"- ZIP 재생성: {report['zips_recreated']}",
        f"- GENERATION_SPEC: {report['generation_specs']}",
        f"- 고유 몬스터: {report['unique_monsters']}",
        f"- area_06: {report['area_06']}",
        f"- 프레임 분리형 주 납품: {report['frame_separated_primary']}",
        f"- contact sheet optional preview only: {report['contact_sheet_optional_preview_only']}",
        f"- 고정 manifest 불변/전체 검증: {report['manifest_invariants']}",
        f"- 오류: {len(report['errors'])}",
        "",
        "## Style priority counts",
        "",
    ]
    for key, value in report["style_priority_counts"].items():
        md.append(f"- {key}: {value}")
    md += ["", "## Errors", ""] + ([f"- {e}" for e in report["errors"]] or ["- 없음"])
    (PACKAGES / "PACKAGE_CORRECTION_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    if report["errors"]:
        raise SystemExit(json.dumps(report["errors"], ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "packages"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
