from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)

    role = Column(Enum("customer", "airline_staff", "airport_authority", "admin", name="user_roles"), default="customer")

    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=True)
    airport_id = Column(Integer, ForeignKey("airports.id"), nullable=True)

    bookings = relationship("Booking", back_populates="user")

    airline = relationship("Airline", back_populates="staff", foreign_keys=[airline_id])
    airport = relationship("Airport", back_populates="staff", foreign_keys=[airport_id])
