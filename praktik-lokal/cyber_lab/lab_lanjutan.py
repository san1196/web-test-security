"""Lab v2 lokal. SSRF/path hanya fixture, tanpa outbound atau akses file OS."""
import argparse, html, json, secrets, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from http.cookies import SimpleCookie
from threading import Lock
MODE='vulnerable';SESSIONS={};COUNTERS={};LOCK=Lock();PROFILE={'display_name':'Alice','role':'vendor','email':'alice@example.test'}
FILES={'public/readme.txt':'Dokumen publik fiktif','private/config.txt':'SECRET-LAB-ONLY'}
PREVIEWS={'https://vendor.example.test/info':'Informasi vendor fiktif','http://internal.example.test/status':'INTERNAL-LAB-ONLY'}
BALANCE=0;USED=False

def over_limit(key, limit):
    now=time.monotonic()
    with LOCK:
        start,count=COUNTERS.get(key,(now,0))
        if now-start>=30:start,count=now,0
        count+=1;COUNTERS[key]=(start,count)
        return count>limit

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,obj,cookie=None,retry=False):
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store')
        if cookie:self.send_header('Set-Cookie',cookie+'; Path=/; HttpOnly; SameSite=Lax')
        if retry:self.send_header('Retry-After','30')
        self.end_headers();self.wfile.write(json.dumps(obj).encode())
    def session(self):
        cookie=SimpleCookie()
        try:cookie.load(self.headers.get('Cookie',''))
        except Exception:return None
        item=cookie.get('sid');return SESSIONS.get(item.value) if item else None
    def do_GET(self):
        u=urlparse(self.path);q=parse_qs(u.query,keep_blank_values=True)
        if u.path=='/':self.reply(200,{'mode':MODE,'notice':'Lab fixture only','endpoints':['/limited','/preview','/file','/profile','/preferences','/coupon']})
        elif u.path=='/limited':
            if MODE=='fixed' and over_limit('limited:'+self.client_address[0],3):self.reply(429,{'error':'Batas lab 3 request per 30 detik'},retry=True)
            else:self.reply(200,{'result':'OK-LAB'})
        elif u.path=='/preview':
            target=q.get('url',[''])[0]
            if MODE=='fixed' and target!='https://vendor.example.test/info':self.reply(403,{'error':'Tujuan tidak diizinkan'})
            elif target in PREVIEWS:self.reply(200,{'fixture':PREVIEWS[target],'outbound_request':False})
            else:self.reply(404,{'error':'Fixture tidak ada','outbound_request':False})
        elif u.path=='/file':
            target=q.get('name',[''])[0];virtual='public/'+target
            if MODE=='vulnerable':virtual=virtual.replace('public/../','')
            if MODE=='fixed' and target!='readme.txt':self.reply(403,{'error':'Nama tidak diizinkan'})
            elif virtual in FILES:self.reply(200,{'fixture':FILES[virtual],'os_file_read':False})
            else:self.reply(404,{'error':'Tidak ditemukan'})
        elif u.path in ['/profile','/preferences']:
            ses=self.session()
            if not ses:self.reply(401,{'error':'Login diperlukan'});return
            obj=dict(PROFILE)
            if u.path=='/preferences':obj['csrf_token']=ses['csrf']
            self.reply(200,obj)
        elif u.path=='/coupon':self.reply(405,{'error':'Gunakan POST'})
        else:self.reply(404,{'error':'Tidak ditemukan'})
    def do_POST(self):
        global BALANCE,USED
        length=int(self.headers.get('Content-Length','0'))
        if length>4096:self.reply(413,{'error':'Body terlalu besar'});return
        args=parse_qs(self.rfile.read(length).decode(),keep_blank_values=True)
        if self.path=='/login':
            if MODE=='fixed' and over_limit('login:'+self.client_address[0],3):self.reply(429,{'error':'Coba kembali nanti'},retry=True);return
            if args.get('username',[''])[0]=='alice' and args.get('password',[''])[0]=='alice-lab':
                token=secrets.token_urlsafe(32);SESSIONS[token]={'user':'alice','csrf':secrets.token_urlsafe(24)};self.reply(200,{'result':'Login berhasil'},'sid='+token)
            else:self.reply(401,{'error':'Login gagal'})
            return
        ses=self.session()
        if not ses:self.reply(401,{'error':'Login diperlukan'});return
        if self.path=='/profile':
            allowed={'display_name'} if MODE=='fixed' else set(PROFILE)
            for key in allowed:
                if key in args:PROFILE[key]=args[key][0]
            self.reply(200,PROFILE)
        elif self.path=='/preferences':
            if MODE=='fixed' and not secrets.compare_digest(args.get('csrf_token',[''])[0],ses['csrf']):self.reply(403,{'error':'CSRF token tidak valid'});return
            PROFILE['email']=args.get('email',[PROFILE['email']])[0];self.reply(200,{'email':PROFILE['email']})
        elif self.path=='/coupon':
            if args.get('code',[''])[0]!='LAB10':self.reply(400,{'error':'Kupon tidak valid'});return
            with LOCK:
                if MODE=='fixed' and USED:self.reply(409,{'error':'Kupon sudah digunakan'});return
                USED=True;BALANCE+=10;balance=BALANCE
            self.reply(200,{'credits':balance})
        else:self.reply(404,{'error':'Tidak ditemukan'})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['vulnerable','fixed'],default='vulnerable');p.add_argument('--port',type=int,default=8001);o=p.parse_args();MODE=o.mode
    print(f'Lab lanjutan {MODE} http://127.0.0.1:{o.port}; Ctrl+C untuk berhenti')
    ThreadingHTTPServer(('127.0.0.1',o.port),Handler).serve_forever()
