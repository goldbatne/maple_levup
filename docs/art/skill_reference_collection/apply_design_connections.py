from pathlib import Path
import csv, io, json, zipfile, hashlib, re, tempfile, datetime, html
from PIL import Image
from skill_design_assignments import SOURCES, ASSIGNMENTS

ROOT = Path(__file__).parent
BASE = ROOT.parent / 'images-input-packages'
STAGE = Path(tempfile.gettempdir()) / 'msw_design_connection_20260913'
REFS = {r['key']: r for r in json.loads((STAGE/'refs.json').read_text(encoding='utf-8'))}
STAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
def sha(b): return hashlib.sha256(b).hexdigest()
def norm(b): return re.sub(r'\n{3,}', '\n\n', b.decode('utf-8-sig').replace('\r',''))
def jbytes(x): return json.dumps(x,ensure_ascii=False,indent=2).encode('utf-8')
def csvbytes(rows,fields):
    s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    return s.getvalue().encode('utf-8-sig')

POLICY = '''## 스킬별 실제 이미지 연결 — 제작 순서

이 Area 전체를 새로 제작한다. AREA 00도 새 제작 대상이며 기존 00 OUTPUT은 덮어쓰지 않고 마감 기준으로만 사용한다. 다른 Area를 자동 시작하지 않는다.
첨부 INPUT ZIP과 이 TXT만으로 필요한 자료를 볼 수 있게 구성했다. 공통 대용량 ZIP, 웹 링크, PC의 절대 경로를 추가로 요청할 필요가 없다.

1. AREA_MANIFEST와 각 몬스터의 MONSTER_INFO, GENERATION_SPEC, RUNTIME_ROLE_MAP, DESIGN_REFERENCE_BRIEF를 읽는다. MONSTER_IMAGE를 실제 이미지로 연다.
2. DESIGN_REFERENCE_BRIEF의 공식 VFX 원본 GIF/PNG와 연속 프레임, 기본 ICON, 지정 AREA00 PNG를 실제로 연다. reference_resource_design/REFERENCE_VIEWER.html에서 한 스킬씩 비교할 수 있다. 파일명·RUID·설명만 읽는 것은 이미지 참조가 아니다.
3. 한 번에 **한 몬스터의 한 스킬**을 제작한다. Area 전체의 여러 몬스터를 한 장의 콘셉트 시트로 생성하지 않는다. VFX가 필수인 스킬은 VFX 프레임 완성도를 먼저 판정하고 그 결과와 같은 소재로 ICON을 제작한다. ICON-only 패시브는 불필요한 VFX를 만들지 않는다.
4. VFX 생성 호출에 해당 MONSTER_IMAGE, 지정 공식 VFX의 준비/중간/절정/해체 실제 PNG, AREA00 마감 PNG를 실제 reference image input으로 전달한다. 파일 경로를 문장에 적는 것만으로 완료하지 않는다. 관련 프레임은 넉넉히 제공하되 다른 스킬 자료를 무차별로 섞지 않는다. 호출 이미지 수 한도가 있으면 모두 먼저 보고 역할별 필요한 프레임을 선택하고 실제 전달 목록을 기록한다. 이어지는 생성에서도 기준 이미지를 유지한다.
5. ICON 호출에는 MONSTER_IMAGE, 완성 VFX의 대표 프레임(필수 VFX가 있는 경우), 해당 공식 ICON 및 AREA00 ICON을 실제 입력한다. 공식 ICON의 대비·명암 면·작은 크기 읽힘을 참고하되 원본의 숫자·글자·UI 테두리·캐릭터·무기는 복제하지 않는다.
6. 공식 참조는 **아트 디자인·재질·명암·코어광·파편·프레임 구성**을 함께 참고하는 이미지다. 단순 역할 분리와 시간 구조만으로 제한하지 않는다. 다만 목표 소재·팔레트·형태·효과는 GENERATION_SPEC를 유지한다. brief의 적용/제외 지시가 해당 참조의 사용 범위다. 기존 광범위 스타일 목록은 배경 자료이며 스킬별 지정 이미지 대신 무작위 선택하지 않는다.
7. 이미지를 보고 확인한 사실과 실제 생성 호출에 전달한 사실을 구분한다. REFERENCE_INPUTS.json에 실제 입력 파일/해시/용도/전달 여부와 누락 이유를 기록한다. 도구가 이미지를 받을 수 없으면 해당 제작만 BLOCKED로 남기고 참조했다고 꾸미지 않는다.

## 참조 파일의 성격

공식 PNG/GIF는 MSW 공개 리소스 API의 표시용 미디어다. 연속 PNG는 그 GIF의 실제 전체 프레임 추출본이며 엔진 원본 RGBA 복구본이 아니다. 흰 배경이 구워진 프리뷰는 디자인 관찰용이다. 그 흰 배경·낮은 해상도·알파를 새 OUTPUT에 복사하지 않는다. 새 자산의 투명도는 별도로 검증한다.
현재 API에서 조회된 사실만으로 최신 출시/개편을 주장하지 않는다. VI나 팩 이름도 최신성의 증거가 아니다. 이 연결은 실제 표시 이미지의 적합성을 보고 선택한 것이며 날짜가 검증되지 않은 자료는 currentness=UNVERIFIED다.
공식 고유 소재를 그대로 복제하지 않되 참고를 무의미하게 제한하지 않는다. 어두운 유색 면, 선명한 중간톤, 국소 코어, 재질별 반사, 얇은 반투명 외곽과 프레임 분해 방식을 새 스킬의 고유 소재에 적용한다.
'''

