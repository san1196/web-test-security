# Paket praktik Cyber Security

Lab sengaja rentan, hanya localhost dan data fiktif. Jangan deploy ke internet.
Memerlukan Python 3.10+; tidak memerlukan pip, Docker, atau lisensi berbayar.

## Windows PowerShell
Buka terminal pada folder ini:
    py -3 lab.py --mode vulnerable
Jika py tidak tersedia gunakan python.

## macOS Terminal
    python3 lab.py --mode vulnerable

Buka http://127.0.0.1:8000. Login alice/alice-lab atau bob/bob-lab.
Invoice 1001 milik Alice; 1002 milik Bob.
Ctrl+C untuk menghentikan server.
Jalankan kembali dengan --mode fixed untuk retest. Login ulang setelah restart.
Jika port digunakan, tambahkan --port 8001 dan ubah semua URL menjadi port 8001.

## Verifikasi otomatis
Windows: py -3 verifikasi_lab.py
macOS: python3 verifikasi_lab.py
Script menjalankan sendiri kedua mode pada port lokal sementara.
Script memeriksa HTTP dan encoding output; eksekusi XSS harus dicek di browser.

## URL latihan pada mode rentan
Baseline: http://127.0.0.1:8000/search?q=Laptop
SQL: http://127.0.0.1:8000/search?q=%27%20OR%201%3D1%20--%20
XSS: http://127.0.0.1:8000/echo?q=%3Cscript%3Ealert%28%27LAB-XSS%27%29%3C%2Fscript%3E
IDOR: login Alice lalu bandingkan /api/invoices/1001 dan /api/invoices/1002.

## Batas lab
Mode fixed memperbaiki celah yang diajarkan, bukan seluruh keamanan produksi.
Password dalam kode, tanpa TLS, hashing, expiry sesi, logout, rate limit, CSRF lengkap.
Database dan sesi dalam memori; restart mereset semuanya.
Lihat buku untuk langkah, bukti, penilaian risiko, dan contoh laporan.

# Materi dan lab tambahan edisi diperluas

## Server lanjutan
Windows: py -3 lab_lanjutan.py --mode vulnerable
macOS: python3 lab_lanjutan.py --mode vulnerable
URL: http://127.0.0.1:8001
Stop Ctrl+C; ulangi dengan --mode fixed untuk retest.
Semua state direset saat restart. Akun: alice / alice-lab.

## Endpoint tambahan
/limited: GET empat kali serial; fixed mengembalikan 429 setelah tiga request per IP dalam 30 detik.
/login: POST username dan password; fixed membatasi tiga request per IP dalam 30 detik.
/preview?url=...: simulasi allowlist URL dalam kamus, TIDAK melakukan outbound request.
/file?name=...: simulasi path dalam kamus, TIDAK membaca file OS.
/profile: POST display_name dan role; fixed hanya mengizinkan display_name.
/preferences: GET token CSRF sesi; POST email dengan csrf_token pada fixed.
/coupon: POST code=LAB10; fixed menolak penggunaan ulang dengan 409.

Contoh login curl (Windows gunakan curl.exe):
    curl -c alice.cookies -d "username=alice&password=alice-lab" http://127.0.0.1:8001/login
    curl -b alice.cookies http://127.0.0.1:8001/preferences
    curl -b alice.cookies -d "display_name=Alice2&role=admin" http://127.0.0.1:8001/profile
    curl -b alice.cookies -d "code=LAB10" http://127.0.0.1:8001/coupon

Jika login telah dibatasi, restart atau tunggu window 30 detik. Hitungan lab fixed mencakup login benar dan salah.
File cookie jar bukan cookie browser; lihat bab CSRF untuk login browser memakai fetch.
Untuk form lokal CSRF jalankan server statis di folder ini:
    python3 -m http.server 8002 --bind 127.0.0.1
atau Windows:
    py -3 -m http.server 8002 --bind 127.0.0.1
Buka http://127.0.0.1:8002/csrf_demo.html setelah login browser pada port 8001.

## Simulasi ketersediaan tanpa jaringan
Windows: py -3 simulasi_ketersediaan.py
macOS: python3 simulasi_ketersediaan.py
Model antrean offline. Bukan generator DDoS, bukan benchmark produksi.

## Verifikasi tambahan
Windows: py -3 verifikasi_lanjutan.py
macOS: python3 verifikasi_lanjutan.py
Maksimal 20 request serial per mode, hanya proses server yang dijalankan script sendiri di loopback.

## Batas bukti
Tidak ada eksploitasi jaringan SSRF, pembacaan file OS, upload payload aktif, atau race concurrent.
Role fixture dapat berubah di vulnerable, tetapi tidak mengaktifkan permission admin.
Lab ini mengajarkan kontrol dan pelaporan; fixed bukan baseline produksi lengkap.
JWT, upload, command injection, dan monitoring mempunyai latihan review/desain dalam buku.
