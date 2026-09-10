const fs=require("node:fs");
const path=require("node:path");
const {MapBuilder}=require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const {ModelBuilder}=require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");
const root=path.resolve(__dirname,"../..");
const dataDir=path.join(root,"RootDesk/MyDesk/GameData");
const mapDir=path.join(root,"map");
const modelDir=path.join(root,"RootDesk/MyDesk/Models/Monsters");
function fail(message){throw new Error(message);}
function rows(file){const text=fs.readFileSync(path.join(dataDir,file),"utf8").replace(/^\uFEFF/,"").trim();const [head,...lines]=text.split(/\r?\n/);const headers=head.split(",");return lines.filter(Boolean).map(line=>{const values=line.split(",");return Object.fromEntries(headers.map((header,i)=>[header,values[i]||""]));});}

const areaIds=["area_11","area_12","area_13","area_14"];
const tilesets={
  area_11:"tileset://7a070000-0000-4000-8000-000000000007",
  area_12:"tileset://7a080000-0000-4000-8000-000000000008",
  area_13:"tileset://7a090000-0000-4000-8000-000000000009",
  area_14:"tileset://7a100000-0000-4000-8000-000000000010",
};
const expectedMonsters={
  area_11:["m_ratz","m_drumming_bunny","m_bloctopus","m_king_bloctopus","m_rombot"],
  area_12:["m_brown_teddy","m_toy_trojan","m_master_robo","m_chronos","m_timer"],
  area_13:["m_white_sand_rabbit","m_scarf_plead","m_meercat","m_sand_dwarf","m_deo"],
  area_14:["m_cube_slime","m_mithril_mutae","m_homun","m_roid","m_chimera"],
};
const fileByMonster={
  m_ratz:"Ratz",m_drumming_bunny:"DrummingBunny",m_bloctopus:"Bloctopus",m_king_bloctopus:"KingBloctopus",m_rombot:"Rombot",
  m_brown_teddy:"BrownTeddy",m_toy_trojan:"ToyTrojan",m_master_robo:"MasterRobo",m_chronos:"Chronos",m_timer:"Timer",
  m_white_sand_rabbit:"WhiteSandRabbit",m_scarf_plead:"ScarfPlead",m_meercat:"Meercat",m_sand_dwarf:"SandDwarf",m_deo:"Deo",
  m_cube_slime:"CubeSlime",m_mithril_mutae:"MithrilMutae",m_homun:"Homun",m_roid:"Roid",m_chimera:"Chimera",
};
const tileFile={area_11:"RectTileData_Sleepywood.tileset",area_12:"RectTileData_Orbis.tileset",area_13:"RectTileData_ElNath.tileset",area_14:"RectTileData_AquaRoad.tileset"};
const opposite={north:"south",south:"north",east:"west",west:"east"};
const portalName={north:"Portal_N",south:"Portal_S",east:"Portal_E",west:"Portal_W"};
const allAreas=rows("AreaTable.csv"),allRooms=rows("RoomTable.csv"),allMonsters=rows("MonsterTable.csv"),allSkills=rows("SkillTable.csv"),allItems=rows("ItemTable.csv"),landmarks=rows("LandmarkTable.csv");
const roomById=new Map(allRooms.map(row=>[row.id,row])),monsterById=new Map(allMonsters.map(row=>[row.id,row])),skillById=new Map(allSkills.map(row=>[row.id,row]));
const sectorText=fs.readFileSync(path.join(root,"Global/SectorConfig.config"),"utf8");
const sectorMissing=[],summaries=[];

