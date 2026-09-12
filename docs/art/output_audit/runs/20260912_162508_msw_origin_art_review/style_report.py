from style_finish_review import *
import datetime
old=list(csv.DictReader((P/'ART_REVIEW.csv').open(encoding='utf-8-sig')))
OLD={(x['area_id'],x['monster_id'],x['role']):x for x in old}
SEL={x['area_id']:x for x in csv.DictReader((P/'AREA_SELECTION.csv').open(encoding='utf-8-sig'))}
D={ (x['area_id'],x['monster_id'],x['role']):x for x in json.loads((P/'STYLE_VISUAL_DECISIONS.json').read_text(encoding='utf-8'))}
area_notes={
'area_01':'이슬/물막은 승인 재사용과 같은 곡면 반사. 버섯 포자 구름은 부드러운 덩어리 음영과 선명한 잎/빛 입자를 결합하며, 뿔은 불투명한 재질에 맞는 면 음영을 유지한다.',
'area_02':'돌·뿌리·뼈의 거친 표면은 소재 차이로 허용. VFX의 얇은 발광선·먼지/파편의 분해와 금속 반사는 연결되며 ICON의 두꺼운 윤곽은 별도 판단한다.',
'area_03':'점액의 곡면, 나무 껍질의 결, 요정의 얇은 금빛/민트 궤적, 인형의 천과 종이 재질을 구분하면서 반사/잔광의 연속성을 유지한다.',
'area_04':'먹물은 광택 있는 액체, 망령 손자국/안개는 차가운 반투명, 셰이드는 가는 보라 경계와 어두운 곡면으로 표현한다. 어두움 자체는 결함이 아니다.',
'area_05':'CAST의 리본 곡면·수중 별가시·왕게 집게/파도는 부드러운 명암과 예리한 빛 끝을 유지한다. ICON 및 두 REFERENCE의 픽셀 마감과 분리해서 판정했다.',
'area_07':'부식 구리/뼈/비늘의 표면 결을 유지하면서 화염은 얇은 밝은 중심선, 번개는 예리한 분기, 그림자 발톱은 보라 잔광으로 재질을 구별한다.',
'area_08':'별/달의 밝은 핵·초승달 유리광, 화염 띠, 잎이 섞인 바람은 서로 다른 소재지만 윤곽과 광선의 연속성을 유지한다. 별탄과 태양 참고의 단순화만 판단 보류.',
'area_09':'눈 가루의 입상 질감, 얼음의 각진 반사면, 발톱/엄니의 차가운 가는 빛이 ICON과 VFX에서 연결된다. 눈/얼음의 거친 입자를 픽셀 마감과 혼동하지 않았다.',
'area_10':'물방울·가면·잉크 안개·상어의 물/금속·피아누스 광선이 각각 곡면광과 얇은 가장자리/부드러운 외곽으로 연결된다. 가면의 평평함은 얇은 물체의 소재 특성이다.',
'area_11':'북면/진동륜, CAST 왕관 블록과 롬바드 금속 고리는 면 음영·가는 반사와 연속 잔광을 유지한다. 라츠/블록퍼스 REFERENCE 및 왕관 PROJECTILE만 마감 이탈.',
'area_12':'CAST 목마의 바퀴·태엽·목재 파편, 크로노스 유리/시계, 타이머 금속/결정의 마감은 유지 가능. 목마 ICON 및 두 REFERENCE의 픽셀 외곽과 구별했다.',
'area_13':'모래는 부드러운 먼지 덩어리와 개별 입자, 데우의 선인장/가시는 입체 면과 날카로운 조각으로 마무리된다. 목도리 REFERENCE만 작은 픽셀 외곽 차이가 두드러진다.',
'area_14':'액체·유리·금속·독무에서 반복되는 픽셀 계단형 마감이 전체 역할에서 관찰된다. 지역 내부 일치만으로 AREA00 기준 적합으로 승격하지 않는다.',
'area_15':'짚의 세선·목재 결·꽃잎의 얇은 윤곽·태륜의 청백 타격 잔상은 소재별 차이를 유지하면서 입체감/반사광과 소멸을 연결한다. 원공 PROJECTILE 외곽은 별도 판단.',
'area_16':'깃털의 결, 비늘 면과 붉은 균열, 얼음의 날카로운 결정, 화염의 밝은 선과 어두운 중간층이 역할 사이에 이어진다. 재질/보스 밀도 차이를 허용한다.',
'area_17':'구슬 염주의 곡면 반사, 유리 기도핵, 경사진 석판 금장, 도도의 종이와 어두운 소용돌이가 ICON/VFX에서 연결된다. 문양의 평면성과 재질의 입체성을 구별한다.',
'area_18':'금속·수정·레이저·정신망·중력륜 모두에 픽셀 계단형 테두리와 발광선이 반복된다. 외계/회로 소재가 다르다는 사실만으로 AREA00와 다른 마감을 허용하지 않는다.',
'area_19':'번개의 얇은 중심선, 깃털의 가는 결, 그림자 천의 반투명 겹침, 불꽃의 선명한 리본, 여제의 꽃잎/왕관 음영이 역할 사이에 이어진다.',
'area_20':'균열 암석의 거친 면·나무의 결·금속 코의 반사는 소재대로 다르지만 가는 경계와 먼지/보라 잔상의 층이 연결된다. 어두운 팔레트나 낮은 광택은 수정 근거가 아니다.'}
hashrows=[];selection=[];cache=[];review=[]
for a in sorted(SEL):
 r=next(x for x in R if x['area_id']==a);s=SEL[a]
 ih=sha(r['input_zip']);oh=sha(r['output_zip']);prevout=sha(s['output_path'])
 assert ih==s['input_sha256'] and prevout==s['output_sha256']
 if a!='area_12':assert oh==s['output_sha256']
 selection.append({'area_id':a,'input_version':'V2.4','input_path':r['input_zip'],'input_sha256':ih,'output_path':r['output_zip'],'output_sha256':oh,'basis':'AREA12 새 패키지의 45 원화 바이트 일치/패키지 검증 기록' if a=='area_12' else '최신 원본 검수 AREA_SELECTION의 OUTPUT 해시 일치; AREA11 원본 유지/수정 후보 미채택','prior_output_sha256':prevout,'prior_file_checks':'기존 CRC/규격 검사 재사용; AREA11 기술 보류는 해제하지 않음' if a=='area_11' else '원화 해시와 INPUT 동일; 구조검사는 해당 패키지 기존 기록 재사용'})
