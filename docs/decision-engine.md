Decision Engine and Agent Skills

BoilerHouse AI’s recommendations come from a weighted multi-criteria decision matrix. It’s packaged as an agentskills.io-compliant skill, so our local Hermes Agent running Gemma 4 can discover and run it on its own.

How it works

Each apartment is scored on three criteria: monthly rent per bed, distance to Purdue’s Engineering Mall, and resident rating. We min-max normalize each criterion so that 1.0 is always “best” (rent and distance are inverted). The final score is a weighted sum on a 0–100 scale.

The agent converts natural language into weights. “I’m broke” shifts weight toward price. “I want to walk to class” shifts it toward distance. Hard constraints such as budget, bedroom count, required amenities, and CityBus access filter candidates out before scoring.

Why it’s explainable

The output doesn’t stop at a ranking. Every result includes its raw values, its normalized values, and a weighted_contribution breakdown, so the agent can explain why one place beat another. Every filtered-out property comes with a reason, such as “price $1,050 > budget $900,” so users understand why a place they expected is missing.

Built to the open standard
Spec-compliant skill: the decision-matrix-calculator/ directory follows the agentskills.io layout (SKILL.md, scripts/, references/), with a keyword-dense description for semantic routing.
Progressive disclosure: the agent loads only the skill’s name and description at startup. It reads the full instructions and runs the scripts only when a housing question comes in.
Strict CLI contract: scripts write clean JSON to stdout, put human-readable logs on stderr, and return structured errors with exit code 2, so the agent never has to parse noise.
LLM-friendly input: a single --json argument accepts every parameter, which is more reliable for a local model than assembling CLI flags.
Zero cost, fully offline

The engine uses only the Python standard library and has no network calls, API keys, or paid services. Combined with Gemma 4 running locally through Ollama, the entire recommendation pipeline runs on a laptop.

Verified

We wrote a spec validator, tools/validate_skills.py, that checks the naming rules, the frontmatter limits, and the script shebangs. An 11-test suite covers ranking order, weight normalization, filters, JSON mode, and error handling.

Limitations and next steps

The 15 West Lafayette properties are real complexes, but the rent, distance, and rating figures are demo values chosen for the hackathon, not live listings. Next steps would be ingesting real listing data (the Snowflake integration path), adding commute time by CityBus route, and letting users save weight profiles.

