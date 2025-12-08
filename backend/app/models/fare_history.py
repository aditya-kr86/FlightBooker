from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base


class FareHistory(Base):
    __tablename__ = "fare_history"

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tier = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    remaining_seats = Column(Integer)
    demand_level = Column(String(20))

    flight = relationship("Flight")
