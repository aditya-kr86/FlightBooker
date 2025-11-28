from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    pnr = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    status = Column(Enum("Pending", "Confirmed", "Cancelled", name="booking_status"), default="Pending")

    user = relationship("User", back_populates="bookings")
    tickets = relationship("Ticket", back_populates="booking")
    payment = relationship("Payment", back_populates="booking", uselist=False)