def build_sources():
    assets={}; metas={}
    for key,(roles,observed,exclude) in SOURCES.items():
        r=REFS[key]; es=[]
        for role in roles.split()+['icon']:
            e=next(e for e in r['elements'] if e['rel_path']==role)
            raw=(STAGE/key/e['filename']).read_bytes()
            assert sha(raw)==e['sha256']
            prefix=f'reference_resource_design/{key}/'
            source=prefix+'source/'+e['filename']; assets[source]=raw
            im=Image.open(io.BytesIO(raw)); n=getattr(im,'n_frames',1); frames=[];duration=[]
            if role!='icon':
                for i in range(n):
                    im.seek(i); o=io.BytesIO();im.convert('RGBA').save(o,format='PNG')
                    p=prefix+f'frames/{e["ruid"]}_F{i:03}.png';assets[p]=o.getvalue();frames.append(p);duration.append(im.info.get('duration'))
            es.append({'role':role,'ruid':e['ruid'],'source_path':source,'source_sha256':sha(raw),'frames':frames,'frame_count':n,'duration_ms':duration})
        meta={'key':key,'pack_id':r['pack_id'],'official_name':r['name'],'observed_rendering':observed,'exclude':exclude,'currentness':'UNVERIFIED','media_kind':'official display preview; extracted frames are not engine RGBA originals','elements':es}
        assets[f'reference_resource_design/{key}/SOURCE.json']=jbytes(meta);metas[key]=meta
    return assets,metas

def fixed_fields(text):
    # These lines are immutable WHAT, format, and target identity, not style assignments.
    return [s for s in text.splitlines() if s.startswith('- ') and any(t in s for t in ['핵심 소재:','주 색상:','보조 색상:','아이콘 핵심 모티브:','실제 현재 효과:','실제 현재 동작:','VFX:','ICON:','profile:','monster_id:','skill_id:','최종 스킬 이름:','스킬 타입:','효과 발생 위치:','진행 방향:','대상 표현:','화면 점유율:','이펙트 밀도:','시간 흐름:'])]

def baseline_paths(data,key):
    # Choose material-appropriate finish triplet; this is not a new silhouette instruction.
    if key in ('m_snail',): tag='001_m_snail'
    elif key in ('m_slime','m_jellyfish','m_cube_slime','m_brown_teddy'): tag='005_m_slime'
    elif key in ('m_mano','m_mushmom','m_eliza','m_snow_witch','m_cygnus'): tag='004_m_mano'
    elif any(x in key for x in ('pig','boar','hog','kargo','knight_c','trojan')): tag='003_m_red_snail'
    else: tag='002_m_blue_snail'
    candidates=[p for p in data if '/area00_finish_baseline/' in p and p.endswith('.png') and tag in p]
    return sorted(p for p in candidates if '/selected_vfx_frames/' in p), next(p for p in candidates if '/icons/' in p)

