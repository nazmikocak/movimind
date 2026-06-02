"""Betimsel istatistik ve grafik verisi üretimi (saf fonksiyonlar).

Veri Seti Analizi sayfasındaki grafikleri besler. Yüklenmiş
DataFrame'ler üzerinde çalışır; CSV okuma yapmaz (recommender çağırır).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Türlerin sabit sırası (görsel tutarlılık)
GENRE_ORDER = [
    "Drama", "Comedy", "Thriller", "Action", "Romance", "Adventure",
    "Crime", "Sci-Fi", "Horror", "Fantasy", "Children", "Animation",
    "Mystery", "Documentary", "War", "Musical", "Western", "Film-Noir",
]


def genre_distribution(movies: pd.DataFrame) -> list[dict]:
    """Tür başına film sayısı (çoktan-çoğa, '|' ayrılmış)."""
    exploded = movies["genres"].str.split("|").explode().str.strip()
    counts = exploded[exploded != "(no genres listed)"].value_counts()
    return [{"genre": g, "count": int(c)} for g, c in counts.items()]


def rating_distribution(ratings: pd.DataFrame) -> list[dict]:
    """0.5–5.0 yarım yıldız aralıklı puan histogramı."""
    counts = ratings["rating"].value_counts().sort_index()
    return [{"rating": float(r), "count": int(c)} for r, c in counts.items()]


def year_distribution(movies: pd.DataFrame, ratings: pd.DataFrame) -> list[dict]:
    """Yıllara göre film sayısı + ortalama puan."""
    df = movies.dropna(subset=["year"]).copy()
    df["year"] = df["year"].astype(int)
    df = df[(df["year"] >= 1920) & (df["year"] <= 2025)]
    avg_by_movie = ratings.groupby("movieId")["rating"].mean()
    df["avg"] = df["movieId"].map(avg_by_movie)
    grouped = df.groupby("year").agg(
        count=("movieId", "count"), avg_rating=("avg", "mean")
    )
    return [
        {
            "year": int(y),
            "count": int(row["count"]),
            "avg_rating": round(float(row["avg_rating"]), 2)
            if not np.isnan(row["avg_rating"]) else 0.0,
        }
        for y, row in grouped.iterrows()
    ]


def popularity_distribution(ratings: pd.DataFrame) -> list[dict]:
    """Filmleri aldıkları oy sayısına göre kovalar; veri setinin uzun
    kuyruk yapısını gösterir (çoğu film az, az film çok oy alır)."""
    per_movie = ratings.groupby("movieId").size()
    bins = [0, 100, 500, 2000, 10000, float("inf")]
    labels = ["< 100", "100 - 500", "500 - 2.000", "2.000 - 10.000", "10.000+"]
    binned = pd.cut(per_movie, bins=bins, labels=labels, right=False)
    counts = binned.value_counts().reindex(labels, fill_value=0)
    return [{"bucket": str(b), "count": int(c)} for b, c in counts.items()]


def descriptive_stats(ratings: pd.DataFrame) -> dict:
    """Puanların betimsel istatistikleri."""
    r = ratings["rating"]
    return {
        "count": int(len(r)),
        "mean": round(float(r.mean()), 3),
        "median": round(float(r.median()), 2),
        "std": round(float(r.std()), 3),
        "min": float(r.min()),
        "max": float(r.max()),
        "q1": float(r.quantile(0.25)),
        "q3": float(r.quantile(0.75)),
        "ratings_per_user": round(float(len(r) / ratings["userId"].nunique()), 1),
        "ratings_per_movie": round(float(len(r) / ratings["movieId"].nunique()), 1),
    }


def build_analysis(movies: pd.DataFrame, ratings: pd.DataFrame) -> dict:
    return {
        "genre_distribution": genre_distribution(movies),
        "rating_distribution": rating_distribution(ratings),
        "year_distribution": year_distribution(movies, ratings),
        "popularity_distribution": popularity_distribution(ratings),
        "descriptive": descriptive_stats(ratings),
    }
