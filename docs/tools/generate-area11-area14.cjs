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
    id:"area_11",name:"루더스 호수",entry:"r_111",order:11,unlock:100,prefix:"11",
    tileset:"tileset://7a070000-0000-4000-8000-000000000007",
    priorBossRoom:"r_105",priorBossSkill:"s_mon_pianus",statGate:515,
    note:"지역 20칸의 열한 번째 (Lv101~110). 에오스탑을 아래로 내려가 숨겨진 탑의 롬바드에 닿는다",
    rooms:[
      ["1","에오스탑 97층","m_ratz",4,101],["2","에오스탑 66층","m_drumming_bunny",4,103],
      ["3","에오스탑 33층","m_bloctopus",5,105],["a","태엽 장치의 샛길","m_king_bloctopus",4,109],
      ["4","에오스탑 32층","m_king_bloctopus",5,108],["5","숨겨진 탑","m_rombot",1,110],
      ["6","에오스탑 보급 창고","m_ratz",5,102],["7","블록 장치 통로","m_bloctopus",5,104],
    ],
  },
  {
    id:"area_12",name:"루디브리엄",entry:"r_121",order:12,unlock:110,prefix:"12",
    tileset:"tileset://7a080000-0000-4000-8000-000000000008",
    priorBossRoom:"r_115",priorBossSkill:"s_mon_rombot",statGate:565,
    note:"지역 20칸의 열두 번째 (Lv111~120). 장난감 성과 공장을 지나 시간의 소용돌이 타이머에 닿는다",
    rooms:[
      ["1","구름테라스","m_brown_teddy",4,111],["2","하늘테라스","m_toy_trojan",4,113],
      ["3","장난감공장 메인공정","m_master_robo",5,115],["a","멈춘 시계의 비밀방","m_chronos",4,119],
      ["4","시간의 길","m_chronos",5,118],["5","시간의 소용돌이","m_timer",1,120],
      ["6","버려진 장난감 창고","m_brown_teddy",5,112],["7","태엽 생산 라인","m_master_robo",5,114],
    ],
  },
  {
    id:"area_13",name:"니할 사막",entry:"r_131",order:13,unlock:120,prefix:"13",
    tileset:"tileset://7a090000-0000-4000-8000-000000000009",
    priorBossRoom:"r_125",priorBossSkill:"s_mon_timer",statGate:615,
    note:"지역 20칸의 열세 번째 (Lv121~130). 아리안트 밖 사막길과 유적을 지나 잠든 데우를 깨운다",
    rooms:[
      ["1","아리안트 동문 밖","m_white_sand_rabbit",4,121],["2","메마른 사막","m_scarf_plead",4,123],
      ["3","북쪽 사막길 1","m_meercat",5,125],["a","바람에 묻힌 오아시스","m_sand_dwarf",4,129],
      ["4","붉은 모래 사막","m_sand_dwarf",5,128],["5","잠자는 사막","m_deo",1,130],
      ["6","모래토끼 굴","m_white_sand_rabbit",5,122],["7","메마른 감시길","m_meercat",5,124],
    ],
  },
  {
    id:"area_14",name:"마가티아",entry:"r_141",order:14,unlock:130,prefix:"14",
    tileset:"tileset://7a100000-0000-4000-8000-000000000010",
    priorBossRoom:"r_135",priorBossSkill:"s_mon_deo",statGate:665,
    note:"지역 20칸의 열네 번째 (Lv131~140). 제뉴미스트와 알카드노 연구소를 가로질러 키메라 실험실에 닿는다",
    rooms:[
      ["1","연구소 101호","m_cube_slime",4,131],["2","연구소 B-1구역","m_mithril_mutae",4,133],
      ["3","연구소 201호","m_homun",5,135],["a","봉인된 연금 장치실","m_roid",4,139],
      ["4","연구소 C-1구역","m_roid",5,138],["5","연구소 202호","m_chimera",1,140],
      ["6","제뉴미스트 배양실","m_cube_slime",5,132],["7","알카드노 금속 통로","m_mithril_mutae",5,134],
    ],
  },
];
const monsters = [
  {id:"m_ratz",name:"라츠",level:101,skill:"s_mon_ratz",model:"ratz",file:"Ratz",template:"BluePig",actions:{stand:"383e34f2a8584a96a01b80a8fadbb813",move:"b5df6800c752484eb85105a082bacb5d",hit:"fc89d969cba24d5092fbd9471954fb1a",die:"96a7f097c85d414886c39265b53bb8df"},speed:1.45,box:[0.55,0.45],offset:[0,0.23]},
  {id:"m_drumming_bunny",name:"북치는 토끼",level:103,skill:"s_mon_drumming_bunny",model:"drummingbunny",file:"DrummingBunny",template:"BluePig",actions:{stand:"20283346c1db42b593fdddb218ea769a",move:"213bcc0125864e56ae52cf6a6eef4bc0",hit:"4bde7de298ff46ea9c28289c9a957e9d",die:"4f2864a83c454979b57b2e9cfc95833b"},speed:1.35,box:[0.55,0.62],offset:[0,0.31]},
  {id:"m_bloctopus",name:"블록퍼스",level:105,skill:"s_mon_bloctopus",model:"bloctopus",file:"Bloctopus",template:"BluePig",actions:{stand:"826410e1bd4e4a12a612ab642c19c705",move:"5417210796834fe8a6648451ec86a395",jump:"19f52894c1d24b33ae7c6a4f357effb0",hit:"bd3f11d2c6a04c3b8021179b1bdf6752",die:"286658fc7b984f49bbbb79e5d86d71b1"},speed:1.3,box:[0.58,0.64],offset:[0,0.32]},
  {id:"m_king_bloctopus",name:"킹 블록퍼스",level:108,skill:"s_mon_king_bloctopus",model:"kingbloctopus",file:"KingBloctopus",template:"BluePig",actions:{stand:"cb5eb9faaf68477292af0b710e383c9d",move:"85bf19a24eb54ac1b7c83313acf0115a",jump:"f36b52fe11044eb6bdda8b2549837d92",attack:"c9c73dc14a80445893d2baef34f31692",hit:"6dad564f922a420eab103ff36758db28",die:"704d03ced6f64ad097d31fc18e9d4428"},speed:1.35,box:[0.72,0.88],offset:[0,0.44]},
  {id:"m_rombot",name:"롬바드",level:110,skill:"s_mon_rombot",model:"rombot",file:"Rombot",template:"JrBalrog",actions:{stand:"b41def4288404055b3b8850daa99cfbf",move:"041d85c246e04fc7a92959175e434d4c",attack:"921caf97260c40e28320b761c34a011c",hit:"5d9b9bbdfc2e4d8fb6c10e3d3ef3e4dd",die:"ecab635256da4dbcbac70ee157fa641d"},speed:0.9,box:[1.7,1.8],offset:[0,0.9]},

  {id:"m_brown_teddy",name:"브라운테니",level:111,skill:"s_mon_brown_teddy",model:"brownteddy",file:"BrownTeddy",template:"BluePig",actions:{stand:"46fd51a318b64738a36beeb3db02a970",move:"dcdfa9fce83949229330906599350caa",hit:"5266f286ebc749198328728131670684",die:"014e06210ad6433185b2d923520dd846"},speed:1.3,box:[0.6,0.56],offset:[0,0.28]},
  {id:"m_toy_trojan",name:"장난감 목마",level:113,skill:"s_mon_toy_trojan",model:"toytrojan",file:"ToyTrojan",template:"WildBoar",actions:{stand:"f9a2d6e8feaf4c90a3e00d022932fdaa",move:"99f7ff29ebb245358c50dcddc2716e8d",attack:"fc4857ea48be477c9546c775e0f31d49",hit:"8fe12a540d2b49229936f18879682bda",die:"7fe0b06b59aa4da683444e518a8d8d66"},speed:1.5,box:[1.25,1.05],offset:[0,0.52]},
  {id:"m_master_robo",name:"마스터 로보",level:115,skill:"s_mon_master_robo",model:"masterrobo",file:"MasterRobo",template:"WildBoar",actions:{stand:"f5d65e28cb0e4990bf5727015f22e0f1",move:"58bf9d896e6d4e11a80498dd5e39fb01",hit:"12f6ce4a4088425b8219ab00d4378427",die:"69f98ba3fea146698b6ffaa5fdad0edc"},speed:1.2,box:[0.9,0.96],offset:[0,0.48]},
  {id:"m_chronos",name:"크로노스",level:118,skill:"s_mon_chronos",model:"chronos",file:"Chronos",template:"Fairy",actions:{stand:"1356c7ad27254459aaf789b51a75875c",move:"2e361c296dd94cab820ede0791a44553",hit:"9a0ab5e69833499f9b982e401fb3f5c8",die:"c34007422581490fb12eb9d5c5d01ffb"},speed:1.25,box:[0.65,0.68],offset:[0,0.34]},
  {id:"m_timer",name:"타이머",level:120,skill:"s_mon_timer",model:"timer",file:"Timer",template:"Mushmom",actions:{stand:"cbdd230e5cd34b7b9eeb1cd206d19f34",move:"684685ca8dc84aac920f77e5c5d871f1",attack:"9a4f5adadc25455e88c0394ee41f346d",hit:"a8f2cac815354c40a9147389bc070d78",die:"cb0d2a03101b4210b142a74cd178de88"},speed:0.9,box:[1.5,1.5],offset:[0,0.75]},

  {id:"m_white_sand_rabbit",name:"흰 모래토끼",level:121,skill:"s_mon_white_sand_rabbit",model:"whitesandrabbit",file:"WhiteSandRabbit",template:"BluePig",actions:{stand:"981c64ae30bd4f98aef886e9314d8e64",move:"1eaee5c96fec4a07afdf902b96e3a0d8",attack:"971f0209fc1245b3b755dd250c5a836d",hit:"e77fd0ddfcc44f02af01fd4eb2e9ff97",die:"8e58798019c74928a99bfcbb9054a744"},speed:1.6,box:[0.82,0.58],offset:[0,0.29]},
  {id:"m_scarf_plead",name:"목도리 프릴드",level:123,skill:"s_mon_scarf_plead",model:"scarfplead",file:"ScarfPlead",template:"BluePig",actions:{stand:"30e7faf77c6c41d583f341c234220597",move:"04c69afe7f3e4706a596a624acf3849d",hit:"63e42ff4a95d477b8f7eb0f189176e0a",die:"ed20ea2f2bef45b489c74a62fa65c1d3"},speed:1.45,box:[0.72,0.82],offset:[0,0.41]},
  {id:"m_meercat",name:"미요캐츠",level:125,skill:"s_mon_meercat",model:"meercat",file:"Meercat",template:"BluePig",actions:{stand:"fc3c2944ce44425c8d7f302a8610b886",move:"ba94d969ce604f7b805b80eab305c5e0",attack:"24aa0e092a204bf6b032c29999fcba3b",hit:"c2436109b95b4c4c9b0c9f9134f2ab28",die:"2d72f7695974444a87a5256f13e40282"},speed:1.55,box:[0.58,0.72],offset:[0,0.36]},
  {id:"m_sand_dwarf",name:"모래난쟁이",level:128,skill:"s_mon_sand_dwarf",model:"sanddwarf",file:"SandDwarf",template:"WildBoar",actions:{stand:"64f166fa4e5445bc982071dea297d988",move:"06c4eb04f5f249af9a73705648ca9c33",attack:"8485f7a268a8400682b6dde2b3040bc3",hit:"93559f70054d4b3ea12f71ffc431a1b1",die:"50761c06c0844199beab282871beb3fc"},speed:1.2,box:[1.3,1.2],offset:[0,0.6]},
  {id:"m_deo",name:"데우",level:130,skill:"s_mon_deo",model:"deo",file:"Deo",template:"Mushmom",actions:{stand:"6cf930e280f44694a0a0feedbfd855ed",move:"196bfc9fe38b4266b279f1b3be53c5dc",attack:"4a7d9f008b334c1187c087d6f5e5cdd3",hit:"f86cb206cdbc4954aaa1760ad6e25113",die:"7c264f46b77a41ecb52c50b0f191d249"},speed:0.8,box:[1.8,1.55],offset:[0,0.78]},

  {id:"m_cube_slime",name:"큐브슬라임",level:131,skill:"s_mon_cube_slime",model:"cubeslime",file:"CubeSlime",template:"Mushroom",actions:{stand:"e93e27480f1043ef8e51fa3b0906a4d9",move:"4a141fc777a14395b6af8444cef50d73",hit:"8d69bfe6ca074f12b51f7703b32d885f",die:"5fddbc2a267f463cb513cdd4d0b6b88d"},speed:1.2,box:[0.62,0.58],offset:[0,0.29]},
  {id:"m_mithril_mutae",name:"미스릴 뮤테",level:133,skill:"s_mon_mithril_mutae",model:"mithrilmutae",file:"MithrilMutae",template:"BluePig",actions:{stand:"b06abb18fb52476d8bc7bdd5e46abe19",move:"679e977d594e4392a9848f0e16571aa0",hit:"af0cfa2f179746a6b444ff335594b878",die:"d326521fe8b649348e6e875f8d6a8377"},speed:1.1,box:[0.76,0.7],offset:[0,0.35]},
  {id:"m_homun",name:"호문",level:135,skill:"s_mon_homun",model:"homun",file:"Homun",template:"Mushroom",actions:{stand:"8f0fb531779d41738664009091d7b017",move:"f46c4862e92746afb183cd7351ce36f4",hit:"224bcc0e9d8744df9eea3b1d09b7944d",die:"1656e04f11a64f66b2fd4961390728d6"},speed:1.2,box:[0.66,0.72],offset:[0,0.36]},
  {id:"m_roid",name:"로이드",level:138,skill:"s_mon_roid",model:"roid",file:"Roid",template:"WildBoar",actions:{stand:"364bc76e0cc3429ea8ca758319ec7678",move:"839a58c5ea2e47399f9166d2b034fbd6",hit:"c3600a2a2423490f9206bc4f39c88577",die:"863c7c2f0e9a4a788c451ddbf09f59c1"},speed:1.25,box:[0.72,0.88],offset:[0,0.44]},
  {id:"m_chimera",name:"키메라",level:140,skill:"s_mon_chimera",model:"chimera",file:"Chimera",template:"JrBalrog",actions:{stand:"3f5236d28b1f409797fe7c4b48743b8a",move:"602442e3a83c423b92d2245fb6384858",attack:"18a29b25caeb41a8a4267b68ff49a40a",hit:"e7d383d93dce42548917bb81de8e8cf4",die:"d85f8d59bb5543bcb3ecb8ee8a3ba5ac"},speed:0.9,box:[1.8,1.55],offset:[0,0.78]},
];
const skills = [
  {id:"s_mon_ratz",name:"태엽쥐의 민첩",stat:"DEX",kind:"passive",icon:"thumbnail://383e34f2a8584a96a01b80a8fadbb813",desc:"에오스탑의 좁은 장치 틈을 빠져나가는 라츠의 감각을 익혀 보유 수만큼 DEX를 높인다"},
  {id:"s_mon_drumming_bunny",name:"태엽 북진동",stat:"INT",coef:3.35,target:"area",max:4,range:5.2,cool:7,icon:"thumbnail://20283346c1db42b593fdddb218ea769a",layers:"91c5d5dd661e4e079271b4446f7eb262",durations:"0.75",scales:"0.9",desc:"북치는 토끼의 장난감 북소리를 압축해 주변 네 대상에게 진동 충격을 퍼뜨린다"},
  {id:"s_mon_bloctopus",name:"블록 위장",stat:"LUK",kind:"passive",icon:"thumbnail://826410e1bd4e4a12a612ab642c19c705",desc:"장난감 블록 사이에 몸을 감추는 블록퍼스의 위장을 익혀 보유 수만큼 LUK을 높인다"},
  {id:"s_mon_king_bloctopus",name:"왕관 블록탄",stat:"INT",coef:3.5,target:"single",max:1,range:6.8,cool:7,icon:"thumbnail://cb5eb9faaf68477292af0b710e383c9d",projectile:"a2da67e687994755a8943c2bcf871902",layers:"e53471f0f7114343907be7beb520751f",delays:"0.22",durations:"0.65",scales:"0.9",desc:"킹 블록퍼스가 왕관의 자신감을 실은 블록탄을 쏘아 한 대상을 폭발시킨다"},
  {id:"s_mon_rombot",name:"에오스 중력파",stat:"ATK",coef:3.8,target:"area",max:0,range:6,cool:9,key:true,icon:"thumbnail://b41def4288404055b3b8850daa99cfbf",layers:"91c5d5dd661e4e079271b4446f7eb262|06bbe7d534094761b54b147f3a79ca38",delays:"0|0.18",durations:"0.72|0.8",scales:"1.1|0.8",desc:"숨겨진 탑의 수호 기계 롬바드가 장갑의 동력을 터뜨려 넓은 중력 충격파를 일으킨다"},

  {id:"s_mon_brown_teddy",name:"솜인형 완충",stat:"DEX",kind:"passive",icon:"thumbnail://46fd51a318b64738a36beeb3db02a970",desc:"태엽 인형의 부드러운 솜이 충격을 흡수하는 성질을 익혀 보유 수만큼 DEX를 높인다"},
  {id:"s_mon_toy_trojan",name:"태엽 목마 돌진",stat:"ATK",coef:3.55,target:"single",max:1,range:0,cool:7,dash:6.8,icon:"thumbnail://f9a2d6e8feaf4c90a3e00d022932fdaa",layers:"fc4857ea48be477c9546c775e0f31d49",durations:"0.7",scales:"0.72",driftsX:"1.0",desc:"장난감 목마의 태엽을 끝까지 감아 전방으로 내달리며 한 대상을 들이받는다"},
  {id:"s_mon_master_robo",name:"정밀 태엽회로",stat:"DEX",kind:"passive",icon:"thumbnail://f5d65e28cb0e4990bf5727015f22e0f1",desc:"장난감공장의 마스터 로보가 가진 정밀한 태엽 제어를 익혀 보유 수만큼 DEX를 높인다"},
  {id:"s_mon_chronos",name:"크로노스의 시간편린",stat:"INT",coef:3.7,target:"single",max:1,range:6.5,cool:8,icon:"thumbnail://1356c7ad27254459aaf789b51a75875c",layers:"e5558e07445143b6999f20246768a3fe",delays:"0.12",durations:"0.8",scales:"0.9",desc:"시계탑에 쌓인 시간의 파편을 한 대상에게 던져 순간을 비틀어 폭발시킨다"},
  {id:"s_mon_timer",name:"시간 정지 충격",stat:"INT",coef:4,target:"area",max:0,range:6.2,cool:10,key:true,icon:"thumbnail://cbdd230e5cd34b7b9eeb1cd206d19f34",layers:"e5558e07445143b6999f20246768a3fe|3ef6b2dcc75f4d4990e6e7f106bda49e",delays:"0|0.2",durations:"0.78|0.88",scales:"1|0.85",desc:"시간의 소용돌이를 지키는 타이머가 종을 울려 주변의 시간을 멈추고 충격을 한꺼번에 터뜨린다"},

  {id:"s_mon_white_sand_rabbit",name:"사막 굴착탄",stat:"ATK",coef:3.8,target:"single",max:1,range:6.5,cool:7,icon:"thumbnail://981c64ae30bd4f98aef886e9314d8e64",layers:"201c4ae9d7c24438b56fb4d731ed9245",delays:"0.12",durations:"0.72",scales:"0.85",desc:"흰 모래토끼가 땅속에서 모은 모래를 탄환처럼 차 올려 한 대상을 꿰뚫는다"},
  {id:"s_mon_scarf_plead",name:"목도리의 사막감각",stat:"LUK",kind:"passive",icon:"thumbnail://30e7faf77c6c41d583f341c234220597",desc:"거친 모래바람에서도 방향을 잃지 않는 목도리 프릴드의 감각을 익혀 보유 수만큼 LUK을 높인다"},
  {id:"s_mon_meercat",name:"미요캐츠의 모래매복",stat:"ATK",coef:3.95,target:"area",max:3,range:4.8,cool:8,icon:"thumbnail://fc3c2944ce44425c8d7f302a8610b886",layers:"412bce166c844b07ba1b4aa3ddcd53fa",durations:"0.74",scales:"0.9",desc:"미요캐츠 무리가 모래 아래에서 동시에 튀어나와 가까운 적 셋을 기습한다"},
  {id:"s_mon_sand_dwarf",name:"사막 대장장이의 체력",stat:"STR",kind:"passive",icon:"thumbnail://64f166fa4e5445bc982071dea297d988",desc:"모래난쟁이가 사막에서 도구를 다루며 기른 힘을 익혀 보유 수만큼 STR을 높인다"},
  {id:"s_mon_deo",name:"잠든 선인장의 폭발",stat:"INT",coef:4.25,target:"area",max:0,range:6.4,cool:10,key:true,icon:"thumbnail://6cf930e280f44694a0a0feedbfd855ed",layers:"98cd61bf1b2c4ff496455ad956cd95d5|9af96df994cf4794882fec71c027da2b",delays:"0|0.2",durations:"0.78|0.9",scales:"1.05|0.85",desc:"오래 잠든 선인장 장로 데우가 뿌리에 모은 열기와 가시를 폭발시켜 사막을 뒤흔든다"},

  {id:"s_mon_cube_slime",name:"연금 큐브막",stat:"INT",kind:"passive",icon:"thumbnail://e93e27480f1043ef8e51fa3b0906a4d9",desc:"실험실의 용액이 정육면체 형태를 유지하는 성질을 익혀 보유 수만큼 INT를 높인다"},
  {id:"s_mon_mithril_mutae",name:"미스릴 외피",stat:"DEX",kind:"passive",icon:"thumbnail://b06abb18fb52476d8bc7bdd5e46abe19",desc:"알카드노 연구소에서 금속으로 강화된 뮤테의 외피를 익혀 보유 수만큼 DEX를 높인다"},
  {id:"s_mon_homun",name:"플라스크 독무",stat:"INT",coef:4.1,target:"area",max:4,range:5.4,cool:8,icon:"thumbnail://8f0fb531779d41738664009091d7b017",layers:"127defcb953144368b79da1417f8b4b4",durations:"0.82",scales:"0.9",desc:"폐쇄된 연구실의 호문처럼 플라스크 속 불안정한 용액을 퍼뜨려 네 대상을 독무로 덮는다"},
  {id:"s_mon_roid",name:"알카드노 에너지탄",stat:"ATK",coef:4.2,target:"single",max:1,range:7,cool:8,icon:"thumbnail://364bc76e0cc3429ea8ca758319ec7678",projectile:"e51545cbf94349f59f4431e2e76d2cdc",layers:"3ff44a80daba4bb4a903778e036f551d",delays:"0.2",durations:"0.72",scales:"0.9",desc:"알카드노의 전투 로이드가 압축한 연구소 에너지를 한 대상에게 발사한다"},
  {id:"s_mon_chimera",name:"융합체의 산성 포격",stat:"INT",coef:4.55,target:"area",max:0,range:6.8,cool:11,key:true,icon:"thumbnail://3f5236d28b1f409797fe7c4b48743b8a",projectile:"ab113d9a5ca5402d85ecc2ab7a4f51a1",layers:"127defcb953144368b79da1417f8b4b4|ec7b571a85244965b296d26e6511e06d",delays:"0.2|0",durations:"0.8|0.9",scales:"1.05|0.85",desc:"서로 다른 생체 실험이 합쳐진 키메라가 산성 탄환과 연금 폭발을 연달아 쏟아낸다"},
];
const items = [
  {id:"i_ratz_toy_propeller",name:"장난감 프로펠러",slot:"armor",def:14,drop:"m_ratz",ruid:"1efd0c8d09f24cc9b3965078c3f4c707",cat:"cap"},
  {id:"i_drumming_toy_shoes",name:"장난감 구두",slot:"armor",def:14,drop:"m_drumming_bunny",ruid:"421ffff466c14950ae2b28eb94026043",cat:"shoes"},
  {id:"i_bloctopus_block_friends",name:"블록 친구들",slot:"weapon",atk:14,drop:"m_bloctopus",ruid:"54abd55cf81b4c0a92ba9552d08195d8",cat:"onehandedweapon"},
  {id:"i_king_toy_wand",name:"장난감 마술봉",slot:"weapon",int:14,drop:"m_king_bloctopus",ruid:"36638a19057749859e3f74573083786e",cat:"onehandedweapon"},
  {id:"i_rombot_toy_gun",name:"장난감 총",slot:"weapon",atk:15,drop:"m_rombot",ruid:"6139c0bbdeca4e1ea36a2085bb27c5c7",cat:"twohandedweapon",boss:true},

  {id:"i_teddy_toy_memory",name:"장난감의 추억",slot:"armor",def:15,drop:"m_brown_teddy",ruid:"b941359ce02e4d4fac38a64b6f5e39c2",cat:"longcoat"},
  {id:"i_trojan_toy_loafers",name:"장난감 로퍼",slot:"armor",def:15,drop:"m_toy_trojan",ruid:"96f0348b734441938e69cca731c5c8f0",cat:"shoes"},
  {id:"i_robo_blue_watch",name:"블루 전자시계",slot:"accessory",all:15,drop:"m_master_robo",ruid:"3069e862d9f44f239a90746172cc39e0",cat:"glove"},
  {id:"i_chronos_clockwork_doll",name:"시계탑 태엽 인형",slot:"accessory",int:15,drop:"m_chronos",ruid:"97e5c95ed75b4820915f5624c988532b",cat:"cape"},
  {id:"i_timer_master_time",name:"마스터 타임",slot:"weapon",int:16,drop:"m_timer",ruid:"1ab8680c9aa64b4e85b46b23708f472f",cat:"onehandedweapon",boss:true},

  {id:"i_rabbit_desert_fox",name:"사막여우",slot:"armor",def:16,drop:"m_white_sand_rabbit",ruid:"cbec4354aa874206a313aefac24dfb3c",cat:"cap"},
  {id:"i_plead_arabian_hat",name:"아라비안 모자",slot:"armor",def:16,drop:"m_scarf_plead",ruid:"7ce62ca658194bea91c1926532d5695d",cat:"cap"},
  {id:"i_meercat_leather_sandals",name:"가죽 샌들",slot:"armor",def:16,drop:"m_meercat",ruid:"202544d7095c42c5bfb3046619ab58cc",cat:"shoes"},
  {id:"i_dwarf_wilderness",name:"황야",slot:"armor",def:16,drop:"m_sand_dwarf",ruid:"69d19ba5a3214eaa8a8d1d99969a1136",cat:"coat"},
  {id:"i_deo_silent_legend",name:"적막한 전설",slot:"armor",all:17,drop:"m_deo",ruid:"054e596570c2492588ad62d5d0cc426f",cat:"cap",boss:true},

  {id:"i_cube_alchemist_hat",name:"연금술사의 모자",slot:"armor",int:17,drop:"m_cube_slime",ruid:"998b684ad4084177b785e13305b88dd3",cat:"cap"},
  {id:"i_mutae_alcadno_cape",name:"알카드노의 망토",slot:"accessory",def:17,drop:"m_mithril_mutae",ruid:"899285a5cd2a419e9711a465f299b22e",cat:"cape"},
  {id:"i_homun_alchemist_workwear",name:"연금술사의 작업복",slot:"armor",int:17,drop:"m_homun",ruid:"127f8168219240ec9837ccfc36418d76",cat:"longcoat"},
  {id:"i_roid_zenumist_cape",name:"제뉴미스트의 망토",slot:"accessory",all:17,drop:"m_roid",ruid:"c6db07a8f07d4b03af4303cb610f5f9e",cat:"cape"},
  {id:"i_chimera_corrupted_staff",name:"변질된 알리샤의 스태프",slot:"weapon",int:18,drop:"m_chimera",ruid:"7750ca7207d24a2b82ad25ba7490def5",cat:"onehandedweapon",boss:true},
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
  fs.writeFileSync(csv.full, "\uFEFF" + csv.headers.join(",") + "\r\n" + rows.map((row) => row.join(",")).join("\r\n") + "\r\n");
}

