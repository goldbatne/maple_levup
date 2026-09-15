from pathlib import Path
import zipfile,csv,io,json,hashlib,datetime,shutil
root=Path('D:/maplestory_levup')
run=root/'docs/art/output_style_unified_batches'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
run.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
state={'run_id':run.name,'current_batch':'BATCH_01','next_batch':'BATCH_02_NOT_STARTED','status':'IN_PROGRESS','user_approval':'PENDING_USER_REVIEW','game_validation':'NOT_CHECKED','areas':{},'area00_candidate':{}}
ref=root/'docs/art/area00_refinement/20260912_203404/AREA_00_IMAGES_OUTPUT_REFINED_CANDIDATE.zip'
state['area00_candidate']={'path':str(ref),'sha256':sha(ref)}
for a in range(1,6):
 p=root/f'docs/art/images-input-packages-v2_4/AREA_{a:02}_IMAGES_INPUT_V2_4.zip';z=zipfile.ZipFile(p);prefix=f'AREA_{a:02}_IMAGES_INPUT_V2_4/'
 dest=run/'provenance'/f'AREA_{a:02}_INPUT'
 for n in z.namelist():
  rel=n.removeprefix(prefix)
  if n.endswith('/') or not n.startswith(prefix):continue
  if '/' not in rel or rel.startswith('monsters/') or ('STYLE' in Path(rel).name and rel.endswith(('.md','.csv'))):
   f=dest/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n))
 rows=list(csv.DictReader(io.StringIO(z.read(prefix+'OUTPUT_REQUIREMENTS.csv').decode('utf-8-sig'))))
 state['areas'][f'AREA_{a:02}']={'input_path':str(p),'input_sha256':sha(p),'status':'PENDING','roles':[dict(r,status='PENDING' if r['required']=='true' else 'NO_RUNTIME_ROLE',attempts=0) for r in rows]}
 (run/'BATCH_01'/f'AREA_{a:02}_IMAGES_OUTPUT').mkdir(parents=True)
(run/'work').mkdir();shutil.copy2(__file__,run/'work/init.py');shutil.copy2('C:/Users/dddd/Downloads/CODEX_AREA_BATCH5_PRODUCTION_KO.txt',run/'provenance/USER_INSTRUCTIONS.txt')
(run/'PRODUCTION_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
print(run)
