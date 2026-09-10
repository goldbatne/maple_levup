const fs=require("node:fs"),path=require("node:path");
const {MapBuilder}=require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const {ModelBuilder}=require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");
const root=path.resolve(__dirname,"../.."),dataDir=path.join(root,"RootDesk/MyDesk/GameData"),mapDir=path.join(root,"map"),modelDir=path.join(root,"RootDesk/MyDesk/Models/Monsters");
const fail=m=>{throw new Error(m)};
function rows(file){const [head,...lines]=fs.readFileSync(path.join(dataDir,file),"utf8").replace(/^\uFEFF/,"").trim().split(/\r?\n/),h=head.split(",");return lines.filter(Boolean).map(line=>{const v=line.split(",");return Object.fromEntries(h.map((k,i)=>[k,v[i]||""]));});}
const defs={
 area_15:{order:15,unlock:140,prefix:"15",tileset:"tileset://7a070000-0000-4000-8000-000000000007",tileFile:"RectTileData_Sleepywood.tileset",tileStart:9,monsters:["m_straw_dummy","m_wooden_dummy","m_peach_monkey","m_blue_flower_serpent","m_tae_roon"]},
 area_16:{order:16,unlock:150,prefix:"16",tileset:"tileset://7a080000-0000-4000-8000-000000000008",tileFile:"RectTileData_Orbis.tileset",tileStart:9,monsters:["m_harp","m_blood_harp","m_blue_wyvern","m_dark_wyvern","m_manon"]},
 area_17:{order:17,unlock:160,prefix:"17",tileset:"tileset://7a090000-0000-4000-8000-000000000009",tileFile:"RectTileData_ElNath.tileset",tileStart:9,monsters:["m_memory_monk","m_memory_monk_trainee","m_memory_guardian","m_chief_memory_guardian","m_dodo"]},
 area_18:{order:18,unlock:170,prefix:"18",tileset:"tileset://7a100000-0000-4000-8000-000000000010",tileFile:"RectTileData_AquaRoad.tileset",tileStart:8,monsters:["m_mateon","m_plateon","m_mecateon","m_chief_gray","m_zeno"]},
};
const files={m_straw_dummy:"StrawDummy",m_wooden_dummy:"WoodenDummy",m_peach_monkey:"PeachMonkey",m_blue_flower_serpent:"BlueFlowerSerpent",m_tae_roon:"TaeRoon",m_harp:"Harp",m_blood_harp:"BloodHarp",m_blue_wyvern:"BlueWyvern",m_dark_wyvern:"DarkWyvern",m_manon:"Manon",m_memory_monk:"MemoryMonk",m_memory_monk_trainee:"MemoryMonkTrainee",m_memory_guardian:"MemoryGuardian",m_chief_memory_guardian:"ChiefMemoryGuardian",m_dodo:"Dodo",m_mateon:"Mateon",m_plateon:"Plateon",m_mecateon:"Mecateon",m_chief_gray:"ChiefGray",m_zeno:"Zeno"};
const areas=rows("AreaTable.csv"),rooms=rows("RoomTable.csv"),monsters=rows("MonsterTable.csv"),skills=rows("SkillTable.csv"),items=rows("ItemTable.csv"),landmarks=rows("LandmarkTable.csv");
const roomBy=new Map(rooms.map(r=>[r.id,r])),monsterBy=new Map(monsters.map(r=>[r.id,r])),skillBy=new Map(skills.map(r=>[r.id,r]));
const opposite={north:"south",south:"north",east:"west",west:"east"},portal={north:"Portal_N",south:"Portal_S",east:"Portal_E",west:"Portal_W"},sector=fs.readFileSync(path.join(root,"Global/SectorConfig.config"),"utf8"),sectorMissing=[],summaries=[];
for(const [areaId,d] of Object.entries(defs)){
 const area=areas.find(r=>r.id===areaId);if(!area||Number(area.sort_order)!==d.order)fail(areaId+": AreaTable/order 누락");
 if(!landmarks.some(r=>Number(r.level)===d.unlock&&r.reward_value===areaId))fail(areaId+": Lv"+d.unlock+" 랜드마크 누락");
 const datas=JSON.parse(fs.readFileSync(path.join(root,"RootDesk/MyDesk",d.tileFile),"utf8")).ContentProto.Json.datas;
 if(datas.slice(d.tileStart,d.tileStart+3).some(t=>t.IsCollidable)||datas[d.tileStart+3]?.IsCollidable!==true)fail(areaId+": 타일 충돌 규격 불일치");
 const ar=rooms.filter(r=>r.area_id===areaId);if(ar.length!==8)fail(areaId+": 방 "+ar.length+"개");
 const actual=[...new Set(ar.map(r=>r.monster_id))].sort(),expected=d.monsters.slice().sort();if(JSON.stringify(actual)!==JSON.stringify(expected))fail(areaId+": 몬스터 구성 불일치");
 const areaSkills=[];
 for(const id of expected){const m=monsterBy.get(id);if(!m)fail(id+": MonsterTable 누락");const lv=Number(m.level),hp=Math.round(144+34.2*(lv-1)),def=Math.round((80+19*(lv-1))*10)/10,exp=Math.round(5*Math.pow(1.10,lv-1));if(Number(m.hp)!==hp||Number(m.def)!==def||Number(m.exp)!==exp)fail(id+": 성장식 불일치");const s=skillBy.get(m.drop_skill_id);if(!s||!s.icon_ruid)fail(id+": 포획 스킬/아이콘 누락");if(s.skill_kind!=="passive"&&!s.layer_ruids&&!s.projectile_ruid)fail(s.id+": 액티브 연출 누락");areaSkills.push(s);const drop=items.filter(i=>i.drop_from===id);if(drop.length!==1||drop[0].item_type!=="equip"||!drop[0].icon_ruid.startsWith("thumbnail://")||!drop[0].avatar_category)fail(id+": 장비 드랍 형식 불일치");const model=ModelBuilder.read(path.join(modelDir,files[id]+".model")),errors=model.validate().filter(x=>x.severity==="error");if(errors.length)fail(id+": 모델 오류 "+JSON.stringify(errors));}
 const passives=areaSkills.filter(s=>s.skill_kind==="passive").length;if(passives!==2||areaSkills.length-passives!==3)fail(areaId+": 액티브/패시브 구성 불일치");
 for(const r of ar){const map=MapBuilder.read(path.join(mapDir,r.map_name+".map")),info=map.getMapInfo();if(info.TileMapMode!==1||info.tileCount!==448)fail(r.map_name+": mode/tile "+info.TileMapMode+"/"+info.tileCount);const tm=map.component("RectTileMap","MOD.Core.RectTileMapComponent");if(!tm||tm.TileSetRUID!==d.tileset)fail(r.map_name+": tileset 불일치");if(map.getTiles("RectTileMap").some(t=>t.tileIndex<d.tileStart||t.tileIndex>d.tileStart+3))fail(r.map_name+": 타일 인덱스 범위 불일치");const names=new Set(map.listEntities().map(e=>e.name));for(const dir of Object.keys(opposite)){const target=r["conn_"+dir];if(Boolean(target)!==names.has(portal[dir]))fail(r.id+": "+dir+" 포탈 불일치");if(target&&roomBy.has(target)&&roomBy.get(target).area_id===areaId&&roomBy.get(target)["conn_"+opposite[dir]]!==r.id)fail(r.id+"->"+target+": 역연결 누락");}if((r.room_type==="boss")!==names.has("Portal_Return"))fail(r.id+": 보스 귀환 포탈 불일치");if(!sector.includes('"map://'+r.map_name+'"'))sectorMissing.push(r.map_name);}
 summaries.push({areaId,rooms:8,monsters:5,active:3,passive:2,tileRange:[d.tileStart,d.tileStart+3]});
}
const bossIds=["m_tae_roon","m_manon","m_dodo","m_zeno"];
for(const id of bossIds){const drop=items.find(i=>i.drop_from===id);if(!drop||Number(drop.drop_rate)!==.02)fail(id+": 보스 장비 드랍 규격 불일치");}
console.log(JSON.stringify({summaries,totalRooms:32,totalMonsters:20,totalSkills:20,totalItems:20,tileCountEach:448,reciprocalConnections:true,hazardTilesCollidable:true,bossEquipmentRows:4,sectorMissing},null,2));
if(sectorMissing.length)console.warn("SectorConfig 미기록 맵은 Maker refresh 후 move_map·Play로 실제 등록 여부를 확인해야 합니다.");
