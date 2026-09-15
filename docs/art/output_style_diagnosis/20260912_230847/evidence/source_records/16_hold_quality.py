from pathlib import Path
import json,hashlib,csv,shutil,html
from PIL import Image
R=Path(__file__).resolve().parents[1];p=R/'PRODUCTION_STATE.json';s=json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s.update(status='HOLD_QUALITY_GATE_FAILED',resume_allowed=False,packaging_allowed=False,first_incomplete_role='AREA_01/m_mushroom/CAST_VFX',reason='Fresh rendering trials failed AREA00-quality gate after initial generation plus two retries. No generation proceeds on this failed style. No new delivery ZIP.',current_batch='BATCH_01_STOPPED',next_batch='BATCH_02_NOT_STARTED')
gates=[{'criterion':1,'result':'PASS_LIMITED','evidence':'m_mushroom / s_mon_mushroom / 포자 살포; 8 frames, 384px, 0.10s; three beige spore puffs and sparse green accents; no game edits.'},{'criterion':2,'result':'PASS_LIMITED','evidence':'Three powder puffs correspond to INPUT; identity is supported by motif and original monster comparison, not claimed official skill.'},{'criterion':3,'result':'FAIL','evidence':'Third attempt has weak midtone readability against light background; rendering remains diffuse volumetric haze rather than AREA00 crisp selected contours and separated luminous layers. Does not establish target style.'},{'criterion':4,'result':'PASS_FILE_SEQUENCE_ONLY','evidence':'Appearance, growth, peak, open contours and dissolution visibly differ. No browser playback/game validation claimed.'},{'criterion':5,'result':'NOT_CHECKED','evidence':'New matching ICON deliberately not generated while VFX quality gate failed.'},{'criterion':6,'result':'PASS_LIMITED','evidence':'Third attempt is a local transient effect, not a poster composition; this alone is insufficient.'},{'criterion':7,'result':'PASS_LIMITED','evidence':'No monster body, copied shell/spiral, other-area props, text, numbers or UI in attempt3.'}]
for a,v in s['areas'].items():
 v['status']='HOLD_QUALITY_GATE' if a=='AREA_01' else 'NOT_STARTED_RESTART'
 for r in v['roles']:
  if a=='AREA_01' and r['monster_id']=='m_mushroom' and r['effect_role']=='CAST_VFX':r.update(status='REJECTED_QUALITY_GATE',attempts=3,quality_gate=gates,staging_is_delivery=False)
