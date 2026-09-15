from produce import *
from PIL import ImageFont,ImageDraw
import html
F='C:/Windows/Fonts/malgun.ttf'
font=ImageFont.truetype(F,18);small=ImageFont.truetype(F,13)
def writecsv(p,rs):
 if not rs:return
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def bg(im,size,color):
 out=Image.new('RGBA',(size,size),color);im=im.copy();im.thumbnail((size,size),Image.Resampling.LANCZOS);out.alpha_composite(im,((size-im.width)//2,(size-im.height)//2));return out
def package(a):
 s=json.loads(S.read_text(encoding='utf-8'));area=s['areas'][a];out=R/'BATCH_01'/f'{a}_IMAGES_OUTPUT';required=[r for r in area['roles'] if r['required']=='true'];records=[];checks=[]
 if s.get('resume_allowed') is False:raise RuntimeError('USER_STOPPED_REJECTED: withdrawn run cannot be packaged')
 for r in required:
  files=r.get('files',{});scale=1
  if r['production_decision']=='NEW_ART' and files and not r.get('final_transform'):
   for rec in files.values():
    im=Image.open(R/rec['path']);n=im.width
    for threshold,fraction in [(16,.85),(128,.70)]:
     box=im.getchannel('A').point(lambda x:255 if x>=threshold else 0).getbbox()
     if box:
      extent=max(abs(box[0]-n/2),abs(box[1]-n/2),abs(box[2]-n/2),abs(box[3]-n/2));scale=min(scale,(fraction*n/2-1)/max(extent,1))
   scale=min(1,scale)
   for rec in files.values():
    p=R/rec['path'];im=Image.open(p);n=im.width
    if scale<1:
     # One shared transform around the fixed normalized center; never autocrop/recenter.
     im=im.transform((n,n),Image.Transform.AFFINE,(1/scale,0,n/2-n/2/scale,0,1/scale,n/2-n/2/scale),Image.Resampling.BICUBIC)
     im.save(p)
   r['final_transform']={'scale':scale,'pivot':[.5,.5],'reason':'common role safe area: alpha>=16 inside85%; alpha>=128 inside70%'}
  for i,rec in sorted(files.items(),key=lambda x:int(x[0])):
   p=R/rec['path'];im=Image.open(p);alpha=im.getchannel('A');box=alpha.point(lambda x:255 if x>=16 else 0).getbbox();n=im.width
   safe=bool(box and min(box[0],box[1])>=.075*n-1 and max(box[2],box[3])<=.925*n+1)
   edge=max(alpha.crop((0,0,n,1)).getextrema()[1],alpha.crop((0,n-1,n,n)).getextrema()[1],alpha.crop((0,0,1,n)).getextrema()[1],alpha.crop((n-1,0,n,n)).getextrema()[1])
   valid=im.mode=='RGBA' and im.size==(int(r['canvas'].split('x')[0]),)*2 and alpha.getextrema()[0]==0 and alpha.getbbox() is not None and edge<16
   rec['sha256']=sha(p)
   records.append({'monster_id':r['monster_id'],'skill_id':r['skill_id'],'role':r['effect_role'],'frame':i,'path':str(p.relative_to(out)).replace('\\','/'),'sha256':sha(p),'size':f'{n}x{n}','frame_seconds':r['frame_seconds'],'runtime_use':r['runtime_use'],'production_decision':r['production_decision'],'registration':'UNASSIGNED','approval_status':'PENDING_USER_REVIEW'})
   checks.append({'path':str(p.relative_to(out)),'RGBA_nonempty_transparent_size_edge':valid,'safe85_alpha16':safe,'bbox_alpha16':str(box),'edge_alpha_max':edge,'source_cell_to_output_scale':r.get('source_cell_scale_to_output',1)})
  if len(files)==int(r['frame_count']):r['status']='PENDING_USER_REVIEW'
 area['status']='PENDING_USER_REVIEW' if all(len(r.get('files',{}))==int(r['frame_count']) for r in required) else 'PARTIAL'
 writecsv(out/'AREA_MANIFEST.csv',records);writecsv(out/'VALIDATION_FILES.csv',checks)
 blocks=[];overview=Image.new('RGB',(1400,80+len(set(r['monster_id'] for r in required))*440),'#20242c');d=ImageDraw.Draw(overview);d.text((20,20),a+' • '+area['status'],font=font,fill='white')
 for j,m in enumerate(dict.fromkeys(r['monster_id'] for r in required)):
  rs=[r for r in required if r['monster_id']==m];md=next((R/'provenance'/f'{a}_INPUT'/'monsters').glob(rs[0]['work_order']+'_'+m+'_*'))
  spec=(md/'GENERATION_SPEC.md').read_text(encoding='utf-8-sig');title=spec.splitlines()[0].replace('# GENERATION SPEC — ','')
  row=Image.new('RGB',(1400,440),'#30353e');dr=ImageDraw.Draw(row);dr.text((12,8),title,font=font,fill='white');monster=Image.open(md/'MONSTER_IMAGE.png').convert('RGBA');row.paste(bg(monster,120,'#555555').convert('RGB'),(10,48))
  monsterout=out/'monsters'/md.name;monsterout.mkdir(exist_ok=True,parents=True);shutil.copy2(md/'MONSTER_IMAGE.png',monsterout/'MONSTER_IMAGE_REFERENCE.png')
  rolehtml=[]
  for k,r in enumerate(rs):
   fr=[R/x['path'] for _,x in sorted(r.get('files',{}).items(),key=lambda x:int(x[0]))];y=52 if r['effect_role']=='ICON' else 182+(k-1)*0
   dr.text((145,y-22),r['effect_role']+' '+r['status']+' / '+r['frame_seconds']+'s',font=small,fill='#bde4ff')
   for i,p in enumerate(fr):
    im=Image.open(p);x=145+(i%8)*150;yy=y+(i//8)*125;row.paste(bg(im,112,'#777777').convert('RGB'),(x,yy));dr.text((x,yy+112),f'F{i:02}' if len(fr)>1 else 'ICON',font=small,fill='white')
   urls=[str(p.relative_to(out)).replace('\\','/') for p in fr]
   if urls:rolehtml.append('<div><h4>'+r['effect_role']+' '+('runtime_use=false' if r['runtime_use']=='false' else '')+'</h4><img class="anim" width="256" data-frames=\''+html.escape(json.dumps(urls),quote=True)+'\' data-ms="'+str(100 if r['frame_seconds']=='static' else round(float(r['frame_seconds'])*1000))+'" src="'+urls[0]+'"></div>')
   else:rolehtml.append('<p>'+r['effect_role']+': PENDING — no placeholder asset</p>')
  overview.paste(row,(0,70+j*440));(monsterout/'PREVIEW').mkdir(exist_ok=True);row.save(monsterout/'PREVIEW/labeled_preview.png')
  (monsterout/'RESULT_INFO.md').write_text(title+'\n\nPENDING_USER_REVIEW. NEW_ART generated with built-in image_gen; existing runtime RUIDs are provenance only. Game import and playback NOT_CHECKED.\n\n'+ '\n'.join(f'- {r["effect_role"]}: {r["status"]}; {len(r.get("files",{}))}/{r["frame_count"]}; runtime_use={r["runtime_use"]}; transform={r.get("final_transform","byte reuse")}' for r in rs),encoding='utf-8')
  blocks.append('<section><h2>'+title+'</h2><img width="120" src="monsters/'+md.name+'/MONSTER_IMAGE_REFERENCE.png"><div class="roles">'+''.join(rolehtml)+'</div></section>')
 overview.save(out/'AREA_OVERVIEW_PREVIEW.png')
 page='<!doctype html><meta charset="utf-8"><title>'+a+'</title><style>body{background:#242832;color:#eee;font:16px sans-serif;margin:24px}.roles{display:flex;gap:20px}img.anim{background:var(--bg,#777)}section{border-bottom:1px solid #777;padding:20px}</style><h1>'+a+' '+area['status']+'</h1><p>파일 기반 프레임 Preview · 게임 실행 NOT_CHECKED · 사용자 승인 대기</p><button onclick="document.body.style.setProperty(\'--bg\',\'#000\')">검정</button><button onclick="document.body.style.setProperty(\'--bg\',\'#fff\')">흰색</button><button onclick="document.body.style.setProperty(\'--bg\',\'#777\')">회색</button><button onclick="paused=!paused">재생/일시정지</button>'+''.join(blocks)+'<script>let paused=false;document.querySelectorAll(".anim").forEach(e=>{const f=JSON.parse(e.dataset.frames);let i=0;setInterval(()=>{if(!paused){e.src=f[i];i=(i+1)%f.length}},Number(e.dataset.ms))});</script>'
 (out/'AREA_REVIEW.html').write_text(page,encoding='utf-8')
 (out/'AREA_MANIFEST.md').write_text(a+' '+area['status']+'\n\nSee AREA_MANIFEST.csv for every delivered PNG. NO_RUNTIME_ROLE inventory retained in INPUT_PROVENANCE. Source sheets are original generated raster art, not overview crops.\n',encoding='utf-8')
 report=f'{a} {area["status"]}\n\n- Required roles: {len(required)}; delivered PNG: {len(records)}\n- File checks: {sum(c["RGBA_nonempty_transparent_size_edge"] for c in checks)}/{len(checks)} pass\n- Safe85 alpha>=16: {sum(c["safe85_alpha16"] for c in checks)}/{len(checks)}\n- Alpha: preserved native RGBA or documented exterior black matting. Dark enclosed material retained, soft boundary unpremultiplied.\n- Role common transform: alpha>=16 inside central85%, alpha>=128 central70%, pivot0.5/0.5, no per-frame recenter.\n- Source resolution scaling reported per file; boss sheet may require enlargement; art review required.\n- Timing preserved as input; viewer repeats only for inspection, runtime clips remain nonloop.\n- Game runtime/import/ruid assignment: NOT_CHECKED / NOT_PERFORMED.\n- Human approval: PENDING_USER_REVIEW.\n- Browser actual playback: NOT_CHECKED.\n'
 (out/'VALIDATION_REPORT.md').write_text(report,encoding='utf-8')
 prov=out/'INPUT_PROVENANCE';prov.mkdir(exist_ok=True)
 for f in (R/'provenance'/f'{a}_INPUT').glob('*'):
  if f.is_file():shutil.copy2(f,prov/f.name)
 (out/'TRANSFORM_RECORDS.json').write_text(json.dumps(required,ensure_ascii=False,indent=2),encoding='utf-8')
 save(s)
 suffix='_PARTIAL' if area['status']=='PARTIAL' else ''
 zp=R/'BATCH_01'/f'{a}_IMAGES_OUTPUT{suffix}.zip'
 with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
  for p in out.rglob('*'):
   if p.is_file():z.write(p,str(p.relative_to(out.parent)))
 with zipfile.ZipFile(zp) as z:
  assert z.testzip() is None
  for rec in records:assert hashlib.sha256(z.read(out.name+'/'+rec['path'])).hexdigest()==rec['sha256']
 area['zip']={'path':str(zp.relative_to(R)),'sha256':sha(zp),'crc_and_reextract_hash':'PASS'};save(s);print(a,area['status'],len(records),str(zp))
if __name__=='__main__':package(sys.argv[1])
