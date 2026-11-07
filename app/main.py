from fastapi import FastAPI
from app.routes.links import router as link_router
from app.routes.auth import router as auth_router
from app.routes.redirects.short_code import router as links_router

app = FastAPI()
app.include_router(link_router)
app.include_router(auth_router)
app.include_router(links_router)

@app.get("/")
def root():
    return {"status": "ok"}
