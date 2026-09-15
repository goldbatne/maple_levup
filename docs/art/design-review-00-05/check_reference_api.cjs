const fs = require('fs');
const path = require('path');
const api = require('../../../.agents/skills/msw-search/scripts/msw_resource_api.cjs');
const out=path.resolve(__dirname,'20260914_astra_review');
const refs=JSON.parse(fs.readFileSync(path.join(out,'references.json'),'utf8'));
const records=JSON.parse(fs.readFileSync(path.join(out,'records.json'),'utf8'));
const ids=[...new Set([...records.map(r=>r.ruid),...refs.flatMap(r=>r.elements.map(e=>e.ruid))])];
(async()=>{
 const results=[];
 for(let i=0;i<ids.length;i+=30){
  try{results.push({requested:ids.slice(i,i+30),response:await api.getResourcesBatch(ids.slice(i,i+30))});}
  catch(e){results.push({requested:ids.slice(i,i+30),error:String(e)});}
 }
 fs.writeFileSync(path.join(out,'LIVE_RESOURCE_API.json'),JSON.stringify(results,null,2));
 console.log(JSON.stringify(results.map(r=>({requested:r.requested.length,error:r.error,responseKeys:Object.keys(r.response||{})}))));
})();
