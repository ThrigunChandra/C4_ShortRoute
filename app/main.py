from fastapi import FastAPI
from app.routes import urls_route
from app.routes.auth.register import router as register_router

app = FastAPI()
app.include_router(urls_route.router)
app.include_router(register_router)

@app.get("/")
def root():
    return {"status": "ok"}
