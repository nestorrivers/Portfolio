import pytest
from allocation.engine import allocate_suppliers, AllocationReason
from allocation.models import (
    BookingContext,
    SupplierCandidate,
    PriceAgreement,
    POIMatch,
    BookingPreference,
)


# --- Fixtures ---

@pytest.fixture
def suppliers():
    return [
        SupplierCandidate(supplier_id=1, base_coords=(0, 0), vehicle_types={"Sedan"}),
        SupplierCandidate(supplier_id=2, base_coords=(1, 1), vehicle_types={"Sedan", "Van"}),
        SupplierCandidate(supplier_id=3, base_coords=(2, 2), vehicle_types={"Van"}),
    ]


@pytest.fixture
def booking_sedan():
    return BookingContext(
        pickup_coords=(0, 0),
        destination_coords=(5, 5),
        mileage=10,
        vehicle_type="Sedan",
        preference=BookingPreference.SHORTEST_DISTANCE,
    )


@pytest.fixture
def price_agreements():
    return [
        PriceAgreement(supplier_id=2, agreed_cost=50),
        PriceAgreement(supplier_id=3, agreed_cost=30),
    ]


@pytest.fixture
def poi_matches():
    return [
        POIMatch(supplier_id=1, distance_miles=0.05),
        POIMatch(supplier_id=3, distance_miles=0.2),  # too far
    ]


# --- Tests ---

def test_passenger_preference_first(suppliers, booking_sedan):
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=[],
        passenger_preferred_supplier=2,
        poi_matches=[],
    )
    assert result.ordered_suppliers[0] == 2
    assert AllocationReason.PASSENGER_PREFERENCE.value in result.reasons[2]


def test_vehicle_type_filtering(suppliers, booking_sedan):
    # Supplier 3 only has Van, should be excluded
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=[],
    )
    assert 3 not in result.ordered_suppliers


def test_price_agreement_cheapest_first(suppliers, booking_sedan, price_agreements):
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=price_agreements,
    )
    # Supplier 2 is eligible and has price agreement, supplier 3 is Van only
    assert result.ordered_suppliers[0] == 2
    assert AllocationReason.PRICE_AGREEMENT.value in result.reasons[2]


def test_poi_match_priority(suppliers, booking_sedan, poi_matches):
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=[],
        poi_matches=poi_matches,
    )
    # Only supplier 1 within POI threshold
    assert result.ordered_suppliers[0] == 1
    assert AllocationReason.POI_MATCH.value in result.reasons[1]


def test_shortest_distance_ordering(suppliers, booking_sedan):
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=[],
    )
    # Should order by distance (supplier 1 is closest, supplier 2 next)
    assert result.ordered_suppliers[0] == 1
    assert result.ordered_suppliers[1] == 2


def test_most_competitive_pricing(suppliers, booking_sedan, price_agreements):
    booking_sedan.preference = BookingPreference.MOST_COMPETITIVE_PRICING
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=price_agreements,
    )
    # Supplier 2 eligible, supplier 3 excluded
    assert result.ordered_suppliers[0] == 2
    assert AllocationReason.PRICING_PRIORITY.value in result.reasons[2]


def test_fastest_eta_sorting(suppliers, booking_sedan):
    booking_sedan.preference = BookingPreference.FASTEST_ETA
    result = allocate_suppliers(
        booking=booking_sedan,
        suppliers=suppliers,
        agreements=[],
    )
    # ETA currently uses same distance calculation
    assert result.ordered_suppliers[0] == 1
