"""KNN (Öklid) model eğitimi — item-based collaborative filtering.

Doğruluk optimizasyonu: ham puanlar yerine **kullanıcı-ortalaması
merkezlenmiş** puanlarla film vektörleri kurulur. Böylece Öklid mesafesi
kullanıcının "cömert/cimri" puanlama eğilimini değil, tercih *şeklini*
yakalar ve öneri kalitesi artar.
"""
import json
import os
import pickle

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from app.config import config
from app.model import evaluate as ev


def run() -> dict:
    proc = config.PROC_DIR
    os.makedirs(config.ARTIFACTS_DIR, exist_ok=True)

    print("[eğitim] İşlenmiş veri yükleniyor...")
    ratings = pd.read_csv(proc / "ratings_clean.csv")
    movies = pd.read_csv(proc / "movies_clean.csv")
    print(f"[eğitim] Rating sayısı: {len(ratings):,}")

    # ── İndeks eşlemeleri (sıfırdan başlayan tam sayılar) ────
    movie_ids = ratings["movieId"].unique()
    user_ids = ratings["userId"].unique()
    movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}

    # ── Kullanıcı-ortalaması merkezleme ──────────────────────
    user_mean = ratings.groupby("userId")["rating"].transform("mean")
    centered = ratings["rating"].to_numpy() - user_mean.to_numpy()

    row = ratings["movieId"].map(movie_to_idx).to_numpy()
    col = ratings["userId"].map(user_to_idx).to_numpy()

    print(f"[eğitim] Sparse matris: {len(movie_ids):,} film x {len(user_ids):,} kullanıcı")
    matrix = csr_matrix(
        (centered, (row, col)), shape=(len(movie_ids), len(user_ids))
    )
    print(f"[eğitim] Dolu hücre: {matrix.nnz:,}")

    k = config.KNN_K
    print(f"[eğitim] KNN eğitiliyor (K={k}, metric=euclidean)...")
    model = NearestNeighbors(
        metric="euclidean", algorithm="brute", n_neighbors=k + 1, n_jobs=-1
    )
    model.fit(matrix)
    print("[eğitim] Model eğitimi tamamlandı")

    # ── Doğruluk değerlendirmesi (örneklemli) ────────────────
    print("[eğitim] Doğruluk değerlendiriliyor...")
    metrics = ev.evaluate(model, matrix, movie_to_idx, ratings)
    metrics.update({
        "algorithm": "KNN — Öklid Mesafesi",
        "k": k,
        "n_movies": int(len(movie_ids)),
        "n_users": int(len(user_ids)),
        "n_ratings": int(len(ratings)),
        "centering": "user-mean",
    })
    with open(config.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"[eğitim] Metrikler: RMSE={metrics.get('rmse')} "
          f"Precision@{metrics.get('precision_k')}={metrics.get('precision')}")

    with open(config.MODEL_PATH, "wb") as f:
        pickle.dump(
            {
                "model": model,
                "matrix": matrix,
                "movie_ids": movie_ids,
                "movie_to_idx": movie_to_idx,
                "k": k,
            },
            f,
        )
    print(f"[eğitim] Model kaydedildi -> {config.MODEL_PATH}")
    return metrics


def is_done() -> bool:
    return config.MODEL_PATH.exists()


if __name__ == "__main__":
    run()
