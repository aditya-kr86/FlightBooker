from pydantic import BaseModel
from datetime import datetime

class FlightResponse(BaseModel):
    id: int
    airline: str
    source: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    base_price: float
    seats_left: int

    class Config:
        orm_mode = True
