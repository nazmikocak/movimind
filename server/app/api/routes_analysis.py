from fastapi import APIRouter

from app.model import recommender as rec

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/analysis")
def analysis():
    """Veri Seti Analizi sayfası için grafik + betimsel istatistik verisi."""
    data = rec.get_analysis()
    return {
        **data,
        "top_rated": rec.get_top_rated(10),
        "most_rated": rec.get_most_rated(10),
        "stats": rec.get_dataset_stats(),
        "model": rec.get_model_info(),
    }
