const fs = require("node:fs");
const path = require("node:path");

const { MapBuilder } = require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const { ModelBuilder, vector2 } = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const root = path.resolve(__dirname, "../..");
const dataDir = path.join(root, "RootDesk/MyDesk/GameData");
const modelDir = path.join(root, "RootDesk/MyDesk/Models/Monsters");
const mapDir = path.join(root, "map");

const areas = [
  {
    id: "area_07", name: "슬리피우드", entry: "r_071", order: 7, unlock: 60,
    tileset: "tileset://7a070000-0000-4000-8000-000000000007",
    prefix: "07", priorBossRoom: "r_055", priorBossSkill: "s_mon_king_clang", statGate: 315,
    note: "지역 20칸의 일곱 번째 (Lv61~70). 늪과 개미굴을 지나 주니어 발록의 금지된 제단에 닿는다",
    rooms: [
      ["1", "슬리피우드 늪 입구", "m_zombie_mushroom", 4, 61],
      ["2", "축축한 개미굴", "m_copper_drake", 4, 63],
      ["3", "깊은 드레이크 동굴", "m_drake", 5, 65],
      ["a", "잊힌 신전의 샛길", "m_wild_kargo", 4, 69],
      ["4", "황소 수문장의 회랑", "m_tauromacis", 5, 68],
      ["5", "주니어 발록의 제단", "m_jr_balrog", 1, 70],
      ["6", "독안개 버섯굴", "m_zombie_mushroom", 5, 62],
      ["7", "용암빛 지하 통로", "m_drake", 5, 64],
    ],
  },
  {
    id: "area_08", name: "오르비스", entry: "r_081", order: 8, unlock: 70,
    tileset: "tileset://7a080000-0000-4000-8000-000000000008",
    prefix: "08", priorBossRoom: "r_075", priorBossSkill: "s_mon_jr_balrog", statGate: 365,
    note: "지역 20칸의 여덟 번째 (Lv71~80). 구름공원과 별빛길을 지나 엘리쟈의 정원에 닿는다",
    rooms: [
      ["1", "오르비스 구름공원", "m_star_pixie", 4, 71],
      ["2", "붉은 뿔의 구름길", "m_jr_cellion", 4, 73],
      ["3", "달빛 픽시 정원", "m_lunar_pixie", 5, 75],
      ["a", "숨은 별빛 전망대", "m_luster_pixie", 4, 79],
      ["4", "찬란한 구름 회랑", "m_luster_pixie", 5, 78],
      ["5", "엘리쟈의 어두운 정원", "m_eliza", 1, 80],
      ["6", "작은 별의 산책로", "m_star_pixie", 5, 72],
      ["7", "고요한 월광 구름", "m_lunar_pixie", 5, 74],
    ],
  },
  {
    id: "area_09", name: "엘나스 산맥", entry: "r_091", order: 9, unlock: 80,
    tileset: "tileset://7a090000-0000-4000-8000-000000000009",
    prefix: "09", priorBossRoom: "r_085", priorBossSkill: "s_mon_eliza", statGate: 415,
    note: "지역 20칸의 아홉 번째 (Lv81~90). 설원과 빙벽을 넘어 추방된 설산의 마녀를 상대한다",
    rooms: [
      ["1", "엘나스 눈바람 언덕", "m_jr_yeti", 4, 81],
      ["2", "검은 눈송이 길", "m_dark_jr_yeti", 4, 83],
      ["3", "헥터의 설원", "m_hector", 5, 85],
      ["a", "얼어붙은 사냥꾼 길", "m_white_fang", 4, 89],
      ["4", "화이트팽 빙벽", "m_white_fang", 5, 88],
      ["5", "마녀의 추방지", "m_snow_witch", 1, 90],
      ["6", "어린 예티 골짜기", "m_jr_yeti", 5, 82],
      ["7", "늑대 발자국 협곡", "m_hector", 5, 84],
    ],
  },
  {
    id: "area_10", name: "아쿠아로드", entry: "r_101", order: 10, unlock: 90,
    tileset: "tileset://7a100000-0000-4000-8000-000000000010",
    prefix: "10", priorBossRoom: "r_095", priorBossSkill: "s_mon_snow_witch", statGate: 465,
    note: "지역 20칸의 열 번째 (Lv91~100). 밝은 연안에서 심해로 내려가 피아누스의 동굴에 닿는다",
    rooms: [
      ["1", "아쿠아로드 연안", "m_bubble_fish", 4, 91],
      ["2", "가면 산호초", "m_mask_fish", 4, 93],
      ["3", "스퀴드 먹물 해역", "m_squid", 5, 95],
      ["a", "침몰 유적의 샛길", "m_shark", 4, 99],
      ["4", "위험한 심해", "m_shark", 5, 98],
      ["5", "피아누스의 깊은 동굴", "m_pianus", 1, 100],
      ["6", "방울물고기 산호밭", "m_bubble_fish", 5, 92],
      ["7", "검푸른 해저 협곡", "m_squid", 5, 94],
    ],
  },
];

