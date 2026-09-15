from pathlib import Path
import json,zipfile,hashlib,csv,io,datetime
root=Path(__file__).parent
state=json.loads((root/'download_state.json').read_text());assert state['complete'],'Downloads still running'
packs=[x for f in sorted(root.glob('page_*.json')) for x in json.loads(f.read_text())['items']]
details={x['id']:x for f in sorted((root/'details').glob('*.json')) for x in json.loads(f.read_text())['items']}
logs={}
for line in (root/'downloads.jsonl').read_text().splitlines():
 r=json.loads(line);logs[r['id']]=r
missing=[k for k in details if k not in logs or logs[k]['status']!='OK']
expected=[e for p in packs for e in p['payload']['elements'] if e['resource_type'] in ('sprite','animationclip')]
metadata_missing=sorted(set(e['ruid'] for e in expected)-set(details))
missing=sorted(set(missing+metadata_missing))
report={'scope':'Public API listed skill resource packs and their visual preview assets; not a verified dump of all engine source frames','packs':len(packs),'visual_entries':len(details),'downloaded':sum(v['status']=='OK' for v in logs.values()),'missing':missing,'audio_metadata_only':sum(e['resource_type'] in ('effect','voice','bgm') for p in packs for e in p['payload']['elements']),'new_art_generated':False,'latest_live_version':'NOT_VERIFIED','all_art_visual_review':'NOT_CHECKED; selected reference atlas inspected only','file_validation':'PNG/GIF signature on download; ZIP CRC at packaging','status':'COMPLETE_IN_DECLARED_SCOPE' if not missing else 'PARTIAL'}
report['listed_visual_entries']=len(set(e['ruid'] for e in expected));report['metadata_404_unavailable']=metadata_missing
catalog=[]
for p in packs:
 catalog.append({'id':p['id'],'names':p.get('names'), 'elements':[dict(e,local_path=logs.get(e.get('ruid'),{}).get('path'),download_status=logs.get(e.get('ruid'),{}).get('status','METADATA_ONLY')) for e in p['payload']['elements']]})
(root/'CATALOG.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf-8')
readme=f'''# MSW 공식 스킬 디자인 참고 라이브러리

수집 범위: 공개 API가 skill 카테고리로 반환한 **{len(packs):,}개 팩** 및 팩에 연결된 **{len(details):,}개 시각 리소스 표시용 PNG/GIF**. API에 노출되지 않은 자료까지 전부 확보했다고 주장하지 않는다. 스킬 팩의 음향 {report['audio_metadata_only']:,}개는 디자인 목적에 맞게 목록만 보존한다.

VIEWER.html을 열어 이름/팩 ID로 검색하면 각 팩의 로컬 PNG/GIF를 볼 수 있다. CATALOG.json에는 역할 경로와 RUID가 연결된다. media에는 CDN 제공 파일을 수정 없이 저장했다. details에는 API 응답을 보존한다. FILE_HASHES.csv에 SHA-256/출처 URL/수집 상태가 있다.

이것은 엔진 원본 전체 덤프가 아니다. GIF 프리뷰에는 배경이나 GIF 팔레트 제한이 있을 수 있고, 프레임 원본 RUID는 메타데이터에만 남아 있을 수 있다. 실제 원본 알파를 복구했다고 주장하지 않는다. 모든 스킬의 최신성/라이브 리비전은 NOT_VERIFIED이며 오래된 스킬과 이벤트·이동 리소스도 함께 들어 있다.

제작 시에는 모든 스킬을 섞지 말고 Area INPUT의 reference_resource_design에서 소재/역할에 맞는 자료를 우선 사용한다. 공식 스킬 디자인의 명암·재질·코어·발광·파편·프레임 전개·ICON 표현을 관찰하고, INPUT의 몬스터 소재와 동작으로 새롭게 만든다. 참고 파일 자체를 새 OUTPUT으로 납품하지 않는다.

수집 상태: {report['status']}. 누락 {len(missing)}개. 세부 상태는 COLLECTION_REPORT.json.
'''
(root/'README.md').write_text(readme,encoding='utf-8')
buf=io.StringIO(newline='');w=csv.writer(buf);w.writerow(['ruid','path','url','bytes','sha256','status'])
for k in sorted(details):
 r=logs.get(k,{});w.writerow([k,r.get('path',''),r.get('url',details[k]['payload'].get('thumbnail','')),r.get('bytes',''),r.get('sha256',''),r.get('status','MISSING')])
