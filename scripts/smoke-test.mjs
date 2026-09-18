import './verify.mjs';
import {makeServer} from './serve.mjs';
import assert from 'node:assert/strict';
const server=makeServer();await new Promise((ok,fail)=>{server.once('error',fail);server.listen(0,'127.0.0.1',ok);});
const base=`http://127.0.0.1:${server.address().port}`;
try{
 for(const [path,type]of [['/','text/html'],['/app.js','text/javascript'],['/labs.js','text/javascript'],['/style.css','text/css'],['/favicon.svg','image/svg+xml'],['/supabase-schema.sql','text/plain'],['/Paket_Praktik_Cyber_Security.zip','application/zip']]){
  const r=await fetch(base+path);assert.equal(r.status,200,path);assert.ok(r.headers.get('content-type').startsWith(type));const data=await r.arrayBuffer();assert.ok(data.byteLength>0,path);
 }
 assert.equal((await fetch(base+'/missing-file.js')).status,404);
 assert.equal((await fetch(base+'/',{method:'POST'})).status,405);
 assert.equal((await fetch(base+'/',{method:'HEAD'})).status,200);
 console.log('PASS: local HTTP root, all deployed assets/downloads, missing-file 404, HEAD, and method handling.');
}finally{server.closeAllConnections();await new Promise(ok=>server.close(ok));}
