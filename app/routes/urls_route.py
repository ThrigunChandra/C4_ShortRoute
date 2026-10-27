from ..services.url_services import generate_short_code
from ..schemas.url_schema import LinkCreate
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/links")
def shorten_url(data: LinkCreate):
    shorten = generate_short_code()

    return {
        "given_url" : str(data.given_url),
        "short_code" : shorten
    }