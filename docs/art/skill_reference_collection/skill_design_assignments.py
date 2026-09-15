"""Manually selected after inspecting the real official preview frames, 2026-09-13.
Selections concern rendering technique; target WHAT remains in GENERATION_SPEC.
"""
# key: exact visual roles, observed feature, excluded source-specific content
SOURCES = {
'water': ('hit/0', '얇은 물 테두리와 밝은 물방울이 터진 뒤 분리되어 사라지는 단계', '원형 타격 모양을 모든 물 스킬의 기본 모양으로 강제하지 않는다'),
'water_shield': ('repeat', '투명한 내부와 두꺼운 푸른 테두리, 국소 반사점이 분리된 물막', 'effect의 요정 본체는 사용하지 않는다. 구형 모양은 목표 명세가 막일 때만 적용한다'),
'mist': ('special tile', '흐릿한 외곽 안쪽에 덩어리별 농도와 중간톤이 남는 기체 층', '초록 독 색상과 독의 의미를 포자·먹물로 옮기지 않는다'),
'garden': ('hit/0', '꽃잎처럼 분리되는 짧고 밝은 잎 모양 파편과 코어', '원본 꽃 별 모양이나 대형 정원 구성을 복제하지 않는다'),
'curse': ('hit/0', '짙은 보라 외곽 안에서 날카로운 밝은 타격면이 갈라지는 처리', '숫자 1이 있는 mob/1 표식을 참조 입력에서 제외한다'),
'star': ('effect effect1', '밝은 별 코어와 두께가 다른 곡선 층, 마지막 조각의 분산', '원본 초승달 탄 모양과 분홍 팔레트는 고정 명세를 덮어쓰지 않는다'),
'ice': ('effect hit/0', '얼음의 어두운 면·중간 청색 면·흰 모서리와 각진 파쇄', '빙주 낙하를 목표의 다른 동작으로 대체하지 않는다'),
'earth': ('effect effect0', '지면에서 큰 덩어리가 솟고 작은 조각이 뒤따르는 두께와 전개', '파란 소용돌이 무늬를 암석·뿌리 재질로 복제하지 않는다'),
'metal': ('effect_ple/loop effect_ple/end', '단단한 테두리와 내부면이 분리된 방어막, 끝에서 얇아지는 광층', '왕실 방패 모양·황금색·문장을 복제하지 않는다. 목재·솜을 금속으로 바꾸지 않는다'),
'fire': ('effect', '짙은 주황 덩어리와 노란 코어가 분리된 불꽃 가장자리와 분해', '원형 불 문양·룬은 제외하며 목표의 화염 방향을 유지한다'),
'sand': ('keydown keydownend', '모래의 겹친 띠와 농도 차, 큰 흐름 뒤에 남는 가벼운 먼지', '모든 모래 스킬을 원통형 회오리로 바꾸지 않는다'),
'needle': ('effect/0 effect/1 effect/2', '날카로운 유색 면과 어두운 잔상이 분리되는 짧은 절단광', '삼각 베기 덩어리를 침·가시 자체로 복제하지 않는다'),
'lightning': ('effect hit/0', '진한 청색 면·청록 중간층·흰 코어와 짧은 전기 가지', '구형 탄환·마법진 형태를 발차기나 낙뢰에 복제하지 않는다'),
'bubble': ('ball effect', '밝은 내부 코어와 반투명 외피, 진행 방향 쪽의 압축과 후방 잔상', '보라 구체와 후프를 모든 투사체의 모양으로 사용하지 않는다'),
'gale': ('ball', '굵기 다른 회전 바람띠와 띠 사이 빈 공간, 분리된 작은 입자', '수직 회오리와 연두색을 그대로 복제하지 않는다'),
'clock': ('effect hit/0', '시계 고리의 얇은 중간층과 밝은 순간 코어, 갈라진 시간 잔상', '시계 숫자·원본 문양을 에셋에 넣지 않는다. 시계 아닌 기계에 시계판을 추가하지 않는다'),
'smoke': ('tile/0', '연무 내부 밝고 어두운 입자가 겹치면서 외곽이 부드럽게 풀리는 밀도', '화려한 흰 꽃 같은 입자를 포자·먹물의 주 모양으로 가져오지 않는다'),
'punch': ('effect hit', '작은 압축 코어가 전진해 충격면으로 퍼지고 조각으로 풀리는 운동', '공식 주먹·원형 추진체를 목표의 발굽·리본·엄니로 대체 복사하지 않는다'),
'quake': ('tile hit/0', '낮은 지면층의 균열광과 짧은 각진 충격면, 사라지는 잔진', '주황 전기 균열을 모든 지면 재질로 사용하지 않는다'),
'frost_breath': ('keydown keydownend', '앞쪽 얼음 면과 뒤쪽 옅은 냉기 밀도의 차, 종료 시 잔류 냉기', '늑대 머리·원형 발사 문양을 제외하고 호흡 흐름만 새 소재에 구성한다'),
'earth_breath': ('ball/0', '가늘고 긴 전방 코어와 색이 분리된 짧은 후방 잔상', '원본 불색·두 갈래 날을 광선의 고유 모양으로 복제하지 않는다'),
'dragon_fire': ('hit/0', '어두운 연기·주황 외피·노란 폭발 코어가 분리되어 식는 단계', '드래곤 본체가 등장하는 effect를 제외한다. 목표 화염에 별 폭발을 강제하지 않는다'),
'dark_magic': ('effect', '길게 당겨진 어두운 물질과 얇은 보랏빛 코어가 분리되어 소실', '공식 검이나 날 형상을 그대로 복제하지 않는다'),
'sound': ('end keydown', '얇은 진동띠가 겹치고 마지막 잔광이 단계적으로 빠지는 흐름', '음표와 주변 돌 조각을 목표에 추가하지 않는다'),
'dark_barrier': ('effect/0 finish/0', '어두운 반투명 면과 밝은 가장자리의 대비, 막이 약해지는 단계', '노랑 돔과 원본 문양을 커튼·비늘·나무로 복제하지 않는다'),
'nature': ('effect hit/0', '작은 입자군이 코어 주위에서 퍼져 농도와 광량을 함께 잃는 전개', '꽃별 문양과 연두 팔레트를 강제하지 않는다'),
}
# monster id without m_: source keys | target-specific translation, not generic categories.
DATA = '''
snail|water,water_shield|달팽이 껍질의 청록 계열과 명세의 이슬을 구분해 유지한다. 낮게 끌리는 점액 길과 둥근 이슬이 얇아지며 끊겨야 하며 구형 방패로 바꾸지 않는다.
blue_snail|water_shield,metal|파란 껍질의 곡면 두께를 반원 보호막에 옮긴다. 껍질 결을 내부 중간톤에 남기고 짧은 반사광만 강조한다.
red_snail|punch,fire|빨간 껍질 원반이 전방으로 압축되는 순서를 유지한다. 주먹이나 불 마법진 대신 껍질 곡면과 돌진 잔상으로 읽혀야 한다.
mano|water,star|마노의 껍질 계열을 바탕으로 진주빛 낮은 고리와 무지개 파동을 구성한다. 별 탄환으로 바꾸지 않고 동심 파형 끝을 완전하게 닫는다.
slime|water,water_shield|연두 점액이 눌리고 테두리가 되튀는 탄성을 그린다. 액체 내부 두께와 분리 방울을 적용하되 구형 보호막·별 모양 타격으로 바꾸지 않는다.
mushroom|mist,nature|주황 갓의 소재감과 명세 팔레트를 유지한다. 세 포자 구름의 농도·작은 점 입자·분산 간격을 나누며 불꽃이나 독무로 바꾸지 않는다.
mushmom|mist,quake|큰 포자 코어가 낮은 갓 형태로 부풀고 지면 충격 후 포자로 흩어진다. 화염 폭발이나 돌 분화구 대신 포자 덩어리 두께를 유지한다.
horny_mushroom|metal,needle|푸른 회색 뿔의 단단한 쐐기 면과 짧은 반사를 ICON에 압축한다. 칼날이나 왕실 방패를 추가하지 않는다.
stone_golem|earth,metal|회색 석판 두 층의 맞물림과 이끼·균열의 재질 대비를 적용한다. 푸른 파도나 황금 문장을 암석으로 대체하지 않는다.
axe_stump|punch,needle|실제 도끼 부위와 목질을 분리한다. 무거운 전방 호와 나무 조각이 뒤따르는 순서를 짧은 베기 코어로 마감한다.
dark_axe_stump|earth,dark_magic|나무 밑동에서 검은 뿌리 발톱이 위로 솟는다. 보라 흙먼지는 보조이며 에너지 검으로 바꾸지 않는다.
wild_boar|punch,sand|두 엄니 방향이 전방으로 모이며 압축 충격을 만든다. 갈색 먼지는 뒤에만 남기고 회오리나 주먹을 넣지 않는다.
iron_hog|punch,metal|철갑의 어두운 판면과 밝은 모서리를 강철 발굽 초승달 충격에 옮긴다. 작은 금속 가루가 지면을 따라 풀린다.
skeleton_commander|earth,quake|뼈 기둥이 비스듬히 솟고 무덤 흙이 떨어진다. 기사의 몸이나 탈것·금속 방패 대신 뼈의 밝은 면과 틈 그림자를 보존한다.
fire_boar|fire,punch|낮은 불꽃 혀가 앞으로 말리는 화염 돌풍이다. 뒤따르는 소수 불씨와 순간 코어를 분리하고 거대한 원형 불 문양을 넣지 않는다.
stumpy|nature,bubble|나이테 새싹이 빛나는 씨앗으로 압축되어 발사된다. 구체 광층은 씨앗 두께에 적용하고 외계 탄환이나 문양으로 바꾸지 않는다.
dark_stump|metal,dark_barrier|나이테가 있는 어두운 목질 방패와 짧게 박힌 뿌리를 유지한다. 방어막 참조의 면 분리만 목재로 번역하며 바위·황금 방패를 만들지 않는다.
bubbling|water_shield,bubble|푸른 물방울 외피 안의 마력과 작은 기포 궤도를 ICON에 압축한다. 얼굴을 넣거나 구체 주위에 불필요한 무기를 추가하지 않는다.
fairy|nature,garden|작은 날개의 소재 연결은 보조로 두고 별가루가 나선으로 모였다 흩어지는 흐름을 만든다. 굵은 광선이나 날개 달린 캐릭터로 바꾸지 않는다.
faust|curse,needle|실에 묶인 인형 표식과 떨어지는 가느다란 저주 침이 구분되어야 한다. 숫자 표식·공식 삼각 칼날·실제 인형 캐릭터는 넣지 않는다.
octopus|mist,water|짙은 남청색 먹물 방울이 불규칙한 꽃잎 같은 면으로 튄다. 물빛 반사보다 먹물의 불투명 코어와 얇은 끝을 우선한다.
stirge|sound,dark_magic|박쥐의 몸 대신 얇은 야간 음파와 작은 붉은 감지점을 ICON에 담는다. 음표·큰 회오리·검 모양은 제외한다.
jr_wraith|water_shield,curse|차가운 반투명 손자국이 나타나 짧게 충격을 남기고 풀린다. 유령 본체 대신 손자국 경계의 두께 차를 사용한다.
wraith|dark_magic,water_shield|굽은 영혼 리본의 반투명 내부와 작은 혼불의 코어를 분리한다. 칼날·물방울로 모양이 바뀌지 않게 한다.
shade|dark_barrier,dark_magic|빛을 흡수하는 얇은 장막과 보라 가장자리를 보존한다. 노란 반구 방패 대신 세로로 늘어지는 커튼의 실루엣을 만든다.
ribbon_pig|punch,star|분홍 매듭이 풀려 앞으로 나가는 리본의 앞뒤 면과 돌진 리듬을 만든다. 불주먹이나 초승달 탄환을 복제하지 않는다.
blue_pig|metal,star|푸른 리본 매듭이 층을 이루며 조이는 고리다. 리본의 접힘 그림자를 유지하고 딱딱한 금속 방패로 바꾸지 않는다.
starfish|star,water|다섯 가시가 읽히는 회전과 짧은 수중 궤적을 만든다. 내부에 또 다른 별 문양을 겹치거나 공식 초승달 실루엣으로 바꾸지 않는다.
jellyfish|water_shield,ice|차가운 젤리가 늘어나고 되튈 때 가장자리만 서리처럼 밝힌다. 단단한 빙주로 몸통 재질을 대체하지 않는다.
king_clang|water,punch|양쪽 집게가 닫힌 뒤 넓은 파도 마루가 퍼지는 순서다. 껍질 본체 대신 집게 방향성과 물의 층을 결합한다.
zombie_mushroom|mist,nature|마른 포자 덩어리와 낮은 생기 불빛을 ICON에 담는다. 독의 녹색 농도를 자동으로 복사하거나 불씨로 대체하지 않는다.
copper_drake|metal,earth|겹친 청동 비늘 판의 어두운 홈과 금속 모서리를 유지한다. 황금 방패나 바위 덩어리를 직접 넣지 않는다.
drake|fire,dragon_fire|좁은 출구에서 넓어지는 붉은 동굴 브레스다. 밝은 코어 뒤로 어두운 연무가 식되 드래곤 본체나 별 폭발은 제외한다.
wild_kargo|needle,dark_magic|세 검은 발톱이 낮게 앞으로 긁고 그림자 잔상이 짧게 풀린다. 삼각 칼날 한 덩어리로 합치지 않는다.
jr_balrog|fire,dragon_fire|뿔을 연상시키는 화염 고리가 전방 파동으로 열린다. 고리의 방향과 내부 밝기 차만 사용하고 룬·드래곤 본체를 넣지 않는다.
tauromacis|lightning,metal|미궁 수문장 표식 위로 굵은 청백색 낙뢰가 떨어진다. 둥근 전기탄이나 왕실 문장을 대신 넣지 않는다.
star_pixie|star,bubble|별 코어 뒤로 곧은 꼬리가 남는 탄환을 유지한다. 픽시 모자나 얼굴 없이 별의 굵은 중심과 가는 잔상으로 구분한다.
jr_cellion|fire,nature|붉은 뿔끝의 활력과 압력 고리를 ICON으로 읽히게 한다. 불 마법진이나 동물 얼굴이 주제가 되지 않게 한다.
lunar_pixie|star,bubble|초승달이 드러난 달 구체와 은빛 궤도를 유지한다. 공식 분홍 탄의 장식을 복제하지 않고 달의 명암 면을 분리한다.
luster_pixie|star,garden|작은 태양 코어에서 양쪽으로 벌어지는 금빛 잔상을 만든다. 꽃잎 자체가 주제가 되거나 거대한 날개 본체로 바뀌지 않는다.
eliza|gale,garden|잎과 꽃잎이 나선 폭풍을 구성하되 큰 바람층과 잎 파편은 따로 읽히게 한다. 연두 원통 회오리 한 개로 축약하지 않는다.
jr_yeti|nature,ice|따뜻한 둥근 코어 곁의 작은 눈 결정이 녹는 소재를 ICON으로 압축한다. 추위 공격이나 꽃 문양으로 바꾸지 않는다.
dark_jr_yeti|sand,dark_magic|검은 눈가루가 낮게 감추는 소용돌이를 ICON에 표현한다. 갈색 모래나 에너지 검으로 재질을 바꾸지 않는다.
hector|needle,ice|세 늑대 발톱이 전방으로 긁고 눈가루가 늦게 떨어진다. 얼음 기둥이나 삼각 참격 덩어리를 주제로 넣지 않는다.
white_fang|ice,punch|두 송곳니가 교차한 얼음 능선의 순간 충격을 만든다. 두 방향을 읽히게 하고 단순 원형 타격으로 바꾸지 않는다.
snow_witch|gale,ice|갈고리처럼 휘는 바람이 얼음 결정을 끌어들인다. 회오리 빈 공간과 결정의 단단한 면을 분리하고 마녀 본체를 넣지 않는다.
bubble_fish|water_shield,water|기포막의 반사와 비늘 같은 무지개 광층을 구분한다. 투명 내부를 유지하고 얼굴이나 물요정을 넣지 않는다.
mask_fish|sound,water_shield|가면 눈의 감지점을 중심으로 수중 동심파를 ICON에 압축한다. 실제 물고기 얼굴·음표 대신 감지 모티브만 남긴다.
squid|mist,water|농밀한 먹물 코어가 수중 검은 구름으로 터진다. 부드러운 외곽과 응집한 중앙을 나누며 하얀 포자나 불꽃으로 바꾸지 않는다.
shark|bubble,water|이빨처럼 날카로운 압축 수류의 앞부분과 기포 꼬리를 유지한다. 둥근 보라 구슬이나 상어 본체가 되면 안 된다.
pianus|earth_breath,water|왕관 같은 발광기관 모티브에서 두꺼운 수평 광선이 이어진다. 가는 붉은 불칼을 복제하지 말고 수중 광량과 폭을 명세대로 만든다.
ratz|clock,metal|작은 태엽 기어의 빠른 맞물림과 민첩 잔상을 ICON에 담는다. 시계판·숫자·총을 넣지 않는다.
drumming_bunny|sound,clock|북판의 둥근 진동과 태엽 별이 순차적으로 퍼진다. 음표나 시계판 대신 북 진동의 두께와 간격을 읽히게 한다.
bloctopus|metal,water_shield|네모 블록의 면이 색을 바꾸며 위장하는 ICON이다. 구형 기포나 금속 방패로 사각 소재를 바꾸지 않는다.
king_bloctopus|bubble,metal|왕관 블록이 회전하는 각진 에너지탄을 만든다. 블록의 평면과 모서리, 후방 꼬리를 나누고 구형 탄으로 바꾸지 않는다.
rombot|clock,dark_barrier|기어 코어 아래로 공간이 눌리고 중력 고리가 겹친다. 시계 숫자·황금 날개·총·로봇 본체를 넣지 않는다.
brown_teddy|water_shield,metal|갈색 솜 쿠션이 눌렸다 부푸는 부드러운 방어 형태다. 딱딱한 방패나 유리 기포로 재질을 대체하지 않는다.
toy_trojan|punch,metal|나무 바퀴와 태엽의 전방 돌진을 재질 면과 잔상으로 구분한다. 목마 본체·주먹·총을 넣지 않는다.
master_robo|clock,metal|세 정밀 기어와 동심 회로가 ICON에서 구분되어야 한다. 시계판 숫자나 단일 황금 방패를 복제하지 않는다.
chronos|clock,dark_magic|깨진 시계판 조각이 짧게 역행하는 궤도를 만든다. 시간 잔상을 쓰되 숫자·유령 본체·황금 날개를 넣지 않는다.
timer|clock,punch|멈춘 시곗바늘과 각진 충격 고리가 순간 정지 후 해체된다. 같은 시계 일러스트를 확대하는 것으로 애니메이션을 대신하지 않는다.
white_sand_rabbit|sand,bubble|모래 알갱이가 원뿔 굴착탄으로 모여 앞으로 나간다. 원통 회오리나 둥근 보라 구체로 대체하지 않는다.
scarf_plead|gale,sand|목도리 끝에서 이어지는 얇은 바람 감지선을 ICON에 담는다. 커다란 토네이도나 모래폭풍으로 만들지 않는다.
meercat|earth,sand|두 모래 매복 흔적이 지면에서 솟는 간격을 유지한다. 파란 물결이나 한 개 거대 회오리로 합치지 않는다.
sand_dwarf|metal,nature|대장장이 망치 표식과 붉은 체력 불꽃을 ICON으로 구성한다. 왕실 방패·꽃 문양을 복제하지 않는다.
deo|sand,needle|선인장 가시가 방사형으로 터지며 모래가 뒤따른다. 굵은 삼각 참격이나 회오리 한 개로 만들지 않는다.
cube_slime|water_shield,metal|투명 연금 큐브의 네모 모서리가 휘어지는 젤리 방어막이다. 구형 기포로 바꾸지 않고 큐브의 앞뒤 면 두께를 구분한다.
mithril_mutae|metal,ice|미스릴 육각판의 차가운 반사와 겹침 홈을 ICON에 담는다. 얼음 덩어리·황금 문장 대신 금속판이 먼저 읽혀야 한다.
homun|mist,water|깨진 플라스크의 보라 독무와 액체 방울이 구분된다. 초록 독 색을 복사하지 않고 유리·액체·기체의 경계를 나눈다.
roid|bubble,earth_breath|금속 코어가 압축한 직선 에너지탄이다. 총 본체나 마법 후프 대신 작은 단단한 코어와 곧은 잔상을 사용한다.
chimera|water,mist|두 산성 흐름이 합쳐진 뒤 포격으로 터진다. 물빛 소용돌이나 불 폭발로 바꾸지 않고 합류 지점을 밝은 코어로 읽힌다.
straw_dummy|nature,metal|짚 매듭이 균형을 되찾는 고리를 ICON에 담는다. 짚 섬유와 따뜻한 중간톤을 유지하고 금속 문장으로 바꾸지 않는다.
wooden_dummy|punch,needle|목재 팔축이 원운동하며 톱밥이 뒤따른다. 무기 참격 자체 대신 목재 회전면과 짧은 충격을 유지한다.
peach_monkey|bubble,nature|복숭아와 잎 꼬리가 포물선을 그린다. 과육·껍질의 명암을 유지하고 보라 에너지 구체나 꽃 문양으로 바꾸지 않는다.
blue_flower_serpent|metal,garden|푸른 꽃잎 비늘이 S자 곡선을 따라 겹친다. 용 몸체·금속 방패 대신 꽃잎 판의 두께와 겹침으로 방어를 읽힌다.
tae_roon|punch,gale|두 권풍이 따로 압축된 뒤 쌍 회오리를 만든다. 한 개 수직 토네이도나 공식 주먹 실루엣을 복제하지 않는다.
harp|gale,star|깃털과 부드러운 공기 결이 날개 잔상으로 이어지는 ICON이다. 별 탄환·수직 회오리 대신 깃의 얇고 두꺼운 면을 살린다.
blood_harp|sound,star|붉은 깃털이 진동 고리를 남기는 ICON이다. 음표나 초승달보다 붉은 깃의 핵심 모티브를 우선한다.
blue_wyvern|frost_breath,ice|긴 냉기 브레스와 쐐기 얼음 조각을 분리한다. 참조 늑대 머리·마법진·와이번 본체는 생성하지 않는다.
dark_wyvern|metal,dark_barrier|검은 비늘 판 사이 붉은 근력 맥을 만든다. 노란 돔이나 황금 방패로 바꾸지 않고 비늘의 단단한 중간면을 유지한다.
manon|fire,dragon_fire|큰 용뿔 모티브를 따라 고온 화염이 여러 층으로 겹친다. 용 본체는 제외하고 불의 외피·내부·코어를 나눈다.
memory_monk|clock,nature|바랜 기억 조각이 느린 구슬 궤도를 도는 ICON이다. 시계 숫자·꽃 문양 대신 명세 기억 조각을 유지한다.
memory_monk_trainee|star,nature|기도 구슬이 모인 뒤 전방 파동으로 열린다. 별 구체 하나로 고정하지 않고 구슬의 모임과 분산을 읽히게 한다.
memory_guardian|metal,earth|기억 석판이 갑주처럼 겹친다. 회색 석질 내부면과 가장자리 광을 나누며 황금 방패를 복제하지 않는다.
chief_memory_guardian|metal,clock|네 석판이 맞물리는 수호진을 만든다. 시계판·숫자 대신 네 조각의 조립 순서와 보호층을 유지한다.
dodo|dark_magic,clock|검은 구체가 바랜 기억 조각을 안으로 삼킨다. 참조 검·시계판은 제외하고 inward 방향과 어두운 코어를 보존한다.
mateon|bubble,lightning|외계 수정 코어의 둥근 황록 광탄과 꼬리를 분리한다. 푸른 전기탄·마법 후프를 그대로 사용하지 않는다.
plateon|metal,clock|외계 장갑의 겹친 판과 조종 회로를 유지한다. 시계 숫자·왕실 문양·비행체 본체는 제외한다.
mecateon|earth_breath,lightning|기계 렌즈에서 수평 분홍 레이저가 나간다. 원형 구체나 불칼 대신 렌즈 압축광·직선 코어·잔광을 구분한다.
chief_gray|bubble,clock|큰 뇌파 구체와 연결된 작은 연산 노드를 ICON에 담는다. 얼굴·시계 숫자·총 대신 노드 사이 명확한 간격을 만든다.
zeno|dark_barrier,clock|여러 중력 고리가 오목하게 공간을 누르고 되풀린다. 돔 하나나 시계 숫자로 축약하지 않는다.
official_knight_c|lightning,punch|두 번의 발차기 호에 전기 코어와 짧은 가지를 나눈다. 주먹·전기 구슬로 동작을 바꾸지 않는다.
official_knight_d|gale,earth_breath|바람 깃이 초점으로 모이고 조준선이 압축되는 ICON이다. 수직 회오리나 화염탄을 복제하지 않는다.
advanced_knight_a|dark_magic,needle|그림자 망토의 갈라진 위치 잔상을 ICON에 담는다. 기사 본체나 칼날이 주제가 되지 않게 한다.
advanced_knight_b|fire,dragon_fire|이프리트 뿔의 두 불꽃과 기사 표식이 구분되게 만든다. 드래곤 본체·원형 룬·단일 폭발로 대체하지 않는다.
cygnus|gale,dark_magic|시든 검은 정원의 꽃잎이 왕관 같은 와류 장막을 만든다. 거대 검이나 연두 회오리보다 꽃잎과 커튼 층을 유지한다.
mutant_dark_stump|dark_barrier,metal|뒤틀린 나이테와 검게 굳은 수액의 갑질을 만든다. 목질·수액을 노란 마법 돔이나 금속판으로 바꾸지 않는다.
mutant_iron_hog|punch,sand|두꺼운 금속 주둥이 모티브가 전진하고 황무지 먼지가 뒤따른다. 돼지 본체·주먹·회오리는 제외한다.
mutant_stone_mask|earth,metal|깨진 돌 가면과 발굴 흔적이 겹쳐 보호층을 만든다. 실제 얼굴을 재현하지 말고 돌 조각과 음각의 재질을 유지한다.
ancient_dark_golem|earth,quake|고대 암석 균열에서 검은 기둥이 솟고 지진층이 낮게 퍼진다. 푸른 물파도나 주황 전기 폭발로 바꾸지 않는다.
mutant_stumpy|earth,dark_magic|검은 뿌리와 묘비가 맞물려 지면에서 자란 뒤 무너진다. 검 모양이나 추상 검은 구체 대신 두 소재를 따로 읽히게 한다.
'''
ASSIGNMENTS = {}
for line in DATA.strip().splitlines():
    key, sources, translation = line.split('|')
    assert key not in ASSIGNMENTS
    ASSIGNMENTS['m_'+key] = (sources.split(','), translation)
