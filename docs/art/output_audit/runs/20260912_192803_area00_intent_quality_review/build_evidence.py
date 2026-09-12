from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import zipfile,json,csv,io,hashlib,math,re
P=Path(__file__).parent
S=json.loads((P/'SELECTION.json').read_text(encoding='utf-8'))
IZ=next(r['path'] for r in S if r['kind']=='AREA00_INPUT');OZ=next(r['path'] for r in S if r['kind']=='AREA00_OUTPUT')
ZI=zipfile.ZipFile(IZ);ZO=zipfile.ZipFile(OZ)
IP='AREA_00_IMAGES_INPUT/';OP='AREA_00_IMAGES_OUTPUT/'
def zcsv(z,n):return list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig'))))
R=zcsv(ZI,IP+'AREA_MANIFEST.csv');REF=zcsv(ZI,IP+'global_skill_style_library/STYLE_INDEX.csv')
F=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);H=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',23)
BG=(32,38,48,255)
for f in ['evidence','sources','reference_boards','input_documents','playback']: (P/f).mkdir(exist_ok=True)
def im(z,n):return Image.open(io.BytesIO(z.read(n))).convert('RGBA')
def wc(n,rows):
 with (P/n).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def wraptext(d,xy,t,width,font=F,color='white'):
 x,y=xy;s=''
 for c in t:
  if c=='\n' or d.textlength(s+c,font=font)>width:
   d.text((x,y),s,font=font,fill=color);s='' if c=='\n' else c;y+=25
  else:s+=c
 if s:d.text((x,y),s,font=font,fill=color);y+=25
 return y
for n in ZI.namelist():
 if n.endswith('.md') and ('/monsters/' in n or n.count('/')==1 or n.endswith('STYLE_ATLAS.md')):
  target=P/'input_documents'/n.removeprefix(IP);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(ZI.read(n))
lookup={}
for x in REF:
 names=[n for n in ZI.namelist() if f"/skills/{int(x['index']):04d}_" in n and n.endswith('/preview.png')]
 assert len(names)==1
 x['zip_member']=names[0];x['sha256']=hashlib.sha256(ZI.read(names[0])).hexdigest();lookup[int(x['index'])]=x
 # Exact unmodified preview copies for later evidence; original ZIP untouched.
 dest=P/'sources'/f"ref_{int(x['index']):03d}.png";dest.write_bytes(ZI.read(names[0]));x['local_copy']=str(dest)
def refboard(rr,label,cell=220):
 cols=5;cw=cell+15;rh=cell+80;out=Image.new('RGBA',(cw*cols,60+math.ceil(len(rr)/cols)*rh),BG);d=ImageDraw.Draw(out);d.text((10,12),label,font=H,fill='white')
 for j,x in enumerate(rr):
  pic=im(ZI,x['zip_member']);pic.thumbnail((cell,cell));xx=j%cols*cw;yy=60+j//cols*rh
  out.alpha_composite(pic,(xx+(cell-pic.width)//2,yy));wraptext(d,(xx+4,yy+cell+5),f"{x['index']} {x['skill_resource_name']}\n{x['style_priority']}",cw-10)
 return out
for start in range(0,len(REF),25):refboard(REF[start:start+25],f'INPUT STYLE LIBRARY / {start+1}–{min(start+25,len(REF))} / inventory only').convert('RGB').save(P/'reference_boards'/f'library_{start//25+1:02d}.png')
recent=[x for x in REF if x['style_priority']=='RECENT_SECONDARY']
refboard(recent,'RECENT_SECONDARY 20 / chronology unverified / actual INPUT previews',256).convert('RGB').save(P/'reference_boards'/'recent_secondary_all.png')
for x in recent:
 pic=im(ZI,x['zip_member']);out=Image.new('RGBA',(max(700,pic.width*2),pic.height+70),BG);out.alpha_composite(pic,(0,60));d=ImageDraw.Draw(out);d.rectangle((pic.width,60,out.width,out.height),fill='white');out.alpha_composite(pic,(pic.width,60));d.text((10,10),f"{x['index']} {x['RUID']} / native dark + white",font=F,fill='white');out.convert('RGB').save(P/'reference_boards'/f"recent_{int(x['index']):03d}_native.png")
wc('REFERENCE_INVENTORY.csv',REF)
metrics=[]
for r in R:
 prefix=OP+r['folder']+'/';r['vfx_files']=sorted(n for n in ZO.namelist() if n.startswith(prefix+'VFX/') and n.endswith('.png'));r['icon_file']=next(n for n in ZO.namelist() if n.startswith(prefix+'ICON/') and n.endswith('.png'))
 r['spec']=ZI.read(IP+r['folder']+'/GENERATION_SPEC.md').decode('utf-8-sig');r['monster_image']=IP+r['folder']+'/MONSTER_IMAGE.png'
 for n in r['vfx_files']+[r['icon_file']]:
  image=im(ZO,n);a=image.getchannel('A');hist=a.histogram();bbox=a.point(lambda x:255 if x>=16 else 0).getbbox()
  metrics.append({'monster_id':r['monster_id'],'file':n,'width':image.width,'height':image.height,'mode_original':Image.open(io.BytesIO(ZO.read(n))).mode,'alpha_min':min(i for i,v in enumerate(hist) if v),'alpha_max':max(i for i,v in enumerate(hist) if v),'transparent_fraction':hist[0]/(image.width*image.height),'partial_alpha_fraction':sum(hist[1:255])/(image.width*image.height),'bbox_alpha16':json.dumps(bbox),'sha256':hashlib.sha256(ZO.read(n)).hexdigest()})
  dest=P/'sources'/r['monster_id']/Path(n).name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(ZO.read(n))
 (P/'sources'/r['monster_id']/'MONSTER_IMAGE.png').write_bytes(ZI.read(r['monster_image']))
 # 2-column native sheets: every pixel remains 1:1, including boss frames.
 for start in range(0,len(r['vfx_files']),4):
  size=im(ZO,r['vfx_files'][0]).width;out=Image.new('RGBA',(max(800,size*2),80+(size+45)*2),BG);d=ImageDraw.Draw(out);d.text((10,10),f"{r['monster_name']} / {r['skill_name']} / native 1:1",font=H,fill='white')
  for j,n in enumerate(r['vfx_files'][start:start+4]):
   x=j%2*size;y=70+j//2*(size+45);d.text((x+10,y),f'F{start+j:02d}',font=F,fill='#ffce7d');out.alpha_composite(im(ZO,n),(x,y+30))
  out.convert('RGB').save(P/'evidence'/f"{r['monster_id']}_frames_{start:02d}_{min(start+3,len(r['vfx_files'])-1):02d}.png")
(P/'RECORDS.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf-8');wc('PNG_CHECKS.csv',metrics)
print('ready',len(R),'monsters',len(metrics),'PNG',len(REF),'refs')
