from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum



class BookingPreference(str, Enum):
    SHORTEST_DISTANCE = "Shortest Distance"
    MOST_COMPETITIVE_PRICING = "Most Competitive Pricing"
    FASTEST_ETA = "Fastest ETA"


@dataclass(frozen=True)
class BookingContext:
    pickup_coords: Tuple[float, float]
    destination_coords: Tuple[float, float]
    mileage: float
    vehicle_type: str
    preference: BookingPreference


@dataclass(frozen=True)
class SupplierCandidate:
    supplier_id: int
    base_coords: Tuple[float, float]
    vehicle_types: set[str]


@dataclass(frozen=True)
class PriceAgreement:
    supplier_id: int
    agreed_cost: float
    accept_return: bool


@dataclass(frozen=True)
class POIMatch:
    supplier_id: int
    distance_miles: float


@dataclass
class AllocationResult:
    ordered_suppliers: List[int]
    reasons: Dict[int, List[str]]

