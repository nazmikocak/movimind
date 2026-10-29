"""Neon (PostgreSQL) erişim katmanı; tüm veritabanı çağrıları buradadır.

Okuma `SELECT * FROM fn_...`, yazma `CALL sp_...` ile yapılır. `get_*` fonksiyonları
kayıt yoksa `None` döndürür; kontrol servis katmanındadır.
"""
from __future__ import annotations

import atexit
from datetime import datetime

import psycopg
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from app.config import config
from app.db import mappers
from app.db.enums import MetaKey

MOVIE_BATCH = 1000  # sp_insert_movies çağrısı başına film

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        if not config.DATABASE_URL:
            raise RuntimeError("DATABASE_URL tanımlı değil (server/.env)")
        _pool = ConnectionPool(
            config.DATABASE_URL,
            min_size=0,  # boştaki bağlantılar da kapansın; açık bağlantı Neon'un uyumasını engeller
            max_size=config.DB_POOL_MAX,
            max_idle=240,  # Neon 5 dk boşta kalınca uyur; bağlantıyı ondan önce bırak
            check=ConnectionPool.check_connection,
            kwargs={"autocommit": True},
            open=True,
        )
        atexit.register(_pool.close)  # çıkışta havuz thread'leri açık kalmasın
    return _pool


def connect(url: str) -> psycopg.Connection:
    """Yayın adımı için havuz dışı, transaction'lı bağlantı."""
    if not url:
        raise RuntimeError("Veritabanı adresi tanımlı değil")
    return psycopg.connect(url)


def get_movies() -> list[dict] | None:
    with _get_pool().connection() as conn:
        rows = conn.execute("SELECT * FROM fn_get_movies()").fetchall()
    return [mappers.movie_from_row(r) for r in rows] or None


def get_meta() -> dict[MetaKey, object] | None:
    with _get_pool().connection() as conn:
        rows = conn.execute("SELECT * FROM fn_get_meta()").fetchall()
    return mappers.meta_from_rows(rows) or None


def get_external_cache(key: str) -> tuple[dict, datetime] | None:
    """(detay verisi, son güncellenme zamanı) döndürür."""
    with _get_pool().connection() as conn:
        row = conn.execute("SELECT * FROM fn_get_external_cache(%s)", (key,)).fetchone()
    return mappers.external_cache_from_row(row) if row else None


def upsert_external_cache(key: str, data: dict) -> datetime:
    """Kaydı ekler veya günceller; güncellenme zamanını döndürür."""
    with _get_pool().connection() as conn:
        return conn.execute(
            "CALL sp_upsert_external_cache(%s, %s, NULL)", (key, Jsonb(data))
        ).fetchone()[0]


def get_meta_value(conn: psycopg.Connection, key: MetaKey):
    row = conn.execute(
        "SELECT * FROM fn_get_meta_value(%s::app_meta_key)", (str(key),)
    ).fetchone()
    return row[0] if row else None


def get_poster_paths(conn: psycopg.Connection) -> dict[int, str | None] | None:
    rows = conn.execute("SELECT * FROM fn_get_poster_paths()").fetchall()
    return mappers.poster_paths_from_rows(rows) or None


def replace_catalog(
    conn: psycopg.Connection,
    movies: list[dict],
    meta: dict[MetaKey, object],
) -> int:
    """Katalog ve meta veriyi tek transaction'da yeniler; yazılan film sayısını döndürür."""
    n_movies = 0
    with conn.transaction():
        conn.execute("CALL sp_clear_catalog()")
        for i in range(0, len(movies), MOVIE_BATCH):
            n_movies += conn.execute(
                "CALL sp_insert_movies(%s, NULL)", (Jsonb(movies[i:i + MOVIE_BATCH]),)
            ).fetchone()[0]
        for key, value in meta.items():
            conn.execute(
                "CALL sp_set_meta(%s::app_meta_key, %s, NULL)", (str(key), Jsonb(value))
            )
    return n_movies
