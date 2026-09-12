from review_audit import *
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
def paste(c,im,x,y,w,h):
    im=im.convert('RGBA');im.thumbnail((w,h),Image.Resampling.NEAREST);c.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2),im)
def make(only_area00=False):
    rs=json.loads((RUN/'records.json').read_text('utf8'));sels=readcsv(RUN/'AREA_SELECTION.csv')
    b=readcsv(ART/'output_audit/BASELINE_INDEX.csv');z=zipfile.ZipFile(next(r['path'] for r in b if r['kind']=='AREA00_OUTPUT'))
    dirs=sorted(set(n.split('/ICON/')[0] for n in z.namelist() if '/ICON/' in n and n.endswith('.png')))
    c=Image.new('RGB',(2000,len(dirs)*220),(36,40,48));d=ImageDraw.Draw(c)
    for i,p in enumerate(dirs):
        d.text((10,i*220+5),'APPROVED AREA00 '+p.split('/')[-1],font=font,fill='white')
        ns=sorted(n for n in z.namelist() if n.startswith(p+'/') and ('/ICON/' in n or '/VFX/' in n) and n.endswith('.png'))
        for j,n in enumerate(ns):paste(c,Image.open(io.BytesIO(z.read(n))),j*150,i*220+35,145,170)
    c.save(RUN/'boards/area00_approved_actual.png')
    if only_area00:return
    z=zipfile.ZipFile(rs[0]['input_zip']); candidates=[]
    for n in z.namelist():
        if not n.endswith('info.md'):continue
        t=z.read(n).decode('utf-8-sig')
        if 'reference_role: `VFX`' in t and 'preview_usable: `true`' in t and 'style_priority: `EXCLUDE_STYLE`' not in t:
            ims=[p for p in z.namelist() if p.startswith(n[:-7]) and p.lower().endswith(('.png','.gif','.webp'))]
            if ims:candidates.append((n,ims[0],t))
    candidates=candidates[:16];c=Image.new('RGB',(1400,4*300),(36,40,48));d=ImageDraw.Draw(c);srows=[]
    for k,(n,p,t) in enumerate(candidates):
        im=Image.open(io.BytesIO(z.read(p)));x=(k%4)*350;y=(k//4)*300
        if getattr(im,'n_frames',1)>1:im.seek(im.n_frames//2)
        paste(c,im,x,y+45,340,235);d.text((x+5,y+5),n.split('/')[-2][:32],font=font,fill='white')
        srows.append({'info_path':rs[0]['input_zip']+'::'+n,'image_path':p,'image_sha256':hashlib.sha256(z.read(p)).hexdigest(),'classification_record':t,'review_use':'PENDING_VISUAL'})
    c.save(RUN/'boards/style_reference_candidates.png');writecsv('STYLE_REFERENCE_CHECK.csv',srows)
    prev=[]
    for s in sels:
        z=zipfile.ZipFile(s['output_path']);ns=[n for n in z.namelist() if n.endswith('AREA_OVERVIEW_PREVIEW.png')];assert len(ns)==1
        data=z.read(ns[0]);im=Image.open(io.BytesIO(data));out=RUN/'boards'/f'{s["area_id"]}_actual_overview.png';im.save(out)
        prev.append({'area_id':s['area_id'],'output':s['output_path'],'preview':ns[0],'sha256':hashlib.sha256(data).hexdigest(),'copy':str(out),'dimensions':str(im.size)})
    for k in range(0,len(prev),4):
        chunk=prev[k:k+4];c=Image.new('RGB',(2000,1500),(36,40,48));d=ImageDraw.Draw(c)
        for j,r in enumerate(chunk):
            x=(j%2)*1000;y=(j//2)*750;d.text((x+10,y+5),r['area_id']+' actual OUTPUT preview',font=font,fill='white');paste(c,Image.open(r['copy']),x,y+35,990,710)
        c.save(RUN/'boards'/f'preview_review_{k//4+1:02}.png')
    writecsv('PREVIEW_CHECK.csv',prev)
    preserve=readcsv(REPACK/'PNG_BYTE_PRESERVATION.csv');look={r['monster_id']:r for r in rs};reuse=[]
    for p in preserve:
        r=look[p['monster_id']];h=[h for n,h in r['file_hashes'].items() if n.endswith('/'+p['output_path'])];assert len(h)==1
        reuse.append({'area_id':p['area_id'],'monster_id':p['monster_id'],'role':p['role'],'file':p['output_path'],'current_sha256':h[0],'previous_source_sha256':p['source_sha256'],'preservation_record_sha256':p['output_sha256'],'match':h[0]==p['source_sha256']==p['output_sha256']})
    writecsv('REUSE_PNG_CHECK.csv',reuse)
    rooms=readcsv(ROOT/'RootDesk/MyDesk/GameData/RoomTable.csv');pr=readcsv(RUN/'PROJECT_DATA_CHECK.csv');rd={r['monster_id']:r for r in pr}
    for r in rs:
        rr=[x for x in rooms if x['monster_id']==r['monster_id']];rd[r['monster_id']].update(input_area_id=r['area_id'],project_area_ids='|'.join(sorted(set(x['area_id'] for x in rr))),project_room_ids='|'.join(x['id'] for x in rr),area_match=any(x['area_id']==r['area_id'] for x in rr))
    writecsv('PROJECT_DATA_CHECK.csv',pr)
    print('ROLE_COUNTS',len(rs),sum(len(r['role_files']) for r in rs));print('PRESERVE',len(reuse),all(r['match'] for r in reuse));print('REGION',sum(r['area_match'] for r in pr),[r for r in pr if not r['area_match']]);print('PREVIEW_SIZES',[(r['area_id'],r['dimensions']) for r in prev]);print('STYLECOUNT',len(srows))
if __name__=='__main__':make()
