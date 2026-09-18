# Cyber Security Lab — paket lengkap untuk Vercel

Paket ini mempertahankan 12 skenario, mode rentan/diperbaiki, laporan temuan, ekspor Markdown, dan koneksi Supabase dari website sebelumnya.
Website adalah simulator browser; SQL, SSRF, JWT, dan DDoS merupakan model konseptual. Untuk latihan HTTP nyata dengan curl/ZAP/Burp gunakan folder praktik-lokal/cyber_lab dan README di dalamnya.

## Perubahan untuk deployment

- Seluruh file yang dipublikasikan ada di public/, termasuk public/index.html.
- vercel.json secara eksplisit menentukan preset static (framework: null), output public, dan perintah build.
- Pemeriksaan build memverifikasi file, sintaks JavaScript, dan logika dasar skenario. Tidak ada dependensi npm yang perlu diunduh.
- Konfigurasi internal hosting sebelumnya tidak disertakan.

404 pada screenshot adalah respons Vercel. Salah output/root directory dapat menimbulkan 404, tetapi screenshot saja tidak memastikan penyebab. Pastikan deployment berstatus Ready dan domain terhubung ke deployment Production proyek yang benar.

## Deploy melalui GitHub + dashboard Vercel

1. Ekstrak ZIP ke folder baru. File vercel.json, package.json, README.md, scripts/, public/, dan praktik-lokal/ berada pada tingkat yang sama.
2. Unggah **seluruh isi folder hasil ekstrak** ke root repository GitHub yang Anda gunakan untuk Vercel. Jangan hanya unggah ZIP dan jangan hanya unggah folder public. Jangan mencampur file build/framework lama ke paket ini; gunakan branch atau repository bersih bila perlu.
3. Import repository tersebut di Vercel, atau gunakan proyek yang sudah terhubung.
4. Atur Settings / Build and Deployment sesuai tabel berikut, lalu lakukan deployment Production baru. vercel.json menetapkan build/output untuk paket ini, tetapi tidak mengoreksi Root Directory yang salah.

| Pengaturan | Nilai |
| --- | --- |
| Framework Preset | Other |
| Root Directory | kosong/default jika vercel.json ada di root repository |
| Build Command | npm run build |
| Output Directory | public |
| Install Command | kosong; paket tidak mempunyai dependensi |
| Node.js Version | 22.x atau versi yang lebih baru yang didukung Vercel |

Jika Anda mengunggah paket di dalam subfolder cyber-security-lab-vercel, Root Directory harus cyber-security-lab-vercel. Jangan pilih public atau dist sebagai Root Directory.

5. Tunggu status **Ready**. Buka URL deployment Production dari dashboard. Bila URL deployment tersebut berhasil tetapi domain web-test-security.vercel.app tetap 404, periksa Settings / Domains dan pastikan domain menunjuk ke proyek/deployment Production yang benar.
6. Bila masih gagal, periksa Build Logs: harus ada tulisan PASS: deployment package. Pastikan public/index.html ada di repository dan nama file menggunakan huruf kecil.

Referensi: https://vercel.com/docs/project-configuration/vercel-json

## Deploy menggunakan Vercel CLI (opsional)

Di Terminal/PowerShell, masuk ke folder yang berisi vercel.json, lalu jalankan:

```sh
npx vercel --prod
```

Login dengan akun Vercel Anda dan pilih proyek yang benar. Penggunaan CLI membutuhkan akses npm dan Vercel.

## Menjalankan dan memeriksa di Windows / macOS

Pasang Node.js 22 atau versi lebih baru terlebih dahulu. Dari folder yang berisi package.json:

```sh
npm run build
npm test
npm run dev
```

Buka http://127.0.0.1:3000. Hentikan server dengan Ctrl+C. Tidak perlu npm install untuk build/test/dev karena semua skrip memakai modul bawaan Node.js. Gunakan server HTTP; jangan menguji sesi/login melalui file://.

## Supabase

Koneksi ke proyek vwjlqxissuumelwgoliv sudah disertakan di public/app.js. Konfigurasi memakai endpoint API https://vwjlqxissuumelwgoliv.supabase.co, bukan URL dashboard. Key yang disertakan adalah publishable key milik proyek yang Anda berikan; tidak ada service-role key dalam paket.

- Bila tabel belum dibuat: jalankan public/supabase-schema.sql satu kali melalui SQL Editor proyek. Jangan menjalankan ulang skrip pembuatan tabel bila tabel sudah ada.
- Provider Email harus aktif. Daftar/login melalui menu Akun & database di website.
- Jika konfirmasi email aktif: di Supabase Authentication / URL Configuration, set Site URL ke URL deployment Vercel Anda. Tambahkan origin deployment yang digunakan ke Redirect URLs sesuai pengaturan Auth proyek.
- Sesi login hanya berada di memori browser; masuk kembali setelah refresh.
- Laporan dan riwayat memakai tabel cyber_lab_findings dan cyber_lab_runs. RLS memisahkan data per akun; mode rentan simulator tidak menonaktifkan aturan database.
- Skema tidak diterapkan otomatis oleh Vercel. Key publishable tidak berwenang membuat tabel.
- Jika mengganti proyek, ubah SUPABASE_URL dan SUPABASE_KEY di public/app.js kemudian deploy ulang.

## Pemeriksaan setelah deploy

1. Halaman / menampilkan Laboratorium keamanan dan daftar 12 skenario.
2. IDOR: mode rentan + invoice 1002 menampilkan data Bob; mode diperbaiki menolak dengan 403. Invoice 1001 tetap boleh dibaca.
3. Coba navigasi Laporan temuan dan Akun & database. Navigasi menggunakan hash (#lab, #findings, #setup), sehingga tidak membutuhkan rewrite SPA.
4. Setelah skema tersedia dan Anda masuk, simpan satu hasil pengujian serta satu laporan. Periksa baris terkait di Table Editor Supabase.
5. Masuk dengan akun peserta kedua: data peserta pertama seharusnya tidak muncul. Konfirmasi juga melalui API sesuai ruang lingkup pengujian Anda.

## Batas verifikasi paket

Paket telah diperiksa melalui build, uji logika, dan server HTTP lokal. Tidak ada akses ke dashboard Vercel Anda, sehingga perubahan pengaturan proyek/domain dan deployment di akun Anda harus Anda lakukan. Pengujian penyimpanan dua akun pada proyek Supabase membutuhkan skema dan akun yang valid; pemeriksaan lokal tidak membuktikan kebijakan database sudah diterapkan.
