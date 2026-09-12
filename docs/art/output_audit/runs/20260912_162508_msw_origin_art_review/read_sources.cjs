const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root='D:/maplestory_levup',run=__dirname;
const {ModelBuilder}=require(root+'/.agents/skills/msw-general/scripts/model/msw_model_builder.cjs');
const {getResourcesBatch}=require(root+'/.agents/skills/msw-search/scripts/msw_resource_api.cjs');
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);}
async function main(){
 const rows=JSON.parse(fs.readFileSync(run+'/records.json','utf8'));
 const models=walk(root+'/RootDesk/MyDesk/Models/Monsters').filter(p=>p.endsWith('.model')).map(p=>{let b=ModelBuilder.read(p);return {path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),snapshot:b.snapshot(),values:b.listValues(),children:b.listChildren()};});
 fs.writeFileSync(run+'/model_snapshots.json',JSON.stringify(models,null,2));
 const ids=[...new Set(rows.map(r=>r.monster_image_ruid))]; let all=[];
 for(let i=0;i<ids.length;i+=35){let result=await getResourcesBatch(ids.slice(i,i+35));fs.writeFileSync(run+'/resource_batch_'+i+'.json',JSON.stringify({queried_at:new Date().toISOString(),ids:ids.slice(i,i+35),endpoint:'GET/POST MSW public v3 resources via validated wrapper',result},null,2));let list=Array.isArray(result)?result:result.items||result.results||[];all.push(...list);console.log('batch',i,'returned',list.length);}
 fs.writeFileSync(run+'/resource_metadata.json',JSON.stringify(all,null,2));console.log('models',models.length,'resources',all.length,'sample',JSON.stringify(all[0]));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