const monsters = [
  { id:"m_zombie_mushroom", name:"좀비버섯", level:61, skill:"s_mon_zombie_mushroom", model:"zombiemushroom", file:"ZombieMushroom", template:"Mushroom", actions:{stand:"3ee3fc0f4d2e443cbb9ec424dd2c012f",move:"c23b523cd2c14558bf5812999db8690f",hit:"e47274fe9ecd47989d9a9480ee04def4",die:"0be38336b56b477993d5809b1a6ca977"}, speed:1.2, box:[0.64,0.58], offset:[0,0.29] },
  { id:"m_copper_drake", name:"카파 드레이크", level:63, skill:"s_mon_copper_drake", model:"copperdrake", file:"CopperDrake", template:"WildBoar", actions:{stand:"da160cd4b78c479ab8dfaa225b2dcd47",move:"dc5a939bc6c14988837a63c86fb701f0",hit:"55b079678de0448288e48692fa1880f7",die:"0c05fd44e1fd4da4a8494830028ceff9"}, speed:1.25, box:[0.88,0.72], offset:[0,0.36] },
  { id:"m_drake", name:"드레이크", level:65, skill:"s_mon_drake", model:"drake", file:"Drake", template:"WildBoar", actions:{stand:"f8cfac4e30394735861603f6bfcb1932",move:"c1c6069005ef4fb3bf104eea7a52df3d",hit:"364f3fe34c3147aebd6a0b3fe50e9f63",die:"2964ac3bd9904c67830f67176cc7234e"}, speed:1.3, box:[0.92,0.82], offset:[0,0.41] },
  { id:"m_wild_kargo", name:"와일드카고", level:68, skill:"s_mon_wild_kargo", model:"wildkargo", file:"WildKargo", template:"WildBoar", actions:{stand:"7d1c1d17eff44687b35ca0d5108084dc",move:"18bc35666910441f98a80bd4a24010c8",jump:"4925464495b44873a6740cb7d9ac582c",hit:"15428c5f3212470580a0852002afb646",die:"a62cfa427587410181aff9331e5e5b15"}, speed:1.55, box:[0.92,0.7], offset:[0,0.35] },
  { id:"m_tauromacis", name:"타우로마시스", level:70, skill:"s_mon_tauromacis", model:"tauromacis", file:"Tauromacis", template:"JrBalrog", actions:{stand:"5ef751fd743e41609bf98e03de4df51c",move:"c62af154ef414ebaa329a68d79b5cc37",attack:"a81c0e470e3b40b19fe7ef15f878c80a",hit:"ae9cdda9f26c4ccba9fdb28709e90ec3",die:"00bb89f4a87a4cafb52268392817afbf"}, speed:1.05, box:[1.35,1.55], offset:[0,0.78] },

  { id:"m_star_pixie", name:"스타픽시", level:71, skill:"s_mon_star_pixie", model:"starpixie", file:"StarPixie", template:"Fairy", actions:{stand:"ca136923b7e84267af993bdbabada385",move:"a25f27e01d7446c6910550d595ef08b6",jump:"6128b714a94c431a88ef0a06d5c40644",attack:"0c9e55cecc774a4290c10590358b9b4d",hit:"f0f493b1149e4b6a863890a82d82fca6",die:"8bff7824fb974b69b02d576b7c6ed257"}, speed:1.35, box:[0.55,0.62], offset:[0,0.31] },
  { id:"m_jr_cellion", name:"주니어 샐리온", level:73, skill:"s_mon_jr_cellion", model:"jrcellion", file:"JrCellion", template:"BluePig", actions:{stand:"016bc9a459104e2a8a2fea03d7130519",move:"966306ea1fca44fe861a2b6e7043e15d",jump:"2809d8483b664d9cb5fc20cc1a18eb53",hit:"f3261f7cba9247c48f6c751d600ee21c",die:"ac0cca74a98e4f9a818ebc69759bc75d"}, speed:1.4, box:[0.72,0.62], offset:[0,0.31] },
  { id:"m_lunar_pixie", name:"루나픽시", level:75, skill:"s_mon_lunar_pixie", model:"lunarpixie", file:"LunarPixie", template:"Fairy", actions:{stand:"ff4a57bc3d4a4488b0053c33f4c3369f",move:"6c09e340af2f4ca697463ef36a95f523",jump:"494c4c4625c74d0b85d6055aac15e11a",attack:"a6556d61dbef4153ab4815d8d63c5768",hit:"187b73445d4645d68750ed12f924203a",die:"64990174c8d2411a82a12a9569abf085"}, speed:1.4, box:[0.6,0.68], offset:[0,0.34] },
  { id:"m_luster_pixie", name:"러스터픽시", level:78, skill:"s_mon_luster_pixie", model:"lusterpixie", file:"LusterPixie", template:"Fairy", actions:{stand:"35f555b27d3a4d438224a29e73fac305",move:"7230c88964604573b9b687a919855b00",jump:"f8a572a977894c69911d5749371e2ba1",attack:"d8d759053a5f4e338ccd47be39802179",hit:"dc25c90c27904ce8b20ae1ada438bf9a",die:"1b0641033e0b4d90bdadd2cdf1fb70e3"}, speed:1.45, box:[0.64,0.7], offset:[0,0.35] },
  { id:"m_eliza", name:"엘리쟈", level:80, skill:"s_mon_eliza", model:"eliza", file:"Eliza", template:"Mushmom", actions:{stand:"d458879e2e2949f2bb2e915ff67fbc64",move:"e4e1fb8384994d8890b786f7b9df93a3",jump:"d72a977e76a04ffcbab240d8cfb39da7",attack:"8c933520034f4a3a8fb4163495ab714e",hit:"5ee4cd91882446e99905bea46f26e8e6",die:"1ebdf7b4f5b64af3a385a18551a410fe"}, speed:1.2, box:[1.45,1.28], offset:[0,0.64] },

  { id:"m_jr_yeti", name:"주니어 예티", level:81, skill:"s_mon_jr_yeti", model:"jryeti", file:"JrYeti", template:"BluePig", actions:{stand:"1975dd704eec461ab49bdeb0c11c54d9",move:"842a6865f7074f94ac4a190ed90e2e21",jump:"f59ed8ac1cfa4aec918331209a15dc1b",hit:"63a1a5f280f04e55b935d6a2155edcef",die:"13b9f2b2f7664cc5a08e663f2fe0502b"}, speed:1.25, box:[0.72,0.78], offset:[0,0.39] },
  { id:"m_dark_jr_yeti", name:"다크 주니어 예티", level:83, skill:"s_mon_dark_jr_yeti", model:"darkjryeti", file:"DarkJrYeti", template:"BluePig", actions:{stand:"ce56cf9613174f80976dab5b61f7b604",move:"8d2b8951794d406a86cc580e9eeff18d",jump:"44a5db43346e4bd0904005a73525a756",hit:"cbe070cdf1fa4611a3529f3d70296a33",die:"fad50a0e478c40fcbd383e069bc278da"}, speed:1.3, box:[0.74,0.8], offset:[0,0.4] },
  { id:"m_hector", name:"헥터", level:85, skill:"s_mon_hector", model:"hector", file:"Hector", template:"WildBoar", actions:{stand:"7dcc64a4725b4777b8f86a5404b4d4cc",move:"5e3fe57af79849ec9fd521dbd498f70d",jump:"7e5783e93a96463184f8a7acfa246523",attack:"ab421fbae9c942219123b08228fbfca3",hit:"17e6ef4f715547bc9565c4a75b7dc340",die:"e827e51a595e4d888e8982ded639e769"}, speed:1.55, box:[0.9,0.66], offset:[0,0.33] },
  { id:"m_white_fang", name:"화이트팽", level:88, skill:"s_mon_white_fang", model:"whitefang", file:"WhiteFang", template:"WildBoar", actions:{stand:"aaa3b506804d4418b025da47dbb65b3f",move:"a669487dc36d43df99ecef932ccf6f00",jump:"e1890c8e5b8d446eb9b18b7a0380f6ac",attack:"e7d12e44869040ed8d6cd4c25c41d543",hit:"8e3cd0c02fca425388e6f9cc909f12f9",die:"ec707ca9121f4e4cb536c37a29084760"}, speed:1.65, box:[0.94,0.7], offset:[0,0.35] },
  { id:"m_snow_witch", name:"설산의 마녀", level:90, skill:"s_mon_snow_witch", model:"snowwitch", file:"SnowWitch", template:"Faust", actions:{stand:"4b50438f59154f41aba918b2d28bb8d2",move:"8816e805196a4f09aca79f27de12ade8",attack:"bdd2cc8707254cbeac714bbc260b367e",hit:"79d70b581e22411abbd0f142c038b7ad",die:"ba9ce08382224dd9ad9e3a97428d4cdd"}, speed:1.2, box:[1.25,1.45], offset:[0,0.72] },

  { id:"m_bubble_fish", name:"버블피쉬", level:91, skill:"s_mon_bubble_fish", model:"bubblefish", file:"BubbleFish", template:"Starfish", actions:{stand:"c968133e75534a1b933d28da29c4e584",move:"20946ff7a9ed48bb8a92a69d035a0133",jump:"669b0c89c6d84658b9b2e0a34a43a514",hit:"57f09ef245f845f5bd24110a0f548ba9",die:"1a9b8846c9084c908adcc1acf2ee6190"}, speed:1.25, box:[0.58,0.5], offset:[0,0.25] },
  { id:"m_mask_fish", name:"마스크피쉬", level:93, skill:"s_mon_mask_fish", model:"maskfish", file:"MaskFish", template:"Starfish", actions:{stand:"fb9037f43fcd442a971ee007b9f7cc26",move:"49a2600dc1af49e495508a8dc9387168",jump:"a9ec92bb1ee94e08bc8a804f410caffa",hit:"506ea5470ea841749e43ab017602edc8",die:"ef7d716b68ab44548c69c842ab41908f"}, speed:1.35, box:[0.62,0.56], offset:[0,0.28] },
  { id:"m_squid", name:"스퀴드", level:95, skill:"s_mon_squid", model:"squid", file:"Squid", template:"Jellyfish", actions:{stand:"013b3e6ba18249269e4a1b85c536a0d9",move:"6adccbc2b8f64db8a62022711bcf8747",jump:"4ea2f3d7923a497aaa16a8991f15ee69",attack:"1087756cca494034abe6226cd33562b2",hit:"33b17dffdf08474fa36578f78b1f9303",die:"38939a433f3140d380dbd9f5bd601759"}, speed:1.25, box:[0.9,0.9], offset:[0,0.45] },
  { id:"m_shark", name:"샤크", level:98, skill:"s_mon_shark", model:"shark", file:"Shark", template:"WildBoar", actions:{stand:"b95f05df46124b3485d0a15bb79b10fb",move:"5c1f92f9c3b4410fb5b14abdaed83820",jump:"a92b48ab44934b9d8fd6ac83459e27d7",attack:"b36a9430477a46b5a722f31164baaae4",hit:"636f8875664c4ceb9f74e4e5924b5ae5",die:"bd1345f5ec4548c58e291b78f93c8ef4"}, speed:1.7, box:[1.2,0.72], offset:[0,0.36] },
  { id:"m_pianus", name:"피아누스", level:100, skill:"s_mon_pianus", model:"pianus", file:"Pianus", template:"JrBalrog", actions:{stand:"207c5d6dcee243ad9a141397244ba9a9",move:"207c5d6dcee243ad9a141397244ba9a9",attack:"e76534125d994b9c8a1f3bb520c4533f",hit:"09dd05ae2710401fb33adce7e376a16e",die:"d63b783f0ba847fda76f340ccb8995ea"}, speed:0.7, box:[2.2,1.65], offset:[0,0.82] },
];

