#!/usr/bin/env bash
# BoilerHouse AI one-command setup (macOS / Linux / Git Bash on Windows)
set -u
echo "== BoilerHouse AI setup =="
PY=$(command -v python3 || command -v python)
[ -d venv ] || "$PY" -m venv venv
if [ -f venv/bin/activate ]; then source venv/bin/activate; else source venv/Scripts/activate; fi
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

if command -v ollama >/dev/null 2>&1; then
  ollama pull gemma4:e2b || echo "WARN: could not pull gemma4:e2b (is Ollama running?)"
else
  echo "WARN: Ollama not found. Install from https://ollama.com/download then run: ollama pull gemma4:e2b"
  echo "      The app still runs in ranking-only mode without it."
fi

if [ ! -d vendor/hermes-agent ]; then
  git clone --depth 1 https://github.com/NousResearch/hermes-agent vendor/hermes-agent \
    || echo "WARN: Hermes clone failed; app will run without the agent."
fi
if [ -f vendor/hermes-agent/pyproject.toml ]; then pip install -e vendor/hermes-agent -q || echo "WARN: Hermes install failed"
elif [ -f vendor/hermes-agent/requirements.txt ]; then pip install -r vendor/hermes-agent/requirements.txt -q || echo "WARN: Hermes deps failed"
fi

python tools/validate_skills.py >/dev/null && python -m unittest discover -s tests >/dev/null 2>&1 \
  && echo "Skill checks: PASS" || echo "WARN: skill checks failed - run: python -m unittest discover -s tests -v"
echo "Done. Start the app with:  streamlit run app.py"
