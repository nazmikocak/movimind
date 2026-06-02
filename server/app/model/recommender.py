"""Öneri motoru — eğitilmiş KNN modelini ve işlenmiş veriyi yükler.

Tüm öneri/arama/istatistik fonksiyonları buradan servis edilir.
Algoritma: item-based KNN, **Öklid mesafesi** (cosine DEĞİL).
"""
from __future__ import annotations

import json
import pickle

import pandas as pd

from app.config import config
from app.data import analysis as analysis_mod

# ── Modül durumu (ilk import'ta yüklenir) ────────────────────
_model = None
_matrix = None
_movie_ids = None
_movie_to_idx = None
_k = config.KNN_K

movies: pd.DataFrame | None = None
ratings: pd.DataFrame | None = None
avg_ratings: pd.Series | None = None
rating_counts: pd.Series | None = None
movie_imdb: dict = {}
movie_tmdb: dict = {}
_analysis: dict = {}
_metrics: dict = {}


def load() -> None:
    """Model ve veriyi belleğe al. main.py bootstrap'tan sonra çağrılır."""
    global _model, _matrix, _movie_ids, _movie_to_idx, _k
    global movies, ratings, avg_ratings, rating_counts, movie_imdb, movie_tmdb
    global _analysis, _metrics

    with open(config.MODEL_PATH, "rb") as f:
        payload = pickle.load(f)
    _model = payload["model"]
    _matrix = payload["matrix"]
    _movie_ids = payload["movie_ids"]
    _movie_to_idx = payload["movie_to_idx"]
    _k = payload.get("k", config.KNN_K)

    movies = pd.read_csv(config.PROC_DIR / "movies_clean.csv")
    ratings = pd.read_csv(config.PROC_DIR / "ratings_clean.csv")
    avg_ratings = ratings.groupby("movieId", sort=False)["rating"].mean().round(2)
    rating_counts = ratings.groupby("movieId", sort=False)["rating"].count()

    links = pd.read_csv(config.PROC_DIR / "movie_links.csv")
    movie_imdb = links.set_index("movieId")["imdbId"].to_dict()
    movie_tmdb = links.set_index("movieId")["tmdbId"].to_dict()

    _analysis = analysis_mod.build_analysis(movies, ratings)

    if config.METRICS_PATH.exists():
        with open(config.METRICS_PATH, encoding="utf-8") as f:
            _metrics = json.load(f)


# ── Yardımcılar ──────────────────────────────────────────────
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


# ── Benzer filmler (KNN — Öklid) ─────────────────────────────
def get_similar_movies(movie_id: int, n: int = 10) -> list[dict]:
    if movie_id not in _movie_to_idx:
        return []
    idx = _movie_to_idx[movie_id]
    distances, indices = _model.kneighbors(_matrix[idx], n_neighbors=n + 1)
    results = []
    for dist, i in zip(distances.flatten()[1:], indices.flatten()[1:]):
        mid = int(_movie_ids[i])
        data = _movie_row(mid, f"Benzer izleyici profili (Öklid: {dist:.2f})")
        if data:
            data["distance"] = round(float(dist), 4)
            results.append(data)
    return results


# ── Kriterli öneri ───────────────────────────────────────────
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

    # KNN tohum filmi: önce komşu havuzuna indir
    if movie_id is not None and movie_id in _movie_to_idx:
        idx = _movie_to_idx[movie_id]
        k_search = min(n * 8, len(_movie_ids))
        distances, indices = _model.kneighbors(_matrix[idx], n_neighbors=k_search + 1)
        neighbor_ids = [int(_movie_ids[i]) for i in indices.flatten()[1:]]
        df = df[df["movieId"].isin(neighbor_ids) & (df["movieId"] != movie_id)]
        knn_reason = {
            int(_movie_ids[i]): round(float(d), 4)
            for d, i in zip(distances.flatten()[1:], indices.flatten()[1:])
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

    # Sıralama stratejisi
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
            "reason": reason,
        })
    return results


# ── Listeler ─────────────────────────────────────────────────
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
        }
        for _, r in df.iterrows()
    ]


def get_movie_base(movie_id: int) -> dict | None:
    """Detay sayfası için veri setindeki temel film bilgisi."""
    return _movie_row(int(movie_id))


# ── İstatistik / analiz / model bilgisi ──────────────────────
def get_dataset_stats() -> dict:
    used_ratings = int(len(ratings))
    used_movies = int(movies["movieId"].nunique())
    used_users = int(ratings["userId"].nunique())
    return {
        "total_users": used_users,
        "total_movies": used_movies,
        "total_ratings": used_ratings,
        "avg_rating": round(float(ratings["rating"].mean()), 2),
        "algorithm": f"KNN (K={_k}, Öklid Mesafesi)",
        "dataset": "MovieLens ml-32m",
        "sample_info": {
            "original_ratings": config.ORIGINAL_RATINGS,
            "original_movies": config.ORIGINAL_MOVIES,
            "original_users": config.ORIGINAL_USERS,
            "used_ratings": used_ratings,
            "used_movies": used_movies,
            "used_users": used_users,
            "ratings_pct": round(used_ratings / config.ORIGINAL_RATINGS * 100, 2),
            "movies_pct": round(used_movies / config.ORIGINAL_MOVIES * 100, 2),
            "users_pct": round(used_users / config.ORIGINAL_USERS * 100, 2),
            "film_threshold": config.FILM_MIN_RATINGS,
            "user_threshold": config.USER_MIN_RATINGS,
        },
    }


def get_analysis() -> dict:
    return _analysis


def get_model_info() -> dict:
    return _metrics or {
        "algorithm": "KNN — Öklid Mesafesi",
        "k": _k,
        "n_movies": int(len(_movie_ids)) if _movie_ids is not None else 0,
        "n_users": int(_matrix.shape[1]) if _matrix is not None else 0,
    }
