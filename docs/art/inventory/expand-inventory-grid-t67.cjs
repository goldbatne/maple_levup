// T67 — 카테고리당 최대 36칸을 넘는 장비를 위해 6x8, 48칸으로 확장한다.
// 구조화 UI는 UIBuilder로만 수정하고 UUID 바인딩도 builder가 주입한다.
const {UIBuilder}=require("../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");
const uiPath="ui/Inventory.ui",controllerPath="RootDesk/MyDesk/UI/InventoryPanel.mlua";
const box="/ui/Inventory/Window/Box",slotRuid="129f02486c2baef49a41b31ce16171f6";
const b=UIBuilder.load(uiPath),bindings={};
for(let i=0;i<48;i++){
  const col=i%6,row=Math.floor(i/6),cell=`${box}/ItemRow${i}`;
  if(b.find(cell)===null){
    b.button(cell,"",{anchor:"top-center",pos:[-250+col*100,-322-row*55],rect_size:[88,53],pivot:[.5,1],image_ruid:slotRuid,sprite_type:1,bg_color:"#E9E6E1",color:"#292E38",font_size:13});
    b.sprite(cell+"/Icon",{anchor:"middle-center",pos:[0,-1],rect_size:[44,44],pivot:[.5,.5],image_ruid:"",preserve_aspect:false,raycast:false,color:"#FFFFFF",alpha:1});
    b.text(cell+"/Count","",{anchor:"bottom-right",pos:[-3,2],rect_size:[48,20],pivot:[1,0],size:13,color:"#FFFFFF",bold:true,outline:true,outline_color:"#252932",outline_width:2,best_fit:true,min_size:10,max_size:13});
  }
  b.patch(cell,{anchor:"top-center",pos:[-250+col*100,-322-row*55],rect_size:[88,53],pivot:[.5,1]});
  b.patch(cell+"/Icon",{anchor:"middle-center",pos:[0,-1],rect_size:[44,44],pivot:[.5,.5]});
  b.patchComponent(cell+"/Icon","MOD.Core.SpriteGUIRendererComponent",{PreserveSprite:0,Color:{r:1,g:1,b:1,a:1}});
  b.patch(cell+"/Count",{anchor:"bottom-right",pos:[-3,2],rect_size:[48,20],pivot:[1,0]});
  bindings[`itemRow${i}`]=cell;
}
b.write(uiPath,{strict:true,lint:true,bind:{mlua:controllerPath,props:bindings}});
console.log("[T67] Inventory 6x8 슬롯 48칸 생성 및 바인딩 완료");