def make_prompt(old,rows):
    # Retain detailed technical rules, discard both old prefatory reference policies and old precedence chain.
    m=re.search(r'^# AREA \d+ ',old,re.M); assert m
    s=old[m.start():]
    s=re.sub(r'개정: [^\n]+',f'개정: {STAMP} — 스킬별 실제 디자인 연결',s)
    s=re.sub(r'제작 절차·도구·패시브 역할·품질 판정은[^\n]+', '이 TXT와 ZIP의 CHATGPT_IMAGES_MASTER_PROMPT는 동일한 지침이다. WHAT과 출력 규격은 GENERATION_SPEC, 필수 NEW_ART 역할은 RUNTIME_ROLE_MAP, 실제 참조 선택은 DESIGN_REFERENCE_BRIEF를 따른다.',s)
    a=s.index('## 2. 이미지 생성 도구');b=s.index('## 3. 실제 이미지 생성',a)
    s=s[:a]+POLICY+'\n\n'+s[b:]
    s=re.sub(r'\n이번 공식 디자인 참조 지침:[^\n]+','',s)
    s += '\n\n## 스킬별 필수 참조 연결\n\n'
    for row in rows:
        s+=f'- {row["monster_name"]} / {row["skill_name"]} / `{row["skill_id"]}`: `{row["folder"]}/DESIGN_REFERENCE_BRIEF.md`\n'
    s+='\n해당 brief의 실제 이미지 경로를 생성 도구에 첨부한다. INPUT ZIP과 이 TXT 외의 파일은 필요 없다. 보고서만 작성하지 말고 실제 생성·검증·납품을 실행한다.\n'
    return s

