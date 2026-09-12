from style_finish_review import *
import datetime
review=list(csv.DictReader((P/'CROSS_AREA_STYLE_REVIEW.csv').open(encoding='utf-8-sig')))
review=[r for r in review if r['area_id']!='area_00']
for r in review:r['scope']='TARGET_OUTPUT'
baseline=[]
obs={
'm_snail':'곡면 물방울 반사와 얇은 점액 띠; 팽창/튐 뒤 방울로 분리',
'm_blue_snail':'청색 곡면 반사/연속 물결 가장자리; 열린 물결에서 돔을 형성하고 다시 해체',
'm_red_snail':'ICON의 정돈된 붉은 색면; VFX 나선 코어와 얇은 잔상/후반 조각',
'm_mano':'진주/조개 곡면과 다층 광륜; F06 발현 뒤 고리와 입자가 줄어듦',
'm_slime':'젤의 곡면 반사/매끄러운 윤곽; 팽창에서 방사형 튐과 잔류 젤로 이어짐'}
for key,roles in B['files'].items():
 mid=next(k for k in obs if key.startswith(k+'_'))
 for role,files in roles.items():
  rr={k:'' for k in review[0]};h={}
  with zipfile.ZipFile(B['zip']) as z:
   for n in files:h[n]=hashlib.sha256(z.read(n)).hexdigest()
  rr.update(area_id='area_00',monster_id=mid,monster_name=key[len(mid)+1:].replace('_',' '),skill_id=files[0].split(mid+'_',1)[1].split('_ICON')[0].split('_F00')[0].split('.png')[0],role=role,style_judgment='CONSISTENT_WITH_REFERENCE',scope='APPROVED_REFERENCE',actual_output_zip=B['zip'],actual_output_files='|'.join(files),actual_file_sha256=json.dumps(h,ensure_ascii=False),reference_zip=B['zip'],reference_file='|'.join(files),reference_basis='BASELINE_INDEX의 실제 승인 원화; 기존 승인 사실을 사용. 이번 사용자 승인 추가 아님',finish_observation=obs[mid],observed_sequence=obs[mid],observed_frame_scope='ICON 전체' if role=='ICON' else f'F00–F{len(files)-1:02d} 전체',native_board=str(P/'CROSS_AREA_STYLE_BOARD'/('BASELINE_'+key+'.png')),user_approved='NO_NEW_APPROVAL',user_decision_needed='NO',display_conditions=review[0]['display_conditions'],temporal_review=review[0]['temporal_review'],game_size_review=review[0]['game_size_review'])
  rr['skill_id']=Path(files[0]).name.split(mid+'_',1)[1].split('_ICON')[0].split('_F00')[0].split('.png')[0]
  assert Path(rr['native_board']).exists();baseline.append(rr)
