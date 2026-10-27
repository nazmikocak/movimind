# MOVIMIND

> **Veri Madenciliği Dönem Projesi** <br/>
> *MovieLens ml-32m veri seti üzerinde KNN (Öklid Mesafesi) algoritması ile geliştirilmiş, Netflix dokunuşlarına sahip kişiselleştirilmiş film öneri platformu.*

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Özet

MOVIMIND, geniş çaplı **MovieLens ml-32m** veri seti üzerinden kullanıcı zevklerine en uygun filmleri önermeyi amaçlayan bir web sistemidir. Proje makine öğrenmesi süreçlerini ve modern web teknolojilerini bir araya getirerek, kullanıcılara modern bir film keşif deneyimi sunar. MOVIMIND film yayını yapmaz; yalnızca öneri, film bilgisi ve resmi fragman sunar.

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
└── CITATION.cff          # Proje ve veri seti atıf bilgisi
```

## Kurulum ve Çalıştırma

Projeyi yerel ortamınızda ayağa kaldırmak için aşağıdaki adımları sırasıyla izleyin. 

### 1. Ortam Değişkenleri (.env)
Örnek dosyaları kopyalayıp kendi değerlerinizi girin. Gerçek `.env` dosyaları `.gitignore` ile dışlanır; depoda yalnızca `.env.example` bulunur.

```bash
cp server/.env.example server/.env   # TMDB_API_KEY, OMDB_API_KEY, CORS_ORIGINS ...
cp client/.env.example client/.env   # VITE_API_BASE
```

### Veri Seti
[MovieLens ml-32m](https://grouplens.org/datasets/movielens/32m/) arşivini indirip içeriğini `server/data/raw/ml-32m/` dizinine çıkarın. Ham veri lisans gereği ve boyutu nedeniyle depoya dahil edilmez.

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

## Veri Seti ve Atıf

Bu projede GroupLens Research (University of Minnesota) tarafından yayımlanan **MovieLens 32M** veri seti kullanılmıştır. Veri seti 200.948 kullanıcının 87.585 filme 9 Ocak 1995 – 12 Ekim 2023 arasında verdiği 32.000.204 puan ile 2.000.072 etiketi içerir.

GroupLens'in talep ettiği atıf:

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. <https://doi.org/10.1145/2827872>

```bibtex
@article{harper2015movielens,
  author    = {Harper, F. Maxwell and Konstan, Joseph A.},
  title     = {The MovieLens Datasets: History and Context},
  journal   = {ACM Transactions on Interactive Intelligent Systems},
  volume    = {5},
  number    = {4},
  pages     = {19:1--19:19},
  year      = {2015},
  publisher = {ACM},
  doi       = {10.1145/2827872}
}
```

**Kullanım koşulları:** Veri seti yalnızca araştırma/eğitim amaçlı, ticari olmayan biçimde kullanılmaktadır. MOVIMIND, University of Minnesota veya GroupLens Research tarafından onaylanmış ya da desteklenmiş değildir. Ayrıntılar için veri setiyle gelen `README.txt` dosyasındaki *Usage License* bölümüne bakın.

## Üçüncü Taraf Veri Kaynakları

- Film detayları, posterler ve fragman bağlantıları [TMDB](https://www.themoviedb.org/) API'si üzerinden alınır. *This product uses the TMDB API but is not endorsed or certified by TMDB.*
- IMDb puanı, ödüller ve ek meta veriler [OMDb API](https://www.omdbapi.com/) üzerinden alınır.
