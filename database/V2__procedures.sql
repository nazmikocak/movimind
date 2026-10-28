-- V2: DML yapan procedure'ler (sp_*) — `CALL sp_...(...)`
-- Sonuç gereken procedure'ler INOUT o_* parametresiyle değer döndürür.

-- Katalog yenileme sırası (publish.py, tek transaction):
--   sp_clear_catalog -> sp_insert_movies (parça parça) -> sp_set_meta

CREATE OR REPLACE PROCEDURE sp_clear_catalog()
LANGUAGE sql
AS $$
    TRUNCATE movies;
$$;


-- p_movies: [{movie_id, row_order, stats_order, title, genres, tags, year,
--             imdb_id, tmdb_id, avg_rating, rating_count, poster_path}, ...]
CREATE OR REPLACE PROCEDURE sp_insert_movies(
    p_movies       jsonb,
    INOUT o_inserted integer DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO movies (
        movie_id, row_order, stats_order, title, genres, tags, year,
        imdb_id, tmdb_id, avg_rating, rating_count, poster_path
    )
    SELECT m.movie_id, m.row_order, m.stats_order, m.title, m.genres, m.tags, m.year,
           m.imdb_id, m.tmdb_id, m.avg_rating, m.rating_count, m.poster_path
    FROM jsonb_to_recordset(p_movies) AS m (
        movie_id     integer,
        row_order    integer,
        stats_order  integer,
        title        text,
        genres       text,
        tags         text,
        year         integer,
        imdb_id      text,
        tmdb_id      integer,
        avg_rating   double precision,
        rating_count integer,
        poster_path  text
    );
    GET DIAGNOSTICS o_inserted = ROW_COUNT;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_set_meta(
    p_key            app_meta_key,
    p_value          jsonb,
    INOUT o_updated_at timestamptz DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO app_meta (key, value)
    VALUES (p_key, p_value)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    RETURNING updated_at INTO o_updated_at;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_upsert_external_cache(
    p_key            text,
    p_data           jsonb,
    INOUT o_updated_at timestamptz DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO external_cache (key, data)
    VALUES (p_key, p_data)
    ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data
    RETURNING updated_at INTO o_updated_at;
END;
$$;
