import random
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.flight import Flight
from app.models.seat import Seat


def simulate_demand_for_flight(db: Session, flight: Flight) -> None:
    """Simulate demand change for a single flight and update booked seats/demand_level.

    This function mutates the DB object and commits changes.
    """
    now = datetime.now(timezone.utc)
    # Make naive to match database datetime (which is naive)
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    hours = (flight.departure_time - now).total_seconds() / 3600

    # base rate according to demand_level
    base_rate_map = {
        "low": 1,
        "medium": 3,
        "high": 6,
        "extreme": 10,
    }

    base_rate = base_rate_map.get((flight.demand_level or "medium").lower(), 3)

    # increase booking rate as departure approaches
    if hours < 48:
        base_rate *= 2
    elif hours < 168:
        base_rate *= 1.5

    new_bookings = max(0, int(random.gauss(mu=base_rate, sigma=max(1, base_rate * 0.3))))

    # compute totals from Seat rows
    total_seats = db.query(func.count(Seat.id)).filter(Seat.flight_id == flight.id).scalar() or 0
    available = db.query(func.count(Seat.id)).filter(Seat.flight_id == flight.id, Seat.is_available == True).scalar() or 0
    booked = total_seats - available

    # attempt to mark some available seats as booked (update rows)
    to_book = min(new_bookings, available)
    if to_book > 0:
        seats = db.query(Seat).filter(Seat.flight_id == flight.id, Seat.is_available == True).order_by(Seat.id.asc()).limit(to_book).all()
        for s in seats:
            s.is_available = False

    # optionally escalate demand level if near full
    available_after = available - to_book
    remaining_pct = (total_seats - (booked + to_book)) / total_seats if total_seats > 0 else 0
    if remaining_pct < 0.2 and (flight.demand_level or "").lower() != "extreme":
        flight.demand_level = "high"

    db.commit()


def run_demand_simulation_once(db: Session, within_hours: int = 720) -> int:
    """Run one iteration of demand simulation for upcoming flights within `within_hours`.

    Returns number of flights updated.
    """
    now = datetime.now(timezone.utc)
    # Make naive to match database datetime (which is naive)
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    cutoff = now
    from datetime import timedelta

    cutoff = now + timedelta(hours=within_hours)
    flights: List[Flight] = db.query(Flight).filter(Flight.departure_time >= now, Flight.departure_time <= cutoff).all()
    updated = 0
    for f in flights:
        simulate_demand_for_flight(db, f)
        updated += 1

    return updated
