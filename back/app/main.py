import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, master_data, engine as engine_router
from .database import engine, Base

app = FastAPI(title="Designer Panel API")

# Load CORS origins from environment
cors_origins_str = os.getenv("CORS_ORIGINS", '["*"]')
try:
    origins = json.loads(cors_origins_str)
except Exception:
    origins = ["*"]

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(master_data.router)
app.include_router(engine_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to Designer Panel API"}
