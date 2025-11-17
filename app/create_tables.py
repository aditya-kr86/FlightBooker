from .config import Base, engine
from .models.airport import Airport
from .models.airline import Airline
from .models.flight import Flight

def create_all_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    create_all_tables()
