from pathlib import Path
import json,zipfile,io,tempfile,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent; BASE=ROOT.parent/'images-input-packages'
STAGE=Path(tempfile.gettempdir())/'msw_design_connection_20260913';STAGE.mkdir(exist_ok=True)
CAT=json.loads((ROOT/'CATALOG.json').read_text(encoding='utf-8'))
OLD=json.loads((ROOT/'selected.json').read_text(encoding='utf-8'))
EXTRA={
'bubble':('400004429','ball effect hit/0'),
'tree':('162121043','effect special special1'),
'water_shield':('23111005','effect repeat'),
'butterfly':('164120007','effect state'),
'gale':('400031068','ball effect hit/0'),
'vortex':('400031059','effect'),
'clock':('101141012','effect hit/0'),
'crystal':('152101000','special summon/stand'),
'feather':('13141002','hit/0'),
'smoke':('4221006','effect tile/0'),
'gravity':('142100010','effect special hit/0'),
'punch':('400004139','effect hit'),
'quake':('101141005','tile hit/0'),
'flower':('13111024','effect summon/stand summon/die'),
'frost_breath':('2221011','prepare keydown keydownend'),
'earth_breath':('22170065','effect ball/0 hit/0'),
'dragon_fire':('61121105','effect tile/0 hit/0'),
'dark_magic':('27140002','effect hit/0'),
'shard':('151141002','effect'),
'sound':('400004438','prepare keydown end'),
'monsoon':('13121052','effect hit/0'),
'dark_barrier':('400031037','effect/0 finish/0 special/0'),
'nature':('162121021','effect hit/0 special/0'),
'blossom':('151121003','effect hit/0'),
'time_hold':('100001274','effect repeat special')}
def prepare():
 z=zipfile.ZipFile(ROOT/'MSW_SKILL_REFERENCE_LIBRARY_PARTIAL.zip');groups={}
 for r in OLD:
  p=next(p for p in CAT if p['id']==r['pack_id']);groups[r['key']]=(p,[e['rel_path'] for e in r['elements']])
 for k,(sid,roles) in EXTRA.items():groups[k]=(next(p for p in CAT if p['id'].endswith('/'+sid)),roles.split()+['icon'])
 refs=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
 for k,(p,roles) in groups.items():
  d=STAGE/k;d.mkdir(exist_ok=True);es=[]
  for e in p['elements']:
   if e['rel_path'] not in roles or not e.get('local_path'):continue
   b=z.read('MSW_SKILL_REFERENCE_LIBRARY/'+e['local_path']);f=d/Path(e['local_path']).name;f.write_bytes(b)
   im=Image.open(io.BytesIO(b));n=getattr(im,'n_frames',1);ids=sorted(set([0,n//4,n//2,3*n//4,n-1]));dur=[]
   for i in range(n):im.seek(i);dur.append(im.info.get('duration'))
   for i in ids:im.seek(i);im.convert('RGBA').save(d/(e['ruid']+f'_F{i:03}.png'))
   es.append(dict(e,filename=f.name,sha256=hashlib.sha256(b).hexdigest(),frame_count=n,indices=ids,durations_ms=dur))
  refs.append(dict(key=k,pack_id=p['id'],name=' / '.join((p.get('names') or {}).get('ko',[])),elements=es))
 (STAGE/'refs.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8')
 # One row per source; inspect two useful VFX layers over multiple real phases.
 for page in range((len(refs)+6)//7):
  subset=refs[page*7:page*7+7];sheet=Image.new('RGB',(1500,len(subset)*220),(40,40,40));draw=ImageDraw.Draw(sheet)
  for row,r in enumerate(subset):
   draw.text((8,row*220+3),r['key']+' | '+r['name'],font=font,fill='white');col=0
   for e in [e for e in r['elements'] if e['rel_path']!='icon'][:2]:
    for i in e['indices'][1:-1] or e['indices']:
     im=Image.open(STAGE/r['key']/(e['ruid']+f'_F{i:03}.png')).convert('RGBA');im.thumbnail((225,155));sheet.paste(im,(col*245+8,row*220+30),im)
     draw.text((col*245+8,row*220+190),e['rel_path']+f' F{i}',font=font,fill='white');col+=1
  sheet.save(STAGE/f'atlas_{page}.jpg')
 print(str(STAGE),len(refs),flush=True)
if __name__=='__main__':prepare()
