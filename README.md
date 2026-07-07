# Lazarus Telegram Member Scraper & Adder

CLI tool untuk scrape member dari grup sumber dan add ke grup target menggunakan Pyrogram.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Copy `.env.example` ke `.env` dan isi:
```
API_ID=isi_dari_my.telegram.org
API_HASH=isi_dari_my.telegram.org
```

3. Edit `sources.txt` sesuai grup sumber yang diinginkan.

## Cara Jalankan

```bash
# Scrape member dari grup sumber
python lazarus_adder.py --scrape-only

# Add member ke grup target
python lazarus_adder.py --add-only

# Full: scrape + add
python lazarus_adder.py --start

# Resume dari checkpoint terakhir
python lazarus_adder.py --resume
```

## Catatan

- Pertama kali jalan akan minta nomor telepon & OTP untuk login
- Session tersimpan di `lazarus.session`
- Progress tersimpan di `progress.db` (SQLite)
- Bot notifikasi otomatis jalan jika BOT_TOKEN diisi