const skills = [
  {id:"s_mon_zombie_mushroom",name:"죽은 포자의 끈기",stat:"INT",kind:"passive",icon:"thumbnail://3ee3fc0f4d2e443cbb9ec424dd2c012f",desc:"죽어서도 움직이는 버섯의 포자 생명력을 익혀 보유 수만큼 INT를 높인다"},
  {id:"s_mon_copper_drake",name:"청동 비늘",stat:"STR",kind:"passive",icon:"thumbnail://da160cd4b78c479ab8dfaa225b2dcd47",desc:"습한 동굴에서도 단단함을 잃지 않는 비늘을 익혀 보유 수만큼 STR을 높인다"},
  {id:"s_mon_drake",name:"동굴 용염",stat:"INT",coef:2.45,target:"area",max:3,range:4.6,cool:6,icon:"thumbnail://f8cfac4e30394735861603f6bfcb1932",layers:"5638984319fd476ca3d89e2aaca7f32a|a610b14bbc55477cbc78777a5a2e7ed1",delays:"0|0.12",durations:"0.65|0.78",scales:"0.8|0.95",desc:"드레이크가 품은 동굴의 열기를 전방에 터뜨려 가까운 적 셋을 휩쓴다"},
  {id:"s_mon_wild_kargo",name:"야수의 그림자 돌진",stat:"ATK",coef:2.55,target:"single",max:1,range:0,cool:6,dash:6.2,icon:"thumbnail://7d1c1d17eff44687b35ca0d5108084dc",layers:"0207c85c05dd4c4eac12f9ee735d0545|057c2da13da2492c95cb92db424803db",delays:"0|0.04",durations:"0.52|0.65",scales:"0.65|0.72",driftsX:"1.0|0",desc:"저주받은 신전을 지키는 와일드카고처럼 낮게 몸을 숙여 빠르게 돌진한다"},
  {id:"s_mon_tauromacis",name:"수문장의 낙뢰",stat:"INT",coef:2.8,target:"area",max:0,range:5.4,cool:8,icon:"thumbnail://5ef751fd743e41609bf98e03de4df51c",layers:"3cbd85dcfe3c41c4989adec59385c257",delays:"0.08",durations:"0.82",scales:"1.2",desc:"저주받은 신전의 수문장이 창끝으로 번개를 불러 주변을 내리친다"},

  {id:"s_mon_star_pixie",name:"별빛 탄환",stat:"INT",coef:2.45,target:"single",max:1,range:6,cool:5,icon:"thumbnail://ca136923b7e84267af993bdbabada385",projectile:"b61e7e2a50b2405794f88fdddf44b73a",layers:"78e3188f0fc14797a8383658e626e3ea|6ffbabe486c24e5ea6cda2c54022033b",delays:"0|0.18",durations:"0.62|0.58",scales:"0.72|0.7",desc:"스타픽시의 작은 별을 쏘아 한 대상을 밝게 터뜨린다"},
  {id:"s_mon_jr_cellion",name:"붉은 뿔의 기백",stat:"STR",kind:"passive",icon:"thumbnail://016bc9a459104e2a8a2fea03d7130519",desc:"구름공원을 뛰노는 주니어 샐리온의 기백을 익혀 보유 수만큼 STR을 높인다"},
  {id:"s_mon_lunar_pixie",name:"월광 구슬",stat:"INT",coef:2.6,target:"single",max:1,range:6.4,cool:6,icon:"thumbnail://ff4a57bc3d4a4488b0053c33f4c3369f",projectile:"4f6509d9539f4d76a9bb4e8f17e12cc7",layers:"e7ee1a40564c43afbced2da544471266|6d96350411834e2b90a2fe18ff542159",delays:"0|0.2",durations:"0.68|0.62",scales:"0.8|0.75",desc:"루나픽시의 달빛 구슬을 날려 닿은 곳에 푸른 섬광을 남긴다"},
  {id:"s_mon_luster_pixie",name:"태양빛 잔상",stat:"DEX",kind:"passive",icon:"thumbnail://35f555b27d3a4d438224a29e73fac305",desc:"러스터픽시의 눈부신 궤적을 익혀 보유 수만큼 DEX를 높인다"},
  {id:"s_mon_eliza",name:"여신의 정원 폭풍",stat:"INT",coef:3.0,target:"area",max:0,range:5.8,cool:8,key:true,icon:"thumbnail://d458879e2e2949f2bb2e915ff67fbc64",layers:"b14b3dbca0504af28e8d085c12b22000|1660382723ff40c296845e8ded7bbc86",delays:"0|0.22",durations:"0.72|0.85",scales:"1.05|1.25",desc:"잠에서 깨어난 엘리쟈의 분노가 경고진 뒤 폭풍처럼 정원을 휩쓴다"},

  {id:"s_mon_jr_yeti",name:"설인의 체온",stat:"STR",kind:"passive",icon:"thumbnail://1975dd704eec461ab49bdeb0c11c54d9",desc:"눈보라를 견디는 어린 예티의 체온을 익혀 보유 수만큼 STR을 높인다"},
  {id:"s_mon_dark_jr_yeti",name:"검은 설원의 은폐",stat:"LUK",kind:"passive",icon:"thumbnail://ce56cf9613174f80976dab5b61f7b604",desc:"검은 눈 속에 몸을 숨기는 감각을 익혀 보유 수만큼 LUK을 높인다"},
  {id:"s_mon_hector",name:"설원 늑대 발톱",stat:"ATK",coef:2.75,target:"single",max:1,range:0,cool:6,dash:6.5,icon:"thumbnail://7dcc64a4725b4777b8f86a5404b4d4cc",layers:"b9d0ab716c054c58a18c0c38b07695a5|7a41e40ee7d846908e29ec10b94630b0",delays:"0|0.12",durations:"0.58|0.62",scales:"0.82|0.78",driftsX:"1.0|0",desc:"헥터처럼 눈 위를 미끄러지듯 파고들어 발톱으로 한 적을 찢는다"},
  {id:"s_mon_white_fang",name:"화이트팽의 빙설 송곳니",stat:"ATK",coef:2.9,target:"area",max:3,range:4.8,cool:7,icon:"thumbnail://aaa3b506804d4418b025da47dbb65b3f",layers:"dd098279908940fa938d3c5cb3dda732|9fae493a549a4396a2f1378c39f7386f",delays:"0|0.15",durations:"0.65|0.72",scales:"0.9|0.85",desc:"화이트팽의 돌진에 얼음 파편을 실어 전방의 적 셋을 물어뜯는다"},
  {id:"s_mon_snow_witch",name:"추방자의 눈보라",stat:"INT",coef:3.15,target:"area",max:0,range:6,cool:9,key:true,icon:"thumbnail://4b50438f59154f41aba918b2d28bb8d2",layers:"f55dd57a708e43238b64715c02bb06cc|c5a807748e9443348e5b14162948f26b|0719861214fa45578488a1083f49df5a",delays:"0|0.16|0.3",durations:"0.72|0.8|0.92",scales:"0.8|1.0|1.2",desc:"금지된 마법을 익힌 설산의 마녀처럼 얼음탄과 눈보라를 연달아 펼친다"},

  {id:"s_mon_bubble_fish",name:"기포막",stat:"INT",kind:"passive",icon:"thumbnail://c968133e75534a1b933d28da29c4e584",desc:"연안의 수압을 버티는 버블피쉬의 기포막을 익혀 보유 수만큼 INT를 높인다"},
  {id:"s_mon_mask_fish",name:"가면 아래의 감각",stat:"LUK",kind:"passive",icon:"thumbnail://fb9037f43fcd442a971ee007b9f7cc26",desc:"산호초에서 몸을 감추는 마스크피쉬의 감각을 익혀 보유 수만큼 LUK을 높인다"},
  {id:"s_mon_squid",name:"심해 먹물 폭발",stat:"INT",coef:3.0,target:"area",max:4,range:5.2,cool:7,icon:"thumbnail://013b3e6ba18249269e4a1b85c536a0d9",layers:"0906c3a7455940ce9e9db0b0f0278741",delays:"0.12",durations:"0.82",scales:"1.15",desc:"스퀴드가 짙은 먹물을 폭발시켜 주변 네 대상을 어둠으로 덮는다"},
  {id:"s_mon_shark",name:"포식자의 수류탄",stat:"ATK",coef:3.15,target:"single",max:1,range:6.5,cool:7,icon:"thumbnail://b95f05df46124b3485d0a15bb79b10fb",projectile:"209c4567073b424e8d445cea7efb80e3",layers:"a6ab8a49e4174a29bd45a835ed6d3460",delays:"0.22",durations:"0.72",scales:"1.0",desc:"샤크가 사냥감을 향해 압축 수류를 쏘고 송곳니 충격을 터뜨린다"},
  {id:"s_mon_pianus",name:"심해왕의 광선",stat:"INT",coef:3.45,target:"area",max:0,range:6.8,cool:10,key:true,icon:"thumbnail://207c5d6dcee243ad9a141397244ba9a9",layers:"3822f5bc47af488585cef2f0929ec811|306a9aafa3fb43498f1b783b85512305",delays:"0|0.25",durations:"0.82|0.95",scales:"1.2|1.35",desc:"동굴에 몸을 숨긴 피아누스가 입에서 심해의 광선을 뿜어 넓은 범위를 쓸어버린다"},
];

