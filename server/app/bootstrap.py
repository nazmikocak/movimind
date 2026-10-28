"""Açılış akışı: gerekirse veriyi hazırla, modeli eğit, Neon'a yayınla, servisi yükle.

`RUN_PIPELINE=true` (yerel): temizleme, eğitim ve yayın gerektiğinde çalışır.
`RUN_PIPELINE=false` (canlı): yalnızca model dosyası ve Neon verisi yüklenir.
"""
from app.config import config
from app.model import recommender


def prepare() -> None:
    if config.RUN_PIPELINE:
        _run_pipeline()
    else:
        print("[bootstrap] RUN_PIPELINE=false -> eğitim yok; model dosyası + Neon verisi.")

    print("[bootstrap] Model kuruluyor, katalog belleğe yükleniyor...")
    recommender.load()
    print("[bootstrap] Hazır.")


def _run_pipeline() -> None:
    from app.data import clean
    from app.model import publish, train

    if not clean.is_done():
        print("[bootstrap] İşlenmiş veri yok -> temizleme başlıyor...")
        clean.run()
    else:
        print("[bootstrap] İşlenmiş veri mevcut, atlanıyor.")

    if config.RETRAIN_ON_START:
        print("[bootstrap] RETRAIN_ON_START=true -> model yeniden eğitiliyor...")
        train.run()
    elif not train.is_done():
        print("[bootstrap] Eğitilmiş model yok -> eğitim başlıyor...")
        train.run()
    else:
        print("[bootstrap] Eğitilmiş model mevcut, kullanılıyor.")

    if publish.is_published(config.DATABASE_URL):
        print("[bootstrap] Veritabanı güncel, yayın atlanıyor.")
    else:
        print("[bootstrap] Model veritabanından yeni -> yayın başlıyor...")
        publish.run(config.DATABASE_URL)


def publish_production() -> None:
    """Yerel katalogu canlı veritabanına yazar; poster yolları dev'den alınır."""
    if not config.PRODUCTION_DATABASE_URL:
        raise SystemExit("PRODUCTION_DATABASE_URL tanımlı değil (server/.env)")
    from app.model import publish

    print("[bootstrap] Canlı veritabanına yayın başlıyor...")
    publish.run(config.PRODUCTION_DATABASE_URL, poster_source_url=config.DATABASE_URL)

