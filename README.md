# BoilerHouse AI

[![tests](https://github.com/karthkkjr/boilerhouse-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/karthkkjr/boilerhouse-ai/actions/workflows/tests.yml)

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

## Quick start (any laptop)

**Prerequisites:** Python 3.11+, Git, and (for the AI agent) [Ollama](https://ollama.com/download).

```bash
git clone https://github.com/karthkkjr/boilerhouse-ai
cd boilerhouse-ai
./setup.sh            # macOS / Linux / Git Bash
# .\setup.ps1        # Windows PowerShell
streamlit run app.py
```

The setup script creates a venv, installs dependencies, pulls `gemma4:e2b`, clones Hermes Agent into `vendor/`, and runs the test suite. Every optional step warns instead of failing.

**What runs where:**

| Your laptop has | You get |
|---|---|
| Python only | Ranking UI: sliders + budget drive the decision engine directly |
| + Ollama with `gemma4:e2b` + Hermes | Full agent: natural-language chat, visible reasoning, tool calls |

The sidebar shows which mode is active.

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