const items = [
  {id:"i_zombie_blue_pilfer",name:"블루 필퍼",slot:"armor",def:9,drop:"m_zombie_mushroom",ruid:"0516947e3f304b44963c445ada9d0806",cat:"cap"},
  {id:"i_copper_chainmail",name:"블루 이너스 체인메일",slot:"armor",def:9,drop:"m_copper_drake",ruid:"30289888185f4882bfbdb782b79e781f",cat:"coat"},
  {id:"i_drake_zeco",name:"제코",slot:"weapon",atk:9,drop:"m_drake",ruid:"270d3a67004d4ff784801ee6f1ec77b9",cat:"twohandedweapon"},
  {id:"i_kargo_anakamoon",name:"다크 아나카문",slot:"armor",int:9,drop:"m_wild_kargo",ruid:"6e4f1a2f9b6e42d6ae9f03d9e50cb30d",cat:"longcoat"},
  {id:"i_tauromacis_sledge",name:"기간틱 슬레지",slot:"weapon",atk:10,drop:"m_tauromacis",ruid:"c76fe20ed9934413837a2b3d267ef74b",cat:"onehandedweapon"},

  {id:"i_star_blue_moon",name:"블루 문",slot:"accessory",luk:10,drop:"m_star_pixie",ruid:"1930b885522f4328975d192b7e3974f2",cat:"earaccessory"},
  {id:"i_cellion_moon_shoes",name:"레드 문슈즈",slot:"armor",def:10,drop:"m_jr_cellion",ruid:"003950a831b04798a44a6c98c2369d37",cat:"shoes"},
  {id:"i_lunar_engrit",name:"다크 잉그리트",slot:"armor",int:10,drop:"m_lunar_pixie",ruid:"9ba62d43125b43c591663f70122e61a7",cat:"longcoat"},
  {id:"i_luster_noel",name:"다크 노엘",slot:"armor",def:10,drop:"m_luster_pixie",ruid:"8aa7b0b6cdb74e988f1636675c6357d3",cat:"glove"},
  {id:"i_eliza_cloud_cape",name:"노란 누더기 망토",slot:"accessory",all:10,drop:"m_eliza",ruid:"6bb8f406338245b49f0079b0e9702a3f",cat:"cape",boss:true},

  {id:"i_yeti_snow_boots",name:"눈송이 부츠",slot:"armor",def:11,drop:"m_jr_yeti",ruid:"d40b14b4e53d4dcaa7abd35224e9e994",cat:"shoes"},
  {id:"i_dark_yeti_moon_shoes",name:"다크 문슈즈",slot:"armor",def:11,drop:"m_dark_jr_yeti",ruid:"9e83794176804f089f1ec8069e178f08",cat:"shoes"},
  {id:"i_hector_warm_cape",name:"온화의 망토",slot:"accessory",all:11,drop:"m_hector",ruid:"a50a3a381d52464084baa2de3b256b32",cat:"cape"},
  {id:"i_whitefang_hinkel",name:"블루 힌켈",slot:"weapon",atk:11,drop:"m_white_fang",ruid:"1be945649c7d4582986d2e90b7a8fc12",cat:"twohandedweapon"},
  {id:"i_snow_witch_cape",name:"설빙의 망토",slot:"accessory",int:12,drop:"m_snow_witch",ruid:"154277b8d0bb4434b9d8925c3aac622f",cat:"cape",boss:true},

  {id:"i_bubble_goggles",name:"파란색 물안경",slot:"accessory",all:12,drop:"m_bubble_fish",ruid:"ba816bdda0044cbdb25fae7062545383",cat:"cap"},
  {id:"i_mask_aqua_board",name:"아쿠아 스노우보드",slot:"weapon",atk:12,drop:"m_mask_fish",ruid:"70c2515b138b47ee9ea8686c73f806c3",cat:"twohandedweapon"},
  {id:"i_squid_pirate_pants",name:"다크 피라테 바지",slot:"armor",def:12,drop:"m_squid",ruid:"e45338a6d1464d52a6a91b2175d96696",cat:"pants"},
  {id:"i_shark_skipper_boots",name:"샤크투스 스키퍼부츠",slot:"armor",def:12,drop:"m_shark",ruid:"6b01017e6d95406c9132e1c74ca14863",cat:"shoes"},
  {id:"i_pianus_bluemarine",name:"블루마린",slot:"weapon",int:13,drop:"m_pianus",ruid:"86deed73ea274107b9055048adc4474b",cat:"onehandedweapon",boss:true},
];

