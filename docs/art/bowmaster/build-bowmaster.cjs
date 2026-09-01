// T57 — 엘리니아 보우마스터 히든 보스 모델·NPC·귀환 포탈·시험 맵을 Builder로 생성한다.
// .model/.map 원문은 직접 편집하지 않는다.

const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { ModelBuilder } = require(path.join(
  ROOT, '.agents/skills/msw-general/scripts/model/msw_model_builder.cjs'));
const { MapBuilder } = require(path.join(
  ROOT, '.agents/skills/msw-general/scripts/map/msw_map_builder.cjs'));

const heroModel = path.join(ROOT, 'RootDesk/MyDesk/Models/Monsters/Hero.model');
const heroNpcModel = path.join(ROOT, 'RootDesk/MyDesk/Models/Npc/HeroNpc.model');
const returnPortalModel = path.join(ROOT, 'RootDesk/MyDesk/Models/Terrain/ReturnPortal.model');

const bowmasterModel = path.join(ROOT, 'RootDesk/MyDesk/Models/Monsters/Bowmaster.model');
const bowmasterNpcModel = path.join(ROOT, 'RootDesk/MyDesk/Models/Npc/BowmasterNpc.model');
const bowmasterReturnModel = path.join(
  ROOT, 'RootDesk/MyDesk/Models/Terrain/BowmasterReturnPortal.model');

const costume = {
  cap: '4f0d07c4571244f9b9a8c3f6c392265f',       // 레드 헌터
  longcoat: '9fa81ab0a0d248fbb307675e4b79d033', // 레드 아르미스
  shoes: '186a55d192d24b4da5201801422bebf7',    // 히어로와 같은 기본 신발
  hair: '36456c66cf214497a4eadca005063289',     // 얼굴을 가리지 않는 기본 머리
  bow: '3da6e65b218d41178c839b03306da803',      // 레드 힌켈
};

function dressArcher(builder) {
  return builder
    .removeValue('MOD.Core.CostumeManagerComponent', 'CustomOneHandedWeaponEquip')
    .value('MOD.Core.CostumeManagerComponent', 'CustomCapEquip', costume.cap, 'string')
    .value('MOD.Core.CostumeManagerComponent', 'CustomLongcoatEquip', costume.longcoat, 'string')
    .value('MOD.Core.CostumeManagerComponent', 'CustomShoesEquip', costume.shoes, 'string')
    .value('MOD.Core.CostumeManagerComponent', 'CustomHairEquip', costume.hair, 'string')
    .value('MOD.Core.CostumeManagerComponent', 'CustomTwoHandedWeaponEquip', costume.bow, 'string');
}

const boss = dressArcher(ModelBuilder.read(heroModel)
  .renameModel('Bowmaster', 'bowmaster'))
  .value('script.RoomMonster', 'MonsterId', 'm_adv_bowmaster', 'string')
  .value('script.MonsterAttack', 'AvatarAttackAction', 'shoot1', 'string')
  .value('script.MonsterAttack', 'AvatarAttackPlayRate', 1.55, 'float');
boss.write(bowmasterModel, { ensure_sprite_ruid: false });

const npc = dressArcher(ModelBuilder.read(heroNpcModel)
  .renameModel('BowmasterNpc', 'bowmasternpc'))
  .value('script.HeroNpc', 'TargetRoomId', 'r_job_02', 'string')
  .value('script.HeroNpc', 'ChallengerMonsterId', 'm_adv_bowmaster', 'string');
npc.write(bowmasterNpcModel, { ensure_sprite_ruid: false });

const returnPortal = ModelBuilder.read(returnPortalModel)
  .renameModel('BowmasterReturnPortal', 'bowmasterreturnportal')
  .value('script.ReturnPortal', 'TargetRoomId', 'r_29', 'string')
  .value('MOD.Core.TriggerComponent', 'IsLegacy', false, 'boolean');
returnPortal.write(bowmasterReturnModel, { ensure_sprite_ruid: false });

for (const [name, builder] of [['boss', boss], ['npc', npc], ['return', returnPortal]]) {
  const errors = builder.validate().filter((x) => x.severity === 'error');
  if (errors.length) {
    console.error(`[T57] ${name} model validation failed`, errors);
    process.exit(1);
  }
}

const arena = MapBuilder.fromTemplate(path.join(ROOT, 'map/mapjob.map'), 'mapjob02');
arena.remove('/maps/mapjob02/Portal_Return');
arena.placeModel('Portal_Return', bowmasterReturnModel, { pos: [7, 1, 0] });
arena.write(path.join(ROOT, 'map/mapjob02.map'));

const ellinia = MapBuilder.read(path.join(ROOT, 'map/map29.map'));
ellinia.placeModel('BowmasterNpc', bowmasterNpcModel, { pos: [8, 3, 0] });
ellinia.write(path.join(ROOT, 'map/map29.map'));

console.log('[T57] Bowmaster/BowmasterNpc/BowmasterReturnPortal.model 생성 완료');
console.log('[T57] mapjob02 생성 + map29 NPC 배치 완료');
console.log('[T57] mapjob02 entities=' + arena.listEntities().length
  + ' / map29 entities=' + ellinia.listEntities().length);
