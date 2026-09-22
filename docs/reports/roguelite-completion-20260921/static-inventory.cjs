// Read-only census. Emits JSON; caller stores results via apply_patch.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..');
const project=root;
const {MapBuilder}=require(path.join(project,'.agents/skills/msw-general/scripts/map/msw_map_builder.cjs'));
function csv(name){const s=fs.readFileSync(path.join(project,'RootDesk/MyDesk/GameData',name+'.csv'),'utf8').replace(/^\uFEFF/,'');
 const rows=[];let row=[],v='',q=false;for(let i=0;i<s.length;i++){const c=s[i];if(c==='"'){if(q&&s[i+1]==='"'){v+='"';i++;}else q=!q;}else if(c===','&&!q){row.push(v);v='';}else if(c==='\n'&&!q){row.push(v.replace(/\r$/,''));rows.push(row);row=[];v='';}else v+=c;}if(v||row.length){row.push(v.replace(/\r$/,''));rows.push(row);}const h=rows.shift();return rows.filter(r=>r.some(Boolean)).map(r=>Object.fromEntries(h.map((k,i)=>[k,r[i]||''])));}
const rooms=csv('RoomTable'),areas=csv('AreaTable'),skills=csv('SkillTable'),monsters=csv('MonsterTable');
const maps=fs.readdirSync(path.join(project,'map')).filter(f=>f.endsWith('.map')).map(file=>{
 const name=file.slice(0,-4),m=MapBuilder.read(path.join(project,'map',file)); const rs=rooms.filter(r=>r.map_name===name);
 const assigned=rs.filter(r=>r.area_id&&r.room_type!=='town'&&!(r.room_id||r.id).startsWith('r_job_'));
 const category=name==='maptown'?'Town':assigned.some(r=>r.room_type==='boss')?'Special Encounter':assigned.length?'Room/Chunk Source':'Reference Only';
 return {map:name,category,eligibleRunPool:assigned.length>0,areaIds:[...new Set(assigned.map(r=>r.area_id))],roomIds:rs.map(r=>r.room_id||r.id),...m.getMapInfo(),usage:m.build().Usage,bounds:m.getTileBounds(),portals:m.listEntities().filter(e=>e.componentNames.includes('script.RoomPortal')).map(e=>({name:e.name,direction:m.component(e.name,'script.RoomPortal').direction,position:m.component(e.name,'MOD.Core.TransformComponent').Position})),runtime:'SEE_AREA_RUNTIME_EVIDENCE'};
});
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(project,file))).digest('hex');
console.log(JSON.stringify({note:'Pool membership is not proof every map/seed has been played. Trial/reference assets preserved.',maps,areas:areas.map(a=>({area:a.area_id||a.id,name:a.name,maps:maps.filter(m=>m.areaIds.includes(a.area_id||a.id)).map(m=>m.map)})),skillDefinitions:skills.length,monsterDefinitions:monsters.length,hashes:{SkillTable:hash('RootDesk/MyDesk/GameData/SkillTable.csv'),MonsterTable:hash('RootDesk/MyDesk/GameData/MonsterTable.csv')}},null,2));
