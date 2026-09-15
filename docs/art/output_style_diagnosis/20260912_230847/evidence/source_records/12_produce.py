from pathlib import Path
import json,sys,hashlib,shutil,re,csv,zipfile,io
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parents[1]; S=R/'PRODUCTION_STATE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(s):S.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
def find(s,a,m,role):return next(r for r in s['areas'][a]['roles'] if r['monster_id']==m and r['effect_role']==role)
def outputs(r):
 p=r['output_path'].split('...')[0];p=p.split('|')[0]
 if p=='n/a':
  a=r['area_id'].upper();folder=next((R/'provenance'/f'{a}_INPUT'/'monsters').glob(r['work_order']+'_'+r['monster_id']+'_*')).name
  p=f'{a}_IMAGES_OUTPUT/monsters/{folder}/'+r['required_file_set'].split('...')[0]
 return [p] if r['effect_role']=='ICON' else [re.sub(r'_F\d\d.png$',f'_F{i:02}.png',p) for i in range(int(r['frame_count']))]
def ingest(a,m,role,source,cols,rows,start=0):
 s=json.loads(S.read_text(encoding='utf-8'));r=find(s,a,m,role)
 if s.get('resume_allowed') is False:raise RuntimeError('USER_STOPPED_REJECTED: this production run may not resume')
 raw=R/'BATCH_01'/f'{a}_IMAGES_OUTPUT'/'SOURCE_SHEET'/m/role;raw.mkdir(parents=True,exist_ok=True)
 dst=raw/f'source_{start:02}_{r["attempts"]+1}.png';shutil.copy2(source,dst)
 im=Image.open(dst);r['attempts']+=1;r.setdefault('sources',[]).append({'path':str(dst.relative_to(R)),'sha256':sha(dst),'mode':im.mode,'size':im.size,'grid':[cols,rows],'start':start})
 save(s)
 if im.mode!='RGBA' or im.getchannel('A').getextrema()[0]!=0:
  ar=np.asarray(im.convert('RGB')).astype(float);lum=ar.max(2)
  edge=np.concatenate([lum[0],lum[-1],lum[:,0],lum[:,-1]])
  if np.percentile(edge,95)>8:raise ValueError('BLOCKED_NONBLACK_BACKGROUND')
  # Black-matte removal: retain opaque color above32; unpremultiply soft dark edge.
  # Only exterior-connected low light is keyed; enclosed dark material is preserved.
  mask=Image.fromarray(np.where(lum<32,255,0).astype('uint8'))
  padded=Image.new('L',(im.width+2,im.height+2),255);padded.paste(mask,(1,1));ImageDraw.floodfill(padded,(0,0),128)
  ext=np.asarray(padded)[1:-1,1:-1]==128
  alpha=np.where(ext,np.clip((lum-3)/29,0,1),1)
  rgb=np.clip(ar/np.maximum(alpha[:,:,None],1/255),0,255)
  im=Image.fromarray(np.dstack([rgb,alpha*255]).astype('uint8'),'RGBA')
  r['alpha_processing']='black matte: exterior connected maxRGB<32, alpha=(maxRGB-3)/29 clipped, unpremultiply; enclosed dark pixels opaque'
 size=int(r['canvas'].split('x')[0]);w,h=im.size
 r['source_cell_scale_to_output']=size/min(w/cols,h/rows)
 for i in range(min(cols*rows,int(r['frame_count'])-start)):
  box=(round(i%cols*w/cols),round(i//cols*h/rows),round((i%cols+1)*w/cols),round((i//cols+1)*h/rows))
  cell=im.crop(box)
  if not cell.getchannel('A').getbbox():raise ValueError('EMPTY_FRAME')
  f=R/'BATCH_01'/outputs(r)[start+i];f.parent.mkdir(parents=True,exist_ok=True)
  cell.resize((size,size),Image.Resampling.LANCZOS).save(f)
  r.setdefault('files',{})[str(start+i)]={'path':str(f.relative_to(R)),'sha256':sha(f),'source':str(dst.relative_to(R)),'split_box':box,'resize':[size,size]}
 if len(r.get('files',{}))==int(r['frame_count']):r['status']='GENERATED_PENDING_VALIDATION'
 else:r['status']='GENERATING'
 save(s);print(a,m,role,r['status'],len(r.get('files',{})))
def reuse(a):
 s=json.loads(S.read_text(encoding='utf-8'));z=zipfile.ZipFile(s['area00_candidate']['path']);records=[]
 inp=zipfile.ZipFile(s['areas'][a]['input_path'])
 for r in s['areas'][a]['roles']:
  if r['production_decision']!='AREA00_APPROVED_REUSE':continue
  r['files']={}
  for i,rel in enumerate(outputs(r)):
   suffix=f'_{r["skill_id"]}_ICON.png' if r['effect_role']=='ICON' else f'_{r["skill_id"]}_F{i:02}.png'
   matches=[n for n in z.namelist() if n.endswith(suffix) and '/monsters/' in n];assert len(matches)==1,matches
   old=[n for n in inp.namelist() if n.endswith(suffix) and '/approved_reuse/' in n];assert len(old)==1,old
   data=z.read(matches[0]);f=R/'BATCH_01'/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
   r['files'][str(i)]={'path':str(f.relative_to(R)),'sha256':sha(f),'source':matches[0],'byte_preserved':True}
   records.append({'monster_id':r['monster_id'],'skill_id':r['skill_id'],'role':r['effect_role'],'frame':i,'old_approved_path':s['areas'][a]['input_path']+'!'+old[0],'old_sha256':hashlib.sha256(inp.read(old[0])).hexdigest(),'candidate_path':s['area00_candidate']['path']+'!'+matches[0],'candidate_sha256':sha(f),'final_path':str(f.relative_to(R)),'registration':'UNASSIGNED','old_ruid_provenance':r['approved_target_ruid']})
  r['status']='REUSED_BYTE_VERIFIED'
 if records:
  p=R/'BATCH_01'/f'{a}_IMAGES_OUTPUT'/'REUSE_BASELINE_OVERRIDE.csv'
  with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 save(s);print('reuse',a,len(records))
if __name__=='__main__':
 if sys.argv[1]=='ingest':ingest(*sys.argv[2:6],*[int(x) for x in sys.argv[6:]])
 elif sys.argv[1]=='reuse':reuse(sys.argv[2])
