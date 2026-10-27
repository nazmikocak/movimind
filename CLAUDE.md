# MOVIMIND — Proje Rehberi

Veri Madenciliği dönem projesi. **MovieLens ml-32m** veri seti üzerinde
**KNN (Öklid mesafesi)** ile kişiselleştirilmiş film önerisi sunan,
Netflix tarzı bir web sistemi. (Proje genelinde tek CLAUDE.md budur.)

---

## Mimari

```
MovieLens CSV ─► server/app/data/clean.py ─► server/app/model/train.py ─► knn_model.pkl
                                                                              │
Browser ◄── React/Vite (client) ◄── FastAPI (server, :8000) ◄── recommender.py
```

İki bağımsız katman: **server** (Python/FastAPI) ve **client** (React/TypeScript/Vite).
Tek köprü JSON API'dir. Veritabanı yok. **Tüm dış istekleri (TMDb, OMDb, poster)
server yapar; client yalnızca kendi server'ımıza bağlanır.**

## Klasör Haritası

| Yol | İçerik |
|---|---|
| `server/main.py` | Tek giriş: gerekirse temizle+eğit, sonra API'yi başlat |
| `server/app/config.py` | `.env`'den tüm ayarlar (`config` singleton) |
| `server/app/data/` | `clean.py` (temizleme+örneklem), `analysis.py` (grafik verisi) |
| `server/app/model/` | `train.py`, `recommender.py`, `evaluate.py` |
| `server/app/api/` | `routes_*.py` (ince FastAPI router'ları) |
| `server/app/services/external.py` | TMDb + OMDb + poster proxy (cache'li) |
| `server/data/raw/ml-32m/` | Ham CSV'ler (gitignored) |
| `server/artifacts/` | `knn_model.pkl`, metrikler, cache (gitignored) |
| `client/src/features/` | `home`, `dataset`, `recommend`, `movie`, `category` sayfaları |
| `client/src/components/` | Paylaşılan parçalar (Navbar, MovieRow, TonightModal…) |
| `client/src/services/api.ts` | Server'a giden TEK köprü |
| `client/src/styles/_variables.scss` | Tema token'ları (renk/font/spacing) |
| `client/src/extensions/` | Yerel eklenti noktaları; `local/` ve `server/app/api/local/` gitignored, depoya/canlıya gitmez |

## Çalıştırma

```bash
# Backend (sistemdeki Python; sanal ortam YOK)
pip install -r server/requirements.txt
cd server && python main.py          # ilk açılışta veri+model üretir

# Frontend
cd client && npm install && npm run dev
```

`.env` ile kontrol: `RETRAIN_ON_START=true` her açılışta yeniden eğitir;
`USER_SAMPLE` örneklem boyutu; `TMDB_API_KEY`/`OMDB_API_KEY` zengin film detayı.

---

## Proje Kuralları (HER ZAMAN uygula)

### Genel
- **Algoritma:** KNN + **Öklid mesafesi** (cosine KULLANMA — ders gereği).
- **Emoji YOK.** UI'da ikon gerektiğinde `react-icons/lu` (Lucide). Yıldız=`LuStar`,
  oynat=`LuPlay`.
- **Dış istek yalnızca server'da.** Client hiçbir 3. parti API/görsel host'a doğrudan
  bağlanmaz; her şey `client/src/services/api.ts` üzerinden server proxy'sine gider.
- **Marka/tema:** İsim **MOVIMIND**. Netflix tarzı: kırmızı (`#E50914`), siyah, beyaz +
  lacivert/fuşya/bordo gradyanlar. Mavi/cyan tonları kullanma. Font: Inter (gövde) +
  Poppins (başlık). Renkler `_variables.scss` token'larından gelir.
- **Otomasyon:** Tek tek script çalıştırma; `python main.py` her şeyi halleder.

### Backend
- Route'lar ince; iş mantığı `model/recommender.py` ve `services/external.py`'de.
- Yeni dış API çağrısı SADECE `services/`'te (route'tan doğrudan `httpx` çağırma).
- Ağır işi (eğitim) request içinde yapma; bootstrap'ta yap, sonucu belleğe al.
- Yeni ayar → `app/config.py`. Sabit kodlama yok.
- `train.py` **kullanıcı-ort. merkezlenmiş** matris kurar (Öklid kalitesi için).
- Print mesajlarında ASCII `->` kullan (Windows cp1254 Unicode oklarını encode edemez;
  `config.py` stdout'u UTF-8'e çevirir ama yine de güvenli taraf).

### Frontend
- Sadece `import.meta.env.VITE_API_BASE` (kendi server'ımız). Poster bile
  `/api/poster/{imdbId}` proxy'sinden gelir.
- Tüm sayfalar ortak `.page-container` (maks-genişlik + yatay padding) ile hizalanır.
- "Bugün ne izlemek istersin?" modalı günde 1 kez (`localStorage` tarih damgası);
  aynı gün refresh'te tekrar gelmez.

Detaylı kurallar: `.claude/rules/` (architecture, branding-theme, coding-style).
