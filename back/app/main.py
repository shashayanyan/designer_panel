from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, master_data, engine as engine_router
from .database import engine, Base

# We will create tables via Alembic, but we can also ensure they exist here for development
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Designer Panel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all origins
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
