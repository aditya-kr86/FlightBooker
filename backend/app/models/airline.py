from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config import Base


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(5), unique=True, nullable=False)

    flights = relationship("Flight", back_populates="airline")
    staff = relationship("User", back_populates="airline")
