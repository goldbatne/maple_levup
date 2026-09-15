from pathlib import Path
import json,zipfile,io,csv,hashlib,datetime
root=Path(__file__).parent;base=root.parent/'images-input-packages'; rows=list(csv.DictReader(io.StringIO((base/'ALL_AREAS_INDEX.csv').read_text(encoding='utf-8-sig'))))
backup=zipfile.ZipFile(sorted((root/'backups').glob('INPUTS_BEFORE_*.zip'))[0]);results=[]
for r in rows:
 f=base/r['zip_file'];prompt=base/r['prompt_file'];z=zipfile.ZipFile(f);p=f.stem+'/'
 old=zipfile.ZipFile(io.BytesIO(backup.read(f.name)));assert z.testzip() is None
 hashes=list(csv.DictReader(io.StringIO(z.read(p+'INPUT_FILE_HASHES.csv').decode('utf-8-sig'))))
 for h in hashes:assert hashlib.sha256(z.read(p+h['path'])).hexdigest()==h['sha256'],h['path']
 manifest=list(csv.DictReader(io.StringIO(z.read(p+'AREA_MANIFEST.csv').decode('utf-8-sig'))));maps=json.loads(z.read(p+'reference_resource_design/AREA_REFERENCE_MAP.json'))
 assert {m['skill_id'] for m in maps}=={m['skill_id'] for m in manifest}
 preserved=0
 for n in old.namelist():
  if n.endswith('.png') or n.endswith(('AREA_MANIFEST.csv','MONSTER_INFO.md','RUNTIME_ROLE_MAP.md','SOURCE_PROVENANCE.md','OUTPUT_FORMAT_SPEC.md','OUTPUT_NAMING_SPEC.md')):
   assert old.read(n)==z.read(n),n;preserved+=1
  if n.endswith('GENERATION_SPEC.md'):
   assert z.read(n).decode('utf-8').startswith(old.read(n).decode('utf-8-sig')),n
 for m in maps:
  for key in m['groups']:
   assert p+'reference_resource_design/'+key+'/SOURCE.json' in z.namelist()
   assert any(n.startswith(p+'reference_resource_design/'+key+'/frames/') and n.endswith('.png') for n in z.namelist())
 r['zip_bytes']=str(f.stat().st_size);r['zip_sha256']=hashlib.sha256(f.read_bytes()).hexdigest();r['prompt_sha256']=hashlib.sha256(prompt.read_bytes()).hexdigest()
 results.append({'area':r['area_num'],'skills':len(manifest),'crc':'PASS','all_entry_hashes':'PASS','monster_images_and_fixed_spec':'PRESERVED','preserved_files':preserved,'all_skills_have_actual_design_refs':'PASS'})
with (base/'ALL_AREAS_INDEX.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
md=['# AREA INPUT — 공식 스킬 디자인 참조 개편','', '20개 운영 Area / 104개 스킬. AREA06은 기존 기준에서 제외되어 있으며 새로 만들지 않았다.','각 ZIP 내부 reference_resource_design 폴더에서 실제 공식 PNG/GIF, 추출 프레임, 원본 RUID/URL, 몬스터별 연결표를 확인한다.','공식 리소스의 디자인·명암·재질·발광을 참고하도록 지침을 수정했다. 신규 아트 결과 품질을 미리 승인한 것은 아니다.','','|Area|이름|INPUT ZIP|제작 TXT|','|---|---|---|---|']
for r in rows:md.append(f"|{r['area_num']}|{r['area_name']}|[{r['zip_file']}]({r['zip_file']})|[{r['prompt_file']}]({r['prompt_file']})|")
(base/'ALL_AREAS_INDEX.md').write_text('\n'.join(md),encoding='utf-8')
(root/'INPUT_VALIDATION.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'packages':len(results),'skills':sum(r['skills'] for r in results),'checks':'PASS'},ensure_ascii=False))
