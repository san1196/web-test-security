"""Lab pendidikan sengaja rentan. Hanya loopback, data fiktif, tanpa dependensi."""
import argparse
import html
import json
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from http.cookies import SimpleCookie

SESSIONS = {}
USERS = {'alice': 'alice-lab', 'bob': 'bob-lab'}
DB = sqlite3.connect(':memory:', check_same_thread=False)
DB.executescript("CREATE TABLE products(id INTEGER, name TEXT); INSERT INTO products VALUES(1,'Laptop'),(2,'Printer'),(3,'Router');")
INVOICES = {1001: {'owner': 'alice', 'amount': 150000, 'customer': 'PT Contoh A'}, 1002: {'owner': 'bob', 'amount': 250000, 'customer': 'PT Contoh B'}}
MODE = 'vulnerable'

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type='text/html; charset=utf-8', cookie=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        if MODE == 'fixed':
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body.encode())

    def user(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get('Cookie', ''))
        except Exception:
            return None
        token = cookies.get('sid')
        return SESSIONS.get(token.value) if token else None

    def do_GET(self):
        parsed = urlparse(self.path)
        args = parse_qs(parsed.query, keep_blank_values=True)
        q = args.get('q', [''])[0]
        if parsed.path == '/':
            self.send(200, '<h1>Cyber Security Lab</h1><p>Mode: '+MODE+'</p><a href="/login">Login</a> | <a href="/search?q=Laptop">Search</a> | <a href="/echo?q=Halo">Echo</a> | <a href="/api/invoices/1001">Invoice 1001</a>')
        elif parsed.path == '/login':
            self.send(200, '<h1>Login lab</h1><form method="post" action="/login"><input name="username" placeholder="username"><input type="password" name="password"><button>Login</button></form>')
        elif parsed.path == '/echo':
            self.send(200, '<h1>Hasil input</h1><p>'+(html.escape(q) if MODE == 'fixed' else q)+'</p>')
        elif parsed.path == '/search':
            try:
                if MODE == 'fixed':
                    rows = DB.execute('SELECT id,name FROM products WHERE name LIKE ?', ('%'+q+'%',)).fetchall()
                else:
                    rows = DB.execute("SELECT id,name FROM products WHERE name LIKE '%"+q+"%'").fetchall()
                self.send(200, json.dumps(rows), 'application/json')
            except sqlite3.Error:
                self.send(400, json.dumps({'error': 'Query tidak valid'}), 'application/json')
        elif parsed.path.startswith('/api/invoices/'):
            user = self.user()
            if not user:
                self.send(401, '{"error":"Login diperlukan"}', 'application/json')
                return
            try:
                invoice = INVOICES.get(int(parsed.path.rsplit('/', 1)[1]))
            except ValueError:
                invoice = None
            if not invoice or (MODE == 'fixed' and invoice['owner'] != user):
                self.send(404, '{"error":"Tidak ditemukan"}', 'application/json')
            else:
                self.send(200, json.dumps(invoice), 'application/json')
        else:
            self.send(404, 'Tidak ditemukan')

    def do_POST(self):
        if self.path != '/login':
            self.send(404, 'Tidak ditemukan')
            return
        length = min(int(self.headers.get('Content-Length', 0)), 4096)
        args = parse_qs(self.rfile.read(length).decode(), keep_blank_values=True)
        user = args.get('username', [''])[0]
        password = args.get('password', [''])[0]
        if user in USERS and secrets.compare_digest(USERS[user], password):
            token = secrets.token_urlsafe(32)
            SESSIONS[token] = user
            flags = '; HttpOnly; SameSite=Lax' if MODE == 'fixed' else ''
            self.send(200, '<p>Login berhasil</p><a href="/">Beranda</a>', cookie='sid='+token+'; Path=/'+flags)
        else:
            self.send(401, 'Login gagal')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['vulnerable', 'fixed'], default='vulnerable')
    parser.add_argument('--port', type=int, default=8000)
    opts = parser.parse_args()
    MODE = opts.mode
    print('Lab '+MODE+' di http://127.0.0.1:'+str(opts.port)+' — Ctrl+C untuk berhenti')
    ThreadingHTTPServer(('127.0.0.1', opts.port), Handler).serve_forever()
