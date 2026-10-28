-- V3: Değer döndüren, yan etkisiz function'lar (fn_*) — `SELECT * FROM fn_...(...)`

-- Katalog (server açılışında belleğe alınır), işlenmiş CSV sırasıyla
CREATE OR REPLACE FUNCTION fn_get_movies()
RETURNS TABLE (
    movie_id     integer,
    title        text,
    genres       text,
    tags         text,
    year         integer,
    imdb_id      text,
    tmdb_id      integer,
    avg_rating   double precision,
    rating_count integer,
    stats_order  integer,
    poster_path  text
)
LANGUAGE sql
STABLE
AS $$
    SELECT m.movie_id, m.title, m.genres, m.tags, m.year, m.imdb_id, m.tmdb_id,
           m.avg_rating, m.rating_count, m.stats_order, m.poster_path
    FROM movies m
    ORDER BY m.row_order;
$$;


CREATE OR REPLACE FUNCTION fn_get_meta()
RETURNS TABLE (
    key   app_meta_key,
    value jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT a.key, a.value FROM app_meta a;
$$;


CREATE OR REPLACE FUNCTION fn_get_meta_value(p_key app_meta_key)
RETURNS TABLE (value jsonb)
LANGUAGE sql
STABLE
AS $$
    SELECT a.value FROM app_meta a WHERE a.key = p_key;
$$;


-- Detay önbelleği: veri + son güncellenme zamanı. Server kayıt EXTERNAL_CACHE_TTL_DAYS'ten
-- (varsayılan 30) eskiyse ziyaret anında TMDb/OMDb'den yeniler (sp_upsert_external_cache).
CREATE OR REPLACE FUNCTION fn_get_external_cache(p_key text)
RETURNS TABLE (
    data       jsonb,
    updated_at timestamptz
)
LANGUAGE sql
STABLE
AS $$
    SELECT c.data, c.updated_at FROM external_cache c WHERE c.key = p_key;
$$;


-- Yayında daha önce çözülmüş TMDb poster yollarını yeniden sorgulamamak için
CREATE OR REPLACE FUNCTION fn_get_poster_paths()
RETURNS TABLE (
    movie_id    integer,
    poster_path text
)
LANGUAGE sql
STABLE
AS $$
    SELECT m.movie_id, m.poster_path FROM movies m;
$$;