s['input_integrity']=[{'area':a,'path':v['input_path'],'expected_sha256':v['input_sha256'],'actual_sha256':sha(Path(v['input_path'])),'match':sha(Path(v['input_path']))==v['input_sha256']} for a,v in s['areas'].items()]
s['area00_integrity']={'actual_sha256':sha(Path(s['area00_candidate']['path'])),'match':sha(Path(s['area00_candidate']['path']))==s['area00_candidate']['sha256']}
s['preflight_scope']={'AREA_01':'AREA_MANIFEST, MONSTER_INFO all5, prior GENERATION_SPEC new3, naming/format/master, STYLE_INDEX classification all183 and atlas, selected actual previews inspected. Other role docs not all re-read; no claim of full five-area preflight completion.','AREA_02_05':'Extracted verbatim for future read, NOT_STARTED_RESTART; no new art.'}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'evidence/QUALITY_GATE.json').write_text(json.dumps({'result':'FAIL','skill':'s_mon_mushroom','attempts':3,'criteria':gates,'packaging':'FORBIDDEN','latest_reference_limit':'Nexon July23 official update verifies release date, not pixel rendering. June13 Nexon Peak creator showcase images were visually inspected; cutscene/body silhouettes excluded. INPUT RECENT_SECONDARY not promoted.'},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'staging/REJECTED_NOT_DELIVERY.md').write_text('All staged frames are failed quality trials. Do not import, package, approve, or use as positive style reference.',encoding='utf-8')
report='''# BATCH_01 — 중단 / 새 품질 게이트 실패

기존 실행 20260912_212559의 모든 NEW_ART와 기존 OUTPUT ZIP은 납품에서 철회했다. 기존 실행을 재개하지 못하도록 생성·패키징 코드에 중단 검사를 추가했다. 실패 파일은 근거 보관용으로만 남기며 긍정 참고자료로 쓰지 않는다. AREA00 원본 후보와 승인 INPUT, 게임 데이터는 변경하지 않았다.

실패 원인: VFX 대신 ICON 중심 참고, 일반 컨셉아트 표현을 유도한 프롬프트, 큰 불투명 물체·거친 면 분할·외곽광, 셀 경계 문제, 알파/아트 게이트 이전 패키징. 파일 검사는 스타일 승인 근거가 되지 않는다.

새로 한 작업: 원본 AREA00 연속 PNG와 INPUT 원장·실제 몬스터·스타일 분류 재확인, 날짜가 있는 공개 참고자료의 실제 프레임 비교, 실패 이미지를 참조하지 않은 주황 버섯 CAST 신규 생성 3회. 최초 체크무늬 혼입, 두 번째 불투명 덩어리/갈색 테두리, 세 번째 흐린 중간톤/연무형 렌더링으로 각각 탈락했다. 세 번째는 실제 384×384 RGBA 8프레임과 세 배경 합성을 만들었지만 품질 통과본이 아니다.

첨부 CODEX_AREA_BATCH5_PRODUCTION_KO.txt의 같은 결함 초기 생성 + 최대2회 재시도 제한에 도달했다. 기준 미달 표현을 다른 스킬로 확산하지 않으므로 새 BATCH_01 전체 제작은 미완료이며 품질 게이트에서 보류한다. 새 ICON/Area Preview/OUTPUT ZIP은 만들지 않았다. 다음 배치도 시작하지 않았다. 이 보고서는 제작 완료를 대신하지 않는다.

7개 기준의 개별 판정은 QUALITY_GATE.json. 자동 파일 검사, 자체 아트 판정, 사용자 승인, 게임 실행 검증을 분리한다. 런타임과 브라우저 실제 재생은 NOT_CHECKED.
'''
(R/'evidence/RESTART_RESULT.md').write_text(report,encoding='utf-8')
page='''<!doctype html><meta charset="utf-8"><title>BATCH_01 실패 원인 / 새 시도</title><style>body{background:#20242b;color:#eee;font:16px sans-serif;margin:28px}img{max-width:100%;background:#555}section{margin:32px 0}p{max-width:1000px;line-height:1.7}</style><h1>BATCH_01 중단 — 품질 게이트 미통과</h1><p>기존 결과는 실패 샘플이며 납품 철회. 아래 새 시도들도 승인본·스타일 기준이 아닙니다. 다른 몬스터 제작과 ZIP 패키징을 진행하지 않았습니다.</p><section><h2>기준: 실제 AREA00 프레임</h2><img src="AREA00_ACTUAL_FRAMES.png"></section><section><h2>새 시도2 — 불투명 덩어리와 테두리 때문에 탈락</h2><img src="MUSHROOM_CAST_3_BACKGROUNDS.png"></section><section><h2>새 시도3 — 연무형 렌더링과 약한 중간톤 때문에 탈락</h2><img src="MUSHROOM_CAST_ATTEMPT3_3_BACKGROUNDS.png"></section><p><a href="RESTART_RESULT.md">상태와 실패 기록</a> · <a href="QUALITY_GATE.json">7개 품질 기준</a> · <a href="../PRODUCTION_STATE.json">재개 상태</a></p>'''
(R/'evidence/FAILURE_COMPARISON.html').write_text(page,encoding='utf-8')
with (R/'ALL_AREAS_INDEX.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['area','status','input_sha256','area00_candidate_sha256','output_zip','next_batch'])
 for a,v in s['areas'].items():w.writerow([a,v['status'],v['input_sha256'],s['area00_candidate']['sha256'],'NOT_CREATED_QUALITY_GATE_FAILED','BATCH_02_NOT_STARTED'])
print(json.dumps({'status':s['status'],'input_integrity':all(x['match'] for x in s['input_integrity']),'area00_integrity':s['area00_integrity'],'new_zip_count':len(list((R/'delivery').rglob('*.zip')))},ensure_ascii=False))