function formula(level) {
  return {
    hp: Math.round(144 + 34.2 * (level - 1)),
    def: Math.round((80 + 19 * (level - 1)) * 10) / 10,
    exp: Math.round(5 * Math.pow(1.10, level - 1)),
  };
}

function readCsv(file) {
  const full = path.join(dataDir, file);
  const text = fs.readFileSync(full, "utf8").replace(/^\uFEFF/, "").trimEnd();
  const lines = text.split(/\r?\n/);
  return { full, headers: lines[0].split(","), rows: lines.slice(1).filter(Boolean).map((line) => line.split(",")) };
}

function upsertCsv(file, objects, key = "id") {
  const csv = readCsv(file);
  const keyIndex = csv.headers.indexOf(key);
  const incoming = new Map(objects.map((object) => [String(object[key]), object]));
  const rows = csv.rows.filter((row) => !incoming.has(row[keyIndex] || ""));
  for (const object of objects) rows.push(csv.headers.map((header) => String(object[header] ?? "")));
  fs.writeFileSync(csv.full, `\uFEFF${csv.headers.join(",")}\r\n${rows.map((row) => row.join(",")).join("\r\n")}\r\n`);
}

function roomRows(area) {
  const p = area.prefix;
  const id = (suffix) => `r_${p}${suffix}`;
  const mapName = (suffix) => `map${p}${suffix}`;
  const base = {
    room_type:"hunt", conn_north:"", conn_south:"", conn_east:"", conn_west:"",
    gate_type:"", gate_key:"", gate_value:"", is_start:"", area_id:area.id, portal_x:13, portal_y:1,
  };
  const links = {
    "1": {conn_east:id("2"),conn_west:"r_town",gate_type:"boss",gate_key:area.priorBossRoom},
    "2": {conn_south:id("6"),conn_east:id("3"),conn_west:id("1")},
    "3": {conn_north:id("a"),conn_south:id("7"),conn_east:id("4"),conn_west:id("2")},
    "a": {conn_south:id("3"),gate_type:"key",gate_key:area.priorBossSkill},
    "4": {conn_east:id("5"),conn_west:id("3"),gate_type:"stat",gate_key:"STAT_TOTAL",gate_value:area.statGate},
    "5": {conn_west:id("4"),room_type:"boss"},
    "6": {conn_north:id("2"),conn_east:id("7")},
    "7": {conn_north:id("3"),conn_west:id("6")},
  };
  return area.rooms.map(([suffix,name,monster,count,level]) => ({
    id:id(suffix), name, ...base, ...links[suffix], map_name:mapName(suffix), monster_id:monster,
    monster_count:count, monster_level:level,
  }));
}

