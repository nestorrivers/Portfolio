from allocation.engine import allocate_suppliers
from allocation.models import *

booking = BookingContext(
    pickup_coords=(0,0),
    destination_coords=(5,5),
    mileage=10,
    vehicle_type="Sedan",
    preference=BookingPreference.SHORTEST_DISTANCE,
)

suppliers = [
    SupplierCandidate(supplier_id=1, base_coords=(0,0), vehicle_types={"Sedan"}),
    SupplierCandidate(supplier_id=2, base_coords=(1,1), vehicle_types={"Sedan"}),
]

result = allocate_suppliers(
    booking=booking,
    suppliers=suppliers,
    agreements=[],
    passenger_preferred_supplier=1,
)

print("Ordered suppliers:", result.ordered_suppliers)
print("Reasons:", result.reasons)
