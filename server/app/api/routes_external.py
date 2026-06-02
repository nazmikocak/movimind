from fastapi import APIRouter, Response

from app.services import external

router = APIRouter(prefix="/api", tags=["external"])


@router.get("/poster/{imdb_id}")
def poster(imdb_id: str):
    """Poster görselini server üzerinden proxy'ler (client dış servise gitmez)."""
    result = external.poster_bytes(imdb_id)
    if result is None:
        return Response(status_code=404)
    content, content_type = result
    return Response(
        content=content,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=604800"},
    )