def main():
    packages=sorted(BASE.glob('AREA_*_IMAGES_INPUT.zip')); assert len(packages)==20
    # Validate every source/mapping before any canonical package is changed.
    assets,metas=build_sources()
    for zp in packages:
        with zipfile.ZipFile(zp) as z:
            rows=list(csv.DictReader(io.StringIO(z.read(zp.stem+'/AREA_MANIFEST.csv').decode('utf-8-sig'))))
            assert all(r['monster_id'] in ASSIGNMENTS for r in rows)
    backup=ROOT/'backups'/f'INPUTS_BEFORE_SKILL_DESIGN_CONNECTION_{STAMP}.zip'; backup.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_STORED) as b:
        for p in packages+sorted(BASE.glob('AREA_*_CHATGPT_PRODUCTION_PROMPT.txt'))+[BASE/'ALL_AREAS_INDEX.csv']:
            b.write(p,p.name)
    report={'status':'INPUT_CONNECTION_VALIDATED','timestamp':STAMP,'backup':str(backup),'generation_performed':False,'live_monster_ruid_check':'NOT_CHECKED; existing MONSTER_IMAGE and provenance preserved','areas':[]}
    for zp in packages:
        root=zp.stem+'/';area=zp.stem[5:7]
        with zipfile.ZipFile(zp) as z: old={n[len(root):]:z.read(n) for n in z.namelist() if not n.endswith('/')}
        data={p:b for p,b in old.items() if not p.startswith('reference_resource_design/') and p!='INPUT_FILE_HASHES.csv'}
        rows=list(csv.DictReader(io.StringIO(old['AREA_MANIFEST.csv'].decode('utf-8-sig')))); maps=[]; viewer=[]
        for row in rows:
            folder=row['folder'].strip('/'); mid=row['monster_id']; keys,adapt=ASSIGNMENTS[mid]
            spec=norm(old[folder+'/GENERATION_SPEC.md']);before=fixed_fields(spec)
            spec=spec.split('## 이번 개편의 지정 레퍼런스')[0].rstrip()
            spec=re.sub(r'^- 스타일 적용 우선순위:.*\n?', '',spec,flags=re.M)
            spec+='\n\n## 스킬별 확정 디자인 참조\n\n같은 폴더의 DESIGN_REFERENCE_BRIEF.md에 지정한 실제 이미지들을 사용한다. WHAT은 위 문구를 유지하고, 명암·재질·코어광·파편·프레임 전개를 함께 참고한다. 마감 자료의 저레벨 모양을 복사하지 않는다.\n'
            assert fixed_fields(spec)==before
            data[folder+'/GENERATION_SPEC.md']=spec.encode('utf-8')
            vfxbase,iconbase=baseline_paths(data,mid)
            mon=folder+'/MONSTER_IMAGE.png'; assert mon in data
            fields='\n'.join(x for x in before if any(t in x for t in ['핵심 소재:','주 색상:','보조 색상:','아이콘 핵심 모티브:']))
            lines=[f'# {row["monster_name"]} — {row["skill_name"]}: 실제 디자인 참조',f'\nmonster_id: `{mid}` / skill_id: `{row["skill_id"]}` / 타입: {row["skill_type"]}',
                   '\n경로는 INPUT ZIP 루트 기준이다. 원본 소재·역할을 아래 공식 스킬로 대체하는 지시가 아니다.', '\n## 고정 소재와 몬스터',fields,
                   f'\n실제 몬스터 입력: `{mon}`\n\nRUID: `{row["monster_image_ruid"]}` / SHA-256: `{sha(data[mon])}`',
                   '\n## 이 스킬에 적용할 구체적인 디자인',adapt,'\n## 공식 실제 이미지 — 모두 관찰하고 필요한 프레임을 실제 입력']
            selected=[]
            for key in keys:
                meta=metas[key]
                lines += [f'\n### {meta["official_name"]} / `{meta["pack_id"]}`',f'- 관찰한 표현: {meta["observed_rendering"]}',f'- 가져오지 않을 요소: {meta["exclude"]}']
                for e in meta['elements']:
                    lines += [f'- {e["role"]}: `{e["source_path"]}` / SHA-256 `{e["source_sha256"]}`']
                    if e['frames']:
                        n=len(e['frames']);ids=sorted(set([0,n//4,n//2,3*n//4,n-1]));recommended=[e['frames'][i] for i in ids]
                        lines.append(f'  전체 연속 PNG {n}장과 GIF 타이밍은 `{key}/SOURCE.json`이 아니라 `reference_resource_design/{key}/SOURCE.json`의 frames/duration_ms 목록에 있다. 대표 관찰 프레임:')
                        lines += ['  - `'+p+'`' for p in recommended]
                    else: recommended=[]
                    selected.append(dict(e,key=key,representative_frames=recommended))
                for p,b in assets.items():
                    if p.startswith(f'reference_resource_design/{key}/'):data[p]=b
            lines += ['\n## AREA00 마감 실제 입력','이 PNG들은 기존 패키지에 들어 있던 AREA00 수정 후보의 마감 자료다. 기존 파일 바이트를 유지했다. 사용자가 승인한 00의 품질을 기준으로 삼되 새 결과의 합격을 미리 보장하지 않는다.']
            lines += ['- `'+p+'`' for p in vfxbase+[iconbase]]
            lines += ['\n## 이 스킬 생성 순서',
                      '1. MONSTER_IMAGE + 위 공식 연속 프레임 + AREA00 VFX를 실제 입력한다. 한 호출에 여러 몬스터를 섞지 않는다.',
                      '2. RUNTIME_ROLE_MAP의 필수 VFX가 있으면 고정 축에서 준비→성장→절정→해체→fade를 명세 수량과 간격으로 만든다. ICON-only면 이 단계는 NOT_APPLICABLE이다.',
                      '3. ICON은 고정 아이콘 모티브를 사용한다. 공식 ICON의 명암 압축을 관찰하고 완성 VFX와 같은 소재로 그린다. 참조의 UI 테두리·숫자·문자·캐릭터는 새 자산에 넣지 않는다.',
                      '4. 최종 파일의 소재·실루엣·재질·방향·축·알파를 실제 비교한다. 파일 검사 PASS와 아트 PASS를 분리하고 실제 호출에 넣지 않은 이미지에 INPUT_USED=true를 쓰지 않는다.']
            brief=folder+'/DESIGN_REFERENCE_BRIEF.md';data[brief]='\n'.join(lines).encode('utf-8')
            mapping=dict(row,brief=brief,monster_image=mon,monster_sha256=sha(data[mon]),translation=adapt,reference_keys=keys,elements=selected,area00_vfx=vfxbase,area00_icon=iconbase)
            maps.append(mapping)
            # Local viewer resolves everything inside this Area ZIP, never an external archive.
            esc=html.escape
            imgs=f'<img class="monster" src="../{esc(mon)}"><p>{esc(adapt)}</p>'
            for key in keys:
                imgs+=f'<h3>{esc(metas[key]["official_name"])}</h3><p>{esc(metas[key]["observed_rendering"])}<br>제외: {esc(metas[key]["exclude"])}</p>'
                for e in metas[key]['elements']:
                    imgs+=f'<figure><img src="../{esc(e["source_path"])}"><figcaption>{esc(e["role"])} · {e["frame_count"]} frames</figcaption></figure>'
            imgs+='<h3>AREA00 마감 비교</h3>'+''.join(f'<img src="../{esc(p)}">' for p in vfxbase+[iconbase])
            viewer.append(f'<section><h2>{esc(row["monster_name"])} / {esc(row["skill_name"])}</h2>{imgs}</section>')
        data['reference_resource_design/AREA_REFERENCE_MAP.json']=jbytes(maps)
        data['reference_resource_design/AREA_REFERENCE_MAP.md']=('\n'.join(['# Area 스킬별 실제 참조 연결','\n각 몬스터 폴더의 brief를 읽고 실제 이미지를 생성 입력으로 사용한다. 공통 ZIP은 필요 없다.\n']+[f'- {r["monster_name"]} / {r["skill_name"]}: [{r["brief"]}](../{r["brief"]}) — '+', '.join(r['reference_keys']) for r in maps])).encode('utf-8')
        data['reference_resource_design/README.md']=POLICY.encode('utf-8')
        data['reference_resource_design/REFERENCE_VIEWER.html']=('<!doctype html><meta charset="utf-8"><title>AREA '+area+' 스킬 디자인 연결</title><style>body{background:#333;color:#eee;font:16px sans-serif;margin:24px}section{border-bottom:2px solid #999;padding:20px}img{max-width:240px;max-height:230px;object-fit:contain}figure{display:inline-block;margin:8px;vertical-align:top}p{max-width:1100px;line-height:1.6}</style><h1>AREA '+area+' — 스킬별 실제 참조</h1><p>ZIP을 풀고 여세요. 참조의 흰 배경은 공식 표시용 미디어에 포함된 경우가 있습니다. 새 자산에 복제하지 않습니다. 전체 프레임과 출처·타이밍은 각 SOURCE.json에 있습니다.</p>'+''.join(viewer)).encode('utf-8')
        promptpath=BASE/f'AREA_{area}_CHATGPT_PRODUCTION_PROMPT.txt'
        prompt=make_prompt(norm(promptpath.read_bytes()),rows).encode('utf-8')
        data['CHATGPT_IMAGES_MASTER_PROMPT.md']=prompt
        start=norm(data['README_START_HERE.md'])
        data['README_START_HERE.md']=('# 현재 제작 지침\n\nCHATGPT_IMAGES_MASTER_PROMPT.md와 외부 TXT는 동일하다. 각 monsters 폴더의 DESIGN_REFERENCE_BRIEF.md를 필수로 읽고 실제 이미지를 입력한다. AREA00도 새 제작 대상이다. 참고 파일은 모두 이 ZIP에 포함되어 있다.\n\n'+start).encode('utf-8')
        idx='global_skill_style_library/STYLE_INDEX.md'
        data[idx]=('# 스킬별 지정 참조 우선\n\n실제 생성에 사용할 자료는 각 DESIGN_REFERENCE_BRIEF.md와 reference_resource_design/AREA_REFERENCE_MAP.md에 지정되어 있다. 아래 기존 공통 목록은 배경 자료이며 무작위 대체 선택하지 않는다. 공통 목록의 RECENT 표기만으로 새 참조의 최신성을 주장하지 않는다.\n\n'+norm(data[idx])).encode('utf-8')
        hashes=[dict(path=p,sha256=sha(b),bytes=len(b)) for p,b in sorted(data.items())]
        data['INPUT_FILE_HASHES.csv']=csvbytes(hashes,['path','sha256','bytes'])
        # Preserve all original assets except previous generic reference_resource_design.
        preserved=[p for p in old if p.endswith(('.png','.gif','.csv')) and not p.startswith('reference_resource_design/') and p!='INPUT_FILE_HASHES.csv']
        preserved += [p for p in old if p.endswith(('RUNTIME_ROLE_MAP.md','MONSTER_INFO.md','SOURCE_PROVENANCE.md','OUTPUT_NAMING_SPEC.md','OUTPUT_FORMAT_SPEC.md'))]
        assert all(data[p]==old[p] for p in preserved)
        for m in maps:
            for e in m['elements']:
                assert e['source_path'] in data and sha(data[e['source_path']])==e['source_sha256']
                assert all(p in data for p in e['frames'])
            assert all(p in data for p in m['area00_vfx']+[m['area00_icon'],m['monster_image'],m['brief']])
        temp=zp.with_suffix('.zip.tmp')
        with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p,b in sorted(data.items()):z.writestr(root+p,b)
        with zipfile.ZipFile(temp) as z:
            assert z.testzip() is None
            assert len(z.namelist())==len(data)
            assert z.read(root+'CHATGPT_IMAGES_MASTER_PROMPT.md')==prompt
            for h in hashes: assert sha(z.read(root+h['path']))==h['sha256']
        temp.replace(zp);promptpath.write_bytes(prompt)
        entry={'area':area,'skills':len(rows),'reference_sources':len(set(k for m in maps for k in m['reference_keys'])),'reference_pngs':sum(p.startswith('reference_resource_design/') and p.endswith('.png') for p in data),'preserved_files':len(set(preserved)),'zip_sha256':sha(zp.read_bytes()),'zip_bytes':zp.stat().st_size,'prompt_sha256':sha(prompt),'status':'PASS'}
        report['areas'].append(entry); print(json.dumps(entry,ensure_ascii=False),flush=True)
    indexpath=BASE/'ALL_AREAS_INDEX.csv';index=list(csv.DictReader(io.StringIO(indexpath.read_text(encoding='utf-8-sig'))))
    for r in index:
        a=next(a for a in report['areas'] if a['area']==r['area_num'].zfill(2)); r.update(zip_bytes=a['zip_bytes'],zip_sha256=a['zip_sha256'],prompt_sha256=a['prompt_sha256'])
    indexpath.write_bytes(csvbytes(index,list(index[0])))
    report['skill_count']=sum(a['skills'] for a in report['areas'])
    report['checks']=['20 ZIP CRC and entry hashes','104 explicit per-skill briefs and all reference paths','all selected official source bytes match cached official media hashes','monster PNGs and original WHAT unchanged','runtime/naming/format unchanged','external TXT equals internal master','no artwork or game files changed']
    (ROOT/'DESIGN_CONNECTION_VALIDATION.json').write_bytes(jbytes(report))
    (BASE/'SEND_TO_CHATGPT_README.md').write_text('# 보내는 방법\n\n해당 Area의 AREA_XX_IMAGES_INPUT.zip과 AREA_XX_CHATGPT_PRODUCTION_PROMPT.txt 두 파일을 함께 첨부하고 **첨부한 프롬프트대로 실행해줘**라고 보내세요.\n\n공식 스킬의 실제 연속 PNG/GIF·ICON과 AREA00 마감 PNG가 각 ZIP에 들어 있습니다. 공통 대용량 ZIP은 보내지 않습니다. AREA00부터 새로 제작하며 기존 OUTPUT은 덮어쓰지 않습니다. 현재 운영 목록에는 AREA06이 없습니다.\n\nZIP 내부 reference_resource_design/REFERENCE_VIEWER.html을 풀어서 열면 스킬별 연결을 확인할 수 있습니다.\n',encoding='utf-8')
    overview=['# AREA 00–20 실제 디자인 참조 연결','\nINPUT ZIP + TXT 두 파일만 전달한다. AREA06은 기존 운영 목록에서 제외되어 새 패키지를 만들지 않았다.\n']
    for r in index:overview.append(f'- AREA {r["area_num"]}: [{r["zip_file"]}]({r["zip_file"]}) + [{r["prompt_file"]}]({r["prompt_file"]})')
    (BASE/'ALL_AREAS_INDEX.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
    print('COMPLETE',report['skill_count'],str(backup),flush=True)
if __name__=='__main__':main()
