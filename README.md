# **GaganYatra — Flight Booking Simulator with Dynamic Pricing**

A modern Flight Booking & Pricing Simulation system built using **FastAPI**, designed to replicate real-world airline search, pricing algorithms, and booking workflows.

---

## **Project Overview**

GaganYatra simulates core airline operations with:

* **Advanced Flight Search**
* **Dynamic Pricing Engine** (seats, time, demand, fares)
* **Booking Pipeline & PNR Generation**
* **Role-Based Access** (Customer, Airline Staff, Airport Authority)
* **Frontend UI (Jinja2 Templates)**
* **PDF Receipt Generator**

Originally built for the **Infosys Springboard Internship**, the architecture mirrors production-grade backend patterns.

---

## **Tech Stack**

### **Backend**

* FastAPI (Async)
* SQLAlchemy (ORM)
* SQLite / PostgreSQL
* Pydantic v2
* Jinja2 Templates

### **Utilities**

* AsyncIO (background demand simulation)
* ReportLab / WeasyPrint (PDF generation)
* Uvicorn
* Python Dotenv

---

## **Updated ER Diagram (Latest)**
![ER Diagram](ER%20Diagram.png)`

---

## **Project Architecture**

```
GaganYatra/
│
├── backend
│   ├── app/
│   │   ├── models/                 # ORM Models
│   │   ├── routes/                 # FastAPI Routers (module-wise)
│   │   ├── schemas/                # Pydantic Models
│   │   ├── services/               # Business Logic
│   │   │   ├── flight_service.py   # Search + filters
│   │   │   ├── pricing_engine.py   # Dynamic pricing engine
│   │   │   ├── booking_service.py  # Booking + concurrency
│   │   │   └── demand_simulator.py # Background demand updater
│   │   ├── utils/                  # Helpers (PNR, PDF)
│   │   └── config.py               # DB config (SQLite → PostgreSQL)
│   ├── main.py                     # App entry
│   ├── database.db
│   ├── requirements.txt
│   └── README.md
│
├── frontend
│   └── templates/
│
├── ER Diagram.png
├── LICENSE
├── PROJECT_ARCHITECTURE.mmd
└── README.md
```

---

## **Core Features**

### **1. Flight Search & Filters**

* Origin → Destination → Date
* Sorting by fare, departure time, duration
* Real airline/airport dataset simulation

### **2. Dynamic Pricing Engine** 

Pricing adjusts in real-time based on:

* **Remaining seats %**: 4 inventory tiers (0.9× to 1.25× multiplier)
* **Time to departure**: 4 time windows (1.0× to 1.30× multiplier)
* **Demand level**: Simulated demand states (low/medium/high/extreme)
* **Fare tiers**: ECONOMY (1.0×), ECONOMY_FLEX (1.2×), BUSINESS (1.8×), FIRST (2.5×)

Features:
- Live recalculation during search & booking
- Background demand simulator with AsyncIO + Celery support
- Fare history persistence for audit trails
- 60-second cache for performance optimization

### **3. Booking Workflow** 

* Multi-step booking process (booking → payment → confirmation)
* Passenger details collection with validation
* Dynamic fare computation (no manual price override)
* Seat locking with database-level concurrency control (`with_for_update()`)
* Payment validation (insufficient amount rejection)
* Auto PNR + ticket generation on successful payment
* Booking history retrieval & cancellation support
* Multiple payment attempt handling

**Status**: ~85% complete, undergoing stress testing

### **4. Frontend UI**

Planned features:
* Search page with advanced filters
* Real-time dynamic pricing results display
* Multi-step booking page
* Confirmation page with PNR display
* **PDF / JSON receipt download**

**Status**: Pending (Milestone 4)

---

## **Setup Instructions**

### **1. Clone Repo**

```bash
git clone https://github.com/aditya-kr86/GaganYatra.git
cd GaganYatra/backend
```

### **2. Virtual Environment**

```bash
python -m venv .venv
source .venv/bin/activate       # mac/Linux
venv\Scripts\activate          # Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run App**

```bash
uvicorn main:app --reload
```

### **5. (Optional) Start Celery Worker**

For background demand simulation via Celery (requires Redis):

```bash
cd backend
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo
```

**Note:** 
- The `--pool=solo` flag is required for Windows compatibility
- If Redis is unavailable, the system falls back to AsyncIO background tasks (no restart needed)
- Run in a separate terminal from Uvicorn

### **6. Open Browser**

* API: `http://127.0.0.1:8000/docs`
* UI Pages via Jinja2 templates

---

## **Dynamic Pricing Logic (Simplified)**

```
final_price = base_fare
            + (remaining_seats_factor * remaining_seat_ratio)
            + (time_factor * hours_left)
            + (demand_factor * demand_index)
```

Editable inside:
`app/services/pricing_engine.py`

---

## **Project Milestones**

| Milestone | Module                                      | Status         | Completion |
| --------- | ------------------------------------------- | -------------- | ---------- |
| **1**     | Core Flight Search & Data Management        |  Completed   | 100%       |
| **2**     | Dynamic Pricing Engine                      |  Completed   | 100%       |
| **3**     | Booking Workflow & Transaction Management   | In Progress | ~85%       |
| **4**     | User Interface & API Integration            | Pending     | 0%         |

### **Milestone 1 & 2 Achievements:**
- Fully functional flight search with filtering, sorting, and pagination
- Dynamic pricing engine with multi-factor calculations (inventory, time, demand, tiers)
- Background demand simulator (AsyncIO + optional Celery worker)
- Fare history tracking for audit trails
- Comprehensive test coverage (unit + integration tests)

### **Milestone 3 Progress:**
- Multi-step booking flow (booking → payment → confirmation)
- PNR generation and seat allocation
- Concurrency-safe transactions with database locks
- Payment validation and multiple attempt handling
- Booking cancellation and history retrieval endpoints
- Enhanced stress testing and edge case handling (in progress)
