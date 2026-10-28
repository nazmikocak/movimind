"""Öneri motoru: model dosyasını yükler ve KNN'i (Öklid) her istekte çalıştırır.

Film kataloğu, puan özetleri ve analiz verisi açılışta Neon'dan belleğe alınır.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from app.config import config
from app.db import repository as repo
from app.db.enums import MetaKey
from app.model import model_store
from app.services import external

_model: NearestNeighbors | None = None
_matrix: csr_matrix | None = None
_movie_ids: np.ndarray | None = None
_movie_to_idx: dict[int, int] = {}

movies: pd.DataFrame | None = None
avg_ratings: pd.Series | None = None
rating_counts: pd.Series | None = None
movie_imdb: dict = {}
movie_tmdb: dict = {}
movie_poster: dict = {}
_meta: dict[MetaKey, object] = {}


def load() -> None:
    """Modeli, katalogu ve meta veriyi belleğe alır (açılışta bir kez)."""
    global _model, _matrix, _movie_ids, _movie_to_idx
    global movies, avg_ratings, rating_counts, movie_imdb, movie_tmdb, movie_poster, _meta

    rows = repo.get_movies()
    meta = repo.get_meta()
    if rows is None or meta is None:
        raise RuntimeError(
            "Veritabanında katalog yok. Yerelde `python main.py` ile yayınlayın "
            "(canlı için `python main.py --publish-production`)."
        )

    payload = model_store.load()
    _model, _matrix = payload["model"], payload["matrix"]
    _movie_ids, _movie_to_idx = payload["movie_ids"], payload["movie_to_idx"]
    if meta.get(MetaKey.MODEL_VERSION) != model_store.version():
        print("[uyarı] Model dosyası veritabanındaki katalogdan farklı bir eğitime ait; "
              "yeniden yayınlayın.")

    df = pd.DataFrame(rows)
    df["year"] = df["year"].astype(float)

    # Eşit puanlı filmler eğitimdeki sırayla kalsın (stats_order)
    by_stats = df.sort_values("stats_order")
    avg_ratings = by_stats.set_index("movieId")["avg_rating"]
    rating_counts = by_stats.set_index("movieId")["rating_count"]

    movie_imdb = dict(zip(df["movieId"], df["imdbId"]))
    movie_tmdb = dict(zip(df["movieId"], df["tmdbId"]))
    movie_poster = {
        mid: external.poster_url(path) for mid, path in zip(df["movieId"], df["poster_path"])
    }
    movies = df[["movieId", "title_clean", "genres", "tags", "year"]]
    _meta = meta
    _neighbors.cache_clear()


@lru_cache(maxsize=256)
def _neighbors(movie_id: int) -> tuple[tuple[int, ...], tuple[float, ...]] | None:
    """En yakın komşular ve Öklid mesafeleri; ilk eleman filmin kendisidir.

    Sorgu vektörü yoğun (dense) verilir: sonuç aynı, hesap yaklaşık 5 kat hızlı.
    """
    idx = _movie_to_idx.get(movie_id)
    if idx is None:
        return None
    n = min(config.KNN_MAX_NEIGHBORS + 1, _matrix.shape[0])
    distances, indices = _model.kneighbors(_matrix[idx].toarray(), n_neighbors=n)
    return (
        tuple(int(_movie_ids[i]) for i in indices[0]),
        tuple(float(d) for d in distances[0]),
    )


def _movie_row(mid: int, reason: str | None = None) -> dict | None:
    row = movies[movies["movieId"] == mid]
    if row.empty:
        return None
    r = row.iloc[0]
    data = {
        "movieId": int(mid),
        "title": str(r["title_clean"]),
        "genres": str(r["genres"]),
        "tags": str(r.get("tags", "")),
        "year": int(r["year"]) if pd.notna(r.get("year")) else None,
        "avg_rating": float(avg_ratings.get(mid, 0)),
        "rating_count": int(rating_counts.get(mid, 0)),
        "imdbId": str(movie_imdb.get(mid, "")),
        "tmdbId": int(movie_tmdb.get(mid, 0)),
        "poster_url": movie_poster.get(mid),
    }
    if reason:
        data["reason"] = reason
    return data


def _decorate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["avg_rating"] = df["movieId"].map(avg_ratings.to_dict()).fillna(0)
    df["rating_count"] = df["movieId"].map(rating_counts.to_dict()).fillna(0)
    df["imdbId"] = df["movieId"].map(movie_imdb).fillna("")
    df["tmdbId"] = df["movieId"].map(movie_tmdb).fillna(0)
    return df


def get_similar_movies(movie_id: int, n: int = 10) -> list[dict]:
    nb = _neighbors(movie_id)
    if nb is None:
        return []
    ids, dists = nb
    results = []
    for dist, mid in zip(dists[1:n + 1], ids[1:n + 1]):
        data = _movie_row(mid, f"Benzer izleyici profili (Öklid: {dist:.2f})")
        if data:
            data["distance"] = round(float(dist), 4)
            results.append(data)
    return results


def get_recommendations(
    genre: str | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    tag: str | None = None,
    min_votes: int | None = None,
    sort: str = "rating",
    n: int = 10,
    movie_id: int | None = None,
) -> list[dict]:
    df = _decorate(movies)
    knn_reason = None

    # Referans film verildiyse adaylar onun KNN komşularıyla sınırlanır
    nb = _neighbors(movie_id) if movie_id is not None else None
    if nb is not None:
        ids, dists = nb
        k_search = min(n * 8, len(ids) - 1)
        neighbor_ids = list(ids[1:k_search + 1])
        df = df[df["movieId"].isin(neighbor_ids) & (df["movieId"] != movie_id)]
        knn_reason = {
            mid: round(float(d), 4)
            for d, mid in zip(dists[1:k_search + 1], ids[1:k_search + 1])
        }

    if genre:
        wanted = [g.strip() for g in genre.split(",") if g.strip()]
        if wanted:
            df = df[df["genres"].str.contains("|".join(wanted), case=False, na=False)]
    if min_rating is not None:
        df = df[df["avg_rating"] >= min_rating]
    if max_rating is not None:
        df = df[df["avg_rating"] <= max_rating]
    if year_min is not None:
        df = df[df["year"] >= year_min]
    if year_max is not None:
        df = df[df["year"] <= year_max]
    if tag:
        df = df[df["tags"].str.contains(tag, case=False, na=False)]
    if min_votes:
        df = df[df["rating_count"] >= min_votes]

    if knn_reason is not None:
        df = df.assign(_d=df["movieId"].map(knn_reason).fillna(9e9)).sort_values("_d")
    elif sort == "popularity":
        df = df.sort_values("rating_count", ascending=False)
    elif sort == "year":
        df = df.sort_values("year", ascending=False)
    elif sort == "title":
        df = df.sort_values("title_clean", key=lambda s: s.str.lower())
    else:  # rating
        df = df.sort_values(["avg_rating", "rating_count"], ascending=False)

    df = df.head(n)

    results = []
    for _, r in df.iterrows():
        mid = int(r["movieId"])
        if knn_reason is not None:
            reason = f"Beğendiğin filme benzer izleyici profili (Öklid: {knn_reason.get(mid, 0):.2f})"
        elif sort == "popularity":
            reason = f"En çok izlenen ({int(r['rating_count']):,} oy)"
        elif sort == "year":
            reason = "Kriterlerine uygun yeni yapım"
        else:
            reason = f"Kriterlerine en uygun ({r['avg_rating']:.1f}/5)"
        results.append({
            "movieId": mid,
            "title": str(r["title_clean"]),
            "genres": str(r["genres"]),
            "tags": str(r.get("tags", "")),
            "year": int(r["year"]) if pd.notna(r.get("year")) else None,
            "avg_rating": float(r["avg_rating"]),
            "rating_count": int(r["rating_count"]),
            "imdbId": str(r["imdbId"]),
            "tmdbId": int(r["tmdbId"]),
            "poster_url": movie_poster.get(mid),
            "reason": reason,
        })
    return results


def get_top_rated(n: int = 10, min_votes: int = 1000) -> list[dict]:
    eligible = rating_counts[rating_counts >= min_votes].index
    top_ids = avg_ratings.loc[avg_ratings.index.isin(eligible)].nlargest(n).index
    return [row for mid in top_ids for row in [_movie_row(int(mid))] if row]


def get_most_rated(n: int = 10) -> list[dict]:
    top_ids = rating_counts.nlargest(n).index
    return [row for mid in top_ids for row in [_movie_row(int(mid))] if row]


def search_movies(q: str, n: int = 10) -> list[dict]:
    df = _decorate(movies)
    mask = df["title_clean"].str.contains(q.strip(), case=False, na=False, regex=False)
    df = df[mask].nlargest(n, "rating_count")
    return [
        {
            "movieId": int(r["movieId"]),
            "title": str(r["title_clean"]),
            "genres": str(r["genres"]),
            "tags": str(r.get("tags", "")),
            "year": int(r["year"]) if pd.notna(r.get("year")) else None,
            "avg_rating": float(r["avg_rating"]),
            "rating_count": int(r["rating_count"]),
            "imdbId": str(r["imdbId"]),
            "tmdbId": int(r["tmdbId"]),
            "poster_url": movie_poster.get(int(r["movieId"])),
        }
        for _, r in df.iterrows()
    ]


def get_movie_base(movie_id: int) -> dict | None:
    """Detay sayfası için veri setindeki film bilgisi."""
    return _movie_row(int(movie_id))


def get_dataset_stats() -> dict:
    return _meta.get(MetaKey.DATASET_STATS, {})


def get_analysis() -> dict:
    return _meta.get(MetaKey.ANALYSIS, {})


def get_model_info() -> dict:
    return _meta.get(MetaKey.MODEL_INFO, {})
