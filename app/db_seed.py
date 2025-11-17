from datetime import datetime, timedelta
from app.config import SessionLocal
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.flight import Flight

def seed_data():
    db = SessionLocal()

    # Airports
    airports = [
        Airport(code="DEL", name="Indira Gandhi Intl", city="Delhi", country="India"),
        Airport(code="BOM", name="Chhatrapati Shivaji Intl", city="Mumbai", country="India"),
        Airport(code="BLR", name="Kempegowda Intl", city="Bangalore", country="India")
    ]

    # Airlines
    airlines = [
        Airline(code="AI", name="Air India"),
        Airline(code="IND", name="IndiGo"),
        Airline(code="SG", name="SpiceJet")
    ]

    db.add_all(airports)
    db.add_all(airlines)
    db.commit()

    # Flights
    flights = []

    for i in range(3):
        flights.append(
            Flight(
                airline_id=1,
                source_airport=1,
                destination_airport=2,
                departure_time=datetime.now() + timedelta(days=i+1),
                arrival_time=datetime.now() + timedelta(days=i+1, hours=2),
                base_price=3500 + i*500,
                seats_total=120,
                seats_left=120,
            )
        )

    db.add_all(flights)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()
