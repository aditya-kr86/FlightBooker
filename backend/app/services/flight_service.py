from sqlalchemy.orm import Session
from app.models.flight import Flight
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.flight import Flight
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.seat import Seat


def search_flights(db: Session, origin: str | None = None, destination: str | None = None, date: str | None = None, sort_by: str | None = None, limit: int | None = None):
    """Search flights with optional filters. Returns list of dicts matching `FlightResponse` schema.

    origin/destination: airport codes (e.g., 'DEL')
    date: YYYY-MM-DD or None
    sort_by: 'price' or 'duration' or None
    """
    query = db.query(Flight).join(Airline)

    if origin:
        query = query.join(Airport, Flight.departure_airport).filter(Airport.code == origin)

    if destination:
        query = query.join(Airport, Flight.arrival_airport).filter(Airport.code == destination)

    if date:
        # match date with SQLite's strftime
        query = query.filter(func.strftime('%Y-%m-%d', Flight.departure_time) == date)

    # Apply sorting
    if sort_by == "price":
        query = query.order_by(Flight.base_price.asc())
    elif sort_by == "duration":
        query = query.order_by((Flight.arrival_time - Flight.departure_time).asc())

    if limit:
        query = query.limit(limit)

    flights = query.all()

    formatted = []
    for flight in flights:
        airline = db.query(Airline).filter(Airline.id == flight.airline_id).first()
        dep = db.query(Airport).filter(Airport.id == flight.departure_airport_id).first()
        arr = db.query(Airport).filter(Airport.id == flight.arrival_airport_id).first()

        # compute seats left by counting available seats
        seats_left = db.query(func.count(Seat.id)).filter(Seat.flight_id == flight.id, Seat.is_available == True).scalar() or 0

        formatted.append({
            "id": flight.id,
            "airline": airline.name if airline else None,
            "source": dep.code if dep else None,
            "destination": arr.code if arr else None,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "base_price": flight.base_price,
            "seats_left": seats_left,
        })

    return formatted
