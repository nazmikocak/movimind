"""`train.py`'nin ürettiği model dosyasını (`knn_model.pkl`) yükler.

Pickle, eğitimdeki numpy/scipy/scikit-learn sürümleriyle açılır; bu yüzden
`requirements.txt` bu paketleri sabit sürümle kurar.
"""
from __future__ import annotations

import hashlib
import pickle
from pathlib import Path

from app.config import config


def version(path: Path = config.MODEL_PATH) -> str:
    """Dosya içeriğinin sha256 özeti; makineden bağımsız model sürümü."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def load(path: Path = config.MODEL_PATH) -> dict:
    """`train.py` çıktısını döndürür: `{model, matrix, movie_ids, movie_to_idx, k}`."""
    if not path.exists():
        raise RuntimeError(f"Model dosyası yok: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)