for(let areaIndex=0;areaIndex<areaIds.length;areaIndex++){
  const areaId=areaIds[areaIndex],area=allAreas.find(row=>row.id===areaId);
  if(!area)fail(areaId+": AreaTable 누락");
  if(Number(area.sort_order)!==areaIndex+11)fail(areaId+": sort_order "+area.sort_order);
  const expectedUnlock=(areaIndex+10)*10;
  if(!landmarks.some(row=>Number(row.level)===expectedUnlock&&row.reward_value===areaId))fail(areaId+": Lv"+expectedUnlock+" 랜드마크 누락");
  const tileSet=JSON.parse(fs.readFileSync(path.join(root,"RootDesk/MyDesk",tileFile[areaId]),"utf8"));
  const tileDatas=tileSet.ContentProto.Json.datas;
  if(tileDatas.length<8||tileDatas.slice(4,7).some(d=>d.IsCollidable)||tileDatas[7].IsCollidable!==true)fail(areaId+": 확장 타일 충돌 규격 불일치");

  const areaRooms=allRooms.filter(room=>room.area_id===areaId);
  if(areaRooms.length!==8)fail(areaId+": 방 "+areaRooms.length+"개");
  const actualMonsterIds=[...new Set(areaRooms.map(room=>room.monster_id))].sort();
  const expectedIds=expectedMonsters[areaId].slice().sort();
  if(JSON.stringify(actualMonsterIds)!==JSON.stringify(expectedIds))fail(areaId+": 몬스터 구성 불일치 "+actualMonsterIds);

  const areaSkills=expectedIds.map(monsterId=>{
    const monster=monsterById.get(monsterId);if(!monster)fail(monsterId+": MonsterTable 누락");
    const level=Number(monster.level),hp=Math.round(144+34.2*(level-1)),def=Math.round((80+19*(level-1))*10)/10,exp=Math.round(5*Math.pow(1.10,level-1));
    if(Number(monster.hp)!==hp||Number(monster.def)!==def||Number(monster.exp)!==exp)fail(monsterId+": 공식 수치 불일치");
    const skill=skillById.get(monster.drop_skill_id);if(!skill)fail(monsterId+": 포획 스킬 누락");
    if(!skill.icon_ruid)fail(skill.id+": 아이콘 누락");
    if(skill.skill_kind!=="passive"&&!skill.layer_ruids&&!skill.projectile_ruid)fail(skill.id+": 액티브 연출 누락");
    const drops=allItems.filter(item=>item.drop_from===monsterId);
    if(drops.length!==1)fail(monsterId+": 장비 드랍 "+drops.length+"개");
    if(drops[0].item_type!=="equip"||!drops[0].icon_ruid.startsWith("thumbnail://"))fail(monsterId+": 장비 형식 불일치");
    const model=ModelBuilder.read(path.join(modelDir,fileByMonster[monsterId]+".model"));
    const errors=model.validate().filter(finding=>finding.severity==="error");if(errors.length)fail(monsterId+": 모델 오류 "+JSON.stringify(errors));
    return skill;
  });
  const passives=areaSkills.filter(skill=>skill.skill_kind==="passive").length;
  if(passives!==2||areaSkills.length-passives!==3)fail(areaId+": 액티브/패시브 "+(areaSkills.length-passives)+"/"+passives);

  for(const room of areaRooms){
    const map=MapBuilder.read(path.join(mapDir,room.map_name+".map")),info=map.getMapInfo();
    if(info.TileMapMode!==1||info.tileCount!==448)fail(room.map_name+": mode/tile "+info.TileMapMode+"/"+info.tileCount);
    const tileMap=map.component("RectTileMap","MOD.Core.RectTileMapComponent");
    if(!tileMap||tileMap.TileSetRUID!==tilesets[areaId])fail(room.map_name+": tileset 불일치");
    const maxTileIndex=room.map_name==="map13a"?8:7;
    if(map.getTiles("RectTileMap").some(tile=>tile.tileIndex<4||tile.tileIndex>maxTileIndex))fail(room.map_name+": 확장 타일 인덱스 불일치");
    if(room.map_name==="map13a"&&!map.getTiles("RectTileMap").some(tile=>tile.tileIndex===8))fail("map13a: 오아시스 물 타일 누락");
    if(map.component(room.map_name,"script.NautilusWaterBoundary"))fail(room.map_name+": 노틸러스 전용 물 경계 잔존");
    const names=new Set(map.listEntities().map(entity=>entity.name));
    for(const dir of Object.keys(opposite)){
      const target=room["conn_"+dir];
      if(Boolean(target)!==names.has(portalName[dir]))fail(room.id+": "+dir+" 포탈 불일치");
      if(target&&roomById.has(target)&&roomById.get(target).area_id===areaId&&roomById.get(target)["conn_"+opposite[dir]]!==room.id)fail(room.id+"->"+target+": 역연결 누락");
    }
    if((room.room_type==="boss")!==names.has("Portal_Return"))fail(room.id+": 보스 귀환 포탈 불일치");
    if(!sectorText.includes("\\\"map://"+room.map_name+"\\\""))sectorMissing.push(room.map_name);
  }
  summaries.push({areaId,rooms:areaRooms.length,monsters:actualMonsterIds,active:3,passive:2});
}
console.log(JSON.stringify({summaries,totalRooms:32,totalMonsters:20,totalSkills:20,totalItems:20,tileCountEach:448,reciprocalConnections:true,hazardTilesCollidable:true,sectorMissing},null,2));
if(sectorMissing.length)console.warn("SectorConfig 미기록 맵은 Maker move_map·Play로 실제 등록 여부를 확인해야 합니다.");
