from pathlib import Path,PurePosixPath
import csv,json,hashlib,zipfile,io,sys,re,stat
from PIL import Image,ImageDraw,ImageFont
RUN=Path(__file__).parent;ROOT=Path('D:/maplestory_levup');ART=ROOT/'docs/art'
BASE=ART/'output_audit/runs/20260912_162508_msw_origin_art_review'
RS=json.loads((BASE/'records.json').read_text('utf8'))
CON={(r['monster_id'],r['role']):r for r in json.loads((BASE/'CONTRACT_SNAPSHOTS.json').read_text('utf8'))}
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else Path(x).read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(io.StringIO(Path(p).read_text('utf-8-sig'))))
def csvbytes(rr):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rr[0]),lineterminator='\n');w.writeheader();w.writerows(rr);return s.getvalue().encode('utf-8-sig')
def csvwrite(p,rr):Path(p).write_bytes(csvbytes(rr))
def safezip(z):
    ns=z.namelist();assert len(ns)==len(set(ns))
    for i in z.infolist():
        p=PurePosixPath(i.filename);assert not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename and ':' not in i.filename
        assert not stat.S_ISLNK(i.external_attr>>16)
    assert z.testzip() is None
FONTS={n:ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',n) for n in [18,22,28,34]}
def textfit(d,s,xy,width,font,fill):
    assert d.textlength(s,font=font)<=width,(s,width)
    d.text(xy,s,font=font,fill=fill)
def paste(c,im,box):
    im=im.convert('RGBA');im.thumbnail(box[2:],Image.Resampling.LANCZOS);c.paste(im,(box[0]+(box[2]-im.width)//2,box[1]+(box[3]-im.height)//2),im)
def preview(r,files):
    rr=[k for k in r['role_files'] if k!='ICON'];h=430+sum(50+220*((len(files[k])+7)//8) for k in rr)
    c=Image.new('RGB',(1800,h),(29,35,46));d=ImageDraw.Draw(c)
    textfit(d,f"{int(r['work_order']):03}  {r['monster_name']}  |  {r['skill_name']}",(24,16),1750,FONTS[34],'#ffe6ab')
    textfit(d,f"{r['monster_id']}  /  {r['skill_id']}  /  {r['skill_type']}",(24,68),1750,FONTS[22],'white')
    textfit(d,'INPUT V2.4 · 실제 납품 PNG · USER ART APPROVAL: PENDING · RUNTIME: NOT RUN',(24,105),1750,FONTS[18],'#bac7d9')
    iz=zipfile.ZipFile(r['input_zip']);d.text((24,155),'MONSTER_IMAGE (원본 대조 확인)',font=FONTS[22],fill='white');d.text((430,155),'ICON (실제 납품)',font=FONTS[22],fill='white')
    paste(c,Image.open(io.BytesIO(iz.read(r['input_image']))),(24,190,320,210));paste(c,Image.open(io.BytesIO(files['ICON'][0][1])),(430,190,210,210))
    d.text((720,200),'역할별 모든 프레임을 아래에 순서대로 표시',font=FONTS[22],fill='white')
    d.text((720,238),'배경색은 Preview 표시용이며 납품 PNG 알파와 구분',font=FONTS[18],fill='#bac7d9')
    y=430
    for role in rr:
        rq=CON[(r['monster_id'],role)]['output_requirements'];d.text((24,y),f"{role} · {len(files[role])} frames · {rq['frame_seconds']}s/frame · {rq['canvas']}",font=FONTS[22],fill='#9ed9ff');y+=50
        for j,(n,data) in enumerate(files[role]):
            x=24+(j%8)*220;yy=y+(j//8)*220;d.rectangle((x,yy,x+204,yy+192),fill=(41,47,58));paste(c,Image.open(io.BytesIO(data)),(x,yy,204,192));d.text((x+75,yy+195),f'F{j:02}',font=FONTS[18],fill='white')
        y+=220*((len(files[role])+7)//8)
    out=io.BytesIO();c.save(out,format='PNG');return out.getvalue(),c
def build(area):
    selected=[r for r in RS if r['area_id']==area];assert selected
    sels={r['area_id']:r for r in rows(BASE/'AREA_SELECTION.csv')};sel=sels[area]
    assert sha(sel['input_path'])==sel['input_sha256'];assert sha(sel['output_path'])==sel['output_sha256']
    oz=zipfile.ZipFile(sel['output_path']);safezip(oz)
    root=f'AREA_{area[-2:]}_IMAGES_OUTPUT';payload={};manifest=[];pres=[];docchanges=[];cards=[]
    def put(n,b,kind='DOCUMENT'):
        payload[root+'/'+n]=b
        if kind!='ART':docchanges.append({'area_id':area,'relative_path':n,'category':kind,'new_sha256':sha(b),'basis':'V2.4 canonical metadata / actual delivered PNG composition','source_art_changed':'NO'})
    for r in selected:
        files={};mid=r['monster_id'];folder=r['folder'];info=[f"# RESULT_INFO — {r['monster_name']} / {r['skill_name']}",'',f'- area_id: {area}',f"- area_name: {r['area_name']}",f"- work_order: {int(r['work_order']):03}",f'- monster_id: {mid}',f"- monster_name: {r['monster_name']}",f"- skill_id: {r['skill_id']}",f"- skill_name: {r['skill_name']}",f"- skill_type: {r['skill_type']}",'- input_revision: V2.4',f"- input_sha256: {sel['input_sha256']}",f"- source_output_sha256: {sel['output_sha256']}",'- user_art_approval: PENDING','- runtime_validation: NOT_RUN','- pivot: normalized (0.5,0.5); fixed full canvas; no autocrop/recenter','']
        for role,sourcepaths in r['role_files'].items():
            files[role]=[];rq=CON[(mid,role)]['output_requirements'];sc=CON[(mid,role)]['full_art_scope'];token={'CAST_VFX':'CAST','REFERENCE_VFX':'REFERENCE'}.get(role,role)
            info.extend([f'## {role}',f"- contract: {rq['frame_count']} frames / {rq['canvas']} / {rq['frame_seconds']}s per frame / {rq['playback_mode']}",f"- runtime_use: {rq['runtime_use']}",f"- production_decision: {rq['production_decision']}",f"- future_target (not linked): {rq['future_target']}",f"- direction_and_engine_motion: {sc['direction_and_engine_motion']}"])
            for i,oldpath in enumerate(sourcepaths):
                name=f"{int(r['work_order']):03}_{mid}_{r['skill_id']}_{token}"+(f'_F{i:02}' if role!='ICON' else '')+'.png';rel=folder+'/'+token+'/'+name;before=oz.read(oldpath)
                changed=(mid=='m_king_bloctopus' and role=='PROJECTILE')
                data=(RUN/'corrected_projectile'/name).read_bytes() if changed else before
                assert changed or sha(data)==r['file_hashes'][oldpath]
                put(rel,data,'ART');files[role].append((rel,data));info.append(f'- `{rel}` SHA256 `{sha(data)}`')
                manifest.append({'area_id':area,'area_name':r['area_name'],'work_order':f"{int(r['work_order']):03}",'monster_id':mid,'monster_name':r['monster_name'],'skill_id':r['skill_id'],'skill_name':r['skill_name'],'skill_type':r['skill_type'],'effect_role':role,'production_decision':rq['production_decision'],'runtime_use':rq['runtime_use'],'relative_path':rel,'frame_index':i,'frame_count':rq['frame_count'],'canvas':rq['canvas'],'frame_seconds':rq['frame_seconds'],'playback_mode':rq['playback_mode'],'sha256':sha(data),'user_art_approval':'PENDING'})
                pres.append({'area_id':area,'monster_id':mid,'skill_id':r['skill_id'],'role':role,'frame_index':i,'source_zip':sel['output_path'],'source_path':oldpath,'output_path':root+'/'+rel,'source_sha256':sha(before),'output_sha256':sha(data),'change_class':'AUTHORIZED_ART_EDIT' if changed else 'PRESERVED','byte_preserved':sha(before)==sha(data)})
            info.append('')
        info.append('PROJECTILE 4장만 이미지 도구 수정 및 허용된 기술적 알파/고정 셀 출력 처리. CAST/ICON 바이트 유지.' if mid=='m_king_bloctopus' else '모든 납품 원화 PNG는 원본 ZIP 바이트를 보존했다.')
        put(folder+'/RESULT_INFO.md','\n'.join(info).encode('utf8'));pb,card=preview(r,files);put(folder+'/PREVIEW/labeled_preview.png',pb,'PREVIEW');cards.append(card)
    overview=Image.new('RGB',(1800,150+sum(c.height+20 for c in cards)),(17,23,33));d=ImageDraw.Draw(overview);d.text((24,18),f"AREA {area[-2:]} · {selected[0]['area_name']} · V2.4 최종 후보",font=FONTS[34],fill='white');d.text((24,77),'실제 납품 원화 전체 · 역할별 독립 행 · 사용자 최종 승인 대기',font=FONTS[22],fill='#bac7d9');y=150
    for c in cards:overview.paste(c,(0,y));y+=c.height+20
    p=io.BytesIO();overview.save(p,format='PNG');put('AREA_OVERVIEW_PREVIEW.png',p.getvalue(),'PREVIEW');overview.save(RUN/'evidence'/f'AREA_{area[-2:]}_OVERVIEW_PREVIEW.png')
    put('OUTPUT_MANIFEST.csv',csvbytes(manifest));put('OUTPUT_MANIFEST.md',f"# {root} — INPUT V2.4 final candidate\n\n- area_id: {area}\n- input_sha256: {sel['input_sha256']}\n- source_output_sha256: {sel['output_sha256']}\n- role_png_count: {len(manifest)}\n- user_art_approval: PENDING\n- runtime_validation: NOT_RUN\n\nFile-level hashes and role contracts: OUTPUT_MANIFEST.csv. CAST_VFX and REFERENCE_VFX are semantic role names; their folders use CAST and REFERENCE.\n".encode('utf8'))
    put('REPACK_INFO.md',f"# Packaging and art change scope\n\nBaseline review: {BASE.as_posix()}\n\n{'Only m_king_bloctopus PROJECTILE F00..F03 changed. All other role PNG bytes preserved.' if area=='area_11' else 'All role PNG bytes preserved. No art edits.'}\n\nPaths, Manifest, RESULT_INFO, and Preview were reconstructed against INPUT V2.4. Preview uses actual delivered PNGs. No game data, code, RUID, AnimationClip or Maker changes. Final user art approval is PENDING; runtime is NOT_RUN.\n".encode('utf8'))
    out=RUN/f'{root}_V2_4_FINAL_CANDIDATE.zip';assert not out.exists(),'Do not overwrite an already produced candidate ZIP'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n,b in sorted(payload.items()):z.writestr(n,b)
    csvwrite(RUN/f'{area}_PNG_CHANGES.csv',pres);csvwrite(RUN/f'{area}_DOCUMENT_PREVIEW_CHANGES.csv',docchanges)
    verify(out,manifest,payload)
    print('BUILT',out,'PNG',len(pres),'PRESERVED',sum(p['byte_preserved'] for p in pres),'CHANGED',sum(not p['byte_preserved'] for p in pres))
def verify(out,manifest=None,payload=None):
    z=zipfile.ZipFile(out);safezip(z);root=z.namelist()[0].split('/')[0];manifest=list(csv.DictReader(io.StringIO(z.read(root+'/OUTPUT_MANIFEST.csv').decode('utf-8-sig')))); dest=RUN/'verification_extract'/root
    assert not dest.exists(),'verification extraction is non-overwriting';dest.mkdir(parents=True)
    for n in z.namelist():
        rel=PurePosixPath(n).relative_to(root);target=dest.joinpath(*rel.parts);assert target.resolve().is_relative_to(dest.resolve());target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(n))
    checks=[]
    for r in manifest:
        p=dest/r['relative_path'];im=Image.open(p);wh=tuple(map(int,re.match(r'(\d+)x(\d+)',r['canvas']).groups()));assert im.size==wh and im.mode=='RGBA';assert sha(p)==r['sha256'];im.verify()
        checks.append({'area_id':r['area_id'],'relative_path':r['relative_path'],'sha256':sha(p),'canvas':r['canvas'],'role':r['effect_role'],'frame_index':r['frame_index'],'crc':'PASS','name_path_canvas_hash':'PASS'})
    for mid in set(r['monster_id'] for r in manifest):
        rr=[r for r in manifest if r['monster_id']==mid];d=(dest/rr[0]['relative_path']).parent.parent;assert (d/'RESULT_INFO.md').is_file() and (d/'PREVIEW/labeled_preview.png').is_file()
        for role in set(r['effect_role'] for r in rr):
            ss=[r for r in rr if r['effect_role']==role];assert sorted(int(r['frame_index']) for r in ss)==list(range(int(ss[0]['frame_count'])))
    csvwrite(RUN/f'{manifest[0]["area_id"]}_PACKAGE_VALIDATION.csv',checks)
if __name__=='__main__':build(sys.argv[1])
