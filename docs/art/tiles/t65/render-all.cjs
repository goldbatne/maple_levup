const fs=require("node:fs");
const path=require("node:path");
const sharp=require("C:/Users/dddd/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp");
const themes=["luduslake","ludibrium","nihal","magatia"];
async function main(){
  for(const theme of themes){const dir=path.join(__dirname,theme);for(const input of fs.readdirSync(dir).filter(n=>n.endsWith(".svg")).sort()){const output=input.replace(/\.svg$/,".png");await sharp(path.join(dir,input),{density:96}).resize(100,100,{kernel:"nearest"}).png().toFile(path.join(dir,output));process.stdout.write(`${theme}/${output}\n`);}}
  const tiles=[];for(const theme of themes)for(const name of fs.readdirSync(path.join(__dirname,theme)).filter(n=>n.endsWith(".png")).sort())tiles.push(await sharp(path.join(__dirname,theme,name)).resize(160,160,{kernel:"nearest"}).toBuffer());
  await sharp({create:{width:640,height:640,channels:4,background:"#20252c"}}).composite(tiles.map((input,i)=>({input,left:(i%4)*160,top:Math.floor(i/4)*160}))).png().toFile(path.join(__dirname,"contact-sheet.png"));
}
main().catch(e=>{console.error(e);process.exit(1);});