function skillRow(skill) {
  const passive = skill.kind === "passive";
  const layerCount = skill.layers ? skill.layers.split("|").length : 0;
  const fill = (value, fallback) => value || (layerCount ? Array(layerCount).fill(fallback).join("|") : "");
  return {
    id:skill.id,name:skill.name,source:"monster",scaling_stat:skill.stat,coefficient:passive?0:skill.coef,
    slot_type:"monster",effect_type:passive?"shield":"damage",is_key_skill:skill.key?"true":"false",
    cooldown:passive?0:skill.cool,skill_kind:passive?"passive":"attack",target_mode:passive?"self":skill.target,
    max_targets:passive?0:skill.max,effect_value:0,duration:0,range:passive?0:skill.range,dash_distance:skill.dash||0,tier:0,
    icon_ruid:skill.icon,icon_ratio:"1.00",effect_ruid:"",effect_style:"",sfx_ruid:"",projectile_ruid:skill.projectile||"",
    passive_stat:passive?skill.stat:"",passive_value:"",description:skill.desc,layer_ruids:skill.layers||"",
    layer_types:layerCount?Array(layerCount).fill("animationclip").join("|"):"",layer_styles:layerCount?Array(layerCount).fill("clip").join("|"):"",
    layer_delays:fill(skill.delays,"0"),layer_durations:fill(skill.durations,"0.7"),layer_scales:fill(skill.scales,"1"),
    layer_offsets_x:fill("","0"),layer_offsets_y:fill("","0"),layer_drifts_x:fill(skill.driftsX,"0"),layer_drifts_y:fill("","0"),
  };
}

