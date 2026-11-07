from fastapi import APIRouter 
from . import create, detail, list 

router = APIRouter()

# for module in (create):
#     router.include_router(module.router)

router.include_router(create.router)