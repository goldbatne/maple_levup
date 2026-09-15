from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import zipfile,json,hashlib,re,csv,html

ROOT=Path('D:/maplestory_levup/docs/art')
OUT=ROOT/'design-review-07-20'/'20260914_astra_review'
OUT.mkdir(parents=True,exist_ok=True)
FONT=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
SMALL=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',12)
records=[]; sources={}; htmlrows=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def tile(im,size=140):
    im=im.convert('RGBA'); im.thumbnail((size,size),Image.Resampling.LANCZOS)
    t=Image.new('RGBA',(size,size),(65,65,65,255));t.alpha_composite(im,((size-im.width)//2,(size-im.height)//2));return t.convert('RGB')
for a in range(7,21):
    tag=f'AREA_{a:02}'; run='20260914_111705' if a in (7,10) else ('20260914_034024' if a<11 else ('20260914_024951' if a<16 else '20260914_005624'))
    rd=ROOT/'chatgpt-work-runs'/tag/run
    zp=next(rd.glob('*.zip'))
    ir=rd if a not in (7,10) else rd.parent/'20260914_034024'
    ip=next(x.parent for x in ir.rglob('AREA_MANIFEST.csv') if x.parent.name==f'{tag}_IMAGES_INPUT')
    ziphash=sha(zp.read_bytes())
    area=[]
    with zipfile.ZipFile(zp) as z:
        names=z.namelist()
        for md in sorted((ip/'monsters').iterdir()):
            spec=(md/'GENERATION_SPEC.md').read_text(encoding='utf-8')
            brief=(md/'DESIGN_REFERENCE_BRIEF.md').read_text(encoding='utf-8')
            sid=re.search(r'- skill_id: `([^`]+)',spec)[1]
            mid=re.search(r'- monster_id: `([^`]+)',spec)[1]
            sname=re.search(r'최종 스킬 이름: \*\*(.*?)\*\*',spec)[1]
            mname=re.search(r'- 몬스터 이름: (.*)',spec)[1]
            ruid=re.search(r'monster image RUID: `([^`]+)',spec)[1]
            fs=sorted(n for n in names if '/VFX/' in n and n.endswith('.png') and ('/'+md.name+'/') in n)
            icons=sorted(n for n in names if '/ICON/' in n and n.endswith('_ICON.png') and ('/'+md.name+'/') in n)
            if not fs and not icons:
                fs=sorted(n for n in names if '/VFX/' in n and n.endswith('.png') and f'_{sid}_' in n)
                icons=sorted(n for n in names if '/ICON/' in n and n.endswith('_ICON.png') and f'_{sid}_' in n)
            rec=dict(area=tag,monster=mid,monster_name=mname,skill=sid,skill_name=sname,ruid=ruid,zip=str(zp),zip_sha=ziphash,frames=[],icons=[],references=re.findall(r'### (.*?) / `(skill/[^`]+)`',brief),input=str(ip),material='\n'.join(l for l in spec.splitlines() if any(t in l for t in ['핵심 소재:','진행 방향:','아이콘 핵심','- VFX:'])))
            folder=OUT/tag/sid;folder.mkdir(parents=True,exist_ok=True)
            (folder/'ROLE.md').write_text((md/'RUNTIME_ROLE_MAP.md').read_text(encoding='utf-8'),encoding='utf-8')
            monster=Image.open(md/'MONSTER_IMAGE.png');monster.save(folder/'monster.png')
            rec['monster_sha']=sha((md/'MONSTER_IMAGE.png').read_bytes())
            for kind,files in [('frames',fs),('icons',icons)]:
                for n in files:
                    b=z.read(n);im=Image.open(BytesIO(b));dest=folder/Path(n).name;dest.write_bytes(b)
                    alpha=im.convert('RGBA').getchannel('A');w,h=im.size
                    edges=[alpha.crop(box).getextrema()[1] for box in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]]
                    hist=alpha.histogram()
                    rec[kind].append(dict(path=str(dest.relative_to(OUT)).replace('\\','/'),zip_entry=n,sha256=sha(b),mode=im.mode,size=im.size,alpha_range=alpha.getextrema(),edge_max=max(edges),alpha_sum=sum(hist[v]*v for v in range(256))))
            row=Image.new('RGB',(2600,190),(25,28,35));dr=ImageDraw.Draw(row);dr.text((5,2),f'{tag} {mname} / {sname}',font=FONT,fill='white');row.paste(tile(monster,140),(0,36))
            pics=rec['icons']+rec['frames']
            for k,p in enumerate(pics):
                row.paste(tile(Image.open(OUT/p['path']),140),(145*(k+1),36));dr.text((145*(k+1),176),'ICON' if k<len(rec['icons']) else f'F{k-len(rec["icons"]):02}',font=SMALL,fill='white')
            row.save(folder/'strip.jpg',quality=95);area.append(row);records.append(rec)
            (folder/'SPEC.md').write_text(spec,encoding='utf-8')
            htmlrows.append(f'<section><h2>{tag} · {html.escape(mname)} · {html.escape(sname)}</h2><img class="strip" src="{tag}/{sid}/strip.jpg"><p>{html.escape(rec["material"])}</p><img class="anim" data-frames=\'{json.dumps([p["path"] for p in rec["frames"]])}\' data-ms="{80 if len(fs)==12 else 100}"><p>'+ ' · '.join(f'<a href="https://maplestoryworlds-resourcesearch-new.nexon.com/search?category=skill&amp;selected={pid}">{html.escape(n)}</a>' for n,pid in rec['references'])+'</p></section>')
        sheet=Image.new('RGB',(2600,len(area)*190));
        for j,row in enumerate(area):sheet.paste(row,(0,j*190))
        sheet.save(OUT/f'{tag}_ALL_FINAL.jpg',quality=95)
    for p in (ip/'reference_resource_design').glob('*/SOURCE.json'):
        sources.setdefault(p.parent.name,(ip,json.loads(p.read_text(encoding='utf-8'))))
refrows=[];refdata=[]
for key,(ip,s) in sources.items():
    row=Image.new('RGB',(1500,200),(25,28,35));d=ImageDraw.Draw(row);d.text((5,0),key+' / '+s['official_name'],font=FONT,fill='white');x=0
    for el in s['elements']:
        paths=el.get('frames',[])
        if not paths:paths=[el['source_path']]
        inds=sorted(set([0,len(paths)//3,2*len(paths)//3,len(paths)-1])) if len(paths)>1 else [0]
        for j in inds:
            if x+140>1500:break
            row.paste(tile(Image.open(ip/paths[j]),140),(x,40));d.text((x,181),el['role']+f' {j}',font=SMALL,fill='white');x+=145
    row.save(OUT/f'REF_{key}.jpg',quality=95);refrows.append(row);refdata.append(s)
sheet=Image.new('RGB',(1500,len(refrows)*200))
for j,row in enumerate(refrows):sheet.paste(row,(0,j*200))
sheet.save(OUT/'OFFICIAL_REFERENCES.jpg',quality=95)
(OUT/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'references.json').write_text(json.dumps(refdata,ensure_ascii=False,indent=2),encoding='utf-8')
page='''<!doctype html><meta charset="utf-8"><title>AREA 07–20 디자인 비교</title><style>body{background:#171b24;color:#eee;font:16px sans-serif;margin:24px}section{border-top:1px solid #777;margin:25px 0}a{color:#93d5ff}.strip{width:100%}.anim{width:320px;height:320px;object-fit:contain;background:#444}p{white-space:pre-line}</style><h1>AREA 07–20 · 실제 ZIP 기준 비교</h1><p>파일 기반 미리보기 · 게임 실행 미검증. 프레임 간격 100ms / 보스 80ms. 자동 반복 사이에 500ms 정지.</p><button onclick="document.body.style.background='#eee';document.body.style.color='#111';document.querySelectorAll('.anim').forEach(x=>x.style.background='#fff')">흰 배경</button><button onclick="document.body.style.background='#171b24';document.body.style.color='#eee';document.querySelectorAll('.anim').forEach(x=>x.style.background='#000')">검정 배경</button>'''+''.join(htmlrows)+'''<script>document.querySelectorAll('.anim').forEach(im=>{let a=JSON.parse(im.dataset.frames),i=0;if(!a.length){im.remove();return}function go(){im.src=a[i];i=(i+1)%a.length;setTimeout(go,i?+im.dataset.ms:500)}go()})</script>'''
(OUT/'REVIEW_VIEWER.html').write_text(page,encoding='utf-8')
print('Skills:',len(records),'VFX:',sum(len(r['frames']) for r in records),'ICON:',sum(len(r['icons']) for r in records))
print('OUT',OUT)
