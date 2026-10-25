"""Runs Person B's decision-matrix-calculator skill scripts and returns their JSON.

Used by hermes_main.py (Hermes tools) and main.py (backup). Always uses the
current Python (sys.executable), so it works on Windows where `python3` doesn't exist.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent / "skills" / "decision-matrix-calculator"
SCRIPTS = SKILL_DIR / "scripts"


def skill_description():
    """The `description:` line from SKILL.md, so Person B can tune routing in one place."""
    try:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else ""
    except OSError:
        return ""


def _run(script, args):
    # stdout = JSON contract, stderr = logs (ignored). Exit code 2 still prints error JSON.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "error": (proc.stderr or proc.stdout or "no output").strip()[-500:]}


def rank_apartments(query):
    """query: dict with any of budget, max_distance, min_rating, bedrooms,
    require_bus, amenities, weights, top."""
    query = {k: v for k, v in query.items() if v is not None}
    return _run("rank_apartments.py", ["--json", json.dumps(query)])


def lookup_apartments(compare=None, name=None):
    """Side-by-side compare (e.g. 'hub,rise') or look up one apartment by name."""
    if compare:
        return _run("lookup_apartments.py", ["--compare", compare])
    if name:
        return _run("lookup_apartments.py", ["--name", name])
    return _run("lookup_apartments.py", ["--list", "--sort", "price"])
