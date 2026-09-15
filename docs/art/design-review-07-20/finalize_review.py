from pathlib import Path
import json,csv,html,hashlib,zipfile,collections
O=Path(__file__).parent/'20260914_astra_review'
rs=json.loads((O/'records.json').read_text(encoding='utf-8'))
issues={
's_mon_drake':('권장','불꽃 방향·성장·해체는 맞는다. 작은 크기에서 검붉은 잔입자가 거칠게 뭉친다. AREA00의 면 분리와 비교해 주 화염 면을 정리하는 부분 보정을 권장한다.'),
's_mon_jr_balrog':('권장','뿔 고리와 전방 파동이 식별된다. 해체 구간의 검붉은 작은 덩어리가 많이 남아 주 실루엣보다 질감이 앞선다. 잔입자·중간톤 정리 대상으로 남긴다.'),
's_mon_hector':('권장','세 갈래 설원 참격은 맞으나 F03에서 둥근 휘감기 형상으로 바뀌었다가 F04에 다시 발톱이 커진다. 참격 개수와 방향 연결을 다듬을 여지가 있다.'),
's_mon_pianus':('보정 필요','F05~F07의 밝은 수평 빔 끝이 수직 직선으로 동시에 끊긴다. 최외곽 접촉 검사는 통과해도 내부 형상 마감 문제는 남는다. 원본 시트 대조 후 끝 형상을 복구할 것. 기존 가장자리 검사 PASS를 전체 아트 PASS로 해석하면 안 된다.'),
's_mon_wooden_target_dummy':('권장','목재 회전 궤적은 적합하다. 마지막 프레임에도 목재 핵이 또렷하게 남아 one-shot 종료 때 갑자기 사라질 가능성이 있다. 실제 이름/ID는 기록의 값을 우선하며 마지막 alpha 감소를 검토한다.'),
's_mon_blood_harp':('권장','깃털·음파의 색과 재질은 적합하다. F01의 세운 깃털이 F02에서는 빠지고 F03에서 다시 나타난다. 같은 깃털의 진동/회전으로 읽히도록 중간 형상 연결을 다듬는 것을 권장한다.'),
's_mon_blue_wyvern':('보정 필요','F02~F04가 오른쪽 용머리/원형 문에서 왼쪽으로 뿜는 구도다. INPUT의 오른쪽 발사와 충돌한다. 공식 프리징 브레스의 용머리·원형 문 구성까지 매우 가깝게 따라가 마감 참조를 넘어선다. 용머리 표현을 제거하고 쐐기 얼음과 오른쪽 숨결이라는 고유 소재로 다시 구성할 필요가 있다. 바이트 복제 여부는 이 판단에 포함하지 않는다.'),
's_mon_mecateon':('보정 필요','F03의 빔 끝, F04~F05의 오른쪽 타격광·파편이 동일한 수직선에서 끊겨 보인다. 투명 여백을 남긴 채 내부에서 잘린 형태이므로 edge=0만으로 해결됐다고 볼 수 없다. 렌즈·분홍 팔레트는 보존하고 끝/타격광 복구가 필요하다.'),
's_mon_zeno':('권장','중력륜과 외계 코어는 식별된다. F05의 수평 타원륜에서 F06의 정면 나선으로 기울기가 크게 바뀐다. 원근 전환 중간 형상을 다듬어 고정 기준축의 연속성을 높이는 것을 권장한다.'),
's_mon_cygnus':('권장','검은 꽃왕관·시든 꽃잎은 명세에 맞으므로 밝은 불꽃으로 바꾸면 안 된다. 검정 배경에서 꽃잎 중간톤의 구분이 약하다. 어두운 소재를 유지하며 필요한 일부 면만 분리하는 보정을 권장한다.'),
's_mon_mutant_iron_hog':('권장','철갑 코어·오른쪽 돌진은 적합하다. 황야 먼지의 주황 흐름이 화염처럼 읽힐 여지가 있다. 색 전체를 바꾸기보다 먼지 입자와 금속/먼지 경계를 정리하는 권장 항목이다.')
}
# Some manifests use a different English ID for the wooden training dummy.
for r in rs:
 if r['area']=='AREA_15' and '목인 회전' in r['skill_name']:
  issues[r['skill']]=issues['s_mon_wooden_target_dummy']
