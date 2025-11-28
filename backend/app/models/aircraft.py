from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config import Base


class Aircraft(Base):
    __tablename__ = "aircrafts"

    id = Column(Integer, primary_key=True)
    model = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)

    flights = relationship("Flight", back_populates="aircraft")
