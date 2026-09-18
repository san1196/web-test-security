"""Verifikasi fixture sendiri; tidak menerima URL eksternal."""
import subprocess, sys, time, urllib.request, urllib.error, http.cookiejar, json, socket
from pathlib import Path

def request(opener, base, path, data=None):
    try:
        r = opener.open(base+path, data=data, timeout=3)
    except urllib.error.HTTPError as e:
        r = e
    return r.status, r.read().decode(), r.headers

def verify(mode):
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port=s.getsockname()[1]
    proc=subprocess.Popen([sys.executable,str(Path(__file__).with_name('lab.py')),'--mode',mode,'--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    try:
        for _ in range(40):
            try:
                request(opener,base,'/');break
            except (urllib.error.URLError, ConnectionError):time.sleep(.1)
        else: raise RuntimeError('Server tidak siap')
        assert request(opener,base,'/api/invoices/1001')[0]==401
        assert request(opener,base,'/login',b'username=alice&password=salah')[0]==401
        status,body,headers=request(opener,base,'/login',b'username=alice&password=alice-lab')
        assert status==200
        assert ('HttpOnly' in headers['Set-Cookie'])==(mode=='fixed')
        assert ('SameSite=Lax' in headers['Set-Cookie'])==(mode=='fixed')
        assert request(opener,base,'/api/invoices/1001')[0]==200
        assert request(opener,base,'/api/invoices/1002')[0]==(404 if mode=='fixed' else 200)
        assert len(json.loads(request(opener,base,'/search?q=Laptop')[1]))==1
        rows=json.loads(request(opener,base,'/search?q=%27%20OR%201%3D1%20--%20')[1])
        assert len(rows)==(0 if mode=='fixed' else 3)
        status,body,headers=request(opener,base,'/echo?q=%3Cscript%3Ealert%28%27LAB-XSS%27%29%3C%2Fscript%3E')
        assert ('<script>' in body)==(mode=='vulnerable')
        assert ('&lt;script&gt;' in body)==(mode=='fixed')
        assert bool(headers.get('Content-Security-Policy'))==(mode=='fixed')
        assert (headers.get('X-Content-Type-Options')=='nosniff')==(mode=='fixed')
        request(opener,base,'/login',b'username=bob&password=bob-lab')
        assert request(opener,base,'/api/invoices/1002')[0]==200
        assert request(opener,base,'/api/invoices/1001')[0]==(404 if mode=='fixed' else 200)
        print('LULUS',mode,': baseline, SQL, output XSS, akses objek, cookie dan header')
    finally:
        proc.terminate();proc.wait(timeout=5)

if __name__=='__main__':
    verify('vulnerable');verify('fixed')
    print('XSS browser tetap perlu diverifikasi manual sesuai buku.')
