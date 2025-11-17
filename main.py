from app.config import Base, engine
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.flight import Flight
from app.models.user import User

def create_tables():
    Base.metadata.create_all(bind=engine)
