from fastapi import FastAPI
from app.routes import urls_route
from app.routes.auth import router as auth_router

app = FastAPI()
app.include_router(urls_route.router)

# Auth
app.include_router(auth_router)

@app.get("/")
def root():
    return {"status": "ok"}
