# 🌤️ CuacaKita

**CuacaKita** adalah aplikasi widget cuaca modern yang dirancang dengan antarmuka yang bersih, responsif, dan elegan. Aplikasi ini mendukung pencarian kota secara dinamis dan fitur tema gelap/terang untuk kenyamanan pengguna.

---

## ✨ Fitur Utama

- **Premium UI Design**: Antarmuka modern menggunakan teknik *glassmorphism* dan tipografi Inter.
- **Dynamic Search**: Cari cuaca di kota mana pun tanpa perlu memuat ulang halaman.
- **Dark & Light Mode**: Dukungan tema otomatis dan manual yang tersimpan di browser.
- **Production Ready**: Dikonfigurasi untuk dijalankan sebagai layanan Windows (Windows Service) menggunakan Waitress dan NSSM.
- **Responsive Layout**: Tampilan yang optimal di perangkat mobile maupun desktop.

---

## 🚀 Teknologi yang Digunakan

- **Backend**: Python, Flask
- **Frontend**: HTML5, Tailwind CSS, JavaScript (Fetch API)
- **Icons**: Lucide Icons
- **Production Server**: Waitress (WSGI Server)
- **Deployment**: NSSM (Non-Sucking Service Manager)

---

## 🛠️ Cara Penggunaan

### 1. Persiapan
Clone repositori ini dan instal dependensi:
```bash
git clone https://github.com/Apewww/CuacaKita.git
cd CuacaKita
pip install -r requirments.txt
```

### 2. Konfigurasi
Buat file `.env` di direktori utama dan tambahkan API Key dari [WeatherAPI.com](https://www.weatherapi.com/):
```env
API_KEY=your_api_key_here
```

### 3. Menjalankan Mode Pengembangan
```bash
python app.py
```
Akses di browser melalui `http://127.0.0.1:5000`.

### 4. Menjalankan di Mode Produksi
Aplikasi ini sudah mendukung **Waitress** untuk stabilitas lebih tinggi:
```bash
python serve.py
```

---

## 🖥️ Deployment (Windows Server)

Untuk menjalankan aplikasi ini sebagai layanan latar belakang di Windows Server:
1. Pastikan `nssm.exe` sudah terinstal.
2. Gunakan file `run_app.bat` sebagai target aplikasi di NSSM.
3. Untuk panduan lengkap, lihat dokumen [Deployment Guide](C:/Users/apewi/.gemini/antigravity/brain/80b99cc4-f0a6-4942-b864-0cd7be795b21/deployment_guide.md) (lokal).

---

## 👤 Project By

**Apewww**
*Special thanks to the open-source community for the tools and inspiration.*

---

## 📄 Lisensi

Proyek ini berada di bawah lisensi [MIT](LICENSE).
