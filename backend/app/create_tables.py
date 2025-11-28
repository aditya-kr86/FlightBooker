from .config import Base, engine

# Import all model modules so SQLAlchemy registers them before create_all()
from .models import user, airline, airport, aircraft, flight, seat, booking, ticket, payment

def create_all_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    create_all_tables()
