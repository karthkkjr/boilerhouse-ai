#!/usr/bin/env python3
"""List, search, or compare West Lafayette apartments from the local dataset.

Contract: human-readable logs -> stderr, JSON -> stdout. Exit 2 on bad input.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apartments_data import APARTMENTS, DATASET_VERSION  # noqa: E402


def log(msg):
    print(f"[apartment-lookup] {msg}", file=sys.stderr)


def fail(msg):
    log(f"ERROR: {msg}")
    print(json.dumps({"status": "error", "error": msg}))
    sys.exit(2)


def find(term):
    t = term.strip().lower()
    exact = [a for a in APARTMENTS if a["id"] == t or a["name"].lower() == t]
    if exact:
        return exact
    return [a for a in APARTMENTS if t in a["id"] or t in a["name"].lower()]


def main():
    p = argparse.ArgumentParser(description="Query the hardcoded West Lafayette apartment dataset.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="List all apartments.")
    g.add_argument("--name", help="Fuzzy search by name or id (e.g. hub, rise, muinzer).")
    g.add_argument("--compare", help="Comma list of names/ids to compare side-by-side.")
    p.add_argument("--sort", choices=["price", "distance", "rating"], help="Sort output.")
    args = p.parse_args()

    if args.list:
        rows = list(APARTMENTS)
    elif args.name:
        rows = find(args.name)
        if not rows:
            fail(f"No apartment matches '{args.name}'. Try --list.")
    else:
        rows, missing = [], []
        for term in [t for t in args.compare.split(",") if t.strip()]:
            hits = find(term)
            if not hits:
                missing.append(term.strip())
            elif len(hits) > 1:
                fail(f"'{term.strip()}' is ambiguous: {[h['name'] for h in hits]}")
            elif hits[0] not in rows:
                rows.append(hits[0])
        if missing:
            fail(f"Not found: {missing}. Try --list.")
        if len(rows) < 2:
            fail("--compare needs at least 2 distinct apartments.")

    keys = {"price": ("price_per_bed", False), "distance": ("distance_mi", False), "rating": ("rating", True)}
    if args.sort:
        field, rev = keys[args.sort]
        rows = sorted(rows, key=lambda a: a[field], reverse=rev)

    out = {"status": "ok", "skill": "decision-matrix-calculator", "dataset_version": DATASET_VERSION,
           "count": len(rows), "apartments": rows}
    if args.compare:
        out["best_by"] = {
            "price": min(rows, key=lambda a: a["price_per_bed"])["name"],
            "distance": min(rows, key=lambda a: a["distance_mi"])["name"],
            "rating": max(rows, key=lambda a: a["rating"])["name"],
        }
    log(f"returned {len(rows)} apartment(s)")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
