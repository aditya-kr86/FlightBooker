from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, unquote

# Use SQLite for local development by default (no extra DB driver needed).
# If you want to use MySQL in production, replace this with a MySQL URL
# like: "mysql+pymysql://user:pass@host:3306/dbname" and add `PyMySQL`
# to `requirements.txt`.
DATABASE_URL = "sqlite:///./database.db"

def ensure_database_exists(database_url: str) -> None:
    """Create the database if it does not exist (only for server DBs, skips sqlite).

    This helper is convenient for development so you don't have to manually
    create the DB from the console every time. It uses `pymysql` to connect
    to the server (without selecting a database) and runs CREATE DATABASE.
    """
    parsed = urlparse(database_url)
    # skip for sqlite or URLs without a path/database
    if parsed.scheme.startswith("sqlite"):
        return

    db_name = parsed.path.lstrip('/')
    if not db_name:
        return

    user = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    host = parsed.hostname or 'localhost'
    port = parsed.port or 3306

    try:
        import pymysql

        conn = pymysql.connect(host=host, user=user, password=password, port=port, charset='utf8mb4')
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
        conn.close()
    except Exception as exc:
        # For development convenience we raise a clearer error message.
        raise RuntimeError(f"Failed to ensure database '{db_name}' exists: {exc}") from exc


# Ensure the database exists before SQLAlchemy tries to connect.
ensure_database_exists(DATABASE_URL)

# Create engine: only pass `check_same_thread` for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# DB session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI (if needed later)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