function itemRow(item) {
  return {
    id:item.id,name:item.name,item_type:"equip",slot:item.slot,stat_atk:item.atk||0,stat_int:item.int||0,
    stat_def:item.def||0,stat_luk:item.luk||0,stat_all:item.all||0,heal_hp:0,stack_max:5,drop_from:item.drop,
    drop_rate:item.boss?0.02:0.03,icon_ruid:`thumbnail://${item.ruid}`,
    note:`${item.name} 장비 보상. 원작 MSW 아바타 아이템과 이름과 아이콘을 일치시킴`,passive_stat:"",passive_value:"",avatar_category:item.cat,
  };
}

upsertCsv("AreaTable.csv", areas.map((area) => ({
  id:area.id,name:area.name,entry_room_id:area.entry,default_unlocked:"false",sort_order:area.order,note:area.note,
})));
upsertCsv("LandmarkTable.csv", areas.map((area) => ({
  level:area.unlock,reward_type:"area",reward_value:area.id,note:`Lv${area.unlock} 달성 시 ${area.name} 개방`,
})), "level");
upsertCsv("RoomTable.csv", areas.flatMap(roomRows));
upsertCsv("MonsterTable.csv", monsters.map((monster) => {
  const stats = formula(monster.level);
  return {id:monster.id,name:monster.name,level:monster.level,hp:stats.hp,def:stats.def,exp:stats.exp,drop_skill_id:monster.skill,model_id:monster.model,combat_skill_ids:""};
}));
upsertCsv("SkillTable.csv", skills.map(skillRow));
upsertCsv("ItemTable.csv", items.map(itemRow));

