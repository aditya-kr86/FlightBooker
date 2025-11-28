from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.config import get_db
from app.schemas.flight_schema import FlightResponse
from app.services.flight_service import search_flights

router = APIRouter()


@router.get("/", response_model=list[FlightResponse])
def list_flights_api(
    limit: int | None = Query(None, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Return all flights (optionally limited)."""
    flights = search_flights(db, limit=limit)
    return flights


@router.get("/search", response_model=list[FlightResponse])
def search_flights_api(
    origin: str | None = Query(None, min_length=3, max_length=10),
    destination: str | None = Query(None, min_length=3, max_length=10),
    date: str | None = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    sort_by: str | None = Query(None, regex="^(price|duration)$"),
    limit: int | None = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    # Normalize codes
    if origin:
        origin = origin.upper()
    if destination:
        destination = destination.upper()

    # Validate date format if provided
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")

    flights = search_flights(db, origin=origin, destination=destination, date=date, sort_by=sort_by, limit=limit)

    if not flights:
        raise HTTPException(status_code=404, detail="No flights found")

    return flights
