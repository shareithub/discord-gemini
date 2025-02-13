# DISCORD PUSH LEVEL WITH GEMINI AI !!

* Tutorial with VIDEO : https://youtu.be/B6IkggY6ct8

## Prerequisites
Pastikan kamu sudah menginstal:
- [Python](https://www.python.org/downloads/) (Centang **"Add Python to PATH"** saat instalasi!)
- Git Bash (jika belum punya, unduh dari [Git for Windows](https://git-scm.com/downloads))

# Get your discord token, different ways:

### First method:
1. Open your browser and activate developer mode
2. Login your discord account
3. Go to developer mode and click on XHR tab
4. Find login request and click
5. Go to Responses tab and find token value
6. Copy that token

### Second method:
1. Make sure that you already login into your discord account
2. Go to Developers tool in your browser
3. Find javascript console, and paste code below:

```
(
    webpackChunkdiscord_app.push(
        [
            [''],
            {},
            e => {
                m=[];
                for(let c in e.c)
                    m.push(e.c[c])
            }
        ]
    ),
    m
).find(
    m => m?.exports?.default?.getToken !== void 0
).exports.default.getToken()
```

# HOW TO GET GEMINI API :

go to : https://aistudio.google.com/apikey

* Login with your google accounts
* Create API Key
* Copy API Key

# PASTE YOUR DISCORD TOKEN & GEMINI API IN FILE .ENV

## Steps to Setup

### 1. Buka Git Bash dan Masuk ke Direktori Proyek
Jika belum ada, clone repository proyek terlebih dahulu:
```bash
 git clone <repo_url>
```
Lalu masuk ke folder proyek:
```bash
 cd discord-gemini
```

### 2. Buat Virtual Environment
Jalankan perintah berikut untuk membuat virtual environment:
```bash
 python -m venv discord
```
Jika `python` tidak dikenali, coba:
```bash
 python3 -m venv discord
```

### 3. Aktifkan Virtual Environment
Karena di **Windows**, jalankan perintah berikut:
```bash
 source discord/Scripts/activate
```
Jika berhasil, prompt akan berubah menjadi `(discord)`, menandakan virtual environment aktif.

### 4. Install Dependencies
Jalankan:
```bash
 pip install -r requirements.txt
```

### 5. Menjalankan Proyek
Setelah instalasi selesai, kamu bisa menjalankan proyek sesuai dengan instruksi yang ada di repository ini.

### 6. (Opsional) Menonaktifkan Virtual Environment
Jika ingin keluar dari virtual environment, jalankan:
```bash
 deactivate
```

## Troubleshooting
Jika ada error seperti **"python not found"**, pastikan:
- Python sudah ditambahkan ke PATH
- Coba jalankan dengan `python3` daripada `python`

# Youtube Channel :
* https://www.youtube.com/@SHAREITHUB_COM

# Telegram Channel :
* https://t.me/SHAREITHUB_COM

# Group Telegram :
* https://t.me/DISS_SHAREITHUB

---
Semoga berhasil! 🚀 Jika ada kendala, silakan cek dokumentasi atau tanyakan di forum komunitas. 😃

