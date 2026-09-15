from pathlib import Path
import json,zipfile,html,base64,io,csv
root=Path(__file__).parent;base=root.parent/'images-input-packages'
parts=['<!doctype html><meta charset="utf-8"><title>Area별 공식 디자인 참조</title><style>body{font:16px sans-serif;background:#252525;color:#eee;margin:24px}article{border-top:1px solid #888;padding:16px}img{max-width:250px;max-height:170px;object-fit:contain;margin:8px}a{color:#9cdbff}.row{display:flex;flex-wrap:wrap;align-items:center}small{display:block;color:#bbb}h2{position:sticky;top:0;background:#252525;padding:10px}</style><h1>Area별 공식 스킬 디자인 참조</h1><p>공식 실제 PNG/GIF에서 가져온 자료. 새 OUTPUT이나 아트 승인 결과가 아닙니다. 흰 배경은 원본 표시용 GIF에 포함된 경우가 있습니다.</p>']
for f in sorted(base.glob('AREA_*_IMAGES_INPUT.zip')):
 z=zipfile.ZipFile(f);p=f.stem+'/';maps=json.loads(z.read(p+'reference_resource_design/AREA_REFERENCE_MAP.json'));manifest=list(csv.DictReader(io.StringIO(z.read(p+'AREA_MANIFEST.csv').decode('utf-8-sig'))));byid={r['skill_id']:r for r in manifest}
 parts.append('<h2>'+html.escape(f.stem)+'</h2>')
 for m in maps:
  r=byid[m['skill_id']];b=z.read(p+r['folder']+'/MONSTER_IMAGE.png');parts.append('<article><h3>'+html.escape(r['monster_name']+' / '+r['skill_name'])+'</h3><p>'+html.escape(m['material'])+'</p><div class="row"><img src="data:image/png;base64,'+base64.b64encode(b).decode()+'">')
  for k in m['groups']:
   source=json.loads(z.read(p+'reference_resource_design/'+k+'/SOURCE.json'));elem=next(e for e in source['elements'] if e['rel_path']!='icon');idx=elem['selected_frame_indices'][len(elem['selected_frame_indices'])//2];b=z.read(p+f"reference_resource_design/{k}/frames/{elem['ruid']}_F{idx:03}.png")
   parts.append('<div><img src="data:image/png;base64,'+base64.b64encode(b).decode()+'"><small>'+html.escape(' / '.join(source['names'].get('ko',[])))+' — '+html.escape(elem['rel_path'])+'</small><small>'+html.escape(source['purpose'])+'</small></div>')
  parts.append('</div></article>')
(root/'AREA_DESIGN_REFERENCES.html').write_text('\n'.join(parts),encoding='utf-8');print(root/'AREA_DESIGN_REFERENCES.html')
