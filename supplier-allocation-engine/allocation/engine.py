from typing import List, Dict, Optional, Tuple, Iterable
from enum import Enum

from haversine import haversine, Unit

from allocation.utils import distance_miles
from allocation.models import (
    BookingContext,
    SupplierCandidate,
    PriceAgreement,
    POIMatch,
    AllocationResult,
    BookingPreference,
)


class AllocationReason(str, Enum):
    PASSENGER_PREFERENCE = "passenger_preference"
    PRICE_AGREEMENT = "price_agreement"
    POI_MATCH = "poi_match"
    DISTANCE_PRIORITY = "distance_priority"
    ETA_PRIORITY = "eta_priority"
    PRICING_PRIORITY = "pricing_priority"


def allocate_suppliers(
    booking: BookingContext,
    suppliers: List[SupplierCandidate],
    agreements: List[PriceAgreement],
    passenger_preferred_supplier: Optional[int] = None,
    poi_matches: Optional[Iterable[POIMatch]] = None,
) -> AllocationResult:
    if poi_matches is None:
        poi_matches = []

    ordered: List[int] = []
    reasons: Dict[int, List[str]] = {}

    def add_supplier(supplier_id: int, reason: AllocationReason):
        if supplier_id not in ordered:
            ordered.append(supplier_id)
            reasons[supplier_id] = []
        reasons[supplier_id].append(reason.value)

    # 1. Vehicle type filtering (establish eligibility early)
    eligible_suppliers = {
        s.supplier_id: s
        for s in suppliers
        if booking.vehicle_type in s.vehicle_types
    }

    # 2. Passenger preferred supplier (only if eligible)
    if (
        passenger_preferred_supplier is not None
        and passenger_preferred_supplier in eligible_suppliers
    ):
        add_supplier(
            passenger_preferred_supplier,
            AllocationReason.PASSENGER_PREFERENCE,
        )

    # 3. Price agreements (cheapest first)
    for agreement in sorted(agreements, key=lambda a: a.agreed_cost):
        if agreement.supplier_id in eligible_suppliers:
            add_supplier(
                agreement.supplier_id,
                AllocationReason.PRICE_AGREEMENT,
            )

    # 4. POI proximity
    for poi in poi_matches:
        if (
            poi.supplier_id in eligible_suppliers
            and poi.distance_miles < 0.1
        ):
            add_supplier(
                poi.supplier_id,
                AllocationReason.POI_MATCH,
            )

    # 5. Preference-based ordering
    remaining = [
        supplier_id
        for supplier_id in eligible_suppliers.keys()
        if supplier_id not in ordered
    ]

    def sort_by_distance(supplier_ids: List[int]) -> List[int]:
        return sorted(
            supplier_ids,
            key=lambda sid: distance_miles(
                eligible_suppliers[sid].base_coords,
                booking.pickup_coords,
            ),
        )

    if booking.preference == BookingPreference.SHORTEST_DISTANCE:
        for sid in sort_by_distance(remaining):
            add_supplier(sid, AllocationReason.DISTANCE_PRIORITY)

    elif booking.preference == BookingPreference.FASTEST_ETA:
        for sid in sort_by_distance(remaining):
            add_supplier(sid, AllocationReason.ETA_PRIORITY)

    elif booking.preference == BookingPreference.MOST_COMPETITIVE_PRICING:
        priced = {
            a.supplier_id: a.agreed_cost
            for a in agreements
        }
        remaining.sort(key=lambda sid: priced.get(sid, float("inf")))
        for sid in remaining:
            add_supplier(sid, AllocationReason.PRICING_PRIORITY)

    return AllocationResult(
        ordered_suppliers=ordered,
        reasons=reasons,
    )
