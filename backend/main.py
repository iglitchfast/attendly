from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # noqa: F401 — ensures models are registered on Base before create_all

from routers import auth_routes, subjects, timetable, working_days, predictions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(subjects.router)
app.include_router(timetable.router)
app.include_router(working_days.router)
app.include_router(predictions.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "attendly"}