for r in R:
 a,m=r['area_id'],r['monster_id']
 assert sha(r['source_file'])==r['source_sha256'];assert sha(r['model_path'])==r['model_sha256']
 cache.append({'area_id':a,'monster_id':m,'source_level_this_supplement':'CACHED_SOURCE_CONFIRMED','source_path':r['source_file'],'ruid':r['model_sprite_ruid'],'source_sha256':r['source_sha256'],'model_sha256':r['model_sha256'],'basis':'SOURCE_CHECK.csv 조회 시각/RUID/API 증빙 재사용; 원본 사본 및 모델 해시 재확인','new_query_this_supplement':'NO'})
 with zipfile.ZipFile(r['output_zip']) as z:
  for role,files in r['role_files'].items():
   k=(a,m,role);prev=OLD[k];co=CM[k]['full_art_scope'];hh={}
   for n in files:
    h=hashlib.sha256(z.read(n)).hexdigest();assert h==r['file_hashes'][n];hh[n]=h
    hashrows.append({'area_id':a,'monster_id':m,'role':role,'zip':r['output_zip'],'file':n,'sha256_before':r['file_hashes'][n],'sha256_after':h,'result':'BYTE_IDENTICAL'})
   # AREA12 new paths: compare role's bytes, not old path spelling.
   assert sorted(hh.values())==sorted(json.loads(prev['actual_output_file_sha256']).values())
   status=D[k]['status'] if k in D else 'CONSISTENT_WITH_REFERENCE'
   bk,bn=base(role,int(co['canvas'].split('x')[0]))
   native=str(P/'CROSS_AREA_STYLE_BOARD'/(a+'_ICON_NATIVE.png' if role=='ICON' else f'{a}_{m}_{role}_NATIVE.png'))
   assert Path(native).exists()
   review.append({'area_id':a,'monster_id':m,'monster_name':r['monster_name'],'skill_id':r['skill_id'],'skill_name':r['skill_name'],'role':role,'style_judgment':status,
    'actual_output_zip':r['output_zip'],'actual_output_files':'|'.join(files),'actual_file_sha256':json.dumps(hh,ensure_ascii=False),'input_zip':r['input_zip'],'input_version':'V2.4','input_spec_path':prev['input_spec_path'],
    'input_core_material':prev['input_core_material'],'input_role_timing':co['frame_seconds']+' / '+co['playback_mode'],'input_direction':co['direction_and_engine_motion'],
    'observed_frame_scope':'ICON 原寸 전체' if role=='ICON' else f'F00–F{len(files)-1:02d} 전체를 순서대로 직접 대조',
    'observed_sequence':prev['observed_visual_sequence'],'reference_zip':B['zip'],'reference_file':bn,'reference_basis':'AREA00 실제 승인 원화. 해당 보드의 기준 프레임 + ART_STYLE_STANDARD의 전체 기준. 고유 모양/저레벨 규모를 요구하지 않음',
    'finish_observation':D[k]['reason'] if k in D else area_notes[a],
    'within_skill':'동일 몬스터의 실제 ICON 및 모든 VFX 역할 대조. '+('일부 역할의 차이는 아래 별도 후보로 한정' if any(x[:2]==k[:2] for x in D) else '색·소재·반사광 관계에서 명백한 이탈 없음'),
    'within_area':area_notes[a],
    'cross_area':'AREA00 기준 + 전체 Area의 동일 역할 보드 대조; 다수결 기준 사용 안 함. 추가 소재 비교는 CROSS_AREA_MATERIAL_BOARD_INDEX.csv',
    'allowed_difference':'팔레트·재질·형상·레벨/보스 규모·밀도·역할별 프레임/시간 차이 허용',
    'why_not_allowed_difference':('액체/금속/직물 등 소재 자체보다 픽셀 단위의 외곽·명암·광선 연결 방식이 다른 점을 판정' if status==O else '허용된 소재/역할 단순화와 마감 차이의 경계 불명확' if status==U else '해당 없음'),
    'keep_material_motion':prev['input_core_material']+' | '+co['direction_and_engine_motion'],
    'finish_change_candidate':D[k]['finish'] if k in D else '원화 유지',
    'user_decision_needed':'YES' if k in D else 'NO','user_approved':'NO',
    'native_board':native,'detail_board':D[k]['board'] if k in D else '',
    'display_conditions':'PNG 원본을 동일 RGB(32,38,48) 배경에 1:1 합성. 확대는 동일 128px 영역 2배 NEAREST. 큰 보드의 도구 축소 표시 가능; 이탈 상세는 1600px 보드에서 추가 대조',
    'temporal_review':'전 프레임 순서상 형성/변화/해체/잔상 대조. 실시간 재생의 체감 리듬 및 엔진 합성은 미검증',
    'game_size_review':'NOT_CHECKED: 게임 내 최종 배율/카메라/필터/배경에서의 선명도 미검증. 명세 배율만으로 런타임 표시를 보았다고 하지 않음',
    'configuration_judgment_reused':prev['configuration_fit'],
    'technical_hold':'AREA11 수정 후보의 실제 투명도 미해결 및 패키징/Preview 보류 유지' if a=='area_11' else 'AREA12 신규 패키지 구조검증 별도 기록' if a=='area_12' else '기존 파일검사 재사용'})
