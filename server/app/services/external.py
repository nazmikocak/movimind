"""Harici film API'leri (TMDb + OMDb) — TÜM dış istekler burada yapılır.

Frontend hiçbir dış servise bağlanmaz; yalnızca kendi server'ımıza gelir,
server da TMDb/OMDb ve poster servisini proxy'ler. Sonuçlar diske
cache'lenerek tekrarlı çağrılar ve anahtar kotası korunur.
"""
from __future__ import annotations

import json
import threading

import httpx

from app.config import config

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p"
OMDB_BASE = "https://www.omdbapi.com/"
METAHUB = "https://images.metahub.space/poster/medium"

_cache_lock = threading.Lock()
_cache: dict | None = None


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        if config.CACHE_PATH.exists():
            try:
                with open(config.CACHE_PATH, encoding="utf-8") as f:
                    _cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                _cache = {}
        else:
            _cache = {}
    return _cache


def _save_cache() -> None:
    if _cache is None:
        return
    config.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False)


def _img(path: str | None, size: str) -> str | None:
    return f"{TMDB_IMG}/{size}{path}" if path else None


# ── TMDb ─────────────────────────────────────────────────────
def _tmdb_get(path: str, **params) -> dict | None:
    if not config.has_tmdb:
        return None
    params["api_key"] = config.TMDB_API_KEY
    try:
        with httpx.Client(timeout=8.0) as c:
            r = c.get(f"{TMDB_BASE}{path}", params=params)
            if r.status_code == 200:
                return r.json()
    except httpx.HTTPError:
        return None
    return None


def _resolve_tmdb_id(tmdb_id: int, imdb_id: str) -> int:
    if tmdb_id:
        return tmdb_id
    if imdb_id and imdb_id != "tt0000000":
        data = _tmdb_get(f"/find/{imdb_id}", external_source="imdb_id")
        if data and data.get("movie_results"):
            return int(data["movie_results"][0]["id"])
    return 0


def _tmdb_details(tmdb_id: int) -> dict:
    data = _tmdb_get(
        f"/movie/{tmdb_id}", language="tr-TR",
        append_to_response="credits,videos",
    )
    if not data:
        return {}
    credits = data.get("credits", {}) or {}
    cast = [
        {
            "name": c.get("name"),
            "character": c.get("character"),
            "photo": _img(c.get("profile_path"), "w185"),
        }
        for c in (credits.get("cast", []) or [])[:18]
    ]
    director = next(
        (c.get("name") for c in (credits.get("crew", []) or [])
         if c.get("job") == "Director"),
        None,
    )
    trailer = next(
        (v.get("key") for v in (data.get("videos", {}) or {}).get("results", [])
         if v.get("site") == "YouTube" and v.get("type") == "Trailer"),
        None,
    )
    return {
        "tmdb_id": tmdb_id,
        "overview": data.get("overview") or None,
        "tagline": data.get("tagline") or None,
        "runtime": data.get("runtime") or None,
        "release_date": data.get("release_date") or None,
        "poster": _img(data.get("poster_path"), "w500"),
        "backdrop": _img(data.get("backdrop_path"), "w1280"),
        "tmdb_rating": data.get("vote_average"),
        "tmdb_votes": data.get("vote_count"),
        "budget": data.get("budget") or None,
        "revenue": data.get("revenue") or None,
        "cast": cast,
        "director": director,
        "trailer_key": trailer,
    }


# ── OMDb ─────────────────────────────────────────────────────
def _omdb_details(imdb_id: str) -> dict:
    if not config.has_omdb or not imdb_id or imdb_id == "tt0000000":
        return {}
    try:
        with httpx.Client(timeout=8.0) as c:
            r = c.get(OMDB_BASE, params={"apikey": config.OMDB_API_KEY, "i": imdb_id})
            if r.status_code != 200:
                return {}
            d = r.json()
    except httpx.HTTPError:
        return {}
    if d.get("Response") == "False":
        return {}

    def _val(k):
        v = d.get(k)
        return v if v and v != "N/A" else None

    return {
        "imdb_rating": _val("imdbRating"),
        "imdb_votes": _val("imdbVotes"),
        "awards": _val("Awards"),
        "language": _val("Language"),
        "country": _val("Country"),
        "rated": _val("Rated"),
        "plot": _val("Plot"),
        "actors": _val("Actors"),
        "released": _val("Released"),
        "metascore": _val("Metascore"),
    }


# ── Birleşik detay (cache'li) ────────────────────────────────
def movie_external_details(tmdb_id: int, imdb_id: str) -> dict:
    key = f"{tmdb_id}:{imdb_id}"
    with _cache_lock:
        cache = _load_cache()
        if key in cache:
            return cache[key]

    resolved = _resolve_tmdb_id(int(tmdb_id or 0), imdb_id)
    result = {"available": config.has_tmdb or config.has_omdb}
    if resolved:
        result.update(_tmdb_details(resolved))
    result.update(_omdb_details(imdb_id))

    with _cache_lock:
        cache = _load_cache()
        cache[key] = result
        _save_cache()
    return result


# ── Poster proxy (görüntü baytları server üzerinden) ─────────
def poster_bytes(imdb_id: str) -> tuple[bytes, str] | None:
    if not imdb_id or imdb_id == "tt0000000":
        return None
    url = f"{METAHUB}/{imdb_id}/img"
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as c:
            r = c.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and r.content:
                return r.content, r.headers.get("content-type", "image/jpeg")
    except httpx.HTTPError:
        return None
    return None
