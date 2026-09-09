const fs = require("node:fs");
const path = require("node:path");

const outDir = __dirname;

const themes = {
  sleepywood: [
    { name: "00_moss_stone", colors: ["#24352b", "#314b36", "#496742", "#6e8652"], motif: "moss" },
    { name: "01_damp_stone", colors: ["#202b28", "#33413a", "#46594b", "#66705b"], motif: "crack" },
    { name: "02_temple_slab", colors: ["#2b2926", "#45403a", "#62584c", "#8a785f"], motif: "slab" },
    { name: "03_chasm", colors: ["#0d1210", "#171d19", "#253029", "#3b493a"], motif: "void" },
  ],
  orbis: [
    { name: "00_cloud", colors: ["#a9c9d9", "#d3e6eb", "#eef5f1", "#fff7d7"], motif: "cloud" },
    { name: "01_sky_marble", colors: ["#779ebd", "#a7c7db", "#d8e8ec", "#f5e7ad"], motif: "slab" },
    { name: "02_star_path", colors: ["#526a9a", "#7387b3", "#b1bddd", "#f3dc83"], motif: "star" },
    { name: "03_sky_void", colors: ["#24436f", "#315d8f", "#4f82ae", "#9fcfe0"], motif: "void" },
  ],
  elnath: [
    { name: "00_snow", colors: ["#8da8b5", "#bdd0d5", "#e2ebea", "#fff9df"], motif: "snow" },
    { name: "01_packed_snow", colors: ["#708f9d", "#9db7c0", "#ccdadd", "#eef1e7"], motif: "crack" },
    { name: "02_ice", colors: ["#477b9b", "#6ca5bd", "#a7d0d7", "#dff2ef"], motif: "slab" },
    { name: "03_crevasse", colors: ["#173650", "#255776", "#3d7f99", "#7eb6c4"], motif: "void" },
  ],
  aqua: [
    { name: "00_seabed", colors: ["#6b7f72", "#8fa28b", "#b7b990", "#d7cba2"], motif: "sand" },
    { name: "01_coral_sand", colors: ["#7d7770", "#aa947f", "#cbb49a", "#e3cfaa"], motif: "shell" },
    { name: "02_ruin_path", colors: ["#3f6670", "#66858a", "#8ea5a0", "#bdc9b5"], motif: "slab" },
    { name: "03_deep_water", colors: ["#092f4a", "#125476", "#1f7892", "#4ea7ad"], motif: "wave" },
  ],
};

function rect(x, y, w, h, fill, opacity = 1) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" opacity="${opacity}"/>`;
}

function motif(kind, c) {
  const p = [];
  if (kind === "slab") {
    p.push(rect(4, 4, 42, 3, c[0]), rect(54, 4, 42, 3, c[0]));
    p.push(rect(48, 7, 3, 40, c[0]), rect(24, 50, 3, 46, c[0]), rect(75, 50, 3, 46, c[0]));
    p.push(rect(7, 10, 4, 4, c[3]), rect(58, 58, 5, 4, c[3]));
  } else if (kind === "void") {
    for (let y = 8; y < 96; y += 14) p.push(rect((y * 3) % 38, y, 62, 4, c[2], 0.7));
    p.push(rect(0, 0, 100, 7, c[3], 0.45));
  } else if (kind === "wave") {
    for (let y = 10; y < 95; y += 18) {
      p.push(rect(6, y, 32, 4, c[3]), rect(38, y + 4, 32, 4, c[2]), rect(70, y, 24, 4, c[3]));
    }
  } else if (kind === "cloud") {
    p.push(rect(8, 18, 36, 8, c[3]), rect(22, 10, 44, 8, c[3]), rect(54, 18, 38, 8, c[3]));
    p.push(rect(2, 68, 40, 7, c[1]), rect(30, 60, 46, 7, c[3]), rect(68, 68, 30, 7, c[1]));
  } else if (kind === "star") {
    for (const [x, y] of [[18,18],[72,14],[48,48],[15,76],[82,72]]) {
      p.push(rect(x - 2, y, 8, 3, c[3]), rect(x, y - 2, 3, 8, c[3]));
    }
  } else if (kind === "snow") {
    for (const [x, y] of [[12,18],[42,10],[78,22],[25,58],[62,70],[88,54]]) {
      p.push(rect(x, y, 3, 3, c[3]), rect(x + 3, y + 3, 3, 3, c[1]));
    }
  } else if (kind === "shell") {
    p.push(rect(16, 20, 10, 4, c[3]), rect(13, 24, 16, 4, c[2]), rect(16, 28, 10, 4, c[3]));
    p.push(rect(68, 65, 8, 4, c[3]), rect(65, 69, 14, 4, c[2]), rect(68, 73, 8, 4, c[3]));
  } else if (kind === "sand") {
    for (const [x, y] of [[12,16],[39,9],[72,21],[19,63],[55,78],[88,55]]) p.push(rect(x, y, 5, 3, c[3]));
  } else if (kind === "moss") {
    p.push(rect(0, 0, 100, 9, c[2]), rect(8, 9, 22, 5, c[3]), rect(62, 9, 30, 5, c[3]));
    p.push(rect(14, 34, 7, 5, c[3]), rect(74, 66, 9, 5, c[2]));
  } else {
    p.push(rect(12, 22, 28, 3, c[0]), rect(38, 25, 3, 18, c[0]), rect(64, 60, 25, 3, c[0]));
  }
  return p.join("");
}

for (const [theme, tiles] of Object.entries(themes)) {
  const themeDir = path.join(outDir, theme);
  fs.mkdirSync(themeDir, { recursive: true });
  for (const tile of tiles) {
    const c = tile.colors;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%" style="image-rendering:pixelated;image-rendering:crisp-edges">${rect(0,0,100,100,c[1])}${rect(0,0,100,6,c[2])}${rect(0,94,100,6,c[0])}${motif(tile.motif,c)}</svg>`;
    fs.writeFileSync(path.join(themeDir, `${tile.name}.svg`), svg);
  }
}

console.log("T64 tile SVG sources generated");