wc('CROSS_AREA_STYLE_REVIEW.csv',review);wc('STYLE_PNG_BYTE_PRESERVATION.csv',hashrows);wc('STYLE_AREA_SELECTION.csv',selection);wc('STYLE_SOURCE_CACHE_REUSE.csv',cache)
actions=[]
for row in review:
 if row['style_judgment'] not in [O,U]:continue
 actions.append({k:row[k] for k in ['area_id','monster_id','monster_name','skill_id','skill_name','role','style_judgment','actual_output_files','finish_observation','keep_material_motion','finish_change_candidate','detail_board']}|{'action':'원화 수정 후보' if row['style_judgment']==O else '사용자 판단','implemented':'NO','scope_guard':'목록 역할에 한정. CAST/ICON 본체 금지 철회 판정은 번복하지 않음; 스타일 판단과 별도'})
wc('STYLE_ACTION_ITEMS.csv',actions)
stats=collections.Counter(x['style_judgment'] for x in review)
ar=[]
for a in sorted(SEL):
 rr=[x for x in review if x['area_id']==a];cc=collections.Counter(x['style_judgment'] for x in rr)
 ar.append({'area_id':a,'pairs':len([r for r in R if r['area_id']==a]),'roles':len(rr),**{s:cc[s] for s in ['CONSISTENT_WITH_REFERENCE',O,U,'NOT_CHECKED']}})
wc('STYLE_AREA_COUNTS.csv',ar)
evidence_hashes=[]
for name in ['AUDIT_RULES.md','BASELINE_INDEX.csv','BASELINE_OUTPUT_INDEX.csv']:
 f=P.parent.parent/name
 if f.exists():evidence_hashes.append({'kind':'audit_baseline','path':str(f),'sha256':sha(f)})
for name in ['CONTRACT_SNAPSHOTS.json','ART_REVIEW.csv','SOURCE_CHECK.csv','AREA_SELECTION.csv']:
 evidence_hashes.append({'kind':'prior_review','path':str(P/name),'sha256':sha(P/name)})
evidence_hashes.append({'kind':'AREA00_approved_original','path':B['zip'],'sha256':sha(B['zip'])})
assert sha(B['zip'])=='5271fa0682c4cc76caaf6f4e5627c5fbf3c70ec87fe911b9e5398afb770f6853'
wc('STYLE_EVIDENCE_HASHES.csv',evidence_hashes)
print(stats);print('PNG',len(hashrows),'source',len(cache));print(ar)
