from fastapi import FastAPI
from .routes import urls_route

app = FastAPI()
app.include_router(urls_route.router)

@app.get("/")
def root():
    return {"status": "ok"}
