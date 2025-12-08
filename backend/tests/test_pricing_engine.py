from datetime import datetime, timedelta, timezone
import pytest

from app.services.pricing_engine import compute_dynamic_price, DemandLevel


def test_compute_dynamic_price_basic():
    now = datetime.now(timezone.utc)
    dep = now + timedelta(days=10)
    price = compute_dynamic_price(1000.0, dep, total_seats=100, booked_seats=10, demand_level=DemandLevel.MEDIUM, tier="ECONOMY", now=now)
    assert price > 0


def test_price_increases_when_near_full():
    now = datetime.now(timezone.utc)
    dep = now + timedelta(days=5)
    price_more_available = compute_dynamic_price(1000.0, dep, total_seats=100, booked_seats=10, demand_level=DemandLevel.MEDIUM, tier="ECONOMY", now=now)
    price_near_full = compute_dynamic_price(1000.0, dep, total_seats=100, booked_seats=95, demand_level=DemandLevel.MEDIUM, tier="ECONOMY", now=now)
    assert price_near_full >= price_more_available
