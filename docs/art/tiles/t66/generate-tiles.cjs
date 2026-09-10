const fs = require("node:fs");
const path = require("node:path");

const outDir = __dirname;
const rect = (x, y, w, h, fill, opacity = 1) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" opacity="${opacity}"/>`;

const tiles = [
  {
    theme: "sleepywood",
    name: "08_lava_fissure",
    draw() {
      const p = [rect(0, 0, 100, 100, "#242a27"), rect(0, 0, 100, 6, "#39423a"), rect(0, 94, 100, 6, "#151917")];
      for (const [x, y, w, h] of [[5,15,20,4],[72,12,19,4],[12,61,23,4],[68,72,24,4],[40,35,18,3]]) p.push(rect(x,y,w,h,"#343c35"));
      const crack = [[48,0,5,17],[43,14,9,6],[42,19,5,14],[35,29,10,6],[34,34,5,16],[30,47,8,6],[31,51,5,16],[25,64,9,6],[24,69,5,14],[18,80,9,6],[17,85,5,15]];
      for (const [x,y,w,h] of crack) p.push(rect(x,y,w,h,"#7e2d16"));
      for (const [x,y,w,h] of crack.map(([x,y,w,h])=>[x+1,y+1,Math.max(2,w-2),Math.max(2,h-2)])) p.push(rect(x,y,w,h,"#e75a1b"));
      for (const [x,y,w,h] of [[49,1,2,15],[44,16,6,2],[43,21,2,10],[36,31,7,2],[35,36,2,12],[31,49,5,2],[32,53,2,12],[26,66,6,2],[25,71,2,10],[19,82,6,2],[18,87,2,11]]) p.push(rect(x,y,w,h,"#ffd05a"));
      return p.join("");
    },
  },
  {
    theme: "orbis",
    name: "08_eliza_moon_garden",
    draw() {
      const p = [rect(0, 0, 100, 100, "#53699a"), rect(0, 0, 100, 6, "#7184b0"), rect(0, 94, 100, 6, "#33466f")];
      for (const [x,y] of [[12,16],[42,11],[78,23],[26,58],[63,73],[88,54]]) p.push(rect(x-2,y,8,3,"#efd77c"),rect(x,y-2,3,8,"#efd77c"));
      for (const [x,y] of [[18,37],[53,29],[77,66],[37,82]]) {
        p.push(rect(x-2,y+5,4,8,"#354e58"),rect(x-7,y,14,6,"#6d906d"),rect(x-5,y-4,10,5,"#90aa79"));
        p.push(rect(x-2,y-7,5,5,"#f0b1c0"),rect(x-5,y-4,11,5,"#d66f94"),rect(x-2,y-1,5,5,"#f4d67b"));
      }
      p.push(rect(4,47,92,3,"#40567f",0.65));
      return p.join("");
    },
  },
  {
    theme: "nihal",
    name: "08_oasis_water",
    draw() {
      const p = [rect(0,0,100,100,"#2f8f9d"),rect(0,0,100,7,"#d0a963"),rect(0,93,100,7,"#9c713d")];
      for(let y=14;y<91;y+=18){
        p.push(rect(5,y,25,4,"#8ed3ca"),rect(30,y+4,30,4,"#58b8b2"),rect(60,y,34,4,"#9fe1d3"));
        p.push(rect(12,y+8,18,3,"#257786"),rect(68,y+8,20,3,"#257786"));
      }
      for(const [x,y] of [[9,9],[84,11],[18,86],[72,87]]) p.push(rect(x,y,7,3,"#ead08f"));
      return p.join("");
    },
  },
];

for (const tile of tiles) {
  const dir = path.join(outDir, tile.theme);
  fs.mkdirSync(dir, { recursive: true });
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%" shape-rendering="crispEdges" style="image-rendering:pixelated">${tile.draw()}</svg>`;
  fs.writeFileSync(path.join(dir, `${tile.name}.svg`), svg);
}

console.log("T66 correction tile SVG sources generated");
