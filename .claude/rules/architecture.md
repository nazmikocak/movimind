# Mimari Kuralları

- **İki katman, tek köprü:** `server` (FastAPI) ve `client` (React). Aralarındaki
  tek bağlantı JSON API'dir. Client başka hiçbir kaynağa bağlanmaz.
- **Otomasyon:** Veri temizleme, model eğitme ve API başlatma elle ayrı ayrı
  çalıştırılmaz. `python server/main.py` → bootstrap (gerekirse temizle+eğit) → serve.
  Model varsa yeniden eğitilmez; `RETRAIN_ON_START=true` ile zorlanır.
- **Veri yolu:** Ham veri `server/data/raw/ml-32m/`, işlenmiş `server/data/processed/`,
  model/cache `server/artifacts/`. Hepsi gitignored (büyük dosyalar GitHub'a gitmez).
- **Katman sorumlulukları:** route'lar ince; iş mantığı `model/recommender.py` ve
  `services/external.py`'de. Ağır iş (eğitim) request içinde değil bootstrap'ta.
- **Yapılandırma:** Tüm ayarlar `.env` → `app/config.py:config`. Sabit kodlama yok.
