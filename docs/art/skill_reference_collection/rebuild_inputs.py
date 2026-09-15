from pathlib import Path
import zipfile,json,csv,io,hashlib,datetime,re
root=Path(__file__).parent; base=root.parent/'images-input-packages'
refs={r['key']:r for r in json.loads((root/'selected.json').read_text(encoding='utf-8'))}
groups={
'water':'snail slime bubbling jellyfish bubble_fish shark king_clang cube_slime',
'barrier':'blue_snail dark_stump stone_golem copper_drake mithril_mutae memory_guardian chief_memory_guardian mutant_dark_stump mutant_stone_mask',
'mist':'mushroom mushmom zombie_mushroom octopus squid homun chimera brown_teddy',
'garden':'fairy eliza stumpy peach_monkey blue_flower_serpent cygnus mutant_stumpy',
'curse':'faust wraith jr_wraith shade dodo',
'star':'mano starfish star_pixie lunar_pixie luster_pixie memory_monk memory_monk_trainee',
'ice':'jr_yeti dark_jr_yeti hector white_fang snow_witch blue_wyvern',
'earth':'axe_stump dark_axe_stump wild_boar iron_hog skeleton_commander sand_dwarf ancient_dark_golem mutant_iron_hog wooden_dummy',
'machine':'ratz drumming_bunny bloctopus king_bloctopus toy_trojan master_robo roid mateon plateon mecateon pianus',
'time':'chronos timer',
'psychic':'rombot chief_gray zeno',
'metal':'horny_mushroom dark_wyvern',
'fire':'fire_boar drake jr_balrog jr_cellion manon advanced_knight_b',
'sand':'white_sand_rabbit scarf_plead meercat deo',
'needle':'wild_kargo advanced_knight_a red_snail',
'wind':'stirge mask_fish ribbon_pig blue_pig straw_dummy tae_roon harp blood_harp official_knight_d',
'lightning':'tauromacis official_knight_c'}
mapping={'m_'+m:k for k,ms in groups.items() for m in ms.split()}
secondary={'water':'barrier','barrier':'metal','mist':'water','garden':'wind','curse':'needle','star':'garden','ice':'water','earth':'psychic','machine':'metal','time':'psychic','psychic':'time','metal':'earth','fire':'sand','sand':'earth','needle':'wind','wind':'garden','lightning':'star'}
policy='''# 공식 스킬 디자인 참조 — 이번 개정의 우선 지침

공식 스킬의 실제 디자인을 적극 참고한다. 이전 문서의 “역할 분리와 시간 구조만”이라는 제한은 폐기한다. 명암 면 분리, 재질의 두께, 밝은 코어, 색 외곽, 반투명 발광, 파편의 형태와 배치, 프레임 전개, 작은 아이콘의 시각적 압축을 함께 관찰하고 새 몬스터 스킬에 적용한다.

## 생성 전에 실제로 볼 것
1. MONSTER_IMAGE.png와 GENERATION_SPEC의 고정 소재·동작.
2. reference_resource_design/AREA_REFERENCE_MAP.md에서 해당 skill_id의 참조 폴더와 적용 범위.
3. 지정 폴더의 원본 PNG/GIF와 frames의 추출 PNG. GIF는 실제 재생하고 프레임을 확인한다. 파일명·RUID·설명만 읽고 디자인 참조를 했다고 기록하지 않는다.
4. 기존 AREA00 VFX 실제 PNG는 프로젝트 마감 비교 기준이다. 공식 스킬 디자인 참조를 AREA00 한 종류의 모양으로 대체하지 않는다.

생성 도구에는 MONSTER_IMAGE + 선택한 공식 스킬의 실제 VFX 프레임 + AREA00 마감 PNG를 실제 이미지 입력으로 전달한다. 입력 수 제한이 있으면 선택 수를 줄이고 무엇을 전달했는지 기록한다. 모든 참조를 한 장의 포스터로 재생성해서 대신하지 않는다. ICON은 공식 ICON의 작은 크기 읽힘과 재질 표현을 참고하되, 완성 VFX의 고유 소재를 압축한다.

## 참고와 고정 명세의 관계
참조 팩은 유사한 표현 기법의 예시이며 원본 스킬과 동일한 소재·동작이라는 뜻이 아니다. 산 에움의 바위는 나이테 방패를 바위로 바꾸라는 뜻이 아니고, 포이즌 미스트의 독은 포자를 독무나 불꽃으로 바꾸라는 뜻이 아니다. 어울리지 않는 공식 고유 무기·캐릭터·문양·색·규모를 그대로 가져오지 않는다. 몬스터/skill ID·이름·실제 효과·소재·팔레트·필수 역할·프레임 수는 INPUT을 지킨다.

각 스킬의 REFERENCE_INPUTS 기록에는 공식 팩 이름/ID, 실제 파일과 SHA-256, 어떤 디자인 요소를 적용했는지, 원래 명세와 달라서 가져오지 않은 요소, 실제 생성 입력 여부를 남긴다. 실제 대조 없이 아트 PASS라고 기록하지 않는다.

## 원본 품질과 최신성의 한계
이 폴더의 공식 자료는 공개 리소스 API가 제공한 표시용 PNG/GIF이다. GIF를 추출한 PNG는 표시용 GIF의 프레임이며 엔진 원본 RGBA 복구본이 아니다. 흰 배경이 구워진 미리보기도 있다. 그 배경·알파·해상도를 새 납품 에셋에 복제하지 않는다. 새 납품물의 알파는 별도로 검증한다.
공식 API에서 현재 조회되었다는 사실과 최신 라이브 디자인이라는 주장은 다르다. 출시/개편 날짜는 미검증이다. VI 표기도 현재 최신임의 증거로 사용하지 않는다. 기존 최신성 확인 자료가 있는 경우 해당 근거를 따로 읽는다.

## 전체 자료 보관본
공통 MSW_SKILL_REFERENCE_LIBRARY ZIP은 API skill 카테고리 팩 전체를 탐색하기 위한 자료이다. 모든 파일을 매 생성에 넣거나 5천여 스킬을 섞어 그리라는 지시가 아니다. Area ZIP에는 필요한 참조가 이미 들어 있으므로 보통 Area INPUT ZIP과 제작 TXT만 보내면 된다. 필요한 유사 표현이 부족할 때 공통 목록에서 추가 선택한다. 참조 리소스는 디자인 관찰용이며 그대로 OUTPUT으로 납품하지 않는다.
'''
run=datetime.datetime.now().strftime('%Y%m%d_%H%M%S'); backup=root/'backups';backup.mkdir(exist_ok=True)
files=sorted(base.glob('AREA_*_IMAGES_INPUT.zip'));prompts=sorted(base.glob('AREA_*_CHATGPT_PRODUCTION_PROMPT.txt'))
backup_file=next(iter(sorted(backup.glob('INPUTS_BEFORE_*.zip'))),backup/('INPUTS_BEFORE_'+run+'.zip'))
if not backup_file.exists():
 with zipfile.ZipFile(backup_file,'w',zipfile.ZIP_STORED) as z:
  for f in files+prompts: z.write(f,f.name)
