# BoilerHouse AI one-command setup (Windows PowerShell)
Write-Host "== BoilerHouse AI setup =="
if (-not (Test-Path venv)) { python -m venv venv }
. .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

if (Get-Command ollama -ErrorAction SilentlyContinue) {
    ollama pull gemma4:e2b
} else {
    Write-Warning "Ollama not found. Install from https://ollama.com/download then run: ollama pull gemma4:e2b"
    Write-Warning "The app still runs in ranking-only mode without it."
}

if (-not (Test-Path vendor\hermes-agent)) {
    git clone --depth 1 https://github.com/NousResearch/hermes-agent vendor\hermes-agent
    if ($LASTEXITCODE -ne 0) { Write-Warning "Hermes clone failed; app will run without the agent." }
}
if (Test-Path vendor\hermes-agent\pyproject.toml) { pip install -e vendor\hermes-agent -q }
elseif (Test-Path vendor\hermes-agent\requirements.txt) { pip install -r vendor\hermes-agent\requirements.txt -q }

python tools\validate_skills.py | Out-Null
python -m unittest discover -s tests 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "Skill checks: PASS" } else { Write-Warning "Skill checks failed - run: python -m unittest discover -s tests -v" }
Write-Host "Done. Start the app with:  streamlit run app.py"
