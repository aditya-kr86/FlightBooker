from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.config import get_db
from app.schemas.payment_schema import PaymentCreate, PaymentResponse, PaymentUpdate
from app.schemas.booking_schema import BookingResponse, TicketInfoSimplified
from app.models.booking import Booking
from app.services.flight_service import create_payment, get_payment_by_transaction

router = APIRouter()


def _format_flight_seat(seat_class: str, seat_number: str) -> str:
    """Format flight seat as 'SEAT_CLASS - SEAT_NUMBER' (e.g., 'EC - 32')."""
    seat_class_abbr = {
        "ECONOMY": "EC",
        "ECONOMY_FLEX": "ECF",
        "BUSINESS": "BUS",
        "FIRST": "FC",
    }.get(seat_class.upper(), seat_class[:2].upper())
    
    return f"{seat_class_abbr} - {seat_number}"


def _ticket_to_simplified(ticket) -> TicketInfoSimplified:
    """Convert Ticket model to simplified response format."""
    return TicketInfoSimplified(
        flight_seat=_format_flight_seat(ticket.seat_class or "ECONOMY", ticket.seat_number or ""),
        passenger_name=ticket.passenger_name,
        passenger_age=ticket.passenger_age,
        passenger_gender=ticket.passenger_gender,
        airline_name=ticket.airline_name,
        flight_number=ticket.flight_number,
        route=ticket.route,
        departure_airport=ticket.departure_airport,
        arrival_airport=ticket.arrival_airport,
        departure_city=ticket.departure_city,
        arrival_city=ticket.arrival_city,
        departure_time=ticket.departure_time,
        arrival_time=ticket.arrival_time,
        seat_number=ticket.seat_number or "",
        seat_class=ticket.seat_class or "ECONOMY",
        payment_required=ticket.payment_required,
        currency=ticket.currency,
        ticket_number=ticket.ticket_number,
        issued_at=ticket.issued_at,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_payment_api(payload: PaymentCreate, db: Session = Depends(get_db)):
    # very small validation
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    # use booking_reference only (booking_id removed from API)
    identifier = payload.booking_reference
    try:
        tx = create_payment(db, booking_reference=identifier, amount=payload.amount, method=payload.method)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    # If payment failed, reject with 400 error
    if tx.status != "Success":
        booking_for_calc = db.query(Booking).filter(Booking.id == tx.booking_id).first()
        required_amount = sum(t.payment_required for t in booking_for_calc.tickets) if booking_for_calc else 0
        raise HTTPException(
            status_code=400,
            detail=f"payment failed: insufficient amount. Required: {required_amount}, Paid: {payload.amount}"
        )

    # load updated booking (create_payment issues tickets and PNR on success)
    booking = db.query(Booking).filter(Booking.id == tx.booking_id).first()
    if not booking:
        raise HTTPException(status_code=500, detail="payment recorded but booking not found")

    # Compute total_fare from tickets
    total_fare = sum(t.payment_required for t in booking.tickets)

    # Convert tickets to simplified format
    tickets = [_ticket_to_simplified(t) for t in booking.tickets]

    return BookingResponse(
        pnr=booking.pnr,
        booking_reference=booking.booking_reference,
        status=booking.status,
        created_at=booking.created_at,
        total_fare=total_fare,
        tickets=tickets,
        transaction_id=tx.transaction_id,
        paid_amount=tx.amount,
    )


@router.get("/{transaction_id}", response_model=PaymentResponse)
def get_payment_api(transaction_id: str, db: Session = Depends(get_db)):
    tx = get_payment_by_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    return tx


@router.patch("/{transaction_id}", response_model=PaymentResponse)
def patch_payment_api(transaction_id: str, payload: PaymentUpdate = Body(...), db: Session = Depends(get_db)):
    tx = get_payment_by_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    data = payload.dict(exclude_unset=True)
    if "status" in data and data.get("status"):
        tx.status = data.get("status")
    db.commit()
    db.refresh(tx)
    return tx
