# BoilerHouse AI

**A fully local, open-source AI housing assistant for Purdue students.** Ask in plain English ("cheapest place near the engineering buildings with a gym") and BoilerHouse AI ranks West Lafayette apartments, explains *why* each one ranked where it did, and never sends your data to a cloud API.

Built at the Hello World Hacktoberfest Hack Day, West Lafayette, October 25, 2026.

## Capabilities

- **Natural-language housing search.** Describe your priorities and constraints; the agent turns them into a structured query.
- **Weighted decision matrix.** Scores apartments on rent, distance to Purdue's Engineering Mall, and resident rating, with weights you control ("I'm broke" weights price heavily; "I want to walk to class" weights distance).
- **Hard filters.** Budget, max distance, minimum rating, bedroom count, CityBus access, and required amenities (gym, pool, furnished, pet-friendly, shuttle, ...).
- **Explainable results.** Every recommendation shows how many points rent, distance, and rating each contributed, and every excluded apartment comes with a reason.
- **Side-by-side comparison.** "Compare Hub and Rise" returns both properties with the best option on each criterion.
- **Visible reasoning.** Gemma 4's thinking trace streams separately from its answer, so you can watch the agent decide.
- **Zero cost, fully offline.** Local model, local data, Python standard-library skill scripts. No API keys.

## Architecture

```
Streamlit UI (app.py)
   └─> Hermes Agent (hermes_main.py)   gemma4:e2b via Ollama, 64K context
          └─> skill_bridge.py          exposes skills as 2 tools
                 └─> skills/decision-matrix-calculator/
                        ├─ rank_apartments.py     weighted ranking → JSON
                        └─ lookup_apartments.py   search / compare → JSON
```

`main.py` is a lighter fallback brain that uses the Ollama SDK directly, without Hermes.

## Open-source stack

| Component | Role |
|---|---|
| [Gemma 4](https://ai.google.dev/gemma) (E2B) | Open-weight model with native thinking mode |
| [Ollama](https://ollama.com) | Local inference server |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Agent orchestration and tool calling |
| [Agent Skills](https://agentskills.io) | Open standard for packaging agent capabilities |
| [Streamlit](https://streamlit.io) | Chat UI |

## Quick start

```bash
# 1. Model
ollama pull gemma4:e2b

# 2. Python deps
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Sanity-check the skill (no model needed)
python tools/validate_skills.py
python -m unittest tests/test_decision_matrix.py
python skills/decision-matrix-calculator/scripts/rank_apartments.py --budget 900 --top 3

# 4. Run the app
streamlit run app.py
```

Hermes Agent runs from its own git checkout. See `hermes_main.py` for setup.

## How the ranking works

Each criterion is min-max normalized across the apartments that pass your filters (rent and distance are inverted so 1.0 is always best), then combined as a weighted sum on a 0–100 scale. Full details: [docs/decision-engine.md](docs/decision-engine.md).

## Repository layout

```
skills/decision-matrix-calculator/   Agent Skill: SKILL.md, scripts/, references/
tools/validate_skills.py             agentskills.io spec validator
tests/                               unit tests for the skill scripts
docs/                                technical write-ups
app.py                               Streamlit UI
hermes_main.py / skill_bridge.py     agent brain + tool bridge
main.py                              plain-Ollama fallback brain
```

## Limitations

The 15 apartments are real West Lafayette complexes, but rent, distance, and rating figures are **demo values** for the hackathon, not live listings. Always verify with the property.

## Team

- **Person A:** Agent orchestration (Hermes, Ollama, Gemma 4)
- **Person B:** Decision engine and Agent Skills
- **Person C:** Streamlit UI

## License

MIT. See [LICENSE](LICENSE).