original_backup=zipfile.ZipFile(backup_file)
report=[]
for f in files:
 original_bytes=original_backup.read(f.name)
 before=hashlib.sha256(original_bytes).hexdigest()
 with zipfile.ZipFile(io.BytesIO(original_bytes)) as z: data={n:z.read(n) for n in z.namelist()}
 prefix=f.stem+'/'
 rows=list(csv.DictReader(io.StringIO(data[prefix+'AREA_MANIFEST.csv'].decode('utf-8-sig'))))
 selected=set(); table=['# 이 Area의 공식 스킬 디자인 참조','', '|몬스터 / skill_id|실제 명세 소재|참고 폴더|적용할 표현|','|---|---|---|---|']; records=[]
 for r in rows:
  k=mapping[r['monster_id']]; keys=[k,secondary[k]];selected.update(keys)
  spec=data[prefix+r['folder']+'/GENERATION_SPEC.md'].decode('utf-8');material=next(l.split(':',1)[1].strip() for l in spec.splitlines() if '핵심 소재:' in l).split('‘')[0].strip()
  table.append(f"|{r['monster_name']} / {r['skill_id']}|{material}|"+' + '.join(keys)+'|'+refs[k]['purpose']+'|')
  records.append({'monster_id':r['monster_id'],'skill_id':r['skill_id'],'material':material,'groups':keys,'selection_status':'EXPRESSION_REFERENCE; not identical material or motion'})
 data[prefix+'reference_resource_design/README.md']=policy.encode()
 data[prefix+'reference_resource_design/AREA_REFERENCE_MAP.md']='\n'.join(table).encode()
 data[prefix+'reference_resource_design/AREA_REFERENCE_MAP.json']=json.dumps(records,ensure_ascii=False,indent=2).encode()
 for k in sorted(selected):
  d=root/'selected'/k
  for p in d.rglob('*'):
   if p.is_file():data[prefix+'reference_resource_design/'+k+'/'+p.relative_to(d).as_posix()]=p.read_bytes()
  data[prefix+'reference_resource_design/'+k+'/SOURCE.json']=json.dumps(refs[k],ensure_ascii=False,indent=2).encode()
  data[prefix+'reference_resource_design/'+k+'/README.md']=(str(refs[k]['names'])+'\n\n'+refs[k]['purpose']+'\n\n'+refs[k]['currentness']+'\n원본 표시용 PNG/GIF 및 실제 추출 프레임. 명세를 이 공식 스킬로 변경하지 않는다.').encode()
 # Fix conflicting guidance throughout documentation, without altering skill identity/spec fields.
 changed=[]
 for n,b in list(data.items()):
  if not n.endswith('.md') or '/reference_resource_design/' in n:continue
  t=b.decode('utf-8-sig');old=t
  t=t.replace('MSW resource pack에서는 역할 분리와 시간 구조만 가져옵니다:','MSW resource pack에서는 실제 디자인·명암·재질·발광·입자·ICON 표현과 역할 분리·시간 구조를 함께 참고합니다:')
  t=t.replace('기존 AREA 01~20 OUTPUT, 이전 실패 샘플, 기존 스킬 아이콘은 positive reference가 아닙니다.','기존 AREA 01~20 실패 OUTPUT은 positive reference가 아닙니다. 공식 스킬 ICON은 작은 크기의 디자인·명암 참고로 사용하며 그대로 복제하지 않습니다.')
  if n.endswith('GENERATION_SPEC.md'):
   t+='\n\n## 공식 디자인 참조 개정\nreference_resource_design/AREA_REFERENCE_MAP.md의 이 skill_id 행과 실제 이미지를 우선 확인한다. 이전 지정 팩 목록은 보조 자료이며 디자인 참고를 시간 구조만으로 제한하지 않는다. 소재·효과·동작·출력 규격은 위 원문을 유지한다.\n'
  if n.endswith(('README_START_HERE.md','CHATGPT_IMAGES_MASTER_PROMPT.md','QUALITY_GATE.md')):
   t='이번 공식 디자인 참조 지침: reference_resource_design/README.md 및 AREA_REFERENCE_MAP.md를 먼저 읽고 실제 PNG/GIF를 연다. 이전의 시간 구조만 참고하라는 제한보다 이 개정 지침을 우선한다.\n\n'+t
  if t!=old:data[n]=t.encode('utf-8');changed.append(n)
 index=io.StringIO(newline='');w=csv.writer(index);w.writerow(['path','sha256','bytes'])
 for n,b in sorted(data.items()):
  if not n.endswith('INPUT_FILE_HASHES.csv'):w.writerow([n[len(prefix):],hashlib.sha256(b).hexdigest(),len(b)])
 data[prefix+'INPUT_FILE_HASHES.csv']=index.getvalue().encode('utf-8-sig')
 temp=f.with_suffix('.zip.pending')
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n,b in sorted(data.items()):z.writestr(n,b)
 with zipfile.ZipFile(temp) as z:
  assert z.testzip() is None
  with zipfile.ZipFile(io.BytesIO(original_bytes)) as original:
   for n in original.namelist():
    if n.endswith('MONSTER_IMAGE.png') or n.endswith(('AREA_MANIFEST.csv','MONSTER_INFO.md','RUNTIME_ROLE_MAP.md')):assert original.read(n)==z.read(n),n
 temp.replace(f)
 prompt=base/(f.name.replace('_IMAGES_INPUT.zip','_CHATGPT_PRODUCTION_PROMPT.txt'))
 t=original_backup.read(prompt.name).decode('utf-8');t=t.replace('INPUT이 지정한 공식 스킬 GIF도 앞/중간/끝 프레임을 실제 확인해 시간 구조를 참고하세요.','INPUT의 reference_resource_design/AREA_REFERENCE_MAP.md가 지정한 공식 스킬 PNG/GIF와 추출 프레임을 실제 확인해 디자인·명암·재질·발광·입자·시간 구조를 함께 참고하고 생성 이미지 입력으로 전달하세요.')
 prompt.write_text(policy+'\n\n---\n\n'+t,encoding='utf-8')
 report.append({'area':f.stem,'before_sha256':before,'after_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'groups':sorted(selected),'skills':len(rows),'png_references':sum(n.endswith('.png') and '/reference_resource_design/' in n for n in data),'identity_preservation':'PASS','crc':'PASS','modified_documents':changed})
 print(f.name, f.stat().st_size,flush=True)
(root/'INPUT_REBUILD_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(base/'SEND_TO_CHATGPT_README.md').write_text('# 전달 방법\n\n해당 Area INPUT ZIP과 같은 Area의 CHATGPT_PRODUCTION_PROMPT.txt를 첨부하고 **첨부한 프롬프트대로 실행해줘**라고 요청합니다.\n\n공식 스킬의 실제 디자인 참고 이미지가 INPUT 안 reference_resource_design에 들어 있습니다. 공통 전체 자료 ZIP은 추가 검색용 보관본이며 매번 첨부할 필요가 없습니다. 실제 참조 입력과 결과 품질은 생성 기록/결과 이미지에서 검증해야 하며, 첨부만으로 품질 통과를 보장하지 않습니다.\n\n기준 폴더에는 AREA06 패키지가 없으므로 이 작업에서 임의 제작하지 않았습니다.\n',encoding='utf-8')
