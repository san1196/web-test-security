import {readFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {Script} from 'node:vm';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>readFileSync(resolve(root,p),'utf8');
const config=JSON.parse(read('vercel.json'));
assert.equal(config.framework,null);
assert.equal(config.outputDirectory,'public');
assert.equal(config.buildCommand,'npm run build');
const required=['public/index.html','public/style.css','public/app.js','public/labs.js','public/favicon.svg','public/supabase-schema.sql','public/Paket_Praktik_Cyber_Security.zip'];
for(const p of required)assert.ok(existsSync(resolve(root,p)),`Missing deployment file: ${p}`);
const html=read('public/index.html');
for(const m of html.matchAll(/(?:src|href)="([^"#]+)"/g)){
 if(!/^(https?:|data:)/.test(m[1]))assert.ok(existsSync(resolve(root,'public',m[1])),`Missing asset: ${m[1]}`);
}
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size,'Duplicate element IDs');
for(const m of html.matchAll(/\bfor="([^"]+)"/g))assert.ok(ids.includes(m[1]),`Invalid label target: ${m[1]}`);
for(const p of ['public/app.js','public/labs.js'])new Script(read(p),{filename:p});
for(const m of read('public/app.js').matchAll(/\$\('([^']+)'\)/g))if(!m[1].endsWith('-'))assert.ok(ids.includes(m[1]),`Missing DOM target: ${m[1]}`);
const labs=createRequire(import.meta.url)(resolve(root,'public/labs.js'));assert.equal(labs.length,12);
for(const l of labs)for(const fixed of [false,true])assert.equal(typeof l.run(l.sample,fixed,{}).status,'number');
const get=id=>labs.find(l=>l.id===id);
assert.equal(get('idor').run('1002',false,{}).status,200);assert.equal(get('idor').run('1002',true,{}).status,403);assert.equal(get('idor').run('1001',true,{}).status,200);
assert.equal(get('sqli').run(get('sqli').sample,false,{}).rows.length,3);assert.equal(get('sqli').run(get('sqli').sample,true,{}).rows.length,0);
assert.equal(get('csrf').run('{"email":"demo@example.test"}',true,{}).status,403);assert.equal(get('csrf').run('{"email":"demo@example.test","csrf":"lab-csrf-alice"}',true,{}).status,200);
assert.equal(get('mass').run(get('mass').sample,true,{}).profile.role,'user');
for(const id of ['throttle','coupon']){const s={};let r;for(let i=0;i<4;i++)r=get(id).run(get(id).sample,true,s);assert.equal(r.status,id==='throttle'?429:409);assert.equal(get(id).run(get(id).sample,true,s).status,400);}
assert.ok(get('ddos').run('20',false,{}).ticks.some(t=>t.dropped>0));assert.ok(get('ddos').run('20',true,{}).ticks.every(t=>t.dropped===0));
assert.equal(get('ssrf').run(get('ssrf').sample,true,{}).status,403);assert.equal(get('traversal').run(get('traversal').sample,true,{}).status,403);
console.log('PASS: deployment package, entrypoint, assets, JavaScript syntax, forms, and 12 lab scenarios.');
