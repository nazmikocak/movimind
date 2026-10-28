# Mimari Kuralları

- **İki katman, tek köprü:** `server` (FastAPI) ve `client` (React). Aralarındaki
  tek bağlantı JSON API'dir. Client başka hiçbir API'ye bağlanmaz (istisna: server'ın
  verdiği TMDb görsel adresleri ve YouTube fragman embed'i).
- **Otomasyon:** Veri temizleme, model eğitme, yayın ve API başlatma elle ayrı ayrı
  çalıştırılmaz. `python server/main.py` → bootstrap (gerekirse temizle+eğit, model
  DB'dekinden yeniyse Neon'a yayınla) → serve. `RETRAIN_ON_START=true` eğitimi zorlar.
- **Veritabanı:** Neon (PostgreSQL). Yerel `dev` branch'i, canlı `production` branch'i.
  Eğitim hep yerelde. Canlı server `RUN_PIPELINE=false` ile eğitmez; eğitilmiş model
  dosyasını (`knn_model.pkl`) yükler ve her istekte çalıştırır.
- **Veri yolu:** Ham veri `server/data/raw/ml-32m/`, işlenmiş `server/data/processed/`,
  model `server/artifacts/`. Hepsi gitignored. Canlıda yalnızca model dosyası
  (`knn_model.pkl`) bulunur.
- **Katman sorumlulukları:** route'lar ince; iş mantığı `model/recommender.py` ve
  `services/external.py`'de. Ağır iş (eğitim) request içinde değil bootstrap'ta.
- **Yapılandırma:** Tüm ayarlar `.env` → `app/config.py:config`. Sabit kodlama yok.
