"""Veritabanı satırları ile uygulama nesneleri arasındaki dönüşümler."""
from __future__ import annotations

from datetime import datetime

from app.db.enums import MetaKey


def movie_from_row(row: tuple) -> dict:
    """`fn_get_movies` satırını API'nin film sözlüğüne çevirir."""
    (movie_id, title, genres, tags, year, imdb_id, tmdb_id,
     avg_rating, rating_count, stats_order, poster_path) = row
    return {
        "movieId": movie_id,
        "title_clean": title,
        "genres": genres,
        "tags": tags,
        "year": year,
        "imdbId": imdb_id,
        "tmdbId": tmdb_id,
        "avg_rating": avg_rating,
        "rating_count": rating_count,
        "stats_order": stats_order,
        "poster_path": poster_path,
    }


def external_cache_from_row(row: tuple) -> tuple[dict, datetime]:
    """`fn_get_external_cache` satırı: (detay verisi, son güncellenme zamanı)."""
    data, updated_at = row
    return data, updated_at


def meta_from_rows(rows: list[tuple]) -> dict[MetaKey, object]:
    """`fn_get_meta` satırlarını `{MetaKey: değer}` sözlüğüne çevirir."""
    return {MetaKey(key): value for key, value in rows}


def poster_paths_from_rows(rows: list[tuple]) -> dict[int, str | None]:
    """`fn_get_poster_paths` satırlarını `{movie_id: poster_path}` sözlüğüne çevirir."""
    return {movie_id: poster_path for movie_id, poster_path in rows}


def movie_to_record(
    movie_id: int, row_order: int, stats_order: int, title: str, genres: str,
    tags: str, year: int | None, imdb_id: str, tmdb_id: int, avg_rating: float,
    rating_count: int, poster_path: str | None,
) -> dict:
    """`sp_insert_movies` için tek film kaydı."""
    return {
        "movie_id": movie_id, "row_order": row_order, "stats_order": stats_order,
        "title": title, "genres": genres, "tags": tags, "year": year,
        "imdb_id": imdb_id, "tmdb_id": tmdb_id, "avg_rating": avg_rating,
        "rating_count": rating_count, "poster_path": poster_path,
    }
