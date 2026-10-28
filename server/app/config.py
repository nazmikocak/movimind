"""Merkezi yapılandırma — tüm yollar ve ayarlar .env'den okunur."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Windows konsolu (cp1254) Türkçe dışı Unicode karakterleri yazamaz; çıktı UTF-8'e alınır
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SERVER_DIR = Path(__file__).resolve().parent.parent  # .../server
load_dotenv(SERVER_DIR / ".env")


def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


def _bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SERVER_DIR = SERVER_DIR

    RAW_DIR = SERVER_DIR / "data" / "raw" / "ml-32m"
    PROC_DIR = SERVER_DIR / "data" / "processed"
    ARTIFACTS_DIR = SERVER_DIR / "artifacts"
    MODEL_PATH = ARTIFACTS_DIR / "knn_model.pkl"
    METRICS_PATH = ARTIFACTS_DIR / "model_metrics.json"
    CLEAN_STATS_PATH = PROC_DIR / "clean_stats.json"

    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    # Yalnızca yerelde: `python main.py --publish-production` hedefi
    PRODUCTION_DATABASE_URL = os.getenv("PRODUCTION_DATABASE_URL", "").strip()
    DB_POOL_MAX = _int("DB_POOL_MAX", 4)
    DB_MIGRATIONS_DIR = SERVER_DIR.parent / "database"

    # true (yerel): temizle, eğit, Neon'a yayınla; false (canlı): yalnızca servis et
    RUN_PIPELINE = _bool("RUN_PIPELINE", True)

    FILM_MIN_RATINGS = _int("FILM_MIN_RATINGS", 75)
    USER_MIN_RATINGS = _int("USER_MIN_RATINGS", 30)
    USER_SAMPLE = _int("USER_SAMPLE", 40000)  # 0: örneklem yok, tüm kullanıcılar
    RANDOM_SEED = _int("RANDOM_SEED", 42)

    KNN_K = _int("KNN_K", 10)
    RETRAIN_ON_START = _bool("RETRAIN_ON_START", False)
    EVAL_SAMPLE_USERS = _int("EVAL_SAMPLE_USERS", 1500)
    # Bir sorguda hesaplanan en fazla komşu. /recommend en fazla n=50 x 8 = 400 komşu
    # kullandığından 400'ün altı sonuçları değiştirir.
    KNN_MAX_NEIGHBORS = _int("KNN_MAX_NEIGHBORS", 400)

    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
    OMDB_API_KEY = os.getenv("OMDB_API_KEY", "").strip()
    TMDB_POSTER_SIZE = os.getenv("TMDB_POSTER_SIZE", "w342")
    # Detay önbelleği bu süreden eskiyse ziyaret anında TMDb/OMDb'den yenilenir
    EXTERNAL_CACHE_TTL_DAYS = _int("EXTERNAL_CACHE_TTL_DAYS", 30)

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = _int("PORT", 8000)
    # Virgülle ayrılmış izinli origin listesi (canlıda arayüzün adresi)
    CORS_ORIGINS = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]

    # Ham MovieLens 32M sayıları (örneklem oranını hesaplamak için)
    ORIGINAL_RATINGS = 32_000_204
    ORIGINAL_MOVIES = 87_585
    ORIGINAL_USERS = 200_948
    ORIGINAL_TAGS = 2_000_072

    @property
    def has_tmdb(self) -> bool:
        return bool(self.TMDB_API_KEY)

    @property
    def has_omdb(self) -> bool:
        return bool(self.OMDB_API_KEY)


config = Config()
