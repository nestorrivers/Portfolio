# Supplier Allocation Engine

A pure-Python, rule-driven engine that decides **which service providers should be offered a booking, and in what order** — and records *why* each one was placed where it was.

Given a booking, a pool of candidate suppliers, and optional pricing agreements and preferences, the engine returns an ordered list of supplier IDs plus a machine-readable reason trail for every supplier in that list.

It was extracted from a larger production Django transport-booking system, where allocation logic had become entangled with request handling and persistence. Pulling it out makes the rules explicit, deterministic, and unit-testable in isolation.

- **Zero framework coupling** — no Django, no ORM, no HTTP
- **No side effects** — a pure function in, a plain result object out
- **Explainable** — every placement carries one or more reason codes
- **One runtime dependency** — [`haversine`](https://pypi.org/project/haversine/)

---

## Contents

- [How allocation works](#how-allocation-works)
- [Quick start](#quick-start)
- [API reference](#api-reference)
- [Behavioural notes](#behavioural-notes)
- [Project structure](#project-structure)
- [Development](#development)
- [Design decisions](#design-decisions)
- [Known limitations](#known-limitations)
- [Provenance](#provenance)

---

## How allocation works

`allocate_suppliers` runs a fixed pipeline. Earlier stages take precedence: a supplier is positioned by the **first** stage that selects it.

| # | Stage | Selects | Order within stage | Reason code |
|---|-------|---------|--------------------|-------------|
| 1 | **Eligibility filter** | Suppliers whose `vehicle_types` contain the booking's `vehicle_type` | — (gate only; everything below acts on the eligible set) | — |
| 2 | **Passenger preference** | The passenger's preferred supplier, *if eligible* | Single supplier | `passenger_preference` |
| 3 | **Price agreements** | Eligible suppliers holding a `PriceAgreement` | Cheapest `agreed_cost` first | `price_agreement` |
| 4 | **POI proximity** | Eligible suppliers with a `POIMatch` closer than 0.1 miles | Order supplied by the caller | `poi_match` |
| 5 | **Booking preference** | All remaining eligible suppliers | Depends on `BookingPreference` (below) | `distance_priority` / `eta_priority` / `pricing_priority` |

Stage 5 is driven by `BookingContext.preference`:

| `BookingPreference` | Ordering of remaining suppliers | Reason code |
|---------------------|---------------------------------|-------------|
| `SHORTEST_DISTANCE` | Great-circle distance from supplier base to pickup, ascending | `distance_priority` |
| `FASTEST_ETA` | Currently identical to `SHORTEST_DISTANCE` (see [limitations](#known-limitations)) | `eta_priority` |
| `MOST_COMPETITIVE_PRICING` | Agreed cost ascending; suppliers without an agreement sort last | `pricing_priority` |

A supplier that qualifies at several stages accumulates several reason codes but keeps the position from the earliest one.

---

## Quick start

### Requirements

- Python 3.10+

### Install

```bash
git clone https://github.com/nestorrivers/supplier-allocation-engine.git
cd supplier-allocation-engine

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install pytest-cov            # required by the addopts in pytest.ini
```

### Example

```python
from allocation.engine import allocate_suppliers
from allocation.models import (
    BookingContext,
    BookingPreference,
    PriceAgreement,
    SupplierCandidate,
)

booking = BookingContext(
    pickup_coords=(0, 0),            # (latitude, longitude), decimal degrees
    destination_coords=(5, 5),
    mileage=10,
    vehicle_type="Sedan",
    preference=BookingPreference.SHORTEST_DISTANCE,
)

suppliers = [
    SupplierCandidate(supplier_id=1, base_coords=(0, 0),     vehicle_types={"Sedan"}),
    SupplierCandidate(supplier_id=2, base_coords=(1, 1),     vehicle_types={"Sedan", "Van"}),
    SupplierCandidate(supplier_id=3, base_coords=(2, 2),     vehicle_types={"Van"}),
    SupplierCandidate(supplier_id=4, base_coords=(0.5, 0.5), vehicle_types={"Sedan"}),
]

agreements = [
    PriceAgreement(supplier_id=2, agreed_cost=50, accept_return=True),
    PriceAgreement(supplier_id=3, agreed_cost=30, accept_return=False),
    PriceAgreement(supplier_id=4, agreed_cost=40, accept_return=False),
]

result = allocate_suppliers(
    booking=booking,
    suppliers=suppliers,
    agreements=agreements,
    passenger_preferred_supplier=2,
)

print(result.ordered_suppliers)
# [2, 4, 1]

print(result.reasons)
# {2: ['passenger_preference', 'price_agreement'],
#  4: ['price_agreement'],
#  1: ['distance_priority']}
```

What happened:

- Supplier **3** was dropped at the eligibility gate (Van only; the booking wants a Sedan) — despite holding the cheapest agreement.
- Supplier **2** was placed first as the passenger's choice, and *also* records `price_agreement` because it holds one.
- Supplier **4** came next: it is eligible and holds an agreement, and supplier 2 (the only other eligible agreement holder) was already placed.
- Supplier **1** had no agreement, so it fell through to the booking preference and was ordered by distance.

A minimal runnable version lives in [`allocation/example.py`](allocation/example.py):

```bash
python -m allocation.example
```

---

## API reference

### `allocate_suppliers`

```python
def allocate_suppliers(
    booking: BookingContext,
    suppliers: List[SupplierCandidate],
    agreements: List[PriceAgreement],
    passenger_preferred_supplier: Optional[int] = None,
    poi_matches: Optional[Iterable[POIMatch]] = None,
) -> AllocationResult
```

| Parameter | Description |
|-----------|-------------|
| `booking` | The booking being allocated. |
| `suppliers` | All candidate suppliers. Ineligible ones are filtered out by the engine. |
| `agreements` | Pricing agreements. Pass `[]` if there are none. Agreements for ineligible suppliers are ignored. |
| `passenger_preferred_supplier` | Optional supplier ID the passenger has asked for. Ignored if that supplier is not eligible. |
| `poi_matches` | Optional POI-proximity matches, typically computed upstream. Defaults to none. |

### Models (`allocation/models.py`)

All input models are frozen dataclasses.

| Model | Fields |
|-------|--------|
| `BookingContext` | `pickup_coords: (lat, lon)`, `destination_coords: (lat, lon)`, `mileage: float`, `vehicle_type: str`, `preference: BookingPreference` |
| `SupplierCandidate` | `supplier_id: int`, `base_coords: (lat, lon)`, `vehicle_types: set[str]` |
| `PriceAgreement` | `supplier_id: int`, `agreed_cost: float`, `accept_return: bool` |
| `POIMatch` | `supplier_id: int`, `distance_miles: float` |
| `BookingPreference` | `str` enum: `SHORTEST_DISTANCE`, `MOST_COMPETITIVE_PRICING`, `FASTEST_ETA` |

### `AllocationResult`

| Field | Type | Meaning |
|-------|------|---------|
| `ordered_suppliers` | `List[int]` | Supplier IDs, highest priority first. |
| `reasons` | `Dict[int, List[str]]` | For each supplier in `ordered_suppliers`, the reason codes that applied, in the order they were matched. |

### `AllocationReason`

`str` enum in `allocation/engine.py`. Values: `passenger_preference`, `price_agreement`, `poi_match`, `distance_priority`, `eta_priority`, `pricing_priority`.

---

## Behavioural notes

Verified against the current implementation:

- **Empty in, empty out.** If no supplier is eligible, the result is `ordered_suppliers=[]` and `reasons={}`. The engine never raises for "no match".
- **Ineligible preferences are silently ignored.** A passenger-preferred supplier that can't supply the requested vehicle type is not placed and produces no error.
- **Reasons stack, position doesn't.** Reason lists can contain several codes; only the earliest matching stage determines the supplier's rank.
- **POI threshold is strict.** A match at exactly `0.1` miles does not qualify; `0.09` does. Qualifying matches are placed in the order they are supplied, not re-sorted by distance.
- **Ties preserve input order.** Sorting is stable, so suppliers at equal distance (or equal cost) keep the order in which they appeared in `suppliers` / `agreements`.
- **Distance is great-circle, not road distance.** Coordinates are `(latitude, longitude)` in decimal degrees, measured in miles via `haversine`.
- **Deterministic.** Identical inputs always produce identical output; the engine holds no state and reads no clock.

---

## Project structure

```
supplier-allocation-engine/
├── allocation/
│   ├── engine.py      # allocate_suppliers() and AllocationReason
│   ├── models.py      # Input/output dataclasses and BookingPreference enum
│   ├── utils.py       # distance_miles() — thin wrapper over haversine
│   └── example.py     # Minimal runnable example
├── tests/
│   └── test_engine.py # pytest suite (fixtures + one test per rule)
├── pyproject.toml
├── pytest.ini
└── requirements.txt
```

---

## Development

### Run the tests

```bash
python -m pytest
```

Use `python -m pytest` rather than bare `pytest`: the `allocation` package sits at the repository root, and `python -m` puts the current directory on `sys.path`.

`pytest.ini` enables verbose output and a coverage report (`--cov=allocation --cov-report=term-missing`), which is why `pytest-cov` is needed.

The suite covers each stage of the pipeline: passenger preference, vehicle-type filtering, cheapest-first price agreements, POI threshold behaviour, and each `BookingPreference` ordering.

### Type-check

```bash
mypy --ignore-missing-imports allocation
```

`haversine` ships without type stubs, hence the flag.

---

## Design decisions

- **Explicit rules over inferred behaviour.** The pipeline is a readable sequence of stages rather than a weighted score. You can read `engine.py` top to bottom and know exactly why a supplier ranked where it did.
- **Explainability is part of the output.** Reason codes are returned alongside the ordering so callers can log, display, or audit allocation decisions without re-deriving them.
- **Minimal domain models.** Dataclasses carry only the fields the rules need. Anything else from the host system (names, contact details, commercial terms) stays outside the boundary.
- **Frozen input models.** Input dataclasses are `frozen=True`, so their fields can't be reassigned after construction. Build a new object to change a value.
- **Callers own I/O.** Eligibility candidates, agreements, and POI matches are computed and passed in. The engine only orders them, which is what keeps it free of database and HTTP concerns.
- **Clarity over cleverness.** No plugin system, strategy registry, or scoring framework — just the rules the domain actually required.

---

## Known limitations

These reflect the current state of the code and are worth knowing before building on it:

- **`FASTEST_ETA` is distance in disguise.** There is no speed, traffic, or routing input, so ETA ordering uses the same base-to-pickup distance as `SHORTEST_DISTANCE`. Only the reason code differs.
- **`MOST_COMPETITIVE_PRICING` has little effect on its own.** Every eligible supplier with an agreement is already placed in stage 3 (cheapest first), so by stage 5 the remaining suppliers have no price data and keep their input order. In practice the preference only changes the reason code applied to suppliers without agreements.
- **Some inputs are accepted but not yet used.** `BookingContext.mileage`, `BookingContext.destination_coords`, and `PriceAgreement.accept_return` are part of the data model but do not currently influence allocation.
- **No capacity or availability model.** The engine orders eligible suppliers; it does not know whether they are free, in service, or already committed.

---

## Provenance

This engine was distilled from a real-world transport booking system. Domain-specific identifiers, client data, and commercial logic have been intentionally generalised or omitted.

The goal is to demonstrate system design and rule-driven allocation, not to expose proprietary behaviour.