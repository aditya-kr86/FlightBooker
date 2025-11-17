from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    source_airport = Column(Integer, ForeignKey("airports.id"), nullable=False)
    destination_airport = Column(Integer, ForeignKey("airports.id"), nullable=False)

    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    
    base_price = Column(Float, nullable=False)
    
    seats_total = Column(Integer, nullable=False)
    seats_left = Column(Integer, nullable=False)

    airline = relationship("Airline")
    source = relationship("Airport", foreign_keys=[source_airport])
    destination = relationship("Airport", foreign_keys=[destination_airport])
