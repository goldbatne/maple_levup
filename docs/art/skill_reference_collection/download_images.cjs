const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=__dirname, media=path.join(root,'media');fs.mkdirSync(media,{recursive:true});
const done=new Set(); const log=path.join(root,'downloads.jsonl');
if(fs.existsSync(log))for(const s of fs.readFileSync(log,'utf8').trim().split('\n')){if(!s)continue;const r=JSON.parse(s);if(r.status==='OK'&&fs.existsSync(path.join(root,r.path)))done.add(r.id);}
const attempted=new Set(done);let count=done.size,failed=0,bytes=0;
async function download(r){
 const url=r.payload?.thumbnail;if(!url)return;
 const ext=path.extname(new URL(url).pathname);if(!['.png','.gif','.webp','.jpg'].includes(ext))return;
 const rel=`media/${r.id}${ext}`, file=path.join(root,rel);
 try{const response=await fetch(url,{signal:AbortSignal.timeout(45000)});if(!response.ok)throw Error(`HTTP ${response.status}`);const b=Buffer.from(await response.arrayBuffer());
 const png=b.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])),gif=b.subarray(0,3).toString()==='GIF';
 if((ext==='.png'&&!png)||(ext==='.gif'&&!gif))throw Error('Invalid image signature');
 fs.writeFileSync(file+'.part',b);fs.renameSync(file+'.part',file);bytes+=b.length;count++;
 fs.appendFileSync(log,JSON.stringify({id:r.id,type:r.type,url,path:rel,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex'),status:'OK'})+'\n');
 }catch(e){failed++;fs.appendFileSync(log,JSON.stringify({id:r.id,url,status:'FAILED',error:String(e)})+'\n');}
}
(async()=>{while(true){
 let queue=[];for(const n of fs.readdirSync(path.join(root,'details'))){if(!n.endsWith('.json'))continue;let data;try{data=JSON.parse(fs.readFileSync(path.join(root,'details',n)));}catch{continue;}for(const r of data.items||[]){if(!attempted.has(r.id)){attempted.add(r.id);queue.push(r);}}}
 let next=0;await Promise.all(Array.from({length:40},async()=>{while(next<queue.length){const r=queue[next++];await download(r);if(count%500===0){const s={downloaded:count,failed,bytesThisRun:bytes,complete:false};fs.writeFileSync(path.join(root,'download_state.json'),JSON.stringify(s));console.log(JSON.stringify(s));}}}));
 const complete=JSON.parse(fs.readFileSync(path.join(root,'detail_state.json'))).complete;
 if(complete){fs.writeFileSync(path.join(root,'download_state.json'),JSON.stringify({downloaded:count,failed,bytesThisRun:bytes,complete:true}));break;}
 await new Promise(r=>setTimeout(r,1000));
}})().catch(e=>{console.error(e);process.exitCode=1;});
