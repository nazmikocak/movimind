"""TMDb ve OMDb istekleri; API anahtarları yalnızca server'da kalır.

Film detayları bellekte ve Neon'daki `external_cache` tablosunda tutulur. Kayıt
`EXTERNAL_CACHE_TTL_DAYS`'ten eskiyse ziyaret anında yenilenir; servisler o an
cevap vermezse eski kayıt gösterilir.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone

import httpx

from app.config import config
from app.db import repository as repo

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p"
OMDB_BASE = "https://www.omdbapi.com/"

# Yenileme başarısız olunca eski kayıt bu süre boyunca tekrar denenmeden gösterilir
_RETRY_AFTER = timedelta(hours=1)

_cache_lock = threading.Lock()
_cache: dict[str, tuple[dict, datetime]] = {}   # anahtar -> (veri, geçerlilik sonu)


def _img(path: str | None, size: str) -> str | None:
    return f"{TMDB_IMG}/{size}{path}" if path else None


def poster_url(poster_path: str | None) -> str | None:
    """Liste/kart posterleri için TMDb CDN adresi."""
    return _img(poster_path, config.TMDB_POSTER_SIZE)


def _tmdb_get(path: str, client: httpx.Client | None = None, **params) -> dict | None:
    if not config.has_tmdb:
        return None
    params["api_key"] = config.TMDB_API_KEY
    try:
        c = client or httpx.Client(timeout=8.0)
        try:
            for _ in range(3):
                r = c.get(f"{TMDB_BASE}{path}", params=params)
                if r.status_code == 429:  # hız sınırı: kısa bekleyip tekrar dene
                    time.sleep(float(r.headers.get("retry-after", 1)))
                    continue
                return r.json() if r.status_code == 200 else None
        finally:
            if client is None:
                c.close()
    except httpx.HTTPError:
        return None
    return None


def resolve_poster_path(tmdb_id: int, imdb_id: str, client: httpx.Client | None = None) -> str | None:
    """Poster yolunu önce kayıtlı TMDb ID ile, bulunamazsa IMDb ID ile arar.

    MovieLens'teki bazı TMDb ID'leri eskimiş (ör. dizi olarak taşınmış yapımlar);
    IMDb araması bunları film veya dizi sonucu olarak yakalar.
    """
    if tmdb_id:
        data = _tmdb_get(f"/movie/{tmdb_id}", client)
        if data and data.get("poster_path"):
            return data["poster_path"]
    if imdb_id and imdb_id != "tt0000000":
        data = _tmdb_get(f"/find/{imdb_id}", client, external_source="imdb_id") or {}
        for kind in ("movie_results", "tv_results"):
            for item in data.get(kind) or []:
                if item.get("poster_path"):
                    return item["poster_path"]
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


def _fetch_details(tmdb_id: int, imdb_id: str) -> dict:
    resolved = _resolve_tmdb_id(int(tmdb_id or 0), imdb_id)
    result = {"available": config.has_tmdb or config.has_omdb}
    if resolved:
        result.update(_tmdb_details(resolved))
    result.update(_omdb_details(imdb_id))
    return result


def _remember(key: str, data: dict, valid_until: datetime) -> dict:
    with _cache_lock:
        _cache[key] = (data, valid_until)
    return data


def movie_external_details(tmdb_id: int, imdb_id: str) -> dict:
    key = f"{tmdb_id}:{imdb_id}"
    ttl = timedelta(days=config.EXTERNAL_CACHE_TTL_DAYS)
    now = datetime.now(timezone.utc)

    # Önce bellek, sonra Neon; süresi dolmamış kayıt doğrudan döner
    with _cache_lock:
        memo = _cache.get(key)
    if memo and memo[1] > now:
        return memo[0]
    stale = memo[0] if memo else None
    if memo is None:
        stored = repo.get_external_cache(key)
        if stored is not None:
            data, updated_at = stored
            if updated_at + ttl > now:
                return _remember(key, data, updated_at + ttl)
            stale = data

    # Kayıt yoksa veya eskidiyse servislerden çekilir, aynı satırın üzerine yazılır
    result = _fetch_details(tmdb_id, imdb_id)
    if len(result) > 1:  # en az bir servisten veri geldi
        updated_at = repo.upsert_external_cache(key, result)
        return _remember(key, result, updated_at + ttl)

    # Servisler cevap vermedi veya anahtar yok: eski kayıt varsa o gösterilir
    if stale is not None:
        return _remember(key, stale, now + _RETRY_AFTER)
    return result

