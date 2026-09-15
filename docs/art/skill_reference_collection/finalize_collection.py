from pathlib import Path
import json,zipfile,hashlib,shutil,concurrent.futures
root=Path(__file__).parent.resolve(); workspace=Path('D:/maplestory_levup').resolve()
assert root==workspace/'docs/art/skill_reference_collection'
report=json.loads((root/'COLLECTION_REPORT.json').read_text(encoding='utf-8'))
assert report['status'] in ('COMPLETE_IN_DECLARED_SCOPE','PARTIAL') and report['zip_crc']=='PASS'
assert report['missing']==report.get('metadata_404_unavailable',[]),'Unexpected download loss'
archive=Path(report['zip_path']).resolve();assert archive.parent==root and archive.exists()
logs={}
for s in (root/'downloads.jsonl').read_text().splitlines():
 r=json.loads(s);logs[r['id']]=r
with zipfile.ZipFile(archive) as z:
 for r in logs.values():assert r['status']=='OK'
 with zipfile.ZipFile(root/'download_cache.zip') as cache_zip:
  for info in cache_zip.infolist():
   final_info=z.getinfo('MSW_SKILL_REFERENCE_LIBRARY/'+info.filename)
   assert (info.CRC,info.file_size)==(final_info.CRC,final_info.file_size),info.filename
 # Intermediate directories are newly created by this collection. Every file must
 # already be present byte-for-byte in the verified archive before removal.
 source_files=[]
 for name in ['media','details','selected']:
  d=(root/name).resolve();assert d.parent==root and d.is_relative_to(workspace)
  source_files.extend(p for p in d.rglob('*') if p.is_file())
 def compare(p):
  assert z.read('MSW_SKILL_REFERENCE_LIBRARY/'+p.relative_to(root).as_posix())==p.read_bytes(),str(p)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(compare,source_files))
 for p in root.glob('page_*.json'):assert z.read('MSW_SKILL_REFERENCE_LIBRARY/'+p.name)==p.read_bytes()
for name in ['media','details','selected']:
 d=(root/name).resolve();assert d.parent==root and d.is_relative_to(workspace);shutil.rmtree(d)
for p in root.glob('page_*.json'):p.unlink()
cache=root/'download_cache.zip'
if cache.exists():cache.unlink()
viewer=root/'VIEWER.html'
if viewer.exists():viewer.unlink() # The viewer is usable inside the extracted archive.
report['source_preservation_before_cleanup']='PASS: loose files byte-for-byte; cache entry CRC and size matched to CRC-verified final ZIP';report['intermediate_files']='Archived and removed after preservation check'
(root/'COLLECTION_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'README.md').open('a',encoding='utf-8') as f:f.write('\n\n최종 공통 ZIP 안에 전체 원본 수집 자료가 들어 있습니다. VIEWER.html은 ZIP을 푼 폴더에서 엽니다. 중간 media/details/selected 폴더는 바이트 보존 확인 후 정리했습니다. 수집 스크립트를 다시 사용할 때는 ZIP 내부 MSW_SKILL_REFERENCE_LIBRARY 내용을 이 폴더로 복원하세요.\n')
print(json.dumps(report,ensure_ascii=False))
