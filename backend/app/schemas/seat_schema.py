from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class SeatCreate(BaseModel):
    flight_id: int
    seat_number: str
    row_number: Optional[int] = None
    seat_letter: Optional[str] = None
    seat_class: Optional[str] = "Economy"
    seat_position: Optional[str] = "middle"  # window, middle, aisle
    is_available: Optional[bool] = True
    surcharge: Optional[float] = 0.0


class SeatUpdate(BaseModel):
    seat_number: Optional[str] = None
    seat_class: Optional[str] = None
    seat_position: Optional[str] = None
    is_available: Optional[bool] = None
    surcharge: Optional[float] = None


class SeatResponse(BaseModel):
    id: int
    flight_id: int
    seat_number: str
    row_number: Optional[int] = None
    seat_letter: Optional[str] = None
    seat_class: Optional[str]
    seat_position: Optional[str] = "middle"
    is_available: bool
    surcharge: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)


class SeatBulkCreate(BaseModel):
    flight_number: str
    seat_class: Optional[str] = "Economy"
    seat_numbers: Optional[list[str]] = None
    count: Optional[int] = None


class SeatBulkUpdateItem(BaseModel):
    id: int
    seat_number: Optional[str] = None
    seat_class: Optional[str] = None
    is_available: Optional[bool] = None


class SeatBulkUpdate(BaseModel):
    seats: list[SeatBulkUpdateItem]


class SeatBulkDelete(BaseModel):
    seat_ids: Optional[list[int]] = None
    flight_number: Optional[str] = None
    seat_class: Optional[str] = None


class SeatAvailabilityItem(BaseModel):
    seat_class: str
    available_count: int
    booked_count: int
    available_seats: list[SeatResponse]
    booked_seats: list[SeatResponse]


class SeatAvailabilityResponse(BaseModel):
    flight_id: int
    flight_number: str
    classes: list[SeatAvailabilityItem]

    model_config = ConfigDict(from_attributes=True)


class SeatOverviewResponse(BaseModel):
    model: Optional[str] = None
    flight_no: str
    total_capacity: int
    available_capacity: int
    economy_count: int
    available_economy_count: int
    premium_economy_count: int
    available_premium_economy_count: int
    business_count: int
    available_business_count: int
    first_count: int
    available_first_count: int

    model_config = ConfigDict(from_attributes=True)


class SeatClassBatch(BaseModel):
    seat_class: Optional[str] = "Economy"
    seat_numbers: Optional[list[str]] = None
    count: Optional[int] = None


class SeatBulkByFlightCreate(BaseModel):
    airline_code: str
    flight_number: str
    classes: list[SeatClassBatch]


# ===== Seat Map Models for Visual Seat Selection =====

class SeatMapSeat(BaseModel):
    """Individual seat in the seat map."""
    id: int
    seat_number: str
    row_number: int
    seat_letter: str
    seat_class: str
    seat_position: str  # window, middle, aisle
    is_available: bool
    surcharge: float
    
    model_config = ConfigDict(from_attributes=True)


class SeatMapRow(BaseModel):
    """A row of seats in the aircraft."""
    row_number: int
    seats: List[SeatMapSeat]


class SeatMapConfig(BaseModel):
    """Aircraft seat map configuration."""
    seats_per_row: int  # e.g., 6 for 3-3 configuration
    aisle_after: List[int]  # positions after which there's an aisle (e.g., [3] for 3-3)
    seat_letters: List[str]  # e.g., ["A", "B", "C", "D", "E", "F"]


class SeatMapResponse(BaseModel):
    """Complete seat map for a flight."""
    flight_id: int
    flight_number: str
    aircraft_model: Optional[str] = None
    seat_class_filter: Optional[str] = None  # If filtered by class
    config: SeatMapConfig
    rows: List[SeatMapRow]
    surcharge_info: dict  # {"window": 0.05, "aisle": 0.03, "middle": 0.0}
    base_price: float  # Current dynamic price for reference
    
    model_config = ConfigDict(from_attributes=True)
