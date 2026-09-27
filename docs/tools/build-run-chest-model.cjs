// Run 탐험 상자 모델. 구조화 파일은 ModelBuilder로만 생성한다.
const { ModelBuilder, vector3 } = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const file = "RootDesk/MyDesk/Models/Items/RunChest.model";
const b = new ModelBuilder("RunChest", { model_id: "runchest" });

b.component("TransformComponent")
  .component("InteractionComponent")
  .component("script.RunChest")
  .value("TransformComponent", "Scale", vector3(1, 1, 1), "vector3")
  .value("InteractionComponent", "IsLegacy", false, "bool")
  .value("InteractionComponent", "ColliderType", 2, "integer")
  .value("InteractionComponent", "CircleRadius", 1.35, "number")
  .value("InteractionComponent", "ActionName", "강화 상자 열기", "string")
  .value("InteractionComponent", "ShowActionInfo", true, "bool");

b.child("Visual", ["TransformComponent", "SpriteRendererComponent"])
  .childValue("Visual", "TransformComponent", "Position", vector3(0, 0.12, -0.01), "vector3")
  .childValue("Visual", "TransformComponent", "Scale", vector3(0.78, 0.78, 1), "vector3")
  // MapleStory 공식 보물상자(npc/1052008.img stand) animationclip.
  .childValue("Visual", "SpriteRendererComponent", "SpriteRUID", "346f6996f7384892b10bb417e0506604", "string")
  .childValue("Visual", "SpriteRendererComponent", "SortingLayer", "MapLayer0", "string")
  .childValue("Visual", "SpriteRendererComponent", "OrderInLayer", 105, "integer");

b.write(file, { strict: true, lint: true });
console.log("[RunChestModel] wrote " + file);
