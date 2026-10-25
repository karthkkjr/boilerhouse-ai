#!/usr/bin/env python3
"""Hardcoded West Lafayette apartment dataset. Zero external API dependencies.

Figures are demo values for the hackathon (approximate, not live listings).
Units: price_per_bed = USD/month, distance_mi = miles to Purdue Engineering Mall,
rating = 0.0-5.0.
"""

DATASET_VERSION = "2026.10-demo"

APARTMENTS = [
    {"id": "hub-on-campus", "name": "Hub on Campus West Lafayette", "price_per_bed": 1050, "distance_mi": 0.5, "rating": 4.1, "bus_access": True, "bedrooms": [1, 2, 3, 4, 5], "amenities": ["rooftop", "gym", "study-rooms", "furnished"]},
    {"id": "rise-on-chauncey", "name": "Rise on Chauncey", "price_per_bed": 1095, "distance_mi": 0.6, "rating": 4.2, "bus_access": True, "bedrooms": [1, 2, 3, 4], "amenities": ["gym", "pool", "furnished", "parking-garage"]},
    {"id": "muinzer", "name": "Muinzer Apartments", "price_per_bed": 725, "distance_mi": 0.8, "rating": 3.6, "bus_access": True, "bedrooms": [1, 2, 3], "amenities": ["laundry", "parking"]},
    {"id": "lodge-on-the-wabash", "name": "Lodge on the Wabash", "price_per_bed": 765, "distance_mi": 1.4, "rating": 3.7, "bus_access": True, "bedrooms": [2, 3, 4], "amenities": ["pool", "gym", "furnished", "shuttle"]},
    {"id": "fuse", "name": "Fuse West Lafayette", "price_per_bed": 980, "distance_mi": 0.7, "rating": 4.0, "bus_access": True, "bedrooms": [1, 2, 3, 4], "amenities": ["gym", "study-rooms", "furnished"]},
    {"id": "aspire-discovery-park", "name": "Aspire at Discovery Park", "price_per_bed": 820, "distance_mi": 1.6, "rating": 4.0, "bus_access": True, "bedrooms": [2, 3, 4], "amenities": ["pool", "gym", "furnished", "shuttle"]},
    {"id": "allight-village", "name": "Allight Village", "price_per_bed": 850, "distance_mi": 1.2, "rating": 4.3, "bus_access": True, "bedrooms": [1, 2, 4], "amenities": ["furnished", "study-rooms", "university-owned"]},
    {"id": "lark", "name": "Lark West Lafayette", "price_per_bed": 960, "distance_mi": 0.9, "rating": 4.1, "bus_access": True, "bedrooms": [1, 2, 3, 4, 5], "amenities": ["gym", "rooftop", "furnished"]},
    {"id": "blackbird-farms", "name": "Blackbird Farms", "price_per_bed": 690, "distance_mi": 2.4, "rating": 3.9, "bus_access": True, "bedrooms": [1, 2, 3], "amenities": ["pool", "parking", "pet-friendly"]},
    {"id": "campus-edge-pierce", "name": "Campus Edge on Pierce", "price_per_bed": 870, "distance_mi": 0.6, "rating": 3.8, "bus_access": True, "bedrooms": [2, 3, 4], "amenities": ["furnished", "gym"]},
    {"id": "chauncey-square", "name": "Chauncey Square", "price_per_bed": 1010, "distance_mi": 0.7, "rating": 3.9, "bus_access": True, "bedrooms": [1, 2, 3, 4], "amenities": ["gym", "furnished", "retail-below"]},
    {"id": "cottages-on-lindberg", "name": "The Cottages on Lindberg", "price_per_bed": 735, "distance_mi": 2.1, "rating": 3.8, "bus_access": True, "bedrooms": [3, 4, 5], "amenities": ["pool", "gym", "shuttle", "pet-friendly"]},
    {"id": "redpoint", "name": "Redpoint West Lafayette", "price_per_bed": 740, "distance_mi": 2.6, "rating": 3.7, "bus_access": True, "bedrooms": [2, 3, 4], "amenities": ["pool", "gym", "shuttle"]},
    {"id": "verve", "name": "Verve West Lafayette", "price_per_bed": 1020, "distance_mi": 0.8, "rating": 4.0, "bus_access": True, "bedrooms": [1, 2, 3, 4, 5], "amenities": ["rooftop", "gym", "furnished"]},
    {"id": "fairway", "name": "Fairway Apartments", "price_per_bed": 680, "distance_mi": 2.0, "rating": 3.6, "bus_access": False, "bedrooms": [1, 2], "amenities": ["parking", "pet-friendly"]},
]
