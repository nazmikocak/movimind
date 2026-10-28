-- V1: Temel şema — enum tipleri ve tablolar (Neon / PostgreSQL)

-- app_meta tablosunun izinli anahtarları
CREATE TYPE app_meta_key AS ENUM (
    'analysis',        -- Veri Seti Analizi sayfası grafik verisi
    'dataset_stats',   -- kullanılan örneklemin özeti
    'model_info',      -- KNN metrikleri (RMSE, MAE, precision ...)
    'model_version',   -- katalogla birlikte yayınlanan model dosyasının sürümü (sha256)
    'published_at'     -- son yayın zamanı
);

-- Film kataloğu: veri setindeki film bilgisi + puan özetleri + TMDb poster yolu
CREATE TABLE movies (
    movie_id     integer PRIMARY KEY,
    row_order    integer NOT NULL,          -- işlenmiş CSV'deki sıra (sıralama eşitliklerinde)
    stats_order  integer NOT NULL,          -- puan özetlerinin sırası (top/most rated eşitlikleri)
    title        text    NOT NULL,
    genres       text    NOT NULL,
    tags         text    NOT NULL DEFAULT '',
    year         integer,
    imdb_id      text    NOT NULL,
    tmdb_id      integer NOT NULL,
    avg_rating   double precision NOT NULL,
    rating_count integer NOT NULL,
    poster_path  text
);

-- Analiz grafikleri, veri seti istatistikleri, model metrikleri, model sürümü
CREATE TABLE app_meta (
    key        app_meta_key PRIMARY KEY,
    value      jsonb        NOT NULL,
    updated_at timestamptz  NOT NULL DEFAULT now()
);

-- TMDb/OMDb detay cevapları (server uyuyup diski silinse de kalıcı)
CREATE TABLE external_cache (
    key        text PRIMARY KEY,           -- "<tmdbId>:<imdbId>"
    data       jsonb       NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);
