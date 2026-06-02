from fastapi import APIRouter, Query

from app.model import recommender as rec

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
def stats():
    return rec.get_dataset_stats()


@router.get("/model-info")
def model_info():
    return rec.get_model_info()


@router.get("/top-rated")
def top_rated(n: int = Query(10, ge=1, le=50)):
    return rec.get_top_rated(n)


@router.get("/most-rated")
def most_rated(n: int = Query(10, ge=1, le=50)):
    return rec.get_most_rated(n)
