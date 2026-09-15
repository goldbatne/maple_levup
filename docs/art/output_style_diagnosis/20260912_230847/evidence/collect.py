from pathlib import Path
import json,csv,hashlib,re,shutil
from PIL import Image
R=Path(__file__).resolve().parents[1]; A=Path('D:/maplestory_levup/docs/art'); B=A/'output_style_unified_batches'; F=A/'area00_refinement/20260912_203404'; V=F/'AREA_00_IMAGES_INPUT_IMAGES_OUTPUT/monsters'; G=Path('C:/Users/dddd/.codex/generated_images/01a0955f-0d5b-7931-a751-c770b2046bd8')
log=next(Path('C:/Users/dddd/.codex/sessions/2026/09/12').glob('*01a0955f*.jsonl'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else 'MISSING'
def csvout(n,rows):
 with (R/n).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines=list(log.open(encoding='utf-8'));calls={};snips=[]
for i,l in enumerate(lines[:1410],1):
 o=json.loads(l);q=o.get('payload',{});s=q.get('input','')
 if q.get('type')=='custom_tool_call' and 'await tools.image_gen__imagegen(' in s:
  calls[i]=s; snips.append('## L'+str(i)+' / '+o['timestamp']+' / '+q['call_id']+'\n```javascript\n'+s+'\n```')
(R/'TOOL_INPUT_TRACE.md').write_text('# 실제 호출 발췌\n\n원본 세션: '+str(log)+'\n\n모델 샘플링 내부는 알 수 없다. 아래는 실행된 오케스트레이션 코드이며 load 변수는 REFERENCE_TRACE의 경로로 풀었다. 호출 시점의 파일 내용 전체를 로그가 보증하지는 않으므로 현존 파일 해시 및 저장 원본을 함께 대조했다. 실패한 경로 접근 재시도도 호출과 성공을 혼동하지 않는다.\n\n'+'\n\n'.join(snips),encoding='utf-8')
mi=lambda run,folder:B/run/folder/'monsters/003_m_mushroom_주황_버섯/MONSTER_IMAGE.png'
mano=V/'004_m_mano_마노/VFX/004_m_mano_s_mon_mano_F04.png'; icon=V/'004_m_mano_마노/ICON/004_m_mano_s_mon_mano_ICON.png';blue=V/'002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F04.png';red=V/'003_m_red_snail_빨간_달팽이/VFX/003_m_red_snail_s_mon_red_snail_F05.png';slime=V/'005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F04.png'
trace=[]
def add(run,line,items):
 for p,role,kind in items:trace.append(dict(generation_run=run,tool_log_line=line,reference_path=str(p),sha256=sha(p),reference_role=role,actual_tool_input='YES' if line in calls else 'UNKNOWN',polarity=kind))
for line,n,ns in [(206,6,[5,7]),(227,5,[6])]:add('AREA00_REFINEMENT',line,[(F/f'work/BLACK_004_m_mano_s_mon_mano_F{n:02}.png','EDIT_TARGET','positive')]+[(F/f'work/BLACK_004_m_mano_s_mon_mano_F{x:02}.png','TEMPORAL_NEIGHBOR','positive') for x in ns])
add('AREA00_REFINEMENT',166,[(F/'work/EDIT_004_m_mano_s_mon_mano_F05.png','EDIT_TARGET','positive'),(A/'output_audit/runs/20260912_192803_area00_intent_quality_review/evidence/m_mano_frames_04_07.png','TEMPORAL_REVIEW_BOARD','positive')])
add('AREA00_REFINEMENT',211,[(F/'work/BLACK_004_m_mano_s_mon_mano_F07.png','EDIT_TARGET','positive'),(F/'work/BLACK_004_m_mano_s_mon_mano_F06.png','TEMPORAL_NEIGHBOR','positive'),(A/'output_audit/runs/20260912_192803_area00_intent_quality_review/sources/m_mano/004_m_mano_s_mon_mano_F08.png','TEMPORAL_NEIGHBOR','positive')])
m=mi('20260912_212559','provenance/AREA_01_INPUT')
add('INITIAL_MUSHROOM_ICON',506,[(m,'MONSTER_IDENTITY','positive'),(icon,'AREA00_ICON_FINISH','positive')])
add('INITIAL_MUSHROOM_CAST',522,[(m,'MONSTER_IDENTITY','positive'),(mano,'AREA00_VFX_FINISH','positive'),(G/'exec-2e715bb0-c8f1-410b-9ebe-95db3c561eb7.png','NEW_AREA01_ICON_LATER_REJECTED','positive')])
for line in [1124,1134,1153]:add('RESTART',line,[(mi('20260912_220728_RESTART','provenance/AREA_01'),'MONSTER_IDENTITY','positive'),(blue,'AREA00_VFX_FINISH','positive'),(red,'AREA00_VFX_FINISH','positive')])
add('ANCHOR_01',1254,[(slime,'AREA00_VFX_FINISH','positive'),(B/'20260912_222656_ANCHOR/input/MONSTER_IMAGE.png','MONSTER_IDENTITY','positive')])
add('ANCHOR_02',1269,[(slime,'AREA00_VFX_FINISH','positive')])
add('ANCHOR_ALPHA_TEST',1286,[(B/'20260912_222656_ANCHOR/source/keyframe_attempt02.png','FAILED_EDIT_TARGET_NOT_STYLE_REFERENCE','negative')])
for line in [1373,1396]:add('GRAMMAR',line,[(blue,'AREA00_VFX_FINISH','positive'),(mi('20260912_225116_GRAMMAR','input/AREA_01_IMAGES_INPUT_V2_4'),'MONSTER_IDENTITY','positive')])
# Separate from mushroom: an initial Area01 self-reference call and wrong role selection really existed.
add('INITIAL_MUSHMOM_RETRY',647,[(B/'20260912_212559/provenance/AREA_01_INPUT/monsters/004_m_mushmom_머쉬맘/MONSTER_IMAGE.png','MONSTER_IDENTITY','positive'),(mano,'AREA00_VFX_FINISH','positive'),(B/'20260912_212559/BATCH_01/AREA_01_IMAGES_OUTPUT/SOURCE_SHEET/m_mushmom/ICON/source_00_1.png','CURRENT_AREA01_ICON_SOURCE_CALL_ATTEMPT','positive')])
add('INITIAL_HORN_REFERENCE_VFX',678,[(B/'20260912_212559/provenance/AREA_01_INPUT/monsters/005_m_horny_mushroom_뿔버섯/MONSTER_IMAGE.png','MONSTER_IDENTITY','positive'),(icon,'AREA00_ICON_USED_FOR_VFX','positive')])
trace.append(dict(generation_run='AREA00_ORIGINAL',tool_log_line='UNKNOWN',reference_path='UNKNOWN actual tool input list; manifest only',sha256='UNKNOWN',reference_role='MONSTER/VFX/ICON/STYLE',actual_tool_input='UNKNOWN',polarity='UNKNOWN'))
csvout('REFERENCE_TRACE.csv',trace)
inventory=[]
for root in [A/'area00-images-output',F,B/'20260912_212559/work',B/'20260912_220728_RESTART/work',B/'20260912_222656_ANCHOR/records',B/'20260912_225116_GRAMMAR/records']:
 for p in root.rglob('*'):
  if p.is_file() and p.suffix in ['.md','.csv','.json','.py','.txt']:
   inventory.append(dict(path=str(p),sha256=sha(p)))
csvout('evidence/FILE_INVENTORY.csv',inventory)
for n,p in [('area00_comparison.png',B/'20260912_225116_GRAMMAR/preview/AREA00_INPUT_ORIGINAL_REFINED.png'),('grammar_blue_source.png',B/'20260912_225116_GRAMMAR/source/F03_blue_matte.png'),('grammar_magenta_source.png',B/'20260912_225116_GRAMMAR/source/F03_attempt02_magenta.png'),('grammar_blue_QA.png',B/'20260912_225116_GRAMMAR/preview/F03_ALPHA_QA.png'),('grammar_magenta_QA.png',B/'20260912_225116_GRAMMAR/preview/F03_ATTEMPT02_ALPHA_QA.png'),('initial_icon.png',G/'exec-2e715bb0-c8f1-410b-9ebe-95db3c561eb7.png'),('initial_cast_source.png',G/'exec-b7a2c0e5-d57f-4397-b049-5f9326ca5228.png'),('restart_QA.png',B/'20260912_220728_RESTART/evidence/MUSHROOM_CAST_ATTEMPT3_3_BACKGROUNDS.png')]:
 if p.exists():shutil.copy2(p,R/'evidence'/n)
dupes=[]
root=B/'20260912_212559/BATCH_01/AREA_01_IMAGES_OUTPUT/SOURCE_SHEET/m_mushroom'
for p in root.rglob('*.png'):
 im=Image.open(p);dupes.append(dict(path=str(p),sha256=sha(p),mode=im.mode,size=str(im.size),alpha=str(im.getchannel('A').getextrema()) if 'A' in im.getbands() else 'NONE'))
csvout('evidence/INITIAL_SOURCE_IDENTITY.csv',dupes)
print('trace_rows',len(trace),'tool_calls',len(calls),'source_duplicate_pairs',[(x['sha256'],x['mode']) for x in dupes])
