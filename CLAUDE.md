# MOVIMIND — Proje Rehberi

Veri Madenciliği dönem projesi olarak başladı. **MovieLens 32M** veri seti (`ml-32m`)
üzerinde **KNN (Öklid mesafesi)** ile kişiselleştirilmiş film önerisi sunan bir web
sistemi. (Proje genelinde tek CLAUDE.md budur.)

---

## Mimari

```
YEREL:  MovieLens CSV ─► data/clean.py ─► model/train.py ─► knn_model.pkl ─► model/publish.py ─┐
                                                                                               ▼
CANLI:  Browser ◄── React/Vite (client) ◄── FastAPI (server) ◄── recommender.py (KNN) ◄── Neon (Postgres)
```

İki bağımsız katman: **server** (Python/FastAPI) ve **client** (React/TypeScript/Vite).
Tek köprü JSON API'dir. Veri **Neon (PostgreSQL)**'dedir: eğitim yerelde yapılır,
`publish.py` katalog/analiz verisini Neon'a yazar. Canlı server `train.py`'nin ürettiği
model dosyasını (`knn_model.pkl`) olduğu gibi yükler ve **her istekte
`model.kneighbors` ile canlı çalıştırır** (ön hesaplanmış sonuç yok). **Tüm API istekleri
(TMDb, OMDb) server yapar; client yalnızca kendi server'ımıza bağlanır.** İstisna: TMDb
görsel CDN'i (`image.tmdb.org`, adresleri server üretir) ve YouTube fragman embed'i.

## Klasör Haritası

