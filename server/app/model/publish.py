"""Eğitimden sonra katalog ve analiz verisini Neon'a yazar (yalnızca yerelde).

`movies` tablosuna film bilgisi, puan özetleri ve TMDb poster yolu; `app_meta`
tablosuna analiz grafikleri, istatistikler, model metrikleri ve model sürümü yazılır.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import httpx
import pandas as pd

from app.config import config
from app.data import analysis as analysis_mod
from app.db import mappers, migrations
from app.db import repository as repo
from app.db.enums import MetaKey
from app.model import model_store
from app.services import external

POSTER_WORKERS = 8  # TMDb'ye paralel istek sayısı


def is_published(db_url: str) -> bool:
    with repo.connect(db_url) as conn:
        migrations.migrate(conn)
        return repo.get_meta_value(conn, MetaKey.MODEL_VERSION) == model_store.version()


def _poster_paths(links: pd.DataFrame, known: dict[int, str | None]) -> dict[int, str | None]:
    """Önceden bulunanları yeniden sorgulamaz; yalnızca eksikleri TMDb'den çözer."""
    result = {mid: path for mid, path in known.items() if path}
    todo = links[~links["movieId"].isin(result.keys())]
    if todo.empty or not config.has_tmdb:
        return result
    print(f"[yayın] TMDb poster yolları çözülüyor: {len(todo):,} film...")
    with httpx.Client(timeout=10.0) as client, ThreadPoolExecutor(POSTER_WORKERS) as ex:
        found = ex.map(
            lambda r: external.resolve_poster_path(int(r.tmdbId), str(r.imdbId), client),
            todo.itertuples(),
        )
        for mid, path in zip(todo["movieId"], found):
            result[int(mid)] = path
    return result


def run(db_url: str, poster_source_url: str | None = None) -> None:
    print("[yayın] Model ve işlenmiş veri yükleniyor...")
    payload = model_store.load()
    k = payload.get("k", config.KNN_K)

    movies = pd.read_csv(config.PROC_DIR / "movies_clean.csv")
    ratings = pd.read_csv(config.PROC_DIR / "ratings_clean.csv")
    links = pd.read_csv(config.PROC_DIR / "movie_links.csv")

    # sort=False: eşit puanlı filmlerde ilk görülme sırası korunur (stats_order)
    avg_ratings = ratings.groupby("movieId", sort=False)["rating"].mean().round(2)
    rating_counts = ratings.groupby("movieId", sort=False)["rating"].count()
    stats_order = {int(mid): i for i, mid in enumerate(avg_ratings.index)}

    known: dict[int, str | None] = {}
    for url in (poster_source_url, db_url):
        if url:
            with repo.connect(url) as conn:
                migrations.migrate(conn)
                known.update(repo.get_poster_paths(conn) or {})
    posters = _poster_paths(links, known)

    imdb = links.set_index("movieId")["imdbId"].to_dict()
    tmdb = links.set_index("movieId")["tmdbId"].to_dict()
    movie_records = [
        mappers.movie_to_record(
            movie_id=int(r.movieId), row_order=i, stats_order=stats_order[int(r.movieId)],
            title=str(r.title_clean), genres=str(r.genres),
            tags="" if pd.isna(r.tags) else str(r.tags),
            year=int(r.year) if pd.notna(r.year) else None,
            imdb_id=str(imdb.get(r.movieId, "")), tmdb_id=int(tmdb.get(r.movieId, 0)),
            avg_rating=float(avg_ratings[r.movieId]),
            rating_count=int(rating_counts[r.movieId]),
            poster_path=posters.get(int(r.movieId)),
        )
        for i, r in enumerate(movies.itertuples())
    ]

    if config.METRICS_PATH.exists():
        with open(config.METRICS_PATH, encoding="utf-8") as f:
            model_info = json.load(f)
    else:
        model_info = {
            "algorithm": "KNN — Öklid Mesafesi",
            "k": k,
            "n_movies": int(len(payload["movie_ids"])),
            "n_users": int(payload["matrix"].shape[1]),
        }

    meta = {
        MetaKey.ANALYSIS: analysis_mod.build_analysis(movies, ratings),
        MetaKey.DATASET_STATS: analysis_mod.dataset_stats(movies, ratings, k),
        MetaKey.MODEL_INFO: model_info,
        MetaKey.MODEL_VERSION: model_store.version(),
        MetaKey.PUBLISHED_AT: datetime.now(timezone.utc).isoformat(),
    }

    print(f"[yayın] Veritabanına yazılıyor: {len(movie_records):,} film...")
    with repo.connect(db_url) as conn:
        migrations.migrate(conn)
        n_movies = repo.replace_catalog(conn, movie_records, meta)
    missing = sum(1 for m in movie_records if not m["poster_path"])
    print(f"[yayın] Tamamlandı -> {n_movies:,} film. Postersiz film: {missing}")
