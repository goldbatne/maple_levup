from produce import *
s=json.loads(S.read_text(encoding='utf-8'));jobs=[]
style=str(R.parents[1]/'area00_refinement/20260912_203404/AREA_00_IMAGES_INPUT_IMAGES_OUTPUT/monsters/004_m_mano_마노/ICON/004_m_mano_s_mon_mano_ICON.png')
for a,area in s['areas'].items():
 for r in area['roles']:
  if r['required']!='true' or r['production_decision']!='NEW_ART' or a=='AREA_01':continue
  md=next((R/'provenance'/f'{a}_INPUT'/'monsters').glob(r['work_order']+'_'+r['monster_id']+'_*'));spec=(md/'GENERATION_SPEC.md').read_text(encoding='utf-8-sig')
  visual=spec.split('## 시각 번역')[1].split('## 해석 주의')[0].split('## 출력 프로필')[0]
  n=int(r['frame_count']);cols,rows=({1:(1,1),4:(2,2),6:(3,2),8:(4,2),12:(4,3)})[n]
  layout='One single skill ICON, no animation. Distill specified icon motif into strong64px readable silhouette.' if n==1 else f'Animation source sheet EXACTLY {n} frames, {cols} columns x {rows} rows, row-major fixed equal square cells. All stages distinct, same fixed pivot at cell center(0.5,0.5), no auto-recenter or whole-cell translations. Each source cell target512px; this is dedicated animation source, no overview labels.'
  temporal=''
  if r['effect_role']=='REFERENCE_VFX':temporal='PASSIVE REFERENCE ONLY: identical stable material silhouette with a very short gentle glint/breathing cycle, no attack preparation, impact flash, explosion or projectile. runtime_use=false.'
  elif r['effect_role']=='PROJECTILE':temporal='DIRECTION NEUTRAL projectile. FOUR frames F00condensed F01glow rises F02peak F03settles. Stay anchored exact same local position, NO flight across sheet/cell, no whole-sprite rotation. Engine alone moves and Z-rotates. 4x0.08sec nonloop.'
  elif n>1:temporal='One-shot animation, first2frames prepare/appear, next2form and peak, subsequent dissolve and lastframe few faint residue only. For buff instead close protection and fade without attack. Integrate specified layer timing in one canvas. No duplicate runtime movement.'
  prompt=f'Use case stylized-concept. NEW production skill art {r["monster_id"]} / {r["skill_id"]} / {r["effect_role"]}. Image1 actual MONSTER_IMAGE is reference ONLY; never draw its face/body/full creature. Image2 actual AREA00 candidate is FINISHING reference only: colored clean contour, readable shaped shadows, rich midtones, selective broad highlights and softly fading edge glow. Preserve current skill material and palette, NOT its shell/pearl/rainbow/ribbon shape.\n{layout}\n{temporal}\nAuthoritative role visual specification:\n{visual}\nFinish carefully hand-painted/cartoon game art, material-specific highlights, modest gradients, no photographic texture. Main motif inside central65% of each square, particles inside75% with huge clear margins. Only3-7 distinct fragments, avoid confetti. No ground scene, characters, labels, text, grids, dividing lines, frame, watermark. BACKGROUND uniform pure BLACK #000000 everywhere outside artwork, never checkerboard or white background or fake transparency. Maintain dark material contours colored above black. Output source {cols*512}x{rows*512}.'
  jobs.append({'area':a,'monster':r['monster_id'],'role':r['effect_role'],'cols':cols,'rows':rows,'prompt':prompt,'refs':[str(md/'MONSTER_IMAGE.png'),style]})
(R/'work/JOBS.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8');print(len(jobs))
