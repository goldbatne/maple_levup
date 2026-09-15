from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,csv,hashlib,zipfile
O=Path(__file__).parent/'20260914_astra_review'
rs=json.loads((O/'records.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
rows=[]; extras=[]
for r in rs:
    folder=O/r['area']/r['skill'];spec=(folder/'SPEC.md').read_text(encoding='utf-8');role=(folder/'ROLE.md').read_text(encoding='utf-8')
    m=re.search(r'- VFX: (\d+) frames, 각 (\d+)×(\d+).*?([\d.]+) sec/frame',spec)
    required=bool(re.search(r'required NEW_ART roles:.*VFX',role))
    expected=int(m[1]) if required else 0
    r['required_frames']=expected;r['interval_ms']=round(float(m[4])*1000)
    r['count_ok']=len(r['frames'])==expected and len(r['icons'])==1
    md=next(p.parent for p in Path(r['input']).glob('monsters/*/GENERATION_SPEC.md') if r['skill'] in p.read_text(encoding='utf-8'))
    brief=(md/'DESIGN_REFERENCE_BRIEF.md').read_text(encoding='utf-8')
    r['monster_brief_hash_match']=r['monster_sha'] in brief
    for rolekey in ['frames','icons']:
      for i,p in enumerate(r[rolekey]):
        im=Image.open(O/p['path']);a=im.getchannel('A');w,h=im.size
        p['bbox_a16']=a.point(lambda v:255 if v>=16 else 0).getbbox()
        p['bbox_a128']=a.point(lambda v:255 if v>=128 else 0).getbbox()
        expectedsize=[int(m[2]),int(m[3])] if rolekey=='frames' else [256,256]
        p['size_ok']=p['size']==expectedsize
        box=p['bbox_a16'];p['safe85_a16']=bool(box and box[0]>=w*.075 and box[1]>=h*.075 and box[2]<=w*.925 and box[3]<=h*.925)
        p['partial_alpha_pixels']=sum(a.histogram()[1:255]);p['file_hash_ok']=hashlib.sha256((O/p['path']).read_bytes()).hexdigest()==p['sha256']
        rows.append(dict(area=r['area'],skill=r['skill'],role=rolekey,frame=i,path=p['path'],sha256=p['sha256'],size_ok=p['size_ok'],mode=p['mode'],edge_max=p['edge_max'],safe85_a16=p['safe85_a16'],partial_alpha_pixels=p['partial_alpha_pixels'],hash_ok=p['file_hash_ok']))
    # Same physical display size on three backgrounds; no content-based recentering.
    picks=r['icons']+[max(r['frames'],key=lambda p:p['alpha_sum'])] if r['frames'] else r['icons']
    sheet=Image.new('RGB',(1152,320),(40,40,40));d=ImageDraw.Draw(sheet)
    d.text((4,3),r['monster_name']+' / '+r['skill_name'],font=font,fill='white')
    for k,bg in enumerate([(0,0,0),(128,128,128),(255,255,255)]):
      for j,p in enumerate(picks):
        im=Image.open(O/p['path']).convert('RGBA');sz=64 if j==0 else 256;im.thumbnail((sz,sz),Image.Resampling.LANCZOS)
        t=Image.new('RGBA',(256,256),bg+(255,));t.alpha_composite(im,((256-im.width)//2,(256-im.height)//2))
        # Each background has 128px icon panel and 256px frame panel.
        if j==0:t=t.crop((64,0,192,256))
        sheet.paste(t.convert('RGB'),(384*k+(0 if j==0 else 128),32))
    sheet.save(folder/'backgrounds.jpg',quality=95)
for a in range(7,21):
    part=[r for r in rs if r['area']==f'AREA_{a:02}'];sheet=Image.new('RGB',(1152,320*len(part)))
    for j,r in enumerate(part):sheet.paste(Image.open(O/r['area']/r['skill']/'backgrounds.jpg'),(0,j*320))
    sheet.save(O/f'AREA_{a:02}_BACKGROUNDS.jpg',quality=95)
    with zipfile.ZipFile(part[0]['zip']) as z:
      extras.extend(dict(area=f'AREA_{a:02}',entry=n) for n in z.namelist() if '/ICON/' in n and n.endswith('.png') and not n.endswith('_ICON.png'))
with (O/'TECHNICAL_CHECKS.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(O/'records.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'EXTRA_SOURCE_FILES.json').write_text(json.dumps(extras,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(skills=len(rs),vfx=sum(len(r['frames']) for r in rs),icons=sum(len(r['icons']) for r in rs),count_bad=[r['skill'] for r in rs if not r['count_ok']],monster_hash_bad=[r['skill'] for r in rs if not r['monster_brief_hash_match']],size_bad=[r['path'] for r in rows if not r['size_ok']],safe85_bad=[r['path'] for r in rows if not r['safe85_a16']],extras=extras),ensure_ascii=True))
