from pathlib import Path
import json,zipfile,urllib.request,urllib.parse,concurrent.futures,hashlib,time
root=Path(__file__).parent;logpath=root/'downloads.jsonl';archive=root/'download_cache.zip'
records={}
for line in logpath.read_text().splitlines():
 r=json.loads(line);records[r['id']]=r
details={r['id']:r for f in sorted((root/'details').glob('*.json')) for r in json.loads(f.read_text())['items']}
todo=[r for k,r in details.items() if records.get(k,{}).get('status')!='OK'];done=len(details)-len(todo);failed=0
def get(r):
 url=r['payload'].get('thumbnail');ext=Path(urllib.parse.urlparse(url).path).suffix;rel='media/'+r['id']+ext
 try:
  with urllib.request.urlopen(url,timeout=45) as f:b=f.read()
  if ext=='.png' and b[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('PNG signature')
  if ext=='.gif' and b[:3]!=b'GIF':raise ValueError('GIF signature')
  return r,b,dict(id=r['id'],type=r['type'],url=url,path=rel,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='OK',cache_archive=archive.name)
 except Exception as e:return r,None,dict(id=r['id'],url=url,status='FAILED',error=str(e))
with zipfile.ZipFile(archive,'a',zipfile.ZIP_STORED,allowZip64=True) as z,logpath.open('a',encoding='utf-8') as log,concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
 for r,b,record in pool.map(get,todo):
  if b is not None:z.writestr(record['path'],b);done+=1
  else:failed+=1
  log.write(json.dumps(record)+'\n');log.flush()
  if (done+failed)%250==0:
   state=dict(downloaded=done,failed=failed,complete=False,updated=time.time());(root/'download_state.json').write_text(json.dumps(state));print(json.dumps(state),flush=True)
(root/'download_state.json').write_text(json.dumps(dict(downloaded=done,failed=failed,complete=True)))
