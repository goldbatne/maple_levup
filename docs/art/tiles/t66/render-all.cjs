const fs = require("node:fs");
const path = require("node:path");
const sharp = require("C:/Users/dddd/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp");

const themes = ["sleepywood", "orbis", "nihal"];

async function main() {
  const contact = [];
  for (const theme of themes) {
    const dir = path.join(__dirname, theme);
    for (const input of fs.readdirSync(dir).filter((name) => name.endsWith(".svg")).sort()) {
      const output = input.replace(/\.svg$/, ".png");
      const outputPath = path.join(dir, output);
      await sharp(path.join(dir, input), { density: 96 }).resize(100, 100, { kernel: "nearest" }).png().toFile(outputPath);
      contact.push(await sharp(outputPath).resize(240, 240, { kernel: "nearest" }).toBuffer());
      process.stdout.write(`${theme}/${output}\n`);
    }
  }
  await sharp({ create: { width: 720, height: 240, channels: 4, background: "#20252c" } })
    .composite(contact.map((input, index) => ({ input, left: index * 240, top: 0 })))
    .png()
    .toFile(path.join(__dirname, "contact-sheet.png"));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
