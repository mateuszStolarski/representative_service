from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import model, observation
from settings.base import AppSettings
from utils.mongo import seed

app = FastAPI()

if AppSettings().use_seed:
    seed()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(observation.router)
app.include_router(model.router)
