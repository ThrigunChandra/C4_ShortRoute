from fastapi import FastAPI
from app.routes.links import router as link_router
from app.routes.auth import router as auth_router

app = FastAPI()
app.include_router(link_router)

# Auth
app.include_router(auth_router)

@app.get("/")
def root():
    return {"status": "ok"}
