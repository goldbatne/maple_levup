// T52 — 헤네시스의 일반 몬스터 스톤골렘을 공식 필드 보스 머쉬맘으로 교체한다.
// .model은 원문 편집하지 않고 ModelBuilder로만 만든다.

const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const {
  ModelBuilder,
  actionSheet,
  vector2,
} = require(path.join(ROOT, '.agents/skills/msw-general/scripts/model/msw_model_builder.cjs'));

const source = path.join(ROOT, 'RootDesk/MyDesk/Models/Monsters/Mushroom.model');
const output = path.join(ROOT, 'RootDesk/MyDesk/Models/Monsters/Mushmom.model');

const clips = {
  stand: '86015373d23b4b05bb8fcc6086354652',
  move: 'c745828d831b42739b9a58c07f334864',
  attack: '90c5456e2a8a45478df02500797a9afd',
  hit: '90fee9416184420a9796a679751d1ec5',
  die: 'ec90f0b64a814c4980de89f496d360ec',
  jump: '5ecbcc4002a5491aafd7e1d3191c6ddc',
};

const b = ModelBuilder.read(source)
  .renameModel('Mushmom', 'mushmom')
  .value('StateAnimationComponent', 'ActionSheet', actionSheet(clips))
  .value('SpriteRendererComponent', 'SpriteRUID', clips.stand, 'string')
  // 공식 stand 프레임은 120×112px. 몸 전체보다 조금 안쪽으로 잡아
  // 갓 끝만 스쳤을 때 맞는 판정을 피한다(1 world unit = 100px).
  .value('HitComponent', 'BoxSize', vector2(1.1, 1.05))
  .value('HitComponent', 'ColliderOffset', vector2(0, 0.525))
  .value('MovementComponent', 'InputSpeed', 1.2, 'float')
  .value('script.RoomMonster', 'MonsterId', 'm_mushmom', 'string');

b.write(output, { ensure_sprite_ruid: false });

const findings = b.validate();
const errors = findings.filter((x) => x.severity === 'error');
if (errors.length) {
  console.error(errors);
  process.exit(1);
}
console.log('[T52] Mushmom.model 생성 및 검증 완료');
