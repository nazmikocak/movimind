"""Otomasyon — server açılışında gereken adımları sırayla yürütür.

1. İşlenmiş veri yoksa  → veri temizleme + örneklem.
2. Model yoksa VEYA .env RETRAIN_ON_START=true ise → KNN eğitimi.
3. Modeli belleğe yükle (recommender).

Böylece tek komutla (`python main.py`) sistem kendini hazırlar; ayrı ayrı
script çalıştırmaya gerek kalmaz.
"""
from app.config import config
from app.data import clean
from app.model import recommender, train


def prepare() -> None:
    # 1) Veri
    if not clean.is_done():
        print("[bootstrap] İşlenmiş veri yok -> temizleme başlıyor...")
        clean.run()
    else:
        print("[bootstrap] İşlenmiş veri mevcut, atlanıyor.")

    # 2) Model
    if config.RETRAIN_ON_START:
        print("[bootstrap] RETRAIN_ON_START=true -> model yeniden eğitiliyor...")
        train.run()
    elif not train.is_done():
        print("[bootstrap] Eğitilmiş model yok -> eğitim başlıyor...")
        train.run()
    else:
        print("[bootstrap] Eğitilmiş model mevcut, kullanılıyor.")

    # 3) Belleğe yükle
    print("[bootstrap] Model belleğe yükleniyor...")
    recommender.load()
    print("[bootstrap] Hazır.")
