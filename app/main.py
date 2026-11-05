from fastapi import FastAPI
from app.routes import urls_route
from app.routes.auth.register import router as register_router
from app.routes.auth.logout import router as logout_router
from app.routes.auth.login import router as login_router
from app.routes.auth.me import router as me_router

app = FastAPI()
app.include_router(urls_route.router)

# Auth 
app.include_router(register_router)
app.include_router(logout_router)
app.include_router(me_router)
app.include_router(login_router)


@app.get("/")
def root():
    return {"status": "ok"}
