from fastapi import APIRouter, HTTPException, Query

from app.model import recommender as rec
from app.services import external

router = APIRouter(prefix="/api", tags=["movies"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), n: int = Query(10, ge=1, le=20)):
    return rec.search_movies(q, n)


@router.get("/similar/{movie_id}")
def similar(movie_id: int, n: int = Query(10, ge=1, le=20)):
    return rec.get_similar_movies(movie_id, n)


@router.get("/movie/{movie_id}/details")
def movie_details(movie_id: int):
    base = rec.get_movie_base(movie_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Film bulunamadı")
    base["external"] = external.movie_external_details(
        base.get("tmdbId", 0), base.get("imdbId", "")
    )
    return base
