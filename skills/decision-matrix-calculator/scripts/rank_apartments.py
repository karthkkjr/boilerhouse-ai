#!/usr/bin/env python3
"""Weighted decision matrix for West Lafayette apartments.

Contract: human-readable logs -> stderr, machine-readable JSON -> stdout.
Exit codes: 0 ok, 2 bad input / no results.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apartments_data import APARTMENTS, DATASET_VERSION  # noqa: E402

# criterion -> (dataset field, direction). "min" = lower is better.
CRITERIA = {
    "price": ("price_per_bed", "min"),
    "distance": ("distance_mi", "min"),
    "rating": ("rating", "max"),
}
DEFAULT_WEIGHTS = {"price": 0.4, "distance": 0.35, "rating": 0.25}


def log(msg):
    print(f"[decision-matrix] {msg}", file=sys.stderr)


def fail(msg, code=2):
    log(f"ERROR: {msg}")
    print(json.dumps({"status": "error", "error": msg}))
    sys.exit(code)


def parse_weights(raw):
    """Accept 'price=0.5,distance=0.3,rating=0.2' or a dict. Normalizes to sum 1."""
    if raw is None:
        weights = dict(DEFAULT_WEIGHTS)
    elif isinstance(raw, dict):
        weights = {}
        for k, v in raw.items():
            try:
                weights[str(k).strip().lower()] = float(v)
            except (TypeError, ValueError):
                fail(f"Weight for '{k}' must be a number, got {v!r}.")
    else:
        weights = {}
        for part in str(raw).split(","):
            part = part.strip()
            if not part:
                continue
            if "=" not in part and ":" not in part:
                fail(f"Bad weight '{part}'. Use format price=0.5,distance=0.3,rating=0.2")
            key, val = part.replace(":", "=").split("=", 1)
            try:
                weights[key.strip().lower()] = float(val)
            except ValueError:
                fail(f"Weight for '{key.strip()}' must be a number, got {val.strip()!r}.")
    unknown = set(weights) - set(CRITERIA)
    if unknown:
        fail(f"Unknown criteria {sorted(unknown)}. Valid: {sorted(CRITERIA)}")
    if any(w < 0 for w in weights.values()):
        fail("Weights must be non-negative.")
    for k in CRITERIA:
        weights.setdefault(k, 0.0)
    total = sum(weights.values())
    if total <= 0:
        fail("At least one weight must be > 0.")
    return {k: round(v / total, 4) for k, v in weights.items()}


def normalize(values, direction):
    """Min-max normalize to [0,1]; 1.0 is always 'best'."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0 for _ in values]
    if direction == "min":
        return [(hi - v) / (hi - lo) for v in values]
    return [(v - lo) / (hi - lo) for v in values]


def apply_filters(apts, q):
    kept, excluded = [], []
    for a in apts:
        reason = None
        if q["budget"] is not None and a["price_per_bed"] > q["budget"]:
            reason = f"price ${a['price_per_bed']} > budget ${q['budget']:g}"
        elif q["max_distance"] is not None and a["distance_mi"] > q["max_distance"]:
            reason = f"distance {a['distance_mi']}mi > max {q['max_distance']:g}mi"
        elif q["min_rating"] is not None and a["rating"] < q["min_rating"]:
            reason = f"rating {a['rating']} < min {q['min_rating']:g}"
        elif q["bedrooms"] is not None and q["bedrooms"] not in a["bedrooms"]:
            reason = f"no {q['bedrooms']}-bedroom units"
        elif q["require_bus"] and not a["bus_access"]:
            reason = "no CityBus access"
        elif q["amenities"]:
            missing = [m for m in q["amenities"] if m not in a["amenities"]]
            if missing:
                reason = f"missing amenities {missing}"
        if reason:
            excluded.append({"id": a["id"], "name": a["name"], "reason": reason})
        else:
            kept.append(a)
    return kept, excluded


