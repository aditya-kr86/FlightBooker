from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))

    amount = Column(Float, nullable=False)
    method = Column(Enum("Card", "UPI", "NetBanking", "Wallet", name="payment_method"))
    status = Column(Enum("Initiated", "Success", "Failed", name="payment_status"), default="Initiated")

    transaction_id = Column(String(100), unique=True)
    paid_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")
