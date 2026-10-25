# Dataset reference

Source: `scripts/apartments_data.py` (version 2026.10-demo). Demo values for the hackathon, not live listings.

Fields: `id`, `name`, `price_per_bed` (USD/mo), `distance_mi` (to Engineering Mall),
`rating` (0-5), `bus_access` (CityBus), `bedrooms` (list), `amenities` (list).

Amenity tags: gym, pool, rooftop, furnished, study-rooms, laundry, parking,
parking-garage, shuttle, pet-friendly, retail-below, university-owned.

Formula: for each criterion, `norm = (x - min)/(max - min)` (inverted for price and
distance), `score = 100 * sum(weight_i * norm_i)` with weights summed to 1.
If all candidates share a value, that criterion normalizes to 1.0 for everyone.