function roomRows(area) {
  const id = (suffix) => "r_" + area.prefix + suffix;
  const mapName = (suffix) => "map" + area.prefix + suffix;
  const base = { room_type:"hunt",conn_north:"",conn_south:"",conn_east:"",conn_west:"",gate_type:"",gate_key:"",gate_value:"",is_start:"",area_id:area.id,portal_x:13,portal_y:1 };
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
    id:id(suffix),name,...base,...links[suffix],map_name:mapName(suffix),monster_id:monster,monster_count:count,monster_level:level,
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
    drop_rate:item.boss?0.02:0.03,icon_ruid:"thumbnail://" + item.ruid,
    note:item.name + " 장비 보상. 공식 MSW 아바타 아이템 이름과 아이콘을 일치시킴",
    passive_stat:"",passive_value:"",avatar_category:item.cat,
  };
}

upsertCsv("AreaTable.csv", areas.map((area) => ({
  id:area.id,name:area.name,entry_room_id:area.entry,default_unlocked:"false",sort_order:area.order,note:area.note,
})));
upsertCsv("LandmarkTable.csv", areas.map((area) => ({
  level:area.unlock,reward_type:"area",reward_value:area.id,note:"Lv" + area.unlock + " 달성 시 " + area.name + " 개방",
})), "level");
upsertCsv("RoomTable.csv", areas.flatMap(roomRows));
upsertCsv("MonsterTable.csv", monsters.map((monster) => {
  const stats = formula(monster.level);
  return {id:monster.id,name:monster.name,level:monster.level,hp:stats.hp,def:stats.def,exp:stats.exp,drop_skill_id:monster.skill,model_id:monster.model,combat_skill_ids:""};
}));
upsertCsv("SkillTable.csv", skills.map(skillRow));
upsertCsv("ItemTable.csv", items.map(itemRow));

for (const monster of monsters) {
  const model = ModelBuilder.read(path.join(modelDir, monster.template + ".model"));
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
  model.write(path.join(modelDir, monster.file + ".model"));
}

const templates = {"1":"map071","2":"map072","3":"map073","a":"map07a","4":"map074","5":"map075","6":"map076","7":"map077"};
for (const area of areas) {
  for (const [suffix] of area.rooms) {
    const mapName = "map" + area.prefix + suffix;
    const map = MapBuilder.fromTemplate(path.join(mapDir, templates[suffix] + ".map"), mapName);
    map.patchComponent("RectTileMap", "MOD.Core.RectTileMapComponent", { TileSetRUID: area.tileset });
    for (const tile of map.getTiles("RectTileMap")) tile.tileIndex += 4;
    try {
      map.removeComponent(mapName, "script.NautilusWaterBoundary");
    } catch (error) {
      if (!String(error.message).includes("has no script.NautilusWaterBoundary")) throw error;
    }
    map.write(path.join(mapDir, mapName + ".map"));
  }
}

console.log(JSON.stringify({areas:areas.length,rooms:areas.length*8,monsters:monsters.length,skills:skills.length,items:items.length,maps:areas.length*8}, null, 2));
