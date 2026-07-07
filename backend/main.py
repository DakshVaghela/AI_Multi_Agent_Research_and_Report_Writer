from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.auth import router as auth_router
from backend.api.routes import router as reports_router
from backend.config.settings import settings

app = FastAPI(title=settings.APP_NAME)

# Dev-friendly default: allow any origin so a locally-run frontend (Vite/CRA/etc.)
# can call the API regardless of port. Tighten this before deploying publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(reports_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
