const fs = require("node:fs");
const path = require("node:path");
const sharp = require("C:/Users/dddd/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp");
const themes = ["sleepywood", "orbis", "elnath", "aqua"];

async function main() {
for (const theme of themes) {
  const dir = path.join(__dirname, theme);
  const inputs = fs.readdirSync(dir).filter((name) => name.endsWith(".svg")).sort();
  for (const input of inputs) {
    const output = input.replace(/\.svg$/, ".png");
    await sharp(path.join(dir, input), { density: 96 })
      .resize(100, 100, { kernel: "nearest" })
      .png()
      .toFile(path.join(dir, output));
    process.stdout.write(`${theme}/${output}\n`);
  }
}
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
