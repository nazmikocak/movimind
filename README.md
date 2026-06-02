# MOVIMIND

> **Veri Madenciliği Dönem Projesi** <br/>
> *MovieLens ml-32m veri seti üzerinde KNN (Öklid Mesafesi) algoritması ile geliştirilmiş, Netflix dokunuşlarına sahip kişiselleştirilmiş film öneri platformu.*

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Özet

MOVIMIND, geniş çaplı **MovieLens ml-32m** veri seti üzerinden kullanıcı zevklerine en uygun filmleri önermeyi amaçlayan bir web sistemidir. Proje makine öğrenmesi süreçlerini ve modern web teknolojilerini bir araya getirerek, kullanıcılara profesyonel bir VoD (Video on Demand) sistemi deneyimi sunar.

## Öne Çıkan Özellikler

* **Kişiselleştirilmiş Öneriler:** Kullanıcı geçmişine dayalı olarak KNN (K-Nearest Neighbors) ve Öklid Mesafesi algoritması ile filmler önerilir. (Kosinüs benzerliği yerine veri madenciliği hedefleri doğrultusunda Öklid tercih edilmiştir).
* **Modern Arayüz:** Gerçekçi bir deneyim için Netflix tasarım kalıpları referans alınarak (Karanlık tema, vurgulu kırmızı tonlar, Inter & Poppins tipografileri) sıfırdan oluşturulmuş React arayüzü.
* **Tam Otomasyon:** Arka planda veri ayıklama, model eğitimi ve API sunumu birbirine entegredir. Sistemin ayağa kalkması tek bir komutla sağlanır.
* **Güvenli Proxy Mimarisi:** Frontend (İstemci) hiçbir noktada dış servislere (TMDb, OMDb vb.) doğrudan istek atmaz. Tüm çağrılar ve önbellekleme (caching) mekanizmaları kendi yapılandırdığımız arka plan (Backend) üzerinden işler.

## Sistem Mimarisi

Proje, sorumlulukları kesin olarak ayrılmış iki bağımsız katmandan (Server ve Client) oluşur. Aralarındaki tek haberleşme köprüsü yerel ağ üzerinden sağlanan JSON API'dir. Veritabanı kullanılmamakta olup veriler CSV'ler ve belleğe yüklenen Pickle dosyaları ile yönetilir.

```text
[ MovieLens CSV ] 
      │ 
      ▼
( server/app/data/clean.py )  ──►  ( server/app/model/train.py )  ──►  [ knn_model.pkl ]
                                                                               │
                                                                               ▼
[ Tarayıcı / İstemci ]  ◄── ( FastAPI :8000 ) ◄── ( recommender.py ) ◄─────────┘
```

## Proje Yapısı

```text
movimind/
├── client/               # React, TypeScript, SCSS ve Vite tabanlı önyüz katmanı
│   ├── src/features/     # Sayfa bazlı ayrılmış modüller (home, recommend, dataset vb.)
│   ├── src/services/     # Sadece backend'e giden isteklerin yönetildiği proxy (api.ts)
│   └── src/styles/       # Uygulama genelinde kullanılan kesin tema değişkenleri
├── server/               # Python ve FastAPI tabanlı arka plan katmanı
│   ├── app/api/          # Modüler endpoint'ler
│   ├── app/model/        # Öneri algoritması, modelleme, eğitim mantığı
│   ├── data/raw/         # MovieLens (ml-32m) ham CSV verileri
│   └── artifacts/        # Üretilen Pickle (KNN) modeli, cache dosyaları ve metrikler
└── docs/                 # Proje raporları ve dokümantasyonu
```

## Kurulum ve Çalıştırma

Projeyi yerel ortamınızda ayağa kaldırmak için aşağıdaki adımları sırasıyla izleyin. 

### 1. Ortam Değişkenleri (.env)
`server/` dizininde bir `.env` dosyası oluşturun ve dış servis entegrasyonları için gerekli API anahtarlarını ekleyin:

```env
RETRAIN_ON_START=false      # Başlangıçta veri setini ve modeli zorla yeniden işlemek için 'true' yapın
USER_SAMPLE=5000            # KNN modeli için belleği optimize etmek amacıyla alınacak rastgele kullanıcı sayısı
TMDB_API_KEY=your_tmdb_key  # Zengin film afişleri ve detayları için TMDb anahtarı
OMDB_API_KEY=your_omdb_key  # Alternatif film metadataları için OMDb anahtarı
```

### 2. Backend Geliştirme Sunucusu
Python ortamınızda, `server` dizini içerisindeki gereksinimleri yükleyin ve ana dosya olan `main.py` dosyasını çalıştırın:

```bash
cd server
pip install -r requirements.txt
python main.py
```
*Not: Sunucu ilk kez ayağa kaldırıldığında ham veri ve model bulamazsa temizleme ve eğitim scriptlerini otomatik tetikler.*

### 3. Frontend Geliştirme Sunucusu
Backend aktifken yeni bir terminal sekmesi açın, paketleri yükleyip arayüzü başlatın:

```bash
cd client
npm install
npm run dev
```

İstemci başlatıldıktan sonra modern VOD arayüzüne [http://localhost:5173](http://localhost:5173) adresinden ulaşabilirsiniz.

