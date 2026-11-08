from fastapi import FastAPI
from app.routes.links import router as link_router
from app.routes.auth import router as auth_router
from app.routes.redirects import router as redirect_router

app = FastAPI()
app.include_router(link_router, tags = ["Links"])
app.include_router(auth_router, tags = ["Authentication"])
app.include_router(redirect_router, tags = ["Redircetion's"])

@app.get("/")
def root():
    return {"status": "ok"}
