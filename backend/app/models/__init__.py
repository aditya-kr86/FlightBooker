"""Models package - import submodules so they register with SQLAlchemy.

This file makes it easy to ensure all model classes are imported when
you import `app.models`.
"""
from . import user
from . import airline
from . import airport
from . import aircraft
from . import flight
from . import seat
from . import booking
from . import ticket
from . import payment

__all__ = [
    "user",
    "airline",
    "airport",
    "aircraft",
    "flight",
    "seat",
    "booking",
    "ticket",
    "payment",
]