wc('AREA00_STYLE_REVIEW.csv',baseline);wc('CROSS_AREA_STYLE_REVIEW.csv',baseline+review)
stats=collections.Counter(r['style_judgment'] for r in review)
counts=list(csv.DictReader((P/'STYLE_AREA_COUNTS.csv').open(encoding='utf-8-sig')))
issues=[r for r in review if r['style_judgment'] in ['STYLE_OUTLIER','NEEDS_USER_REVIEW']]
png_counts=collections.Counter()
for r in review:png_counts[r['style_judgment']]+=len(json.loads(r['actual_file_sha256']))
body='''# AREA 00–20 전체 스타일 통일성 검수 결과

## 먼저 답할 네 가지

1. **현재 전체가 동일한 제작 기준으로 보인다고 판정할 수 없다.** AREA00 실제 승인 원화를 1차 기준으로 비교했으며, 픽셀 계단형 윤곽·명암·발광선 차이가 확인된 역할이 남아 있다. 전체 스타일 통일 완료가 아니다.
2. **AREA00 기준 5종/10역할/49 PNG와, AREA01–20의 실제 존재 19개 Area/99종/209역할/933 PNG를 대조했다.** AREA06은 예약 결번이다. 전체 ICON과 역할별 전 프레임을 직접 열어 순서상 변화까지 확인했다. 실시간 재생의 체감 리듬, 게임 배율·필터·배경·엔진 레이어 합성은 미검증이다.
3. **AREA14와 AREA18은 전 역할에서 마감 이탈이 보인다.** AREA05·11·12·13은 일부 역할만 이탈한다. AREA02·08·15의 일부 역할은 사용자 판단이다. 나머지 지역까지 수정 대상으로 확대하지 않는다.
4. **209개 검사 역할 중 162개는 원화 유지 가능, 37개는 마감 수정 후보, 10개는 사용자 판단 대상이다.** 원화 수정은 이번에 하지 않았다. 스타일 판단은 기존 명세·파일 결함을 통과시키지 않는다.

## 범위와 선택 근거

실제 프로젝트는 `D:/maplestory_levup`이다. 원 요청의 `D:/maplestory/_levup` 대신 실제 자료가 존재하고 검수 해시가 이어지는 경로를 사용했다.

`STYLE_AREA_SELECTION.csv`에 Area별 승인 INPUT V2.4·검사 OUTPUT의 실제 경로/해시와 선택 근거를 기록했다. 17개 기존 REPACK은 동일 ZIP이다. AREA11은 최신 원본 검수에 사용한 원본 납품 ZIP을 유지했다. RGB 체크무늬가 남은 생성 시도 2개는 실제 납품 아트로 채택하지 않았으며 이번 스타일 대상에서 제외했다. AREA12는 `output_repacked/20260912_165951_area11_12_final/AREA_12_IMAGES_OUTPUT_V2_4_FINAL_CANDIDATE.zip`을 사용했고, 원래 검수한 45개 역할 PNG와 바이트가 모두 같다.

전체 납품 원화 **933/933 BYTE_IDENTICAL**. 기존 원본 OUTPUT 19개와 승인 INPUT 19개의 해시도 기존 선정 기록과 일치한다. 원본 사본/모델 해시 99쌍을 확인하고 기존 실제 MSW 조회 기록을 재사용했다. 이번 보완의 원본 수준은 **신규 조회 0 / CACHED_SOURCE_CONFIRMED 99 / 미확인 0**이며, 이전 조회 결과를 새 조회로 기록하지 않았다.

기존 `ART_REVIEW.csv`의 설정 판정은 208개 NO_OBVIOUS_ISSUE, AREA11 킹 블록퍼스 PROJECTILE 1역할 SPEC_MISMATCH로 유지한다. 이번 별도 스타일 판정이 기존의 포괄적 스타일 평가를 대체한다. CRC·경로·규격은 해당 해시의 기존 검사 기록 및 AREA12 새 패키지 검증을 재사용했다. 게임 반입 성공이나 사용자 승인은 기록하지 않는다.

## 집계

CSV는 승인 기준 10행을 포함한 219행이다. 아래 집계는 검사 대상 209행만 포함한다. `scope` 필드로 APPROVED_REFERENCE와 TARGET_OUTPUT을 구분한다.

| Area | 종 | 역할 | 유지 가능 | 스타일 이탈 | 사용자 판단 | 이미지 미검토 |
|---|---:|---:|---:|---:|---:|---:|
'''
for r in counts:body+='| '+ ' | '.join(r[k] for k in ['area_id','pairs','roles','CONSISTENT_WITH_REFERENCE','STYLE_OUTLIER','NEEDS_USER_REVIEW','NOT_CHECKED'])+' |\n'
body+='\n파일 수 기준: '+', '.join(f'{k} {v} PNG' for k,v in png_counts.items())+'. 프레임 수의 차이는 스타일 판정 근거가 아니다.\n'
body+='''
## 수정 후보 — 역할 한정

공통 차이는 색이나 화려함이 아니라, 원본 크기에서 보이는 굵은 계단형 윤곽·끊기는 명암 띠·픽셀 단위 발광선이다. AREA14 호문의 독무는 거친 입상 외곽과 딱 끊기는 내부 덩어리도 비교했다. 재질 특성만으로 설명 가능한 차이는 확정 이탈로 넣지 않았다.

| Area | 대상 | 역할 범위 | 유지할 것 |
|---|---|---|---|
| 05 | 리본 돼지·파란 리본돼지·불가사리·쿨 젤리피쉬·킹크랑 | ICON 5개; 파란 리본돼지·쿨 젤리피쉬 REFERENCE 2개 | 리본/물결/젤/서리/집게 모티브, 정상 CAST 전체 |
| 11 | 라츠·블록퍼스 | REFERENCE 각 6프레임 | 톱니/위장 블록과 비전투 호흡; ICON 유지 |
| 11 | 킹 블록퍼스 | PROJECTILE F00–F03 | 왕관 블록 코어·각진 조각, CAST·ICON 유지. 기존 본체 조합의 명세 위반과 투명도 보류 별도 |
| 12 | 장난감 목마 | ICON 1개 | 허용된 눈 있는 목마 머리·태엽. CAST 유지 |
| 12 | 브라운테니·마스터 로보 | REFERENCE 각 6프레임 | 쿠션/솜, 톱니 장갑 및 비전투 호흡. ICON 유지 |
| 13 | 목도리 프릴드 | REFERENCE F00–F05 | 목도리/감지 잔상. ICON 유지 |
| 14 | 큐브슬라임·미스릴 뮤테·호문·로이드·키메라 | 실제 납품 12역할 전체 | 큐브 점액/미스릴판/플라스크 독무/금속 에너지탄/쌍 산성액의 형상·동작·역할 |
| 18 | 마티안·플라티안·메카티안·원로 그레이·제노 | 실제 납품 11역할 전체 | 수정핵/장갑/레이저/정신망/중력륜의 형상·동작·역할 |

모든 후보의 monster_id·skill_id·역할·실제 파일·문제 프레임·비교 기준·이유·유지 소재·변경할 마감은 `STYLE_ACTION_ITEMS.csv`, `CROSS_AREA_STYLE_REVIEW.csv`, `STYLE_OUTLIERS/INDEX.csv`에 있다. 전 역할이 후보인 Area도 내용을 새로 기획하거나 모든 형상을 재생성하라는 뜻은 아니다.

## 사용자 판단 — 확정 이탈과 분리

- AREA02 ICON 7개: 스톤골렘, 엑스텀프, 다크 엑스텀프, 와일드보어, 아이언호그, 스켈레톤 지휘관, 스텀피. 소재의 거친 결은 유지하되 거의 검은 두꺼운 외곽을 다른 Area보다 강조해도 되는지 판단. 파이어보어 ICON과 이 Area의 VFX는 이 목록에 포함하지 않는다.
- AREA08 스타픽시 PROJECTILE: 둥근 배지에 가까운 별핵의 내부/테두리 단순화. 러스터픽시 REFERENCE: 평면 태양 원판·날개 면의 단순화. 밝은 핵이나 참고 모티브를 단순화한 의도일 수 있으므로 확정 수정으로 분류하지 않았다.
- AREA15 원공 PROJECTILE: 같은 ICON/CAST보다 강조된 어두운 외곽과 분리된 명암을 작은 비행체의 가독성 차이로 허용할지 판단.

## AREA11·12와 별도 제한

킹 블록퍼스 CAST와 목마 CAST의 이전 본체 금지 보류는 철회 상태를 유지한다. 목마 ICON의 눈/머리는 허용 소재이고, 이번 후보 사유는 외곽·명암 마감이다. 이 점을 명세 위반으로 바꿔 적지 않았다.

AREA11 PROJECTILE의 기존 본체 조합 문제, 수정 시도 이미지의 **실제 투명도 미해결**, Preview 문구 겹침과 패키징 보류는 그대로 남는다. 이번에는 투명 배경 가공·이미지 생성·편집·재패키징을 수행하지 않았다. AREA12 패키지의 파일 보정 완료 사실과 이번 3개 역할의 새 스타일 후보는 별개다.

162개 유지 가능 역할은 이번 스타일 기준의 수정 대상에서 제외할 수 있다. 이는 사용자 최종 승인이나 게임 반입 준비 완료가 아니다. SkillTable 등록, DEF 패시브, 돌진 CAST 부착점 및 게임 표시 크기/엔진 합성 확인은 별도 런타임 항목으로 남긴다.

## 결과 파일

- `ART_STYLE_STANDARD.md`: 실제 승인 AREA00 관찰 기준과 허용 차이
- `CROSS_AREA_STYLE_REVIEW.csv`: 전체 219행(기준 10 + 검사 209), 설정/스타일/표시 한계 분리
- `CROSS_AREA_STYLE_BOARD/`: 5개 기준 전체 프레임 + 19개 ICON + 110개 역할 전체 프레임 보드; 큰 보드 행별 보조본 및 소재/역할 비교 9장
- `STYLE_OUTLIERS/`: 37개 이탈 + 10개 사용자 판단 역할의 원본/2배 확대 비교 47장과 INDEX
- `STYLE_ACTION_ITEMS.csv`: 사용자 결정·마감 수정 후보 47행
- `STYLE_PNG_BYTE_PRESERVATION.csv`: 검사 원화 933개 바이트 보존
- `STYLE_AREA_SELECTION.csv`, `STYLE_SOURCE_CACHE_REUSE.csv`, `STYLE_EVIDENCE_HASHES.csv`: 경로·해시·기존 검수 재사용 근거

정지 프레임 및 순서상 변화를 확인한 범위의 결론이다. 실제 게임 크기와 실시간 재생 체감까지 통일되었다는 의미로 읽으면 안 된다.
'''
(P/'CROSS_AREA_STYLE_SUMMARY.md').write_text(body,encoding='utf-8')
summary=P/'REVIEW_SUMMARY.md';s=summary.read_text(encoding='utf-8')
notice='> **추가 전체 스타일 검수:** 기존 포괄적 스타일 평가는 [CROSS_AREA_STYLE_SUMMARY.md](CROSS_AREA_STYLE_SUMMARY.md) 및 CROSS_AREA_STYLE_REVIEW.csv로 대체합니다. 검사 대상 209역할 중 유지 가능 162, 스타일 이탈 37, 사용자 판단 10. 기존 명세 판정과 AREA11 투명도 기술 보류는 별도 유지합니다.\n\n'
if '추가 전체 스타일 검수:' not in s:summary.write_text(notice+s,encoding='utf-8')
print('baseline',len(baseline),'all rows',len(baseline+review),'file counts',dict(png_counts))
