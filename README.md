# AirSensa – Sistem Monitoring Kualitas Udara Berbasis IoT

## Deskripsi
Repositori ini berisi project **AirSensa**, sebuah sistem monitoring kualitas udara berbasis **Internet of Things (IoT)** yang dirancang untuk memantau kondisi udara secara **real-time**.

AirSensa mengintegrasikan perangkat IoT dengan aplikasi web berbasis cloud, sehingga data kualitas udara dapat diakses secara daring melalui internet. Aplikasi web AirSensa telah dideploy pada platform **Microsoft Azure** dan dapat diakses secara publik melalui tautan berikut:

🔗 **Live Demo**  
https://web-airsensa-dtgccgc2d8c5abdb.southeastasia-01.azurewebsites.net

Project ini dikembangkan untuk menunjukkan pemahaman konsep:
- Sistem IoT dan sensor lingkungan
- Integrasi perangkat IoT dengan aplikasi web
- Pengiriman dan pengelolaan data secara real-time
- Implementasi cloud deployment menggunakan Microsoft Azure

---

## Struktur
```text
.
├── static/            # File CSS dan aset statis web
├── templates/         # Template tampilan web (HTML)
├── app.py             # Backend aplikasi web (Flask)
├── requirements.txt   # Daftar dependensi Python
├── Procfile           # Konfigurasi perintah saat deployment
└── README.md          # Dokumentasi project
