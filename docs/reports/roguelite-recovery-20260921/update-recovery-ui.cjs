const {UIBuilder}=require('../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs');
const b=UIBuilder.load('ui/SkillBar.ui');
b.panel('AbilityOffer',{anchor:'bottom-right',pos:[-20,158],rect_size:[680,270],color:'#202C39',alpha:0.96,enable:false});
b.text('AbilityOffer/Title','능력 발견',{anchor:'top-left',pos:[20,-12],rect_size:[640,36],size:28,alignment:3});
b.sprite('AbilityOffer/Icon',{anchor:'top-left',pos:[20,-60],rect_size:[80,80],color:'#FFFFFF',sprite_type:0});
b.text('AbilityOffer/Details','',{anchor:'top-left',pos:[116,-55],rect_size:[544,100],size:24,alignment:0,bestfit:true,min_size:22,max_size:24});
for(let i=1;i<=5;i++)b.button('AbilityOffer/Replace'+i,i+'번 교체',{anchor:'bottom-left',pos:[16+(i-1)*108,16],rect_size:[92,88],font_size:23,bg_color:'#35516B'});
b.button('AbilityOffer/Decline','포기',{anchor:'bottom-left',pos:[556,16],rect_size:[108,88],font_size:24,bg_color:'#604B4B'});
b.write('ui/SkillBar.ui',{bind:{mlua:'RootDesk/MyDesk/UI/SkillBar.mlua',props:{offerPanel:'AbilityOffer'}}});
// RoomProgress.ui is currently locked by the editor; its new-mode layout is
// applied through documented UITransform properties in RoomProgressHud instead.
console.log(JSON.stringify(UIBuilder.snapshot('ui/SkillBar.ui')));
