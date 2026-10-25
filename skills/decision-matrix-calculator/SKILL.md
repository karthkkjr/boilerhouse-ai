---
name: decision-matrix-calculator
description: Rank, score, compare, filter and recommend Purdue University off-campus student housing and apartments in West Lafayette, Indiana using a weighted multi-criteria decision matrix. Use whenever the user asks where to live, which apartment is best, cheapest rent, closest to campus, nearest Engineering Mall, best rated, budget housing, roommate bedroom count, lease options, amenities (gym, pool, furnished, pet-friendly, shuttle), CityBus access, or wants to compare Hub on Campus, Rise on Chauncey, Muinzer, Lodge on the Wabash, Fuse, Aspire, Allight Village, Lark, Blackbird Farms, Campus Edge, Chauncey Square, Cottages on Lindberg, Redpoint, Verve, Fairway. Keywords: apartment ranking, housing recommendation, rent per bed, price, distance, rating, weights, trade-off, normalization, scoring, BoilerHouse, Boilermaker, West Lafayette housing search.
license: Apache-2.0
compatibility: Python 3.11+ standard library only. No network, no API keys. Runs fully offline.
metadata:
  project: boilerhouse-ai
  owner: person-b
  dataset: 15 hardcoded West Lafayette apartments (demo values)
---

# Decision Matrix Calculator (BoilerHouse AI)

Ranks 15 West Lafayette apartments by weighted, min-max normalized criteria:
**price** (USD/month per bed, lower is better), **distance** (miles to Purdue
Engineering Mall, lower is better), **rating** (0-5, higher is better).
Score is 0-100. All data is local; never call external APIs for this task.

## When to use
- "Best apartment under $900 near campus" -> `rank_apartments.py`
- "I care most about price" -> raise the `price` weight
- "Compare Hub and Rise" -> `lookup_apartments.py --compare`
- "Tell me about Muinzer" -> `lookup_apartments.py --name`

## Commands (run from this skill directory)

Rank (all flags optional):
```bash
python scripts/rank_apartments.py --budget 900 --max-distance 1.5 --min-rating 3.8 \
  --bedrooms 2 --amenities gym,furnished --weights price=0.5,distance=0.3,rating=0.2 --top 3
```

Preferred for agents - pass everything as one JSON object:
```bash
python scripts/rank_apartments.py --json '{"budget": 900, "max_distance": 1.5, "weights": {"price": 0.5, "distance": 0.3, "rating": 0.2}, "top": 3}'
```
Valid JSON keys: budget, max_distance, min_rating, bedrooms, require_bus, amenities, weights, top.

Lookup / compare:
```bash
python scripts/lookup_apartments.py --list --sort price
python scripts/lookup_apartments.py --name rise
python scripts/lookup_apartments.py --compare hub,rise,muinzer
```

## Mapping user intent to weights
| User says | weights |
|---|---|
| "cheap", "budget", "broke" | price=0.6,distance=0.2,rating=0.2 |
| "close to class", "walkable", "engineering" | price=0.2,distance=0.6,rating=0.2 |
| "nicest", "best reviewed", "quality" | price=0.2,distance=0.2,rating=0.6 |
| nothing specified | default price=0.4,distance=0.35,rating=0.25 |

Weights are auto-normalized to sum to 1, so any positive numbers work.

## Output (stdout JSON)
- `status`: `"ok"` or `"error"`
- `results[]`: `rank`, `name`, `score` (0-100), `raw`, `normalized`, `weighted_contribution`
- `excluded[]`: properties filtered out, each with a `reason`
- `summary`: one-line top pick - quote this to the user, then explain the trade-offs using `weighted_contribution`

Logs go to stderr; parse stdout only. Exit code 2 with
`{"status":"error","error":"..."}` on bad input or zero matches - relay the
error and suggest relaxing constraints.

## Notes
- Normalization is relative to the filtered candidate set, so scores change when filters change.
- Dataset values are demo figures; tell the user to verify current rent with the property.
- Valid amenities: see `references/dataset.md`.