for (const monster of monsters) {
  const model = ModelBuilder.read(path.join(modelDir, `${monster.template}.model`));
  model.renameModel(monster.file, monster.model);
  const actions = { ...monster.actions };
  actions.attack = actions.attack || actions.move || actions.stand;
  actions.jump = actions.jump || actions.move || actions.stand;
  model.value("MOD.Core.StateAnimationComponent", "ActionSheet", actions);
  model.value("MOD.Core.SpriteRendererComponent", "SpriteRUID", actions.stand);
  model.value("MOD.Core.MovementComponent", "InputSpeed", monster.speed);
  model.value("MOD.Core.HitComponent", "BoxSize", vector2(monster.box[0], monster.box[1]));
  model.value("MOD.Core.HitComponent", "ColliderOffset", vector2(monster.offset[0], monster.offset[1]));
  model.value("script.RoomMonster", "MonsterId", monster.id);
  model.write(path.join(modelDir, `${monster.file}.model`));
}

const templates = {"1":"map051","2":"map052","3":"map053","a":"map05a","4":"map054","5":"map055","6":"map056","7":"map057"};
for (const area of areas) {
  for (const [suffix] of area.rooms) {
    const mapName = `map${area.prefix}${suffix}`;
    const map = MapBuilder.fromTemplate(path.join(mapDir, `${templates[suffix]}.map`), mapName);
    map.patchComponent("RectTileMap", "MOD.Core.RectTileMapComponent", { TileSetRUID: area.tileset });
    if (!map.getTiles().some((tile) => tile.tileIndex === 3)) {
      map.removeComponent(mapName, "script.NautilusWaterBoundary");
    }
    map.write(path.join(mapDir, `${mapName}.map`));
  }
}

console.log(JSON.stringify({areas:areas.length,rooms:areas.length*8,monsters:monsters.length,skills:skills.length,items:items.length,maps:areas.length*8}, null, 2));
