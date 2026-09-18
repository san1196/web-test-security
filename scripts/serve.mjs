import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {resolve,dirname,extname,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const publicDir=resolve(dirname(fileURLToPath(import.meta.url)),'../public');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.sql':'text/plain; charset=utf-8','.zip':'application/zip'};
export function makeServer(){return createServer(async(req,res)=>{
 try{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'});return res.end();}
  const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const file=resolve(publicDir,'.'+(path==='/'?'/index.html':path));
  if(!file.startsWith(publicDir+sep)){res.writeHead(403);return res.end('Forbidden');}
  const s=await stat(file);if(!s.isFile()){res.writeHead(404);return res.end('Not found');}
  const content=await readFile(file);res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream','Content-Length':content.length,'Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:content);
 }catch(e){res.writeHead(e.code==='ENOENT'?404:400);res.end(e.code==='ENOENT'?'Not found':'Invalid request');}
 });}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){const port=Number(process.env.PORT||3000);const server=makeServer();server.listen(port,'127.0.0.1',()=>console.log(`Cyber Security Lab: http://127.0.0.1:${server.address().port}`));server.on('error',e=>{console.error(e.message);process.exitCode=1;});}
