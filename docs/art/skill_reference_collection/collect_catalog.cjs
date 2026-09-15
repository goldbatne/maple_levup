const fs = require('node:fs');
const path = require('node:path');
const api = require('../../../.agents/skills/msw-search/scripts/msw_resource_api.cjs');
const out = __dirname;
(async()=>{
 const statePath=path.join(out,'catalog_state.json');
 let state=fs.existsSync(statePath)?JSON.parse(fs.readFileSync(statePath,'utf8')):{pages:0,offset:null,complete:false};
 if(state.complete){console.log(JSON.stringify(state));return;}
 do {
  const r=await api.listResources({resourceTypeFilter:['resource_pack'],categoryFilter:['skill'],limit:100,...(state.offset?{offset:state.offset}:{})});
  fs.writeFileSync(path.join(out,`page_${String(state.pages).padStart(4,'0')}.json`),JSON.stringify(r));
  state={pages:state.pages+1,offset:r.nextOffset||null,complete:!r.nextOffset,updated:new Date().toISOString()};
  fs.writeFileSync(statePath,JSON.stringify(state,null,2));
  console.log(JSON.stringify({page:state.pages,count:r.items?.length,...state}));
 }while(!state.complete);
})().catch(e=>{console.error(e);process.exitCode=1;});