| Yol | İçerik |
|---|---|
| `server/main.py` | Tek giriş: gerekirse temizle+eğit, sonra API'yi başlat |
| `server/app/config.py` | `.env`'den tüm ayarlar (`config` singleton) |
| `server/app/data/` | `clean.py` (temizleme+örneklem), `analysis.py` (grafik verisi) |
| `server/app/model/` | `train.py`, `evaluate.py`, `model_store.py` (knn_model.pkl yükleme), `publish.py` (yerel -> Neon), `recommender.py` (canlı KNN) |
| `database/` | Sürümlü DB script'leri: `V1__init.sql`, `V2__procedures.sql`, `V3__functions.sql`, `V4__triggers.sql` |
| `server/app/db/` | `repository.py` (tüm DB çağrıları), `mappers.py`, `enums.py`, `migrations.py` |
| `server/app/api/` | `routes_*.py` (ince FastAPI router'ları) |
| `server/app/services/external.py` | TMDb + OMDb + poster yolu çözümü (cache: bellek + `external_cache` tablosu, `EXTERNAL_CACHE_TTL_DAYS` sonra ziyaret anında yenilenir) |
| `server/data/raw/ml-32m/` | Ham CSV'ler (gitignored) |
| `server/artifacts/` | `knn_model.pkl`, metrikler (gitignored, yalnızca yerel) |
| `client/src/features/` | `home`, `dataset`, `recommend`, `movie`, `category` sayfaları |
| `client/src/components/` | Paylaşılan parçalar (Navbar, MovieRow, TonightModal…) |
| `client/src/services/api.ts` | Server'a giden TEK köprü |
| `client/src/styles/_variables.scss` | Tema token'ları (renk/font/spacing) |
| `server/Dockerfile`, `client/Dockerfile`, `docker-compose.yml` | Docker: backend imajı (canlı + yerel), arayüz imajı (yalnızca yerel) |
| `.github/workflows/deploy.yml` | CI + deploy: Vercel (client), GHCR imajı -> Render (server) |
| `client/src/extensions/` | Yerel eklenti noktaları; `local/` ve `server/app/api/local/` gitignored, depoya/canlıya gitmez |

## Çalıştırma

```bash
# Backend (sistemdeki Python; sanal ortam YOK)
pip install -r server/requirements.txt
cd server && python main.py          # gerekirse temizle+eğit, Neon'a yayınla, servis et
python main.py --publish-production  # yerel katalogu canlı Neon branch'ine yaz

# Frontend
cd client && npm install && npm run dev

# Ya da ikisi birden Docker ile (server/.env gerekli)
docker compose up --build            # arayüz :5173, API :8000
```

Model dosyası git'e girmez (177 MB). Canlı imaj, son `model-*` **GitHub Release**'indeki
`knn_model.pkl`'yi kullanır: yeniden eğitimden sonra `python main.py --publish-production`
ve yeni Release (`model-v2` ...) yayınlanır, ardından deploy en son modeli alır.

`.env` ile kontrol: `DATABASE_URL` (yerelde Neon `dev` branch'i); `RUN_PIPELINE=false`
canlıda yalnızca servis; `RETRAIN_ON_START=true` her açılışta yeniden eğitir;
`USER_SAMPLE` örneklem boyutu; `TMDB_API_KEY`/`OMDB_API_KEY` zengin film detayı.

---

## Proje Kuralları (HER ZAMAN uygula)

### Genel
- **Algoritma:** KNN + **Öklid mesafesi** (cosine KULLANMA — ders gereği).
- **Emoji YOK.** UI'da ikon gerektiğinde `react-icons/lu` (Lucide). Yıldız=`LuStar`,
  oynat=`LuPlay`.
- **Dış API isteği yalnızca server'da.** Client hiçbir 3. parti API'ye bağlanmaz; veri
  `client/src/services/api.ts` üzerinden server'dan gelir. Yalnızca server'ın verdiği
  TMDb görsel adresleri ve YouTube fragman embed'i tarayıcıda yüklenir.
- **Marka/tema:** İsim **MOVIMIND**. Kırmızı (`#E50914`), siyah, beyaz +
  lacivert/fuşya/bordo gradyanlar. Mavi/cyan tonları kullanma. Font: Inter (gövde) +
  Poppins (başlık). Renkler `_variables.scss` token'larından gelir.
- **Otomasyon:** Tek tek script çalıştırma; `python main.py` her şeyi halleder.

### Backend
- Route'lar ince; iş mantığı `model/recommender.py` ve `services/external.py`'de.
- Yeni dış API çağrısı SADECE `services/`'te (route'tan doğrudan `httpx` çağırma).
- Eğitimi request içinde yapma; yerel bootstrap'ta yap, Neon'a yayınla. Canlı server
  (`RUN_PIPELINE=false`) eğitmez; modeli kurar ve her istekte çalıştırır. Kullanıcı
  modelin canlıda gerçekten çalışmasını istiyor: KNN sonuçlarını önceden hesaplayıp
  tabloya yazmaya geri dönme.
- Veritabanı: ORM ve ham SQL yok; yalnızca `fn_*` / `sp_*` çağrıları, yalnızca
  `app/db/repository.py`'de. Şema değişikliği yeni `database/V<n>__*.sql` dosyasıyla.
- Yeni ayar → `app/config.py`. Sabit kodlama yok.
- `train.py` **kullanıcı-ort. merkezlenmiş** matris kurar (Öklid kalitesi için).
- Print mesajlarında ASCII `->` kullan (Windows cp1254 Unicode oklarını encode edemez;
  `config.py` stdout'u UTF-8'e çevirir ama yine de güvenli taraf).

### Frontend
- Sadece `import.meta.env.VITE_API_BASE` (kendi server'ımız). Posterler film
  verisindeki `poster_url` alanından (`usePoster(movie)` / `getPosterUrl(movie)`).
- Tüm sayfalar ortak `.page-container` (maks-genişlik + yatay padding) ile hizalanır.
- "Bugün ne izlemek istersin?" modalı günde 1 kez (`localStorage` tarih damgası);
  aynı gün refresh'te tekrar gelmez.

- **Git:** Commit ve push'u kullanıcı yapar; Claude yalnızca Conventional Commits
  biçiminde İngilizce mesaj önerir (`git.md`).

Detaylı kurallar: `.claude/rules/` (architecture, branding-theme, coding-style, comments, database, git).
