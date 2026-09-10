const fs=require("node:fs"),path=require("node:path");
const themes={
 future:[
  {name:"00_fallen_stone",c:["#27252f","#464251","#6c6676","#958aa2"],motif:"crack"},
  {name:"01_knight_court",c:["#31313d","#515260","#777986","#aaa6b4"],motif:"court"},
  {name:"02_dark_ereve_sigil",c:["#282038","#49355c","#72577d","#b29abb"],motif:"ereve"},
  {name:"03_dream_void",c:["#100f1a","#211b31","#3d2b50","#74527b"],motif:"void"},
 ],
 twilight:[
  {name:"00_desolate_rock",c:["#533a31","#795346","#a8775b","#d39a70"],motif:"rock"},
  {name:"01_burnt_land",c:["#402923","#6a4030","#985f40","#d28a53"],motif:"ember"},
  {name:"02_excavation_mask",c:["#4b3f38","#716055","#9a8570","#c5ab83"],motif:"mask"},
  {name:"03_black_magma",c:["#1e1718","#3a2420","#73382b","#d36a35"],motif:"magma"},
 ],
};
const rect=(x,y,w,h,fill,opacity=1)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" opacity="${opacity}"/>`;
function motif(kind,c){const p=[];
 if(kind==="crack"){p.push(rect(3,5,8,1,c[2]),rect(10,6,1,5,c[0]),rect(10,10,6,1,c[0]),rect(16,9,1,5,c[0]),rect(17,13,5,1,c[2]),rect(4,18,7,1,c[0]),rect(11,17,1,4,c[0]));}
 if(kind==="court"){p.push(rect(0,0,25,1,c[3]),rect(0,12,25,1,c[0]),rect(12,0,1,12,c[0]),rect(6,13,1,12,c[0]),rect(19,13,1,12,c[0]));for(const[x,y]of[[2,3],[21,3],[3,20],[16,17]])p.push(rect(x,y,2,2,c[2]));}
 if(kind==="ereve"){p.push(rect(11,3,3,4,c[3]),rect(7,6,11,2,c[2]),rect(5,8,3,7,c[2]),rect(17,8,3,7,c[2]),rect(7,15,4,3,c[3]),rect(14,15,4,3,c[3]),rect(10,18,5,4,c[2]),rect(11,10,3,5,c[0]));}
 if(kind==="void"){for(let y=2;y<25;y+=5){p.push(rect((y*2)%8,y,11,1,c[3],.65),rect(((y*2)%8)+5,y+1,14,1,c[2],.55));}p.push(rect(0,10,25,5,c[0],.45));}
 if(kind==="rock"){for(const[x,y,w]of[[1,4,8],[13,2,9],[4,14,11],[17,20,7]]){p.push(rect(x,y,w,2,c[2]),rect(x+2,y+2,Math.max(2,w-4),1,c[3]));}p.push(rect(0,23,25,2,c[0]));}
 if(kind==="ember"){for(const[x,y]of[[3,4],[17,3],[8,12],[21,16],[4,21]]){p.push(rect(x,y,2,1,c[3]),rect(x+1,y+1,1,2,c[2]));}p.push(rect(0,8,25,1,c[0]),rect(10,9,1,6,c[0]),rect(10,14,8,1,c[0]));}
 if(kind==="mask"){p.push(rect(3,3,8,8,c[2]),rect(14,13,8,8,c[2]),rect(5,5,2,2,c[0]),rect(8,5,2,2,c[0]),rect(6,8,3,1,c[3]),rect(16,15,2,2,c[0]),rect(19,15,2,2,c[0]),rect(17,18,3,1,c[3]));}
 if(kind==="magma"){p.push(rect(0,9,25,8,c[2]),rect(0,11,25,4,c[3]));for(let x=1;x<25;x+=6){p.push(rect(x,8,3,2,c[3]),rect(x+2,16,3,2,c[2]));}p.push(rect(0,7,25,1,c[0]),rect(0,18,25,1,c[0]));}
 return p.join("");}
for(const[theme,tiles]of Object.entries(themes)){const dir=path.join(__dirname,theme);fs.mkdirSync(dir,{recursive:true});for(const tile of tiles){const c=tile.c;const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 25" width="100%" height="100%" style="image-rendering:pixelated;image-rendering:crisp-edges">${rect(0,0,25,25,c[1])}${rect(0,0,25,2,c[2])}${rect(0,23,25,2,c[0])}${motif(tile.motif,c)}</svg>`;fs.writeFileSync(path.join(dir,tile.name+".svg"),svg);}}
console.log("T68 tile SVG sources generated");