issues['s_mon_cygnus']=('보정 필요','F05 오른쪽 꽃잎/바닥 고리와 F06 양쪽 가장자리 조각에 수직 절단이 확인된다. 어두운 꽃왕관의 색·재질은 유지하고 원본 추출 영역을 먼저 조사해야 한다. 배경에서의 중간톤 읽힘 개선은 잘림 복구 후 별도 권장 사항이다.')
issues['s_mon_timer']=('권장','시간 고리와 시계바늘의 전개는 명세에 맞는다. F00 하단에 본체와 멀리 떨어진 작은 청록 잔점이 보인다. 주 형상과 분리된 매우 약한 잔류를 원본과 대조한 뒤 정리할 수 있다.')
for r in rs:
 v,n=issues.get(r['skill'],('유지 가능','몬스터/스킬의 선언 소재와 대표 형상이 연결되고, 명암층·주 실루엣·ICON의 형태 언어가 양립한다. 필수 원화 변경을 요구할 명확한 문제는 이번 정적 프레임 검토에서 찾지 못했다.'))
 r['verdict']=v;r['review_note']=n
 if 'required_frames' not in r:raise RuntimeError('Run technical checks first')
summary=[]
for a in range(7,21):
 part=[r for r in rs if r['area']==f'AREA_{a:02}'];c=collections.Counter(r['verdict'] for r in part)
 summary.append(dict(area=f'AREA_{a:02}',skills=len(part),vfx=sum(len(r['frames']) for r in part),icons=len(part),**dict(c)))
api=json.loads((O/'LIVE_RESOURCE_API.json').read_text(encoding='utf-8'))
api_missing=[q for x in api for q in x.get('response',{}).get('notFound',[])];api_errors=[x['error'] for x in api if 'error' in x]
assets=[p for r in rs for p in r['frames']+r['icons']]
tech={'count_fail':[r['skill'] for r in rs if not r['count_ok']], 'size_fail':[p['path'] for p in assets if not p['size_ok']], 'hash_fail':[p['path'] for p in assets if not p['file_hash_ok']], 'monster_hash_fail':[r['skill'] for r in rs if not r['monster_brief_hash_match']], 'mode_fail':[p['path'] for p in assets if p['mode']!='RGBA'], 'edge_contact':[p['path'] for p in assets if p['edge_max']>0], 'safe85_a16_fail':[p['path'] for p in assets if not p['safe85_a16']], 'api_requested':sum(len(x['requested']) for x in api),'api_missing':api_missing,'api_errors':api_errors}
extras=json.loads((O/'EXTRA_SOURCE_FILES.json').read_text(encoding='utf-8'))
with (O/'SKILL_VERDICTS.csv').open('w',encoding='utf-8-sig',newline='') as f:
 keys=['area','monster','monster_name','skill','skill_name','verdict','review_note','zip','zip_sha'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rs)
