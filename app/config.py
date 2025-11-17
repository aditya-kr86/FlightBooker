from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 👉 SQLite development DB (Infosys Module-1 Ke Liye Perfect)
DATABASE_URL = "sqlite:///./database.db"

# 👉 For SQLite: check_same_thread = False is required
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 👉 DB session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 👉 Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI (if needed later)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
