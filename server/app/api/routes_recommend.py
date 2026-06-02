from fastapi import APIRouter, Query

from app.model import recommender as rec

router = APIRouter(prefix="/api", tags=["recommend"])


@router.get("/recommend")
def recommend(
    genre: str = Query(None),
    min_rating: float = Query(None, ge=0, le=5),
    max_rating: float = Query(None, ge=0, le=5),
    year_min: int = Query(None),
    year_max: int = Query(None),
    tag: str = Query(None),
    min_votes: int = Query(None, ge=0),
    sort: str = Query("rating"),
    n: int = Query(10, ge=1, le=50),
    movie_id: int = Query(None),
):
    return rec.get_recommendations(
        genre=genre, min_rating=min_rating, max_rating=max_rating,
        year_min=year_min, year_max=year_max, tag=tag,
        min_votes=min_votes, sort=sort, n=n, movie_id=movie_id,
    )
