from datetime import datetime, timedelta
from app.config import SessionLocal
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.aircraft import Aircraft
from app.models.flight import Flight
from app.models.seat import Seat


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

    # Aircraft
    aircrafts = [
        Aircraft(model="A320", capacity=180),
        Aircraft(model="B737", capacity=160)
    ]

    db.add_all(airports + airlines + aircrafts)
    db.commit()

    # Create sample flights and seats
    flights = []
    seats = []

    for i in range(3):
        f = Flight(
            airline_id=1,
            aircraft_id=1,
            flight_number=f"AI{100+i}",
            departure_airport_id=1,
            arrival_airport_id=2,
            departure_time=datetime.now() + timedelta(days=i+1, hours=8),
            arrival_time=datetime.now() + timedelta(days=i+1, hours=10),
            base_price=3500 + i*500,
            status="Scheduled",
        )
        db.add(f)
        db.flush()  # populate f.id

        # Add a few seats for the flight
        for s in range(1, 21):
            seats.append(Seat(flight_id=f.id, seat_number=str(s), seat_class="Economy", is_available=True))

    db.add_all(seats)
    db.commit()
    db.close()
    print("✅ Sample data seeded successfully.")


if __name__ == "__main__":
    seed_data()
