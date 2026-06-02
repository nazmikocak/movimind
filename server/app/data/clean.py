"""Veri temizleme + örneklem optimizasyonu.

Akış:
  1. Ham CSV'leri yükle (movies, ratings, tags, links).
  2. Eksik / tekrarlı kayıtları temizle, gereksiz sütunları at.
  3. Eşik filtresi: az puanlanan film + az aktif kullanıcıları çıkar
     (eşik mantığı katılaştırılmadı — ham veriye göre gürültü azaltma).
  4. Kullanıcı alt-örneklemi: eşiği geçen kullanıcılardan sabit-tohumlu
     rastgele bir alt küme seç → matris küçülür, KNN hızlanır.
  5. Film özelliklerini zenginleştir (yıl, temiz başlık, tür listesi, tags).
  6. İşlenmiş CSV'leri ve clean_stats.json'ı yaz.

Bu modül `run()` ile çağrılır (bootstrap), ya da doğrudan
`python -m app.data.clean` ile çalıştırılabilir.
"""
import json
import os

import numpy as np
import pandas as pd

from app.config import config


def run() -> dict:
    raw = config.RAW_DIR
    proc = config.PROC_DIR
    os.makedirs(proc, exist_ok=True)

    print("[temizleme] Ham veri yükleniyor (32M satır 1-2 dk sürebilir)...")
    movies = pd.read_csv(raw / "movies.csv")
    ratings = pd.read_csv(raw / "ratings.csv")
    tags = pd.read_csv(raw / "tags.csv")
    links = pd.read_csv(raw / "links.csv")

    before = {
        "movies": int(movies["movieId"].nunique()),
        "users": int(ratings["userId"].nunique()),
        "ratings": int(len(ratings)),
        "tags": int(len(tags)),
    }
    print(f"[temizleme] ÖNCESİ  film={before['movies']:,} "
          f"kullanıcı={before['users']:,} rating={before['ratings']:,}")

    # ── 1) Eksik veri & tekrar temizliği ─────────────────────
    movies.dropna(subset=["title", "genres"], inplace=True)
    movies.drop_duplicates(subset=["movieId"], inplace=True)
    ratings.dropna(inplace=True)
    ratings.drop_duplicates(inplace=True)
    tags.dropna(subset=["tag"], inplace=True)
    tags.drop_duplicates(inplace=True)

    # ── 2) Gereksiz sütunlar ─────────────────────────────────
    ratings.drop(columns=["timestamp"], inplace=True, errors="ignore")
    tags.drop(columns=["timestamp"], inplace=True, errors="ignore")

    # ── 3) Eşik filtresi (gürültü azaltma) ───────────────────
    film_counts = ratings["movieId"].value_counts()
    popular_ids = film_counts[film_counts >= config.FILM_MIN_RATINGS].index
    ratings = ratings[ratings["movieId"].isin(popular_ids)]

    user_counts = ratings["userId"].value_counts()
    active_ids = user_counts[user_counts >= config.USER_MIN_RATINGS].index
    ratings = ratings[ratings["userId"].isin(active_ids)]

    # ── 4) Kullanıcı alt-örneklemi (matrisi küçült) ──────────
    n_active = len(active_ids)
    if config.USER_SAMPLE and 0 < config.USER_SAMPLE < n_active:
        rng = np.random.default_rng(config.RANDOM_SEED)
        sampled = rng.choice(active_ids.to_numpy(), size=config.USER_SAMPLE, replace=False)
        ratings = ratings[ratings["userId"].isin(sampled)]
        # Örneklem sonrası filmler seyrekleşebilir → eşiği tekrar uygula
        film_counts2 = ratings["movieId"].value_counts()
        popular_ids = film_counts2[film_counts2 >= max(10, config.FILM_MIN_RATINGS // 3)].index
        ratings = ratings[ratings["movieId"].isin(popular_ids)]
        print(f"[temizleme] Kullanıcı örneklemi: {n_active:,} -> {ratings['userId'].nunique():,}")

    after = {
        "movies": int(ratings["movieId"].nunique()),
        "users": int(ratings["userId"].nunique()),
        "ratings": int(len(ratings)),
    }
    print(f"[temizleme] SONRASI film={after['movies']:,} "
          f"kullanıcı={after['users']:,} rating={after['ratings']:,}")

    # ── 5) Film özelliklerini zenginleştir ───────────────────
    movies = movies[movies["movieId"].isin(popular_ids)].copy()
    movies["year"] = movies["title"].str.extract(r"\((\d{4})\)")[0].astype(float)
    movies["title_clean"] = (
        movies["title"].str.replace(r"\s*\(\d{4}\)", "", regex=True).str.strip()
    )

    tags_filtered = tags[tags["movieId"].isin(popular_ids)]
    tags_grouped = (
        tags_filtered.groupby("movieId")["tag"]
        .apply(lambda x: ", ".join(x.str.lower().unique()[:40]))
        .reset_index()
        .rename(columns={"tag": "tags"})
    )
    movies = movies.merge(tags_grouped, on="movieId", how="left")
    movies["tags"] = movies["tags"].fillna("")

    # ── 6) IMDb / TMDb bağlantı tablosu ──────────────────────
    links["imdbId_fmt"] = (
        links["imdbId"].fillna(0).astype("int64").apply(lambda x: f"tt{x:07d}")
    )
    links["tmdbId"] = links["tmdbId"].fillna(0).astype("int64")
    movie_links = (
        movies[["movieId"]]
        .merge(links[["movieId", "imdbId_fmt", "tmdbId"]], on="movieId", how="left")
        .rename(columns={"imdbId_fmt": "imdbId"})
    )
    movie_links["imdbId"] = movie_links["imdbId"].fillna("tt0000000")
    movie_links["tmdbId"] = movie_links["tmdbId"].fillna(0).astype("int64")

    # ── Kaydet ───────────────────────────────────────────────
    movies.to_csv(proc / "movies_clean.csv", index=False)
    ratings.to_csv(proc / "ratings_clean.csv", index=False)
    tags_grouped.to_csv(proc / "tags_clean.csv", index=False)
    movie_links.to_csv(proc / "movie_links.csv", index=False)

    stats = {
        "before": before,
        "after": after,
        "thresholds": {
            "film_min_ratings": config.FILM_MIN_RATINGS,
            "user_min_ratings": config.USER_MIN_RATINGS,
            "user_sample": config.USER_SAMPLE,
        },
        "original": {
            "ratings": config.ORIGINAL_RATINGS,
            "movies": config.ORIGINAL_MOVIES,
            "users": config.ORIGINAL_USERS,
            "tags": config.ORIGINAL_TAGS,
        },
    }
    with open(config.CLEAN_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"[temizleme] Tamamlandı -> {proc}")
    return stats


def is_done() -> bool:
    needed = ["movies_clean.csv", "ratings_clean.csv", "movie_links.csv"]
    return all((config.PROC_DIR / f).exists() for f in needed)


if __name__ == "__main__":
    run()
