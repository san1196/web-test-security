"""Maksimal 20 request per mode, serial, loopback, tanpa brute force eksternal."""
import subprocess,sys,time,socket,json,urllib.request,urllib.error,http.cookiejar
from pathlib import Path

def verify(mode):
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    p=subprocess.Popen([sys.executable,str(Path(__file__).with_name('lab_lanjutan.py')),'--mode',mode,'--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));count=0
    def req(path,data=None):
        nonlocal count
        count+=1;assert count<=20
        try:r=op.open(f'http://127.0.0.1:{port}'+path,data=data,timeout=3)
        except urllib.error.HTTPError as e:r=e
        return r.status,json.loads(r.read()),r.headers
    try:
        for _ in range(40):
            with socket.socket() as s:
                if s.connect_ex(('127.0.0.1',port))==0:break
            time.sleep(.1)
        for i in range(4):
            status,_,_=req('/limited');assert status==(429 if mode=='fixed' and i==3 else 200)
        status,body,_=req('/preview?url=http%3A%2F%2Finternal.example.test%2Fstatus');assert status==(403 if mode=='fixed' else 200)
        status,body,_=req('/file?name=..%2Fprivate%2Fconfig.txt');assert status==(403 if mode=='fixed' else 200)
        assert req('/login',b'username=alice&password=alice-lab')[0]==200
        status,body,_=req('/profile',b'display_name=Alice2&role=admin');assert body['role']==('vendor' if mode=='fixed' else 'admin')
        status,body,_=req('/preferences',b'email=changed@example.test');assert status==(403 if mode=='fixed' else 200)
        token=req('/preferences')[1]['csrf_token']
        assert req('/preferences',('email=alice@example.test&csrf_token='+token).encode())[0]==200
        assert req('/coupon',b'code=LAB10')[1]['credits']==10
        status,body,_=req('/coupon',b'code=LAB10');assert status==(409 if mode=='fixed' else 200)
        for i in range(3):
            status,_,_=req('/login',b'username=alice&password=salah-lab');assert status==(429 if mode=='fixed' and i==2 else 401)
        print('LULUS',mode,count,'request; throttling, fixtures, CSRF, assignment, replay')
    finally:p.terminate();p.wait(timeout=5)
if __name__=='__main__':verify('vulnerable');verify('fixed')
