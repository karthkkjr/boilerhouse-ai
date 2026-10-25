"""BoilerHouse AI - the agent brain (Person A), orchestrated by Hermes.

Hermes (AIAgent) runs the agent loop on local Ollama gemma4:e2b and calls
Person B's decision-matrix-calculator skill through two Hermes tools:
rank_apartments and lookup_apartments (see skill_bridge.py).

Run `python hermes_main.py` (from the activated Hermes checkout) to chat.
Person C imports `new_conversation` and `stream_reply_sync` from here.
"""
import json
import os
import queue
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# Where you cloned Hermes (default: C:\Users\<you>\hermes-agent) so `run_agent` can be imported.
sys.path.append(os.environ.get("HERMES_REPO", str(Path.home() / "hermes-agent")))

# Keep Hermes settings inside this project folder instead of your user profile.
os.environ.setdefault("HERMES_HOME", str(HERE / ".hermes"))
_home = Path(os.environ["HERMES_HOME"])
_home.mkdir(exist_ok=True)
# Hermes refuses to run tools with less than 64K context, so ask Ollama for 64K.
# tool_search off = give the model our tools directly (small models get lost otherwise).
(_home / "config.yaml").write_text(
    "model:\n  ollama_num_ctx: 65536\n"
    "tools:\n  tool_search:\n    enabled: off\n"
)

from run_agent import AIAgent  # noqa: E402  (must come after HERMES_HOME is set)
from tools.registry import registry  # noqa: E402

from skill_bridge import lookup_apartments, rank_apartments, skill_description  # noqa: E402

MODEL = "gemma4:e2b"
OLLAMA_URL = "http://localhost:11434/v1"

# --- Person B's skill as Hermes tools -------------------------------------
RANK_SCHEMA = {
    "name": "rank_apartments",
    "description": skill_description()
    or "Rank Purdue / West Lafayette apartments with a weighted decision matrix.",
    "parameters": {
        "type": "object",
        "properties": {
            "budget": {"type": "number", "description": "Max monthly rent per bed in USD."},
            "max_distance": {"type": "number", "description": "Max miles to the Purdue Engineering Mall."},
            "min_rating": {"type": "number", "description": "Minimum rating, 0 to 5."},
            "bedrooms": {"type": "integer", "description": "Required bedroom count, e.g. 2."},
            "require_bus": {"type": "boolean", "description": "Only places with CityBus access."},
            "amenities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Required amenities: gym, pool, rooftop, furnished, study-rooms, laundry, parking, parking-garage, shuttle, pet-friendly.",
            },
            "weights": {
                "type": "object",
                "description": "How much the student cares about each criterion. Cheap: price 0.6. Close to class: distance 0.6. Best reviewed: rating 0.6.",
                "properties": {
                    "price": {"type": "number"},
                    "distance": {"type": "number"},
                    "rating": {"type": "number"},
                },
            },
            "top": {"type": "integer", "description": "How many results to return (default 3)."},
        },
    },
}

LOOKUP_SCHEMA = {
    "name": "lookup_apartments",
    "description": "Compare specific West Lafayette apartments side by side (e.g. compare='hub,rise') or look one up by name (e.g. name='muinzer').",
    "parameters": {
        "type": "object",
        "properties": {
            "compare": {"type": "string", "description": "Comma list of apartment names, e.g. 'hub,rise'."},
            "name": {"type": "string", "description": "One apartment name, e.g. 'muinzer'."},
        },
    },
}


def _rank_handler(args, **kwargs):
    query = dict(args)
    query.setdefault("top", 3)
    return json.dumps(rank_apartments(query))


def _lookup_handler(args, **kwargs):
    return json.dumps(lookup_apartments(compare=args.get("compare"), name=args.get("name")))


registry.register(name="rank_apartments", toolset="boilerhouse", schema=RANK_SCHEMA, handler=_rank_handler)
registry.register(name="lookup_apartments", toolset="boilerhouse", schema=LOOKUP_SCHEMA, handler=_lookup_handler)

SYSTEM_PROMPT = """You are the BoilerHouse AI, a localized housing assistant for Purdue University students.

Workflow:
1. Ask the student for their housing preferences: monthly budget per bed, how much they care about distance to the Engineering Mall, and how much they care about ratings. Also ask about bedrooms or must-have amenities if they mention them. Do not recommend anything yet.
2. Once you know the budget and priorities, call rank_apartments with the budget, any filters, and weights for price, distance and rating.
3. Read the tool result. If "status" is "ok": quote the "summary", list the "results" in order with rent per bed, distance and rating, and explain why the top pick won using "weighted_contribution". If "status" is "error": tell the student the "error" message and suggest relaxing their budget, distance, rating or bedroom filters.
4. If the student asks to compare specific apartments, or asks about one by name, call lookup_apartments.

Rules:
- Never invent apartments, prices, distances or ratings. Only use what the tools return.
- Remind the student that prices are demo values and to confirm current rent with the property.
- If the student asks about something unrelated to Purdue housing, politely steer back to housing.
- Keep answers short and clear."""


def _make_agent(on_text, on_thinking, on_tool):
    return AIAgent(
        model=MODEL,
        base_url=OLLAMA_URL,
        provider="custom",  # Hermes' OpenAI-compatible provider, which passes num_ctx to Ollama
        api_key="ollama",  # Ollama ignores it, but Hermes wants a value
        quiet_mode=True,  # no spinners/progress bars, so Streamlit output stays clean
        enabled_toolsets=["boilerhouse"],  # only Person B's tools, no terminal/web/file tools
        ephemeral_system_prompt=SYSTEM_PROMPT,
        skip_context_files=True,
        skip_memory=True,
        max_iterations=6,
        stream_delta_callback=on_text,
        reasoning_callback=on_thinking,
        tool_start_callback=on_tool,
    )


def new_conversation():
    """An empty conversation. Hermes adds the system prompt itself."""
    return []


def stream_reply_sync(messages):
    """Answer the last user message in `messages`.

    Yields (kind, text) where kind is "thinking", "answer" or "tool", and
    replaces `messages` with Hermes' full updated history when done.
    """
    user_message = messages[-1]["content"]
    history = messages[:-1]
    events = queue.Queue()
    done = object()

    def run():
        try:
            agent = _make_agent(
                on_text=lambda text: text and events.put(("answer", text)),
                on_thinking=lambda text: text and events.put(("thinking", text)),
                on_tool=lambda call_id, name, args: events.put(("tool", f"Calling {name} with {args}")),
            )
            result = agent.run_conversation(user_message=user_message, conversation_history=history)
            messages[:] = result["messages"]
            if not result.get("final_response"):
                events.put(("answer", "(no answer - check that Ollama is running)"))
        except Exception as e:
            events.put(("answer", f"Error: {e}"))
        finally:
            events.put(done)

    threading.Thread(target=run, daemon=True).start()
    while (event := events.get()) is not done:
        yield event


def main():
    messages = new_conversation()
    print("BoilerHouse AI (Hermes) - type 'quit' to exit\n")
    while True:
        user = input("You: ").strip()
        if user.lower() in ("quit", "exit"):
            break
        messages.append({"role": "user", "content": user})
        last = None
        for kind, text in stream_reply_sync(messages):
            if kind != last:
                print({"thinking": "\n[thinking] ", "answer": "\nAI: ", "tool": "\n[tool] "}[kind], end="")
                last = kind
            print(text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    main()
