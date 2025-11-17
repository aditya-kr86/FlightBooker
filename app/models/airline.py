from sqlalchemy import Column, Integer, String
from app.config import Base

class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(5), unique=True, nullable=False)    # e.g., AI, IND
    name = Column(String(100), nullable=False)
