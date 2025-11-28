from app.config import Base, engine
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.flight import Flight
from app.models.user import User

from fastapi import FastAPI
from app.routes.flight_routes import router as flight_router

app = FastAPI(title="AkashaYatra - Flight Booking System")

app.include_router(flight_router, prefix="/flights", tags=["Flight Search"])

