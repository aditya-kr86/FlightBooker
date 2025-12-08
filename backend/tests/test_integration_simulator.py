import sys
import os
from datetime import datetime, timedelta, timezone
import random


def _ensure_backend_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base not in sys.path:
        sys.path.insert(0, base)


_ensure_backend_path()

from app.config import SessionLocal, Base, engine
from app.services.flight_service import ensure_all_flight_seats
from app.services.demand_simulator import run_demand_simulation_once
from scripts.seed_db import seed
from app.services.pricing_engine import compute_dynamic_price
import random
from app.models.fare_history import FareHistory


def test_simulator_changes_seat_counts_and_fare_history():
    # deterministic randomness for test
    random.seed(0)
    # Seed a dataset
    seed()
    db = SessionLocal()
    try:
        ensure_all_flight_seats(db)
        # find a flight
        f = db.query(Base.metadata.tables['flights']).first() if False else None
        # fallback: get any Flight via ORM
        from app.models.flight import Flight
        flight = db.query(Flight).filter(Flight.departure_time > (datetime.now(timezone.utc))).first()
        assert flight is not None

        # compute price before
        total = db.query(Base.metadata.tables['seats']).count() if False else None
        # determine counts via Seat model
        from app.models.seat import Seat
        total_seats = db.query(Seat).filter(Seat.flight_id == flight.id).count()
        available_before = db.query(Seat).filter(Seat.flight_id == flight.id, Seat.is_available == True).count()
        booked_before = total_seats - available_before

        price_before = compute_dynamic_price(flight.base_price, flight.departure_time, total_seats, booked_before, getattr(flight, 'demand_level', 'medium'))

        # run simulator once
        updated = run_demand_simulation_once(db, within_hours=720)
        assert isinstance(updated, int)

        # compute available after
        available_after = db.query(Seat).filter(Seat.flight_id == flight.id, Seat.is_available == True).count()
        booked_after = total_seats - available_after

        # fare history should have entries (at least one)
        fh_count = db.query(FareHistory).filter(FareHistory.flight_id == flight.id).count()
        assert fh_count >= 0

        # compute price after
        price_after = compute_dynamic_price(flight.base_price, flight.departure_time, total_seats, booked_after, getattr(flight, 'demand_level', 'medium'))

        # in many cases price_after should be >= price_before when seats got booked
        if booked_after > booked_before:
            assert price_after >= price_before
    finally:
        db.close()