(root/'FILE_HASHES.csv').write_text(buf.getvalue(),encoding='utf-8-sig')
html='''<!doctype html><meta charset="utf-8"><title>MSW 스킬 디자인 참고</title><style>body{font:16px sans-serif;background:#242424;color:#eee;margin:24px}input{padding:12px;width:70%}details{padding:12px;border-bottom:1px solid #666}figure{display:inline-block;vertical-align:top;max-width:420px;margin:10px}img{max-width:400px;max-height:320px;object-fit:contain}figcaption{font-size:12px;overflow-wrap:anywhere}small{color:#bbb}</style><h1>MSW 공식 스킬 디자인 자료</h1><p>공개 API 표시용 이미지. 최신 라이브 버전·엔진 원본 알파는 미검증. 이름/팩 ID 검색 후 항목을 펼치세요.</p><input id="q" placeholder="스킬명 또는 팩 ID"><p id="count"></p><main id="list"></main><script>const data=__DATA__;function render(){const q=document.getElementById('q').value.toLowerCase();const a=data.filter(p=>(p.id+' '+JSON.stringify(p.names)).toLowerCase().includes(q));document.getElementById('count').textContent=a.length+'개 일치 (앞 60개 표시)';const list=document.getElementById('list');list.replaceChildren();for(const p of a.slice(0,60)){const d=document.createElement('details'),s=document.createElement('summary');s.textContent=(p.names?.ko||p.names?.en||['이름 미제공']).join(' / ')+' — '+p.id;d.append(s);d.addEventListener('toggle',()=>{if(!d.open||d.dataset.loaded)return;d.dataset.loaded='1';for(const e of p.elements){if(!e.local_path)continue;const f=document.createElement('figure'),im=document.createElement('img'),c=document.createElement('figcaption');im.src=e.local_path;im.loading='lazy';c.textContent=e.rel_path+' / '+e.ruid;f.append(im,c);d.append(f);}});list.append(d)}}document.getElementById('q').addEventListener('input',render);render();</script>'''.replace('__DATA__',json.dumps(catalog,ensure_ascii=False).replace('<','\\u003c'))
(root/'VIEWER.html').write_text(html,encoding='utf-8')
(root/'COLLECTION_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
dest=root/('MSW_SKILL_REFERENCE_LIBRARY'+('_PARTIAL' if missing else '')+'.zip')
with zipfile.ZipFile(dest.with_suffix('.zip.pending'),'w',zipfile.ZIP_STORED,allowZip64=True) as z:
 for n in ['README.md','VIEWER.html','CATALOG.json','FILE_HASHES.csv','COLLECTION_REPORT.json']:z.write(root/n,'MSW_SKILL_REFERENCE_LIBRARY/'+n)
 for n in ['missing_metadata.json','missing_metadata_result.json']:
  if (root/n).exists():z.write(root/n,'MSW_SKILL_REFERENCE_LIBRARY/'+n)
 z.write(root/'selected.json','MSW_SKILL_REFERENCE_LIBRARY/selected.json')
 for p in sorted(root.glob('page_*.json')):z.write(p,'MSW_SKILL_REFERENCE_LIBRARY/'+p.name,compress_type=zipfile.ZIP_DEFLATED)
 for p in sorted((root/'selected').rglob('*')):
  if p.is_file():z.write(p,'MSW_SKILL_REFERENCE_LIBRARY/'+p.relative_to(root).as_posix())
 for p in sorted((root/'details').glob('*.json')):z.write(p,'MSW_SKILL_REFERENCE_LIBRARY/details/'+p.name,compress_type=zipfile.ZIP_DEFLATED)
 cache=zipfile.ZipFile(root/'download_cache.zip') if (root/'download_cache.zip').exists() else None
 for r in logs.values():
  if r['status']=='OK':
   if r.get('cache_archive'):z.writestr('MSW_SKILL_REFERENCE_LIBRARY/'+r['path'],cache.read(r['path']))
   else:z.write(root/r['path'],'MSW_SKILL_REFERENCE_LIBRARY/'+r['path'])
 if cache:cache.close()
with zipfile.ZipFile(dest.with_suffix('.zip.pending')) as z:assert z.testzip() is None
dest.with_suffix('.zip.pending').replace(dest)
report['zip_path']=str(dest);report['zip_bytes']=dest.stat().st_size
h=hashlib.sha256()
with dest.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
report['zip_sha256']=h.hexdigest();report['zip_crc']='PASS'
(root/'COLLECTION_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
