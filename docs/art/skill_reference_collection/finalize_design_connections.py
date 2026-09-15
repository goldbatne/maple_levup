"""Add hash-linked full AREA00 reference sequences and verify final deliverables."""
from apply_design_connections import ROOT,BASE,sha,csvbytes,jbytes
from pathlib import Path
import zipfile,json,csv,io,re,html,base64

def main():
    source=ROOT.parent/'area00_refinement/20260912_203404/AREA_00_IMAGES_OUTPUT_REFINED_CANDIDATE.zip'
    with zipfile.ZipFile(source) as z:
        sourceframes={n:z.read(n) for n in z.namelist() if '/VFX/' in n and n.endswith('.png')}
        sourceicons={n:z.read(n) for n in z.namelist() if '/ICON/' in n and n.endswith('.png')}
    assert len(sourceframes)==44 and len(sourceicons)==5
    byname={Path(n).name:b for n,b in (sourceframes|sourceicons).items()}
    report=json.loads((ROOT/'DESIGN_CONNECTION_VALIDATION.json').read_text(encoding='utf-8'))
    saved_assets={};sections=[]; counts=[]
    def media(b,suffix):
        h=sha(b);saved_assets[h]='data:image/'+('gif' if suffix=='.gif' else 'png')+';base64,'+base64.b64encode(b).decode('ascii')
        return '<img data-asset="'+h+'">'
    for area in report['areas']:
        an=area['area'];zp=BASE/f'AREA_{an}_IMAGES_INPUT.zip';root=zp.stem+'/'
        with zipfile.ZipFile(zp) as z:data={n[len(root):]:z.read(n) for n in z.namelist()}
        # Verify that this is the very same 00 source used by the existing baseline, not a filename guess.
        oldbaseline=[p for p in data if '/area00_finish_baseline/' in p and ('/selected_vfx_frames/' in p or '/icons/' in p)]
        assert len(oldbaseline)==20
        assert all(data[p]==byname[Path(p).name] for p in oldbaseline)
        added=[]
        for n,b in sourceframes.items():
            pieces=n.split('/');monster=pieces[pieces.index('monsters')+1]
            p='global_skill_style_library/area00_finish_baseline/full_vfx_frames/'+monster+'/'+Path(n).name
            data[p]=b;added.append(dict(path=p,sha256=sha(b),source_entry=n))
        sourceinfo={'source_zip':'AREA_00_IMAGES_OUTPUT_REFINED_CANDIDATE.zip','source_zip_sha256':sha(source.read_bytes()),'identification':'all 15 existing VFX and 5 ICON bytes match this archive','frames':added,'frame_count':44,'status':'reference only; existing OUTPUT not modified'}
        data['global_skill_style_library/area00_finish_baseline/FULL_SEQUENCE_SOURCE.json']=jbytes(sourceinfo)
        readme='global_skill_style_library/area00_finish_baseline/README.md'
        data[readme]+=('\n## 전체 연속 원본\n\nfull_vfx_frames에는 위 원본 ZIP과 해시로 연결된 VFX 44프레임 전체가 있다. selected_vfx_frames는 빠른 비교용이며 실제 연속 형상 확인은 full_vfx_frames를 사용한다. 원본 경로/해시는 FULL_SEQUENCE_SOURCE.json에 기록했다. 기존 OUTPUT을 바꾸거나 새 후보를 승인한 것이 아니다.\n').encode('utf-8')
        maps=json.loads(data['reference_resource_design/AREA_REFERENCE_MAP.json'])
        part=['<h1>AREA '+an+'</h1>']
        for m in maps:
            tag=Path(m['area00_vfx'][0]).name.split('_s_mon_')[0]
            full=[f['path'] for f in added if Path(f['path']).name.startswith(tag+'_s_mon_')]
            assert len(full) in (8,12)
            m['area00_full_vfx']=full
            p=m['brief'];s=data[p].decode('utf-8')
            s=re.sub(r'`[a-z_]+/SOURCE.json`이 아니라 ', '',s)
            s+='\n\n## AREA00 전체 연속 마감 이미지\n\n아래 전 프레임을 실제로 보아 형태 변화와 두께·광량의 흐름을 비교한다. 새 스킬의 소재·크기·동작은 GENERATION_SPEC를 따른다.\n'
            s+='\n'.join('- `'+f+'`' for f in full)+'\n'
            data[p]=s.encode('utf-8')
            part+=['<section><h2>'+html.escape(m['monster_name']+' / '+m['skill_name'])+'</h2>',media(data[m['monster_image']],'.png'),'<p>'+html.escape(m['translation'])+'</p>']
            for key in m['reference_keys']:
                meta=json.loads(data[f'reference_resource_design/{key}/SOURCE.json'])
                part+=['<h3>'+html.escape(meta['official_name'])+'</h3><p>'+html.escape(meta['observed_rendering'])+'<br>제외: '+html.escape(meta['exclude'])+'</p>']
                for e in meta['elements']:
                    b=data[e['source_path']]
                    part+=['<figure>'+media(b,Path(e['source_path']).suffix)+'<figcaption>'+html.escape(e['role'])+' · '+str(e['frame_count'])+' frames</figcaption></figure>']
            part+=['<details><summary>AREA00 마감 비교와 실제 참조 경로</summary>']
            for f in m['area00_vfx']:part.append(media(data[f],'.png'))
            part+=['<p>'+html.escape(m['brief'])+'</p><p>각 INPUT의 brief에 전체 원본·추출 프레임·SHA-256 경로가 연결되어 있습니다.</p></details></section>']
            counts.append(sum(len(e['frames'])+(e['role']=='icon') for e in m['elements'])+len(full)+1)
        sections.append('<details open><summary>AREA '+an+'</summary>'+''.join(part)+'</details>')
        data['reference_resource_design/AREA_REFERENCE_MAP.json']=jbytes(maps)
        master=data['CHATGPT_IMAGES_MASTER_PROMPT.md']+'\nAREA00 마감 자료는 brief의 전체 연속 PNG도 확인한다. full_vfx_frames에 기존 기준의 44프레임 전체가 포함되어 있다. 새 00부터 다시 제작하며 기존 파일은 덮어쓰지 않는다.\n'.encode('utf-8')
        data['CHATGPT_IMAGES_MASTER_PROMPT.md']=master
        hashes=[dict(path=p,sha256=sha(b),bytes=len(b)) for p,b in sorted(data.items()) if p!='INPUT_FILE_HASHES.csv']
        data['INPUT_FILE_HASHES.csv']=csvbytes(hashes,['path','sha256','bytes'])
        temp=zp.with_suffix('.zip.tmp')
        with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p,b in sorted(data.items()):z.writestr(root+p,b)
        with zipfile.ZipFile(temp) as z:
            assert z.testzip() is None
            for f in hashes: assert sha(z.read(root+f['path']))==f['sha256']
            for m in maps:
                assert all(root+f in z.namelist() for f in m['area00_full_vfx'])
            # Verify every relative viewer image URL, including Korean paths, against final ZIP.
            viewer=data['reference_resource_design/REFERENCE_VIEWER.html'].decode('utf-8')
            for p in re.findall(r'src="\.\./([^\"]+)"',viewer):assert root+html.unescape(p) in z.namelist()
        temp.replace(zp)
        prompt=BASE/f'AREA_{an}_CHATGPT_PRODUCTION_PROMPT.txt';prompt.write_bytes(master)
        area.update(zip_sha256=sha(zp.read_bytes()),zip_bytes=zp.stat().st_size,prompt_sha256=sha(master),area00_full_frames=44)
        print('final verified AREA',an,flush=True)
    indexpath=BASE/'ALL_AREAS_INDEX.csv';rows=list(csv.DictReader(io.StringIO(indexpath.read_text(encoding='utf-8-sig'))))
    for r in rows:
        a=next(a for a in report['areas'] if a['area']==r['area_num'].zfill(2));r.update(zip_bytes=a['zip_bytes'],zip_sha256=a['zip_sha256'],prompt_sha256=a['prompt_sha256'])
    indexpath.write_bytes(csvbytes(rows,list(rows[0])))
    report['baseline_full_sequence_source']=sourceinfo
    report['per_skill_design_image_count_including_official_icons_and_selected_full_baseline']={'min':min(counts),'max':max(counts),'note':'excludes original MONSTER_IMAGE and other shared background style files'}
    report['checks']+=['full baseline 44 VFX verified against same archive as existing 15 VFX + 5 ICON','all viewer URLs resolve inside each ZIP','final entry hashes and index refreshed']
    (ROOT/'DESIGN_CONNECTION_VALIDATION.json').write_bytes(jbytes(report))
    page='''<!doctype html><meta charset="utf-8"><title>AREA00–20 스킬별 실제 디자인 참조</title><style>body{background:#333;color:#eee;font:16px sans-serif;padding:24px}p{max-width:1100px;line-height:1.6}section{border:1px solid #888;padding:18px;margin:12px 0}img{max-width:240px;max-height:200px;object-fit:contain}figure{display:inline-block;vertical-align:top;margin:8px}summary{cursor:pointer;font-weight:bold;padding:12px}</style><h1>스킬별 실제 이미지 연결</h1><p>20개 Area INPUT / 104개 스킬. 공식 표시용 PNG/GIF와 실제 몬스터, 기존 AREA00 마감의 연결입니다. 새로운 OUTPUT의 품질 검수 결과가 아닙니다. 사용자는 해당 Area INPUT ZIP과 TXT만 첨부하면 됩니다.</p>'''+''.join(sections)+'<script>const assets='+json.dumps(saved_assets)+';document.querySelectorAll("[data-asset]").forEach(im=>im.src=assets[im.dataset.asset]);</script>'
    (ROOT/'AREA_DESIGN_REFERENCES.html').write_text(page,encoding='utf-8')
    print('FINAL COMPLETE',len(rows),len(counts),min(counts),max(counts),flush=True)
if __name__=='__main__':main()