def rank(q):
    weights = parse_weights(q["weights"])
    candidates, excluded = apply_filters(APARTMENTS, q)
    log(f"{len(candidates)}/{len(APARTMENTS)} apartments pass filters; weights={weights}")
    if not candidates:
        fail("No apartments match the filters. Relax budget, distance, rating, or bedroom constraints.")

    norm = {c: normalize([a[f] for a in candidates], d) for c, (f, d) in CRITERIA.items()}

    rows = []
    for i, a in enumerate(candidates):
        breakdown = {c: round(weights[c] * norm[c][i], 4) for c in CRITERIA}
        rows.append({
            "id": a["id"],
            "name": a["name"],
            "score": round(sum(breakdown.values()) * 100, 2),
            "raw": {
                "price_per_bed": a["price_per_bed"],
                "distance_mi": a["distance_mi"],
                "rating": a["rating"],
                "bus_access": a["bus_access"],
                "bedrooms": a["bedrooms"],
                "amenities": a["amenities"],
            },
            "normalized": {c: round(norm[c][i], 4) for c in CRITERIA},
            "weighted_contribution": breakdown,
        })
    # Deterministic tie-break: score desc, then price asc, then name.
    rows.sort(key=lambda r: (-r["score"], r["raw"]["price_per_bed"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    top = rows[: q["top"]]
    best = top[0]
    return {
        "status": "ok",
        "skill": "decision-matrix-calculator",
        "dataset_version": DATASET_VERSION,
        "method": "weighted-sum over min-max normalized criteria (score 0-100)",
        "query": {k: v for k, v in q.items() if k != "weights"},
        "weights": weights,
        "candidate_count": len(candidates),
        "results": top,
        "excluded": excluded,
        "summary": (
            f"Top pick: {best['name']} (score {best['score']}) at "
            f"${best['raw']['price_per_bed']}/bed, {best['raw']['distance_mi']}mi "
            f"to Engineering Mall, rated {best['raw']['rating']}/5."
        ),
    }


def build_parser():
    p = argparse.ArgumentParser(description="Rank West Lafayette apartments with a weighted decision matrix.")
    p.add_argument("--budget", type=float, help="Max monthly rent per bed (USD).")
    p.add_argument("--max-distance", type=float, help="Max miles to Purdue Engineering Mall.")
    p.add_argument("--min-rating", type=float, help="Minimum rating 0-5.")
    p.add_argument("--bedrooms", type=int, help="Required bedroom count (e.g. 2).")
    p.add_argument("--require-bus", action="store_true", help="Only CityBus-accessible properties.")
    p.add_argument("--amenities", help="Comma list, e.g. gym,furnished,pet-friendly")
    p.add_argument("--weights", help="e.g. price=0.5,distance=0.3,rating=0.2 (auto-normalized)")
    p.add_argument("--top", type=int, default=5, help="Number of results (default 5).")
    p.add_argument("--json", dest="json_args", help="All args as one JSON object (LLM-friendly). Overrides flags.")
    return p


def main():
    args = build_parser().parse_args()
    q = {
        "budget": args.budget,
        "max_distance": args.max_distance,
        "min_rating": args.min_rating,
        "bedrooms": args.bedrooms,
        "require_bus": args.require_bus,
        "amenities": args.amenities,
        "weights": args.weights,
        "top": args.top,
    }
    if args.json_args:
        try:
            override = json.loads(args.json_args)
        except json.JSONDecodeError as e:
            fail(f"--json is not valid JSON: {e}")
        if not isinstance(override, dict):
            fail("--json must be a JSON object.")
        for k, v in override.items():
            key = k.replace("-", "_")
            if key not in q:
                fail(f"Unknown --json key '{k}'. Valid: {sorted(q)}")
            q[key] = v
    # Coerce/validate types (JSON path can deliver strings).
    try:
        for k in ("budget", "max_distance", "min_rating"):
            if q[k] is not None:
                q[k] = float(q[k])
        if q["bedrooms"] is not None:
            q["bedrooms"] = int(q["bedrooms"])
        q["top"] = int(q["top"])
    except (TypeError, ValueError) as e:
        fail(f"Invalid numeric argument: {e}")
    if q["top"] < 1:
        fail("--top must be >= 1.")
    if isinstance(q["amenities"], str):
        q["amenities"] = [m.strip().lower() for m in q["amenities"].split(",") if m.strip()]
    q["amenities"] = [str(m).strip().lower() for m in (q["amenities"] or [])]
    q["require_bus"] = bool(q["require_bus"])

    print(json.dumps(rank(q), indent=2))


if __name__ == "__main__":
    main()
