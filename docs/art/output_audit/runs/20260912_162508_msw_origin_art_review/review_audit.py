from pathlib import Path
import csv,json,hashlib,zipfile,io,sys,re
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('D:/maplestory_levup'); ART=ROOT/'docs/art'; RUN=Path(__file__).parent
CACHE=ART/'images-input-packages/_cache'
REPACK=ART/'output_repacked/20260912_153221_v24_repack'
OLD=ART/'output_audit/runs/20260912_145815_content_style'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def readcsv(p): return list(csv.DictReader(Path(p).read_text(encoding='utf-8-sig').splitlines()))
def zcsv(z,n): return list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig'))))
def dump(n,o): (RUN/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def writecsv(n,rows):
    if not rows:return
    with (RUN/n).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def inventory():
    for p in [CACHE,OLD,REPACK]:
        print(str(p), [x.name for x in p.iterdir()] if p.exists() else 'MISSING')
    for n in ['REVALIDATION.csv','PNG_BYTE_PRESERVATION.csv','REPACK_AREA_STATUS.csv']:
        rows=readcsv(REPACK/n); print(n,len(rows),rows[:2])
    for n in ['REUSED_FILE_CHECKS.csv','CONTENT_STYLE_REVIEW.csv']:
        rows=readcsv(OLD/n); print(n,len(rows),rows[:1])
    if CACHE.exists():
        md=json.loads((CACHE/'resource_metadata.json').read_text('utf-8-sig'));print('CACHE',len(md),list(md.items())[:1])
    z=zipfile.ZipFile(ART/'images-input-packages-v2_4/AREA_11_IMAGES_INPUT_V2_4.zip')
    print('INPUT FILES',z.namelist()[:35]); print('MANIFEST',[(n,zcsv(z,n)[:1]) for n in z.namelist() if n.endswith('AREA_MANIFEST.csv')])
    print('SKILL FILES',[str(p) for p in ROOT.rglob('*SkillTable*') if '.git' not in str(p)])
    print('MONSTER',readcsv(ROOT/'RootDesk/MyDesk/GameData/MonsterTable.csv')[:1])
def prepare():
    bas=readcsv(ART/'output_audit/BASELINE_INDEX.csv'); outs=readcsv(ART/'output_audit/BASELINE_OUTPUT_INDEX.csv'); oldhash={r['area_id']:r for r in readcsv(OLD/'REUSED_FILE_CHECKS.csv')}
    checks=[]
    for r in bas+outs:
        checks.append({'path':r['path'],'expected':r['sha256'],'actual':sha(r['path']),'match':sha(r['path'])==r['sha256']})
    writecsv('BASELINE_HASH_CHECK.csv',checks);print('HASH',len(checks),all(r['match'] for r in checks))
    assert all(r['match'] for r in checks)
    choices={r['area_id']:r['path'] for r in outs}; oldz=[]
    for p in (ART/'output').glob('*.zip'):
        h=sha(p);oldz.append({'path':str(p),'sha256':h})
    for a in ['area_11','area_12']:
        candidates=[r for r in oldz if r['sha256']==oldhash[a]['output_sha256']]
        assert len(candidates)==1,(a,candidates)
        choices[a]=candidates[0]['path']
    writecsv('ORIGINAL_OUTPUT_HASHES.csv',oldz)
    recs=[];sel=[]
    for r in bas:
        if r['kind']!='AREA_INPUT':continue
        a=r['area_id']; iz=zipfile.ZipFile(r['path']); oz=zipfile.ZipFile(choices[a]); prefix=iz.namelist()[0].split('/')[0]+'/'
        manifest=zcsv(iz,prefix+'AREA_MANIFEST.csv')
        om=[n for n in oz.namelist() if n.endswith('OUTPUT_MANIFEST.csv')];print(a,'OUTMANIFEST',zcsv(oz,om[0])[:1] if a in ['area_01','area_11','area_12'] else len(manifest))
        for m in manifest:
            m.update(input_zip=r['path'],output_zip=choices[a],input_prefix=prefix)
            m['spec']=iz.read(prefix+m['folder']+'/GENERATION_SPEC.md').decode('utf-8-sig')
            m['input_image']=[n for n in iz.namelist() if n.startswith(prefix+m['folder']+'/') and 'MONSTER_IMAGE' in n and n.endswith('.png')][0]
            recs.append(m)
        sel.append({'area_id':a,'input_path':r['path'],'input_revision':r['revision'],'input_sha256':r['sha256'],'output_path':choices[a],'output_sha256':sha(choices[a]),'basis':'BASELINE_OUTPUT_INDEX hash' if a not in ['area_11','area_12'] else 'HOLD_AREA_11_12 + CONTENT_STYLE REUSED_FILE_CHECKS exact SHA256','pairs':len(manifest)})
    dump('records.json',recs);writecsv('AREA_SELECTION.csv',sel)
    print('PAIRS',len(recs),'RUIDS',len(set(r['monster_image_ruid'] for r in recs)))
    for p in (ART).glob('images-input-packages-v2_*/INPUT*EVIDENCE.zip'):
        z=zipfile.ZipFile(p); ns=z.namelist();print('EVIDENCE',str(p),len(ns),[n for n in ns if any(t in n.lower() for t in ['metadata','cache','source','skilltable','monstertable'])][:30])
    print('AUTH DOC',iz.read(prefix+'DATA_SOURCE_RESOLUTION.md').decode('utf-8-sig'))
    print('STYLE',[(n,iz.read(n).decode('utf-8-sig')[:2000]) for n in iz.namelist() if n.endswith('info.md')][:2])
def boards():
    recs=json.loads((RUN/'records.json').read_text('utf8'));meta={r['id']:r for r in json.loads((RUN/'resource_metadata.json').read_text('utf8'))};downloads={r['ruid']:r for r in json.loads((RUN/'download_log.json').read_text('utf8'))}
    models={m['snapshot']['model_id']:m for m in json.loads((RUN/'model_snapshots.json').read_text('utf8'))};mon={r['id']:r for r in readcsv(ROOT/'RootDesk/MyDesk/GameData/MonsterTable.csv')};old={r['monster_id']:r for r in readcsv(OLD/'CONTENT_STYLE_REVIEW.csv')}
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
    (RUN/'boards').mkdir(exist_ok=True);(RUN/'evidence').mkdir(exist_ok=True)
    def paste(canvas,im,box):
        im=im.convert('RGBA');im.thumbnail((box[2],box[3]),Image.Resampling.NEAREST);canvas.paste(im,(box[0]+(box[2]-im.width)//2,box[1]+(box[3]-im.height)//2),im)
    for a in sorted(set(r['area_id'] for r in recs)):
        rows=[r for r in recs if r['area_id']==a]; board=Image.new('RGB',(1800,len(rows)*340+40),(36,40,48));d=ImageDraw.Draw(board);d.text((10,8),a+' | MSW original animation / INPUT / ICON / all delivered VFX frames',font=font,fill='white')
        for idx,r in enumerate(rows):
            y=45+idx*340;mid=r['monster_id'];m=models[mon[mid]['model_id']];vals=m['snapshot']['values'];r['model_path']=m['path'];r['model_sha256']=m['sha256'];r['model_sprite_ruid']=next(v['value'] for v in vals if v['name']=='SpriteRUID');r['model_action_sheet']=next(v['value'] for v in vals if v['name']=='ActionSheet' and 'StateAnimationComponent' in v['target_type']);r['model_children']=len(m['children']);r['model_match']=r['model_sprite_ruid']==r['monster_image_ruid'];r['project_name_match']=mon[mid]['name']==r['monster_name'];r['project_skill_match']=mon[mid]['drop_skill_id']==r['skill_id']
            iz=zipfile.ZipFile(r['input_zip']);oz=zipfile.ZipFile(r['output_zip']);om=[n for n in oz.namelist() if n.endswith('OUTPUT_MANIFEST.csv')][0];oprefix=om[:-len('OUTPUT_MANIFEST.csv')]
            if a not in ['area_11','area_12']:
                files=[({'CAST':'CAST_VFX','REFERENCE':'REFERENCE_VFX'}.get(p['effect_role'],p['effect_role']),oprefix+p['relative_path']) for p in zcsv(oz,om) if p['monster_id']==mid]
            else:
                files=[]
                for p in old[mid]['actual_files'].split('|'):
                    matches=[n for n in oz.namelist() if n.endswith('/'+p) or n==p];assert len(matches)==1,(mid,p,matches)
                    role='ICON' if '/ICON/' in '/'+p else 'PROJECTILE' if '/PROJECTILE/' in '/'+p else 'REFERENCE_VFX' if '/REFERENCE/' in '/'+p else 'CAST_VFX'
                    files.append((role,matches[0]))
            r['role_files']={role:[n for rr,n in files if rr==role] for role in r['required_roles'].split('|')}
            r['file_hashes']={n:hashlib.sha256(oz.read(n)).hexdigest() for role,n in files}
            orig=Image.open(downloads[r['monster_image_ruid']]['file']);r['source_gif_frames']=orig.n_frames;r['source_api_frames']=meta[r['monster_image_ruid']]['payload'].get('frames',[]);r['source_file']=downloads[r['monster_image_ruid']]['file'];r['source_sha256']=downloads[r['monster_image_ruid']]['sha256'];r['source_url']=downloads[r['monster_image_ruid']]['url'];r['source_names']=meta[r['monster_image_ruid']].get('names',{})
            d.text((10,y),f"{mid} / {r['monster_name']} / {r['skill_name']}",font=font,fill='#ffe59c')
            for j in range(orig.n_frames):
                orig.seek(j);cw=min(110,500//orig.n_frames);paste(board,orig,(10+j*cw,y+28,cw-4,110))
            paste(board,Image.open(io.BytesIO(iz.read(r['input_image']))),(520,y+28,130,110));d.text((535,y+145),'INPUT',font=small,fill='white')
            paste(board,Image.open(io.BytesIO(oz.read(r['role_files']['ICON'][0]))),(680,y+28,110,110));d.text((700,y+145),'ICON',font=small,fill='white')
            paste(board,Image.open(io.BytesIO(oz.read(r['role_files']['ICON'][0]))),(805,y+48,64,64))
            d.text((920,y+30),str(r['source_names'])[:94],font=small,fill='white')
            d.text((920,y+52),f"RUID {r['monster_image_ruid']} / GIF {orig.n_frames} / API frames {len(r['source_api_frames'])}",font=small,fill='white')
            core=next((l for l in r['spec'].splitlines() if l.startswith('- 핵심 소재:')),'');d.text((920,y+77),core[:63],font=small,fill='white');d.text((920,y+98),core[63:126],font=small,fill='white')
            x=10
            for role,ns in r['role_files'].items():
                if role=='ICON':continue
                d.text((x,y+171),role,font=small,fill='#a8d4ff')
                for j,n in enumerate(ns):
                    paste(board,Image.open(io.BytesIO(oz.read(n))),(x,y+193,101,112));d.text((x+35,y+308),f'F{j:02}',font=small,fill='white');x+=108
                x+=15
            d.line((0,y+335,1800,y+335),fill='#727780')
        board.save(RUN/'boards'/f'{a}_source_and_all_frames.png')
    dump('records.json',recs);print('MATCH',sum(r['model_match'] for r in recs),sum(r['project_name_match'] for r in recs),sum(r['project_skill_match'] for r in recs));print('FRAMES',[(r['monster_id'],r['source_gif_frames'],len(r['source_api_frames'])) for r in recs if r['source_gif_frames']!=len(r['source_api_frames'])]);print('CHILDREN',sum(r['model_children'] for r in recs));print('FILES',sum(len(r['file_hashes']) for r in recs))
    s=json.loads((OLD/'REVIEW_STATE.json').read_text('utf8'));print('REUSE_RULES',sha(ART/'output_audit/AUDIT_RULES.md')==s['rules_sha256'],'INDEX',sha(ART/'output_audit/BASELINE_INDEX.csv')==s['baseline_index_sha256'])
    for p in (ROOT/'RootDesk/MyDesk/GameData').glob('*.csv'):print('TABLE',p.name)
def details():
    recs=json.loads((RUN/'records.json').read_text('utf8')); font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
    def paste(c,im,x,y,w,h):
        im=im.convert('RGBA');im.thumbnail((w,h),Image.Resampling.NEAREST);c.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2),im)
    big=[r for r in recs if r['source_gif_frames']>8]
    for k in range(0,len(big),5):
        chunk=big[k:k+5];c=Image.new('RGB',(1150,240*len(chunk)),(38,42,50));d=ImageDraw.Draw(c)
        for i,r in enumerate(chunk):
            y=i*240;d.text((10,y+5),r['area_id']+' '+r['monster_id']+' / '+r['monster_name'],font=font,fill='white');orig=Image.open(r['source_file']);inds=[0,orig.n_frames//2,orig.n_frames-1]
            for j,f in enumerate(inds):orig.seek(f);paste(c,orig,10+j*230,y+40,210,170);d.text((20+j*230,y+210),f'MSW frame {f}',font=small,fill='white')
            iz=zipfile.ZipFile(r['input_zip']);paste(c,Image.open(io.BytesIO(iz.read(r['input_image']))),730,y+40,210,170);d.text((750,y+210),'INPUT',font=small,fill='white')
        c.save(RUN/'boards'/f'source_detail_{k//5+1:02}.png')
    for mid in ['m_king_bloctopus','m_toy_trojan','m_wooden_dummy']:
        r=next(r for r in recs if r['monster_id']==mid);c=Image.new('RGB',(1800,1300),(36,40,48));d=ImageDraw.Draw(c);d.text((20,10),r['area_id']+' / '+r['monster_name']+' / '+r['skill_name'],font=font,fill='#ffe59c');orig=Image.open(r['source_file']);paste(c,orig,20,50,210,180);iz=zipfile.ZipFile(r['input_zip']);oz=zipfile.ZipFile(r['output_zip']);paste(c,Image.open(io.BytesIO(iz.read(r['input_image']))),260,50,210,180);paste(c,Image.open(io.BytesIO(oz.read(r['role_files']['ICON'][0]))),500,50,210,180)
        for x,t in [(20,'MSW actual resource'),(260,'INPUT MONSTER_IMAGE'),(500,'ICON (separate role)')]:d.text((x,238),t,font=small,fill='white')
        d.text((750,60),'RUID '+r['monster_image_ruid'],font=small,fill='white');d.text((750,95),'MSW clip GIF / first frame; all frames in source_copies',font=small,fill='white')
        lines=[l for l in r['spec'].splitlines() if any(l.startswith('- '+q) for q in ['핵심 소재:','런타임 역할:','아이콘 핵심 모티브:','몬스터 본체 금지 범위:','CAST 방향/표현:','PROJECTILE 방향/표현:'])]
        y=285
        for line in lines:
            while line:
                n=min(100,len(line))
                while d.textlength(line[:n],font=small)>1750:n-=1
                d.text((20,y),line[:n],font=small,fill='white');line=line[n:];y+=26
        y=max(y+20,590)
        for role,ns in r['role_files'].items():
            if role=='ICON':continue
            d.text((20,y),role,font=font,fill='#a8d4ff');y+=34
            for j,n in enumerate(ns):
                paste(c,Image.open(io.BytesIO(oz.read(n))),15+j*215,y,208,208);d.text((20+j*215,y+210),f'F{j:02}',font=small,fill='white')
            y+=245
        c.save(RUN/'evidence'/f'{r["area_id"]}_{mid}_comparison.png')
    print('SOURCE_DETAIL_PAGES',(len(big)+4)//5,'DETAIL MONSTERS',len(big))
    z=zipfile.ZipFile(ART/'images-input-packages-v2_1/INPUT_V2_1_EVIDENCE.zip');base=zcsv(z,'INPUT_V2_1_EVIDENCE/baseline_commit/RootDesk/MyDesk/GameData/SkillTable.csv');approved=zcsv(z,'INPUT_V2_1_EVIDENCE/current_candidates/Mislocated_SkillTable.csv');current=readcsv(ROOT/'Mislocated/MyDesk/GameData/SkillTable.csv');bd={r['id']:r for r in base};ad={r['id']:r for r in approved};cd={r['id']:r for r in current}
    print('SKILL_COUNTS',len(base),len(approved),len(current));diff=[]
    for r in recs:
        s=r['skill_id'];a=ad.get(s,{});c=cd.get(s,{});fields=[k for k in set(a)|set(c) if a.get(k)!=c.get(k)]
        diff.append({'area_id':r['area_id'],'monster_id':r['monster_id'],'skill_id':s,'candidate_vs_approved': 'MATCH' if not fields else 'DIFFERENT','changed_fields':'|'.join(fields),'approved_name':a.get('name'),'input_name':r['skill_name'],'name_match':a.get('name')==r['skill_name'],'maker_registered_source':'UNRESOLVED normal RootDesk SkillTable absent; Mislocated candidate only'})
    writecsv('PROJECT_DATA_CHECK.csv',diff);print('DATA_DIFF',[r for r in diff if r['changed_fields'] or not r['name_match']]);print('ROOM_SAMPLE',readcsv(ROOT/'RootDesk/MyDesk/GameData/RoomTable.csv')[:1]);print('SKILL_SAMPLE',current[15])
    for p in ['FULL_ART_SCOPE.csv','OUTPUT_REQUIREMENTS.csv','ASSET_BINDING_PLAN.csv']:
        zz=zipfile.ZipFile(recs[0]['input_zip']);name=recs[0]['input_prefix']+p;rows=zcsv(zz,name);print(p,rows[:1])
if __name__=='__main__':globals()[sys.argv[1]]()
