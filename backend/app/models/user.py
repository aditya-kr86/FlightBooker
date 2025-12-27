from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    
    # Basic info
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    mobile = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    password_hash = Column(String(200), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Role-based access
    role = Column(
        Enum("customer", "airline_staff", "airport_authority", "admin", name="user_roles"),
        default="customer"
    )

    # Foreign keys for staff associations
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=True)
    airport_id = Column(Integer, ForeignKey("airports.id"), nullable=True)

    # Relationships
    bookings = relationship("Booking", back_populates="user")
    airline = relationship("Airline", back_populates="staff", foreign_keys=[airline_id])
    airport = relationship("Airport", back_populates="staff", foreign_keys=[airport_id])

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

