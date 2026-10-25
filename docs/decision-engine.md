# Decision Engine & Agent Skills

BoilerHouse AI ranks West Lafayette apartments with a **weighted multi-criteria decision matrix**, packaged as an [agentskills.io](https://agentskills.io)-compliant skill (`skills/decision-matrix-calculator/`). Our local Hermes Agent, running Gemma 4 through Ollama, calls it through two tools: `rank_apartments` and `lookup_apartments`.

## Criteria

Every apartment is scored on three criteria:

| Criterion | Field | Direction |
|---|---|---|
| Price | rent per bed (USD/month) | lower is better |
| Distance | miles to Purdue's Engineering Mall | lower is better |
| Rating | resident rating, 0-5 | higher is better |

## Filtering

Hard constraints remove candidates **before** scoring, so nothing that breaks a requirement can win:

- `budget`: max rent per bed
- `max_distance`: max miles to the Engineering Mall
- `min_rating`: minimum rating
- `bedrooms`: required bedroom count
- `require_bus`: CityBus access only
- `amenities`: all listed amenities must be present (gym, pool, furnished, pet-friendly, shuttle, ...)

Every excluded property is returned with a reason (e.g. `"price $1050 > budget $900"`), so the agent can explain why a place the user expected is missing.

## Normalization

Raw criteria use different units (dollars, miles, stars), so each one is **min-max normalized** to the range 0-1 across the candidates that survived filtering. Price and distance are inverted so that 1.0 always means "best":

```
rating:          n = (x - min) / (max - min)
price, distance: n = (max - x) / (max - min)
```

If every candidate shares the same value, that criterion scores 1.0 for all of them, which avoids division by zero. Normalization is relative to the filtered set, so the same apartment can score differently under different filters. That is intended: the ranking answers "best among the options that fit you."

## Weights

The final score is a weighted sum scaled to 0-100:

```
score = 100 * (w_price * n_price + w_distance * n_distance + w_rating * n_rating)
```

Weights are **auto-normalized** to sum to 1, so the agent can pass any positive numbers (`price=5,distance=3` works). Omitted criteria get weight 0. The agent maps natural language to weights:

| User says | price / distance / rating |
|---|---|
| "cheap", "budget", "I'm broke" | 0.6 / 0.2 / 0.2 |
| "walk to class", "close to engineering" | 0.2 / 0.6 / 0.2 |
| "nicest", "best reviewed" | 0.2 / 0.2 / 0.6 |
| no preference (default) | 0.4 / 0.35 / 0.25 |

Ties break by lower price, then by name, so results are deterministic.

## Explainability

Each result includes its raw values, its normalized values, and a `weighted_contribution` breakdown showing how many points each criterion added. The agent uses that breakdown to explain *why* the top pick won, not just *that* it won.

## Built to the open standard

- **Spec-compliant skill:** `SKILL.md` with valid frontmatter (lowercase hyphenated name matching the folder, a keyword-dense description for semantic routing, Apache-2.0 license), plus `scripts/` and `references/`.
- **Strict CLI contract:** scripts write clean JSON to stdout and human-readable logs to stderr, and return a structured error `{"status":"error","error":"..."}` with exit code 2.
- **LLM-friendly input:** one `--json` argument accepts every parameter, which is more reliable for a small local model than assembling CLI flags.

## Zero cost, fully offline

The engine uses only the Python standard library: no network calls, API keys, or paid services. Combined with Gemma 4 running locally through Ollama, the whole recommendation pipeline runs on a laptop.

## Verification

- `tools/validate_skills.py` checks the agentskills.io naming rules, frontmatter limits, and script shebangs.
- `tests/test_decision_matrix.py` holds 11 tests covering ranking order, weight normalization, filters, JSON mode, and error handling.

## Limitations

The 15 properties are real West Lafayette complexes, but the rent, distance, and rating figures are **demo values** chosen for the hackathon, not live listings. Next steps would be ingesting real listing data, adding CityBus commute times, and letting users save weight profiles.
