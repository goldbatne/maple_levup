from style_finish_review import *
groups={
'REFERENCE_fabric': [('area_05','m_blue_pig','REFERENCE_VFX',3),('area_13','m_scarf_plead','REFERENCE_VFX',3),('area_15','m_straw_dummy','REFERENCE_VFX',3)],
'REFERENCE_metal': [('area_11','m_ratz','REFERENCE_VFX',3),('area_12','m_master_robo','REFERENCE_VFX',3),('area_07','m_copper_drake','REFERENCE_VFX',3),('area_18','m_plateon','REFERENCE_VFX',3)],
'REFERENCE_liquid': [('area_03','m_bubbling','REFERENCE_VFX',3),('area_05','m_jellyfish','REFERENCE_VFX',3),('area_14','m_cube_slime','REFERENCE_VFX',3)],
'ICON_wood_stone': [('area_02','m_dark_axe_stump','ICON',0),('area_20','m_mutant_stumpy','ICON',0),('area_15','m_wooden_dummy','ICON',0),('area_02','m_stone_golem','ICON',0)],
'ICON_metal': [('area_02','m_iron_hog','ICON',0),('area_12','m_master_robo','ICON',0),('area_18','m_plateon','ICON',0),('area_17','m_memory_guardian','ICON',0)],
'CAST_liquid_smoke': [('area_10','m_squid','CAST_VFX',4),('area_14','m_homun','CAST_VFX',4),('area_01','m_mushroom','CAST_VFX',4)],
'PROJECTILE_light': [('area_08','m_star_pixie','PROJECTILE',2),('area_08','m_lunar_pixie','PROJECTILE',2),('area_14','m_roid','PROJECTILE',2),('area_18','m_mateon','PROJECTILE',2)],
'PROJECTILE_solid': [('area_11','m_king_bloctopus','PROJECTILE',2),('area_15','m_peach_monkey','PROJECTILE',2)],
'CAST_boss_rings': [('area_11','m_rombot','CAST_VFX',6),('area_18','m_zeno','CAST_VFX',6)]}
rows=[]
for name,entries in groups.items():
 pics=[]
 for a,m,role,i in entries:
  r=RM[(a,m)];n=r['role_files'][role][i];pics.append((png(r['output_zip'],n),f'{a} / {m} / F{i:02d}',r['output_zip'],n))
 size=pics[0][0].width;bk,bn=base(entries[0][2],size)
 pics.insert(0,(png(B['zip'],bn),'AREA00 / '+bk,B['zip'],bn))
 # Two to three native cells per row; never shrink assets to fit.
 cols=3;cw=max(size,400);rh=size+75
 im=Image.new('RGBA',(cols*cw,100+((len(pics)+cols-1)//cols)*rh),BG);d=ImageDraw.Draw(im)
 d.text((15,12),name+' / native pixels / 같은 역할·소재 추가 비교',font=FB,fill='white')
 d.text((15,46),'AREA00가 1차 기준. 다른 Area는 소재/역할 차이 해석용이며 새 승인 기준이 아님.',font=F,fill='#bec9da')
 for j,(pic,label,z,n) in enumerate(pics):
  x=(j%cols)*cw;y=100+(j//cols)*rh
  d.multiline_text((x+10,y),label.replace(' / ','\n',1),font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16),fill='white',spacing=1);im.alpha_composite(pic,(x+(cw-pic.width)//2,y+45))
 out=P/'CROSS_AREA_STYLE_BOARD'/('MATERIAL_'+name+'.png');im.convert('RGB').save(out)
 rows.append({'group':name,'board':str(out),'display':'all original pixels 1:1','files':json.dumps([{'zip':z,'member':n} for _,_,z,n in pics],ensure_ascii=False)})
wc('CROSS_AREA_MATERIAL_BOARD_INDEX.csv',rows)
print('material boards',len(rows))
