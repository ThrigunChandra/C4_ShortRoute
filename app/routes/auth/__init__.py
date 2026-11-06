from fastapi import APIRouter 
from . import login, logout, register, me 

router = APIRouter()

for module in (login, logout, register, me):
    router.include_router(module.router)