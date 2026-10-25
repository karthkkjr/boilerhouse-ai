import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

RANK_SCRIPT = Path(__file__).parent / "skills" / "decision-matrix-calculator" / "scripts" / "rank_apartments.py"

# Find a Hermes checkout without manual PYTHONPATH: ./vendor/hermes-agent (setup script) or ~/hermes-agent.
for _hermes in (Path(__file__).parent / "vendor" / "hermes-agent", Path.home() / "hermes-agent"):
    if _hermes.is_dir() and str(_hermes) not in sys.path:
        sys.path.insert(0, str(_hermes))

# Use Person A's Hermes brain if it's present; otherwise fall back to direct ranking.
try:
    from hermes_main import new_conversation, stream_reply_sync
    AGENT_READY = True
except Exception:
    AGENT_READY = False

st.set_page_config(page_title="BoilerHouse AI", page_icon="🏠")
st.title("🏠 BoilerHouse AI")
st.caption("Local AI housing assistant for Purdue · Gemma 4 + Hermes · fully offline")

with st.sidebar:
    st.header("Housing Preferences")
    price_w = st.slider("Price Importance", 0.0, 1.0, 0.5, key="price_weight")
    dist_w = st.slider("Distance Importance", 0.0, 1.0, 0.5, key="distance_weight")
    review_w = st.slider("Review Importance", 0.0, 1.0, 0.5, key="review_weight")
    budget = st.number_input("Max rent per bed ($/mo, 0 = no limit)", 0, 2000, 0, step=50)
    st.divider()
    st.caption("Agent: Hermes + Gemma 4" if AGENT_READY else "Agent offline: ranking with sliders only")


def rank_with_sliders(top=5):
    query = {"weights": {"price": price_w, "distance": dist_w, "rating": review_w}, "top": top}
    if budget:
        query["budget"] = budget
    proc = subprocess.run([sys.executable, str(RANK_SCRIPT), "--json", json.dumps(query)],
                          capture_output=True, text=True, timeout=30)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "error": proc.stderr.strip() or "ranking script failed"}


def format_ranking(result):
    if result.get("status") != "ok":
        return f"⚠️ {result.get('error', 'Unknown error')}"
    lines = [f"**{result['summary']}**", "", "| # | Apartment | Rent/bed | Distance | Rating | Score |",
             "|---|---|---|---|---|---|"]
    for r in result["results"]:
        raw = r["raw"]
        lines.append(f"| {r['rank']} | {r['name']} | ${raw['price_per_bed']} | {raw['distance_mi']} mi "
                     f"| {raw['rating']} | {r['score']} |")
    lines.append("\n_Demo data: verify current rent with each property._")
    return "\n".join(lines)


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content":
        "Hi! Tell me what you're looking for: budget, how close to campus, bedrooms, or must-have "
        "amenities like a gym. You can also adjust the sliders on the left."}]
    if AGENT_READY:
        st.session_state.conversation = new_conversation()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

prompt = st.chat_input("Tell me what you're looking for...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        if AGENT_READY:
            note = (f"\n\n(Sidebar weights: price={price_w}, distance={dist_w}, rating={review_w}"
                    + (f", budget=${budget}/bed" if budget else "") + ")")
            conv = st.session_state.conversation
            conv.append({"role": "user", "content": prompt + note})
            thinking_slot = st.expander("🧠 Thinking", expanded=False).empty()
            answer_slot = st.empty()
            thinking, answer = "", ""
            try:
                for kind, text in stream_reply_sync(conv):
                    if kind == "thinking":
                        thinking += text
                        thinking_slot.markdown(thinking)
                    elif kind == "tool":
                        st.caption("🔧 " + text)
                    else:
                        answer += text
                        answer_slot.markdown(answer)
                if not (conv and conv[-1].get("role") == "assistant"):
                    conv.append({"role": "assistant", "content": answer})
            except Exception as e:
                answer = f"⚠️ Agent error: {e}\n\n" + format_ranking(rank_with_sliders())
                answer_slot.markdown(answer)
        else:
            answer = format_ranking(rank_with_sliders())
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
