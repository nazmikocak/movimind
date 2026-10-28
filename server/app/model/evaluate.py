"""KNN modelinin doğruluğunu kullanıcı örneklemi üzerinde ölçer (RMSE, MAE, precision).

Her test kullanıcısından bir puan saklanır (holdout) ve filmin en yakın komşuları
arasında kullanıcının puanladıklarının mesafe ağırlıklı ortalamasıyla tahmin edilir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.config import config

LIKE_THRESHOLD = 4.0  # bu puan ve üzeri "beğenildi" sayılır


def evaluate(model, matrix, movie_to_idx, ratings: pd.DataFrame) -> dict:
    rng = np.random.default_rng(config.RANDOM_SEED)
    user_mean = ratings.groupby("userId")["rating"].mean()

    counts = ratings["userId"].value_counts()
    eligible = counts[counts >= 5].index.to_numpy()
    if len(eligible) == 0:
        return {"rmse": None, "mae": None, "precision": None,
                "precision_k": LIKE_THRESHOLD, "coverage": 0.0, "n_eval": 0}

    n = min(config.EVAL_SAMPLE_USERS, len(eligible))
    test_users = rng.choice(eligible, size=n, replace=False)

    sub = ratings[ratings["userId"].isin(test_users)]
    by_user = {uid: g for uid, g in sub.groupby("userId")}

    k = config.KNN_K
    idx_to_movie = {v: kk for kk, v in movie_to_idx.items()}
    errors, tp, predicted_pos, n_eval = [], 0, 0, 0

    for uid in test_users:
        g = by_user.get(uid)
        if g is None or len(g) < 2:
            continue
        # Holdout: rastgele bir puan tahmin için saklanır
        held = g.sample(1, random_state=config.RANDOM_SEED)
        held_movie = int(held["movieId"].iloc[0])
        held_rating = float(held["rating"].iloc[0])
        if held_movie not in movie_to_idx:
            continue

        seen = {int(r.movieId): float(r.rating)
                for r in g.itertuples() if int(r.movieId) != held_movie}
        if not seen:
            continue

        idx = movie_to_idx[held_movie]
        dist, ind = model.kneighbors(matrix[idx], n_neighbors=k + 1)
        dist, ind = dist.flatten()[1:], ind.flatten()[1:]

        num = den = 0.0
        umean = float(user_mean.get(uid, ratings["rating"].mean()))
        for d, i in zip(dist, ind):
            mid = idx_to_movie.get(int(i))
            if mid in seen:
                w = 1.0 / (d + 1e-6)
                num += w * (seen[mid] - umean)
                den += w
        if den == 0:
            continue

        pred = umean + num / den
        pred = min(5.0, max(0.5, pred))
        errors.append((pred - held_rating) ** 2)
        n_eval += 1
        if pred >= LIKE_THRESHOLD:
            predicted_pos += 1
            if held_rating >= LIKE_THRESHOLD:
                tp += 1

    if n_eval == 0:
        return {"rmse": None, "mae": None, "precision": None,
                "precision_k": LIKE_THRESHOLD, "coverage": 0.0, "n_eval": 0}

    rmse = float(np.sqrt(np.mean(errors)))
    mae = float(np.mean(np.sqrt(errors)))
    precision = round(tp / predicted_pos, 3) if predicted_pos else None
    return {
        "rmse": round(rmse, 3),
        "mae": round(mae, 3),
        "precision": precision,
        "precision_k": LIKE_THRESHOLD,
        "coverage": round(n_eval / len(test_users), 3),
        "n_eval": int(n_eval),
    }
