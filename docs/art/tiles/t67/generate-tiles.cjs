const fs = require("node:fs");
const path = require("node:path");

const themes = {
  mulung: [
    {name:"00_peach_earth", c:["#6d4c35","#9b7048","#c79c67","#f0c79b"], motif:"petal"},
    {name:"01_dojo_stone", c:["#4d5450","#707b70","#98a28e","#c8c69e"], motif:"stone"},
    {name:"02_bamboo_walk", c:["#405b35","#6f8746","#9fab61","#d6c87b"], motif:"bamboo"},
    {name:"03_cloud_cliff", c:["#18252c","#29404a","#48616a","#91a5a0"], motif:"mist"},
  ],
  minar: [
    {name:"00_ancient_moss", c:["#294a30","#47713d","#71985a","#a8bd76"], motif:"moss"},
    {name:"01_leaf_floor", c:["#35503b","#5e7850","#8c9e68","#cad08a"], motif:"leaf"},
    {name:"02_dragon_scale", c:["#384b49","#566f64","#7e9277","#b7ae76"], motif:"scale"},
    {name:"03_thorn_depth", c:["#15231f","#263c31","#3f5a3d","#715b3c"], motif:"thorn"},
  ],
  temple: [
    {name:"00_memory_marble", c:["#6a706f","#929a94","#bdc1ad","#e0d7b7"], motif:"marble"},
    {name:"01_weathered_slab", c:["#555e5b","#78827a","#a3aa93","#cec79f"], motif:"slab"},
    {name:"02_time_sigil", c:["#4d515a","#707582","#9ca0a4","#d6ba67"], motif:"sigil"},
    {name:"03_time_void", c:["#171a25","#292d3e","#42475c","#777089"], motif:"void"},
  ],
  omega: [
    {name:"00_hq_steel", c:["#293b49","#455e6d","#718896","#a9bac0"], motif:"panel"},
    {name:"01_warning_plate", c:["#313a43","#56616b","#828b91","#d6b84f"], motif:"warning"},
    {name:"02_alien_circuit", c:["#253f46","#38626a","#538b86","#8bc3a4"], motif:"circuit"},
    {name:"03_energy_trench", c:["#151c2a","#28364a","#3c5570","#58b9bb"], motif:"energy"},
  ],
};

const rect = (x,y,w,h,fill,opacity=1) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" opacity="${opacity}"/>`;
function motif(kind,c) {
  const p=[];
  if(kind==="petal") for(const [x,y] of [[4,5],[17,3],[9,18],[21,15]]) p.push(rect(x,y,2,1,c[3]),rect(x+1,y+1,1,1,c[2]));
  if(kind==="stone"||kind==="marble"||kind==="slab") { p.push(rect(0,0,25,1,c[2]),rect(0,12,25,1,c[0]),rect(12,0,1,12,c[0]),rect(6,13,1,12,c[0]),rect(19,13,1,12,c[0])); if(kind!=="stone") p.push(rect(3,5,5,1,c[3]),rect(15,18,6,1,c[2])); }
  if(kind==="bamboo") { for(let x=2;x<25;x+=7){p.push(rect(x,0,4,25,c[2]),rect(x,6,4,1,c[0]),rect(x,17,4,1,c[0]));} p.push(rect(0,3,25,1,c[3]),rect(0,21,25,1,c[0])); }
  if(kind==="mist") for(let y=3;y<25;y+=6){p.push(rect(1,y,10,1,c[3],.55),rect(11,y+1,8,1,c[2],.5),rect(19,y,5,1,c[3],.55));}
  if(kind==="moss") { for(const [x,y,w] of [[1,4,7],[12,2,9],[4,15,10],[17,20,7]]){p.push(rect(x,y,w,2,c[2]),rect(x+2,y+2,3,1,c[3]));} }
  if(kind==="leaf") for(const [x,y] of [[3,4],[14,3],[8,13],[19,17],[2,21]]){p.push(rect(x+1,y,3,1,c[3]),rect(x,y+1,5,2,c[2]),rect(x+1,y+3,3,1,c[0]));}
  if(kind==="scale") for(let y=1;y<25;y+=6) for(let x=(y%12?0:3);x<25;x+=6){p.push(rect(x+1,y,4,1,c[3]),rect(x,y+1,6,3,c[2]),rect(x+1,y+4,4,1,c[0]));}
  if(kind==="thorn") { for(let x=0;x<25;x+=6){p.push(rect(x,0,2,25,c[2]),rect(x+2,5,2,2,c[3]),rect(x+2,16,2,2,c[3]));} }
  if(kind==="sigil") { p.push(rect(10,3,5,1,c[3]),rect(7,4,11,1,c[3]),rect(5,6,3,3,c[3]),rect(17,6,3,3,c[3]),rect(4,9,1,7,c[3]),rect(20,9,1,7,c[3]),rect(6,17,3,3,c[3]),rect(16,17,3,3,c[3]),rect(9,21,7,1,c[3]),rect(11,10,3,6,c[3]),rect(14,14,4,2,c[3])); }
  if(kind==="void") for(let y=2;y<25;y+=5){p.push(rect((y*3)%9,y,12,1,c[3],.5),rect(((y*3)%9)+4,y+1,14,1,c[2],.55));}
  if(kind==="panel") { p.push(rect(0,0,25,1,c[2]),rect(0,24,25,1,c[0]),rect(0,12,25,1,c[0]),rect(12,0,1,25,c[0])); for(const [x,y] of [[2,2],[22,2],[2,22],[22,22]])p.push(rect(x,y,1,1,c[3])); }
  if(kind==="warning") { for(let x=-8;x<32;x+=8){p.push(rect(x,0,4,25,c[3]),rect(x+4,0,4,25,c[0]));} p.push(rect(0,0,25,2,c[2]),rect(0,23,25,2,c[2])); }
  if(kind==="circuit") { p.push(rect(2,5,9,2,c[3]),rect(9,5,2,7,c[3]),rect(9,10,8,2,c[3]),rect(15,10,2,9,c[3]),rect(15,17,8,2,c[3])); for(const [x,y] of [[2,4],[21,16],[7,9]])p.push(rect(x,y,3,3,c[2])); }
  if(kind==="energy") { p.push(rect(0,9,25,7,c[2]),rect(0,11,25,3,c[3]),rect(0,7,25,1,c[0]),rect(0,17,25,1,c[0])); for(let x=2;x<25;x+=6)p.push(rect(x,10,2,5,c[1])); }
  return p.join("");
}

for(const [theme,tiles] of Object.entries(themes)) {
  const dir=path.join(__dirname,theme); fs.mkdirSync(dir,{recursive:true});
  for(const tile of tiles) {
    const c=tile.c;
    const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 25" width="100%" height="100%" style="image-rendering:pixelated;image-rendering:crisp-edges">${rect(0,0,25,25,c[1])}${rect(0,0,25,2,c[2])}${rect(0,23,25,2,c[0])}${motif(tile.motif,c)}</svg>`;
    fs.writeFileSync(path.join(dir,tile.name+".svg"),svg);
  }
}
console.log("T67 tile SVG sources generated");
