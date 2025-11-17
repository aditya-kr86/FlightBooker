# AkashaYatra — Flight Booking Simulator with Dynamic Pricing

A modern Flight Booking & Pricing Simulation system built using **FastAPI**, designed to replicate real-world airline search, pricing logic, and booking workflows.

**AkāshaYātra (आकाशयात्रा)** means *“Sky Journey”*, inspired by Indian–Sanskrit origins, representing a journey through the skies with intelligence and precision.

---

## **Project Overview**

AkashaYatra is a complete simulation of airline operations, focusing on:

* **Flight Search Engine**
* **Dynamic Pricing Algorithm** (based on seat avaibility, time, demand)
* **Seat Inventory + Concurrency Control**
* **Booking Workflow + PNR Generation**
* **Frontend UI (Jinja2 Templates)**
* **Receipt/PDF generation**

Built as part of the **Infosys Springboard Internship**, the project follows industry-standard backend architecture with clear separation of concerns.

---

## **Tech Stack**

### **Backend**

* FastAPI (Async)
* SQLAlchemy (ORM)
* SQLite / PostgreSQL
* Pydantic
* Jinja2 Templates

### **Utilities**

* AsyncIO (background demand simulation)
* ReportLab / WeasyPrint (PDF receipts)
* Python Dotenv
* Uvicorn

---

## **Project Architecture**

```
AkashaYatra/
│
├── main.py                      # App entry point
│
├── app/
│   ├── __init__.py
│   ├── config.py                # DB setup (SQLite → PostgreSQL later)
│   ├── db_seed.py               # For simulated flight data
│
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── airline.py
│   │   ├── airport.py
│   │   ├── flight.py
│   │   ├── booking.py
│   │   └── user.py
│
│   ├── schemas/                 # Pydantic models for request/response
│   │   ├── flight_schema.py
│   │   ├── booking_schema.py
│   │   └── user_schema.py
│
│   ├── services/                # Business logic (per module)
│   │   ├── flight_service.py    # Search + sort
│   │   ├── pricing_engine.py    # Dynamic fare logic
│   │   ├── booking_service.py   # Booking + concurrency
│   │   └── demand_simulator.py  # Background demand engine
│
│   ├── routes/                  # FastAPI routers (module-wise)
│   │   ├── flight_routes.py
│   │   ├── pricing_routes.py
│   │   ├── booking_routes.py
│   │   └── ui_routes.py
│
│   ├── templates/               # Jinja2 templates (for frontend)
│   │   ├── base.html
│   │   ├── search.html
│   │   ├── results.html
│   │   ├── booking.html
│   │   └── confirmation.html
│
│   ├── static/                  # CSS / JS / images
│   │   └── styles.css
│
│   └── utils/                   # Helpers (PNR, PDF, etc.)
│       ├── pnr_generator.py
│       └── pdf_generator.py
│
├── requirements.txt
├── README.md
└── database.db                  # SQLite (local dev)
```

---

## **Core Features**

### 1. Flight Search & Filter

* Search by origin, destination, date
* Sort by price, time, duration
* Includes simulated airline/airport datasets

### 2. Dynamic Pricing Engine

Parameters:

* Remaining seat percentage
* Time left to departure
* Demand index (0–100)
* Base fare tiers

Real-time fare updates during search or booking.

### 3. Booking Workflow

* Passenger details
* Seat lock (Optimistic/Pessimistic concurrency)
* Simulated payment
* PNR generation
* Booking history
* Cancellation API

### 4. Frontend UI

* Search page
* Flight results with updated prices
* Booking page
* PNR confirmation page
* Downloadable receipt (PDF/JSON)

---

## **Setup Instructions**

### 1. Clone Repository

```bash
git clone https://github.com/aditya-kr86/AkashaYatra.git
cd AkashaYatra
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate       # mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the App

```bash
uvicorn main:app --reload
```

### 5. Open Browser

`http://127.0.0.1:8000`
API Docs: `/docs` & `/redoc`

---

## **Dynamic Pricing Logic (Simplified Example)**

```
final_price = base_fare
            + (remaining_seats_factor * remaining_seat_ratio)
            + (time_factor * hours_left)
            + (demand_factor * demand_index)
```

You can modify this inside:

```
app/services/pricing_engine.py
```

---

## 🏁 **Milestone Progress**

| Milestone              | Status         |
| ---------------------- | -------------- |
| Flight Search Engine   | In Progress |
| Dynamic Pricing Engine | Pending      |
| Booking Workflow       | Pending      |
| Frontend Integration   | Pending      |

---

## 🪪 **License**

MIT License — free for academic, learning & experimentation.

---

## 🎤 **Credits**

Developed by **Aditya Kumar**
Infosys Springboard Internship — 2025