from fastapi import APIRouter 
from . import short_code, custom_slug

router = APIRouter()

for module in (short_code, custom_slug):
    router.include_router(module.router)