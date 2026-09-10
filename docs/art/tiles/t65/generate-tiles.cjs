const fs = require("node:fs");
const path = require("node:path");

const outDir = __dirname;
const themes = {
  luduslake: [
    {name:"00_tower_block", c:["#59627a","#7787a3","#aeb8c9","#e8cf76"], motif:"block"},
    {name:"01_clockwork_plate", c:["#465268","#68788f","#9aa9bb","#d8b451"], motif:"gear"},
    {name:"02_eos_bridge", c:["#4e5a67","#71808b","#a8b1b5","#e4c05e"], motif:"rail"},
    {name:"03_tower_shaft", c:["#111828","#222d40","#34445c","#71809a"], motif:"shaft"},
  ],
  ludibrium: [
    {name:"00_toy_block", c:["#b84f57","#df7d72","#f0bd78","#fff0b0"], motif:"toy"},
    {name:"01_factory_floor", c:["#526479","#788ca0","#aab7bf","#e4b85e"], motif:"plate"},
    {name:"02_clock_tile", c:["#65508a","#8d72ad","#c3a9cc","#f3d37a"], motif:"clock"},
    {name:"03_gear_pit", c:["#251c32","#3b2d4c","#59446c","#9878a7"], motif:"shaft"},
  ],
  nihal: [
    {name:"00_desert_sand", c:["#9a6b3a","#c79052","#e4bc74","#f3dda2"], motif:"sand"},
    {name:"01_wind_sand", c:["#a46e39","#d09a58","#edc97f","#ffe5a8"], motif:"dune"},
    {name:"02_ruin_slab", c:["#7c684f","#a58b65","#cbb58c","#ead7ad"], motif:"slab"},
    {name:"03_quicksand", c:["#5f3e2a","#885b34","#b77b3e","#d9a45e"], motif:"quicksand"},
  ],
  magatia: [
    {name:"00_lab_tile", c:["#33484a","#4f6663","#77907f","#b3bd87"], motif:"plate"},
    {name:"01_alchemy_floor", c:["#3e4350","#5d6573","#88929c","#d1bc72"], motif:"rune"},
    {name:"02_metal_grate", c:["#30383e","#4b5960","#718087","#a6b1a7"], motif:"grate"},
    {name:"03_chemical_channel", c:["#173b39","#255c50","#3b8b68","#82c879"], motif:"chemical"},
  ],
};

const rect=(x,y,w,h,fill,opacity=1)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" opacity="${opacity}"/>`;
function motif(kind,c){
  const p=[];
  if(kind==="block"||kind==="plate"){
    p.push(rect(3,3,44,3,c[0]),rect(53,3,44,3,c[0]),rect(48,6,4,41,c[0]),rect(24,52,4,45,c[0]),rect(75,52,4,45,c[0]));
    p.push(rect(9,11,5,5,c[3]),rect(58,60,5,5,c[3]));
  }else if(kind==="gear"||kind==="clock"){
    p.push(`<circle cx="50" cy="50" r="25" fill="${c[0]}"/><circle cx="50" cy="50" r="18" fill="${c[2]}"/><circle cx="50" cy="50" r="7" fill="${c[3]}"/>`);
    for(const [x,y,w,h] of [[47,13,6,12],[47,75,6,12],[13,47,12,6],[75,47,12,6]])p.push(rect(x,y,w,h,c[0]));
    if(kind==="clock")p.push(rect(48,28,4,23,c[3]),rect(49,49,18,4,c[3]));
  }else if(kind==="rail"){
    p.push(rect(0,18,100,7,c[3]),rect(0,73,100,7,c[3]));for(let x=8;x<100;x+=18)p.push(rect(x,18,5,62,c[0]));
  }else if(kind==="shaft"){
    p.push(rect(0,0,100,9,c[3],.55));for(let y=14;y<96;y+=18)p.push(rect((y*3)%31,y,65,4,c[2],.65));
  }else if(kind==="toy"){
    for(const [x,y,col] of [[8,10,c[3]],[58,12,c[2]],[18,58,c[2]],[66,62,c[3]]]){p.push(rect(x,y,28,24,col),rect(x+4,y+4,8,8,c[0],.45));}
  }else if(kind==="sand"){
    for(const [x,y] of [[10,15],[38,8],[72,23],[20,62],[55,80],[86,56]])p.push(rect(x,y,6,3,c[3]));
  }else if(kind==="dune"){
    for(let y=14;y<96;y+=20){p.push(rect(5,y,36,4,c[3]),rect(41,y+4,36,4,c[2]),rect(77,y,18,4,c[3]));}
  }else if(kind==="slab"){
    p.push(rect(4,5,92,4,c[0]),rect(4,49,92,4,c[0]),rect(47,5,4,92,c[0]),rect(17,19,7,5,c[3]),rect(70,70,8,5,c[3]));
  }else if(kind==="quicksand"){
    for(let r=36;r>5;r-=8)p.push(`<ellipse cx="50" cy="50" rx="${r}" ry="${Math.max(4,Math.floor(r/3))}" fill="none" stroke="${r%16===4?c[3]:c[0]}" stroke-width="4"/>`);
  }else if(kind==="rune"){
    p.push(`<path d="M50 16 L74 38 L65 75 L35 75 L26 38 Z" fill="none" stroke="${c[3]}" stroke-width="5"/>`,`<circle cx="50" cy="50" r="10" fill="${c[2]}"/>`);
  }else if(kind==="grate"){
    for(let x=7;x<100;x+=16)p.push(rect(x,0,5,100,c[0]));for(let y=8;y<100;y+=18)p.push(rect(0,y,100,4,c[3],.55));
  }else if(kind==="chemical"){
    for(let y=12;y<96;y+=22)p.push(rect(4,y,33,5,c[3]),rect(37,y+4,34,5,c[2]),rect(71,y,25,5,c[3]));for(const [x,y] of [[17,31],[68,24],[45,72],[84,80]])p.push(`<circle cx="${x}" cy="${y}" r="4" fill="${c[3]}"/>`);
  }
  return p.join("");
}
for(const [theme,tiles] of Object.entries(themes)){
  const dir=path.join(outDir,theme);fs.mkdirSync(dir,{recursive:true});
  for(const tile of tiles){const c=tile.c;const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%" style="image-rendering:pixelated;image-rendering:crisp-edges">${rect(0,0,100,100,c[1])}${rect(0,0,100,6,c[2])}${rect(0,94,100,6,c[0])}${motif(tile.motif,c)}</svg>`;fs.writeFileSync(path.join(dir,`${tile.name}.svg`),svg);}
}
console.log("T65 tile SVG sources generated");
