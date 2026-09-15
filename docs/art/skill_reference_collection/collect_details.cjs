const fs=require('node:fs'),path=require('node:path');
const api=require('../../../.agents/skills/msw-search/scripts/msw_resource_api.cjs');
const root=__dirname, dest=path.join(root,'details');fs.mkdirSync(dest,{recursive:true});
const packs=fs.readdirSync(root).filter(n=>/^page_\d+\.json$/.test(n)).flatMap(n=>JSON.parse(fs.readFileSync(path.join(root,n))).items);
const ids=[...new Set(packs.flatMap(p=>p.payload.elements).filter(e=>['sprite','animationclip'].includes(e.resource_type)).map(e=>e.ruid))];
(async()=>{
 for(let i=0;i<ids.length;i+=100){
  const file=path.join(dest,`batch_${String(i/100).padStart(4,'0')}.json`);
  if(fs.existsSync(file))continue;
  const r=await api.getResourcesBatch(ids.slice(i,i+100));fs.writeFileSync(file,JSON.stringify(r));
  fs.writeFileSync(path.join(root,'detail_state.json'),JSON.stringify({processed:Math.min(i+100,ids.length),total:ids.length,complete:i+100>=ids.length,updated:new Date().toISOString()},null,2));
  if(i%2000===0)console.log(`${i+100}/${ids.length}`);
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
