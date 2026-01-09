from datetime import datetime, timedelta, timezone
import random
import os
import sys
import time
from itertools import permutations

# Ensure the repository `backend` folder is on sys.path so `import app` works
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import SessionLocal, Base, engine
from app.models.airline import Airline
from app.models.airport import Airport
from app.models.aircraft import Aircraft
from app.models.aircraft_seat_template import AircraftSeatTemplate
from app.models.flight import Flight
from app.models.seat import Seat
from app.models.user import User
from app.auth.password import hash_password

# SQLAlchemy for bulk operations
from sqlalchemy.orm import Session
from sqlalchemy import text


# ============================================================================
# REALISTIC INDIAN AVIATION DATA
# ============================================================================

AIRLINES_DATA = [
    ("IndiGo", "6E"), ("Air India", "AI"), ("SpiceJet", "SG"),
    ("Vistara", "UK"), ("Go First", "G8"), ("AirAsia India", "I5"),
    ("Akasa Air", "QP"), ("Air India Express", "IX"),
]

AIRPORTS_DATA = [
    ("DEL", "Indira Gandhi International Airport", "New Delhi", "India"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India"),
    ("BLR", "Kempegowda International Airport", "Bengaluru", "India"),
    ("MAA", "Chennai International Airport", "Chennai", "India"),
    ("CCU", "Netaji Subhas Chandra Bose International Airport", "Kolkata", "India"),
    ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "India"),
    ("AMD", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad", "India"),
    ("PNQ", "Pune Airport", "Pune", "India"),
    ("GOI", "Goa International Airport", "Goa", "India"),
    ("COK", "Cochin International Airport", "Kochi", "India"),
    ("JAI", "Jaipur International Airport", "Jaipur", "India"),
    ("LKO", "Chaudhary Charan Singh International Airport", "Lucknow", "India"),
    ("GAU", "Lokpriya Gopinath Bordoloi International Airport", "Guwahati", "India"),
    ("IXC", "Chandigarh International Airport", "Chandigarh", "India"),
    ("PAT", "Jay Prakash Narayan International Airport", "Patna", "India"),
    ("VNS", "Lal Bahadur Shastri International Airport", "Varanasi", "India"),
    ("IXB", "Bagdogra Airport", "Siliguri", "India"),
    ("TRV", "Trivandrum International Airport", "Thiruvananthapuram", "India"),
    ("IXR", "Birsa Munda Airport", "Ranchi", "India"),
    ("BBI", "Biju Patnaik International Airport", "Bhubaneswar", "India"),
    ("IDR", "Devi Ahilyabai Holkar Airport", "Indore", "India"),
    ("NAG", "Dr. Babasaheb Ambedkar International Airport", "Nagpur", "India"),
    ("SXR", "Sheikh ul-Alam International Airport", "Srinagar", "India"),
    ("IXJ", "Jammu Airport", "Jammu", "India"),
    ("ATQ", "Sri Guru Ram Dass Jee International Airport", "Amritsar", "India"),
]

AIRCRAFT_DATA = [
    ("Airbus A320neo", 75, 45, 20, 0, 10),
    ("Airbus A321neo", 85, 50, 25, 0, 10),
    ("Airbus A320ceo", 90, 50, 25, 0, 15),
    ("Boeing 737-800", 75, 45, 20, 0, 10),
    ("Boeing 737 MAX 8", 85, 50, 25, 0, 10),
    ("ATR 72-600", 90, 50, 25, 0, 15),
    ("Airbus A350-900", 75, 45, 20, 0, 10),
    ("Boeing 787-8 Dreamliner", 85, 50, 25, 0, 10),
    ("Boeing 777-300ER", 90, 50, 25, 0, 15),
    ("Airbus A330-300", 75, 45, 20, 0, 10),
]

def create_if_not_exists(session, model, lookup: dict, defaults: dict | None = None):
    obj = session.query(model).filter_by(**lookup).first()
    if obj:
        return obj
    params = {**lookup}
    if defaults:
        params.update(defaults)
    obj = model(**params)
    session.add(obj)
    session.flush()
    return obj

def generate_seat_templates_data(aircraft_id: int, aircraft) -> list[dict]:
    templates = []
    current_row = 1
    configs = [
        ("First", getattr(aircraft, 'first_count', 0), 4),
        ("Business", getattr(aircraft, 'business_count', 0), 6),
        ("Premium Economy", getattr(aircraft, 'premium_economy_count', 0), 6),
        ("Economy", getattr(aircraft, 'economy_count', 0), 6)
    ]
    for class_name, count, spr in configs:
        if count <= 0: continue
        rows_needed = (count + spr - 1) // spr
        created = 0
        for row in range(current_row, current_row + rows_needed):
            for seat_pos in range(spr):
                if created < count:
                    seat_letters = {6: 'ABCDEF', 4: 'ABCD', 3: 'ABC'}
                    letter = seat_letters.get(spr, 'ABCDEF')[seat_pos % spr]
                    templates.append({
                        "aircraft_id": aircraft_id,
                        "seat_number": f"{row}{letter}",
                        "seat_class": class_name
                    })
                    created += 1
        current_row += rows_needed
    return templates

def seed():
    start_time = time.time()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("⚡ CLOUD SEEDING: LOCAL -> SUPABASE")
        print("=" * 60)
        
        # 1. Assets (Small data, handled normally)
        airline_objs = {code: create_if_not_exists(db, Airline, {"code": code}, {"name": name}) 
                        for name, code in AIRLINES_DATA}
        airport_objs = {code: create_if_not_exists(db, Airport, {"code": code}, 
                        {"name": name, "city": city, "country": country}) 
                        for code, name, city, country in AIRPORTS_DATA}
        aircraft_objs = [create_if_not_exists(db, Aircraft, {"model": m}, 
                         {"capacity": c, "economy_count": e, "business_count": b, 
                          "premium_economy_count": p, "first_count": f}) 
                         for m, c, e, b, p, f in AIRCRAFT_DATA]
        db.commit()

        # 2. Seat Templates
        existing_tpls = set(r[0] for r in db.query(AircraftSeatTemplate.aircraft_id).distinct().all())
        all_templates = []
        for ac in aircraft_objs:
            if ac.id not in existing_tpls:
                all_templates.extend(generate_seat_templates_data(ac.id, ac))
        if all_templates:
            db.execute(AircraftSeatTemplate.__table__.insert(), all_templates)
            db.commit()

        # 3. Comprehensive Flight Seeding
        print("\n📌 Generating Flights & Seats...")
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        airport_codes = list(airport_objs.keys())
        all_possible_routes = list(permutations(airport_codes, 2))
        
        # Batch settings for Cloud Latency
        FLIGHT_BATCH_SIZE = 1000 
        flight_rows = []
        seat_rows = []
        total_f, total_s = 0, 0

        for day_offset in range(30):
            day = today + timedelta(days=day_offset)
            # Sample subset to avoid crashing local memory or exceeding Supabase free tier limits
            sampled_routes = random.sample(all_possible_routes, min(len(all_possible_routes), 120))
            
            for origin, dest in sampled_routes:
                airline = random.choice(list(airline_objs.values()))
                aircraft = random.choice(aircraft_objs)
                flight_no = f"{airline.code}{random.randint(100, 9999)}"
                dep_time = day + timedelta(hours=random.randint(5, 22), minutes=random.choice([0, 30]))

                flight_rows.append({
                    "airline_id": airline.id, 
                    "aircraft_id": aircraft.id,
                    "flight_number": flight_no, 
                    "departure_airport_id": airport_objs[origin].id,
                    "arrival_airport_id": airport_objs[dest].id, 
                    "departure_time": dep_time,
                    "arrival_time": dep_time + timedelta(minutes=random.randint(60, 210)),
                    "base_price": float(random.randint(3000, 12000)),
                    "demand_level": random.choice(["low", "medium", "high"]),
                    "status": "Scheduled", # Corrected to match Enum Case (Scheduled vs scheduled)
                    "delay_minutes": 0 # Added to match table requirements
                })

                # Queue seats for this flight
                for r in range(1, 11): 
                    for s in 'ABCDEF':
                        seat_rows.append({
                            "flight_number_ref": flight_no,
                            "seat_number": f"{r}{s}",
                            "seat_class": "Economy" if r > 2 else "Business",
                            "is_available": random.random() > 0.15,
                        })

            # Check if we should push to Cloud
            if len(flight_rows) >= FLIGHT_BATCH_SIZE:
                print(f"   ☁️  Uploading batch to Supabase (Day +{day_offset})...")
                db.execute(Flight.__table__.insert(), flight_rows)
                db.commit()
                
                # Fetch IDs to link seats (This is the slow part over cloud)
                # Filter by the batch's flight numbers to reduce data transfer
                f_nums = [f["flight_number"] for f in flight_rows]
                new_flights = db.query(Flight.id, Flight.flight_number).filter(Flight.flight_number.in_(f_nums)).all()
                id_map = {f.flight_number: f.id for f in new_flights}
                
                final_seats = []
                for s in seat_rows:
                    fid = id_map.get(s.pop("flight_number_ref"))
                    if fid:
                        s["flight_id"] = fid
                        final_seats.append(s)
                
                if final_seats:
                    # Seat batches are huge, chunk them again
                    for i in range(0, len(final_seats), 5000):
                        db.execute(Seat.__table__.insert(), final_seats[i:i+5000])
                    db.commit()
                
                total_f += len(flight_rows)
                total_s += len(final_seats)
                flight_rows, seat_rows = [], []

        # Final Cleanup commit
        if flight_rows:
            db.execute(Flight.__table__.insert(), flight_rows)
            db.commit()

        print(f"\n✅ Assets and Flights ready. Creating Users...")
        create_admin_user(db)
        create_airline_staff_users(db, airline_objs)
        create_airport_authority_users(db, airport_objs)
        
        elapsed = time.time() - start_time
        print(f"\n✨ SEEDING COMPLETE in {elapsed:.2f}s")
        print(f"📊 Flights: {total_f} | Seats: {total_s}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Cloud Seeding Error: {e}")
        raise
    finally:
        db.close()

def create_admin_user(db):
    from app.models.user import User
    admin_email = "admin@flightbooker.com"
    if not db.query(User).filter_by(email=admin_email).first():
        admin = User(email=admin_email, password_hash=hash_password("Admin@123"),
                     first_name="Admin", last_name="User", role="admin", is_active=True, is_verified=True)
        db.add(admin)
        db.commit()

def create_airline_staff_users(db, airlines):
    from app.models.user import User
    for code, airline in airlines.items():
        email = f"staff@{code.lower()}.flightbooker.com"
        if not db.query(User).filter_by(email=email).first():
            staff = User(email=email, password_hash=hash_password(f"{code}Staff@123"),
                         first_name=airline.name, last_name="Staff", role="airline_staff",
                         airline_id=airline.id, is_active=True, is_verified=True)
            db.add(staff)
    db.commit()

def create_airport_authority_users(db, airports):
    from app.models.user import User
    for code, airport in airports.items():
        email = f"authority@{code.lower()}.airport.in"
        if not db.query(User).filter_by(email=email).first():
            auth = User(email=email, password_hash=hash_password(f"{code}Auth@123"),
                        first_name=airport.city, last_name="Authority", role="airport_authority",
                        airport_id=airport.id, is_active=True, is_verified=True)
            db.add(auth)
    db.commit()

if __name__ == "__main__":
    seed()