(O/'records.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'REVIEW_STATE.json').write_text(json.dumps(dict(status='REVIEW_COMPLETE_NOT_APPROVED',scope='AREA07-20',art_edited=False,runtime='NOT_CHECKED',timed_animation_observation='NOT_CHECKED',areas=summary,technical=tech),ensure_ascii=False,indent=2),encoding='utf-8')
text=['# AREA 07–20 실제 최종 PNG 디자인 검토','', '대상: 14 Area · 71 스킬 · VFX 400프레임 · 최종 ICON 71개. 최종 ZIP에서 추출한 파일로 검토했다. 기존 PASS 상태는 판정 근거로 재사용하지 않았다. 원본 ZIP 및 게임 데이터는 변경하지 않았다.','',
'## 판정 범위와 한계','',
'- 실제 모든 스킬의 전체 순서 프레임, MONSTER_IMAGE, 최종 ICON을 합성해 눈으로 검토했다. 전체 프레임의 정적 흐름을 보았으며 명세 속도로 움직이는 장면을 직접 관찰하거나 게임 실행 검증을 한 것은 아니다. 자동 재생 뷰어는 실제 PNG와 명세 간격(일반100ms/보스80ms)을 사용한다. 실시간 체감, 게임 표시 크기·offset·타격 타이밍은 NOT_CHECKED다.',
'- 명세의 WHAT/필수 NEW_ART 역할과 렌더링 품질을 분리했다. 패시브는 RUNTIME_ROLE_MAP의 ICON-only 선언을 우선하며 GENERATION_SPEC의 일반적인 6프레임 예시로 누락 판정하지 않는다.',
'- INPUT 안의 24종 공식 스킬 참조 이미지 및 SOURCE.json과 비교했다. 공식 API에서 몬스터/참조 RUID 136개를 실제 조회했다. 웹 검색기 화면은 이번 세션에서 두 차례 응답 시간 초과로 열리지 않았다. 사이트의 현재 화면/재생을 보았다고 주장하지 않는다. API와 사이트는 같은 서비스이며 두 독립 데이터셋이 아니다.',
'- 공식 자료에는 오래된 스킬과 VI 계열이 함께 있다. 모두 최신 출시 스킬이라고 하지 않는다. 표시용 GIF에서 추출된 흰 배경 프레임은 엔진 원본 RGBA가 아니므로 공식 알파의 품질 수치 비교에 쓰지 않는다.',
'- AREA00–05 검토에서 확인한 마감 기준과 대비했다. 대부분 게임 스킬용 형태/연속 프레임으로 읽히지만, 공식 원작과 완전히 같은 그림체로 보증할 수준은 아니다. 일부는 광택이 두껍거나 화염 잔입자가 더 거칠다. 이 차이만으로 전량 재생성을 요구하지 않는다.',
'- 유지 가능은 사용자 승인이나 게임 반입 PASS가 아니다. 원화의 직접 복제/생성 참조 실제 전달 여부는 생산 로그 전수 감사하지 않았으므로 NOT_CHECKED다. 다만 블루 와이번의 특정 구성 유사성은 눈으로 확인한 디자인 문제로 기록한다.',
'', '## 우선 보정','']
for r in rs:
 if r['verdict']=='보정 필요':text.append(f"- {r['area']} {r['monster_name']} / {r['skill_name']}: {r['review_note']}")
text+=['','## 파일 검사','',json.dumps(tech,ensure_ascii=False,indent=2),'',
'안전영역 계산: alpha>=16의 bbox가 중앙85%(좌/상7.5% 이상, 우/하92.5% 이하)에 포함되는지 검사. 주요 형상 참고용으로 alpha>=128 bbox도 records.json에 남겼다. 외곽 픽셀 검사/안전영역 검사는 내부에서 잘린 끝, 구멍, 리듬 불연속을 검출하는 검사가 아니다. 미약한 발광까지 무조건 제거하지 않는다.',
'', '## 납품 구조/기록 정리','',
'- AREA19: 상급기사 B의 ICON_KEYED_SOURCE.png가 최종 ICON 폴더에 포함됐다. AREA20: 스톤마스크·다크골렘·스텀피의 동일 유형 제작 원본 3개가 포함됐다. 최종 ICON 71개와 별개로 총4개다. 삭제하지 말고 후속 후보 패키지에서 provenance/source로 분리하고 반입 목록에서 제외해야 한다.',
'- AREA11 WORK_STATE가 생성 전/생성 중으로 남아 실제 ZIP 내용과 불일치한다. 저장된 PASS/COMPLETE와 실제 납품을 분리해야 한다. 이번 결과는 실제 ZIP SHA와 PNG 목록으로 식별했다.',
'','## 스킬별 판정','']
for r in rs:text += [f"### {r['area']} · {r['monster_name']} · {r['skill_name']} — {r['verdict']}",r['review_note'],r['material'],'']
text+=['## 이후 보정 순서','',
'1. 00–05에서 이미 찾은 00 푸른 껍질 alpha 구멍, 02 와일드보어 방향, 04 주니어 레이스 내부 잘림과 이번 10·16·18·19의 문제를 우선 처리한다.',
'2. 잘림은 생성 원본 시트와 분할 기록을 먼저 대조한다. 완전한 형상이 없을 때만 native 편집으로 부분 복원한다. 블루 와이번은 방향 및 원작 고유 구성 문제라 원화 재구성이 필요할 수 있다.',
'3. 00 및 17 캔버스 규격 충돌과 19·20 중간 원본 혼입, 상태 기록을 정리한 독립 후보를 만든다. 단순 확대를 고해상도 원화 복원이라고 하지 않는다.',
'4. 권장 사항은 기존 팔레트/좋았던 재질을 보존한 채 전후 비교로 모은다. 일괄 스타일 변경이나 전체 재생성은 하지 않는다.',
'5. 보정은 여기 Codex에서 수행하며 Work에 다시 외주할 필요가 없다. 승인본은 덮어쓰지 않는다. AREA06은 이번 요청 범위에 없어 추가 검증하지 않았다.']
(O/'DESIGN_REVIEW.md').write_text('\n'.join(text),encoding='utf-8')
css='body{background:#1b1f29;color:#eee;font:16px sans-serif;margin:24px}a{color:#9de}section{border-top:1px solid #678;padding:20px 0}.strip{width:100%;max-width:2600px}.bg{max-width:100%}.anim{width:384px;height:384px;object-fit:contain;background:#555}p{white-space:pre-line}'
page=['<!doctype html><meta charset="utf-8"><title>AREA07–20 비교 검토</title><style>'+css+'</style><h1>AREA07–20 실제 최종 자산 비교</h1><p>사용자 승인 전 검토 · 게임 실행 NOT_CHECKED · 제작 원본 PNG는 최종 ICON에서 제외하여 표시. 파일 기반 재생이며 마지막 프레임 후500ms 간격.</p><a href="DESIGN_REVIEW.md">전체 검증 기록</a> · <a href="SKILL_VERDICTS.csv">스킬별 판정</a>']
for r in rs:
 base=r['area']+'/'+r['skill'];page.append('<section><h2>'+html.escape(r['area']+' '+r['monster_name']+' / '+r['skill_name']+' — '+r['verdict'])+'</h2><p>'+html.escape(r['review_note'])+'</p><img class="strip" src="'+base+'/strip.jpg"><br><img class="bg" src="'+base+'/backgrounds.jpg"><br>')
 if r['frames']:page.append('<img class="anim" data-ms="'+str(r['interval_ms'])+'" data-frames=\''+json.dumps([p['path'] for p in r['frames']])+'\'>')
 page.append('<p>'+html.escape(r['material'])+'</p>'+ ' · '.join('<a href="https://maplestoryworlds-resourcesearch-new.nexon.com/search?category=skill&amp;selected='+pid+'">'+html.escape(n)+'</a>' for n,pid in r['references'])+'</section>')
page.append('<h2>공식 참조 — 표시용 프레임, 엔진 RGBA 아님</h2>')
for r in json.loads((O/'references.json').read_text(encoding='utf-8')):page.append('<h3>'+html.escape(r['official_name'])+'</h3><img class="bg" src="REF_'+r['key']+'.jpg">')
page.append('<script>document.querySelectorAll(".anim").forEach(im=>{let a=JSON.parse(im.dataset.frames),i=0;function go(){im.src=a[i];i=(i+1)%a.length;setTimeout(go,i?+im.dataset.ms:500)}go()})</script>')
(O/'REVIEW_VIEWER.html').write_text(''.join(page),encoding='utf-8')
print(json.dumps({'verdicts':dict(collections.Counter(r['verdict'] for r in rs)),'technical':tech},ensure_ascii=True))
