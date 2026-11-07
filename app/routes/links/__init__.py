from fastapi import APIRouter 
from . import create, detail, list, delete

router = APIRouter()

for module in (create, list, detail, delete):
    router.include_router(module.router)