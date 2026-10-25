"""BoilerHouse AI - the agent brain (Person A).

Run `python main.py` to chat in the terminal.
Person C imports `stream_reply_sync` (or `stream_reply`) from here for Streamlit.
"""
import asyncio
import json

from ollama import AsyncClient

MODEL = "gemma4:e2b"
OPTIONS = {"num_ctx": 8192}  # bigger context so the apartment data is not cut off

# Person B's skill (skills/decision-matrix-calculator), run through skill_bridge.py.
from skill_bridge import lookup_apartments as _lookup, rank_apartments as _rank


def rank_apartments(
    budget: float,
    weight_price: float,
    weight_distance: float,
    weight_rating: float,
    amenities: str = "",
    bedrooms: int = 0,
) -> str:
    """Rank Purdue / West Lafayette apartments with a weighted decision matrix and return the top 3.

    Args:
        budget: Maximum monthly rent per bed in dollars.
        weight_price: How much the student cares about low rent, 0 to 1.
        weight_distance: How much the student cares about being close to the Engineering Mall, 0 to 1.
        weight_rating: How much the student cares about high ratings, 0 to 1.
        amenities: Comma list of required amenities, e.g. "gym,furnished". Empty if none.
        bedrooms: Required bedroom count, or 0 if the student did not say.

    Returns:
        JSON with status, summary and the ranked results.
    """
    query = {
        "budget": budget,
        "weights": {"price": weight_price, "distance": weight_distance, "rating": weight_rating},
        "amenities": [a.strip() for a in amenities.split(",") if a.strip()],
        "top": 3,
    }
    if bedrooms:
        query["bedrooms"] = bedrooms
    return json.dumps(_rank(query))


def lookup_apartments(compare: str = "", name: str = "") -> str:
    """Compare apartments side by side or look one up by name.

    Args:
        compare: Comma list of apartment names to compare, e.g. "hub,rise". Empty if not comparing.
        name: One apartment name to look up, e.g. "muinzer". Empty if not used.

    Returns:
        JSON with the apartment details.
    """
    return json.dumps(_lookup(compare=compare or None, name=name or None))


TOOLS = {"rank_apartments": rank_apartments, "lookup_apartments": lookup_apartments}

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


def new_conversation():
    """A fresh message list that starts with the system prompt."""
    return [{"role": "system", "content": SYSTEM_PROMPT}]


async def stream_reply(messages):
    """Stream one assistant turn. Yields (kind, text) where kind is
    "thinking", "answer" or "tool". Appends everything to `messages`."""
    client = AsyncClient()
    while True:
        thinking, content, tool_calls = "", "", []
        stream = await client.chat(
            model=MODEL,
            messages=messages,
            tools=list(TOOLS.values()),
            options=OPTIONS,
            stream=True,
            think=True,
        )
        async for chunk in stream:
            if chunk.message.thinking:
                thinking += chunk.message.thinking
                yield "thinking", chunk.message.thinking
            if chunk.message.content:
                content += chunk.message.content
                yield "answer", chunk.message.content
            if chunk.message.tool_calls:
                tool_calls.extend(chunk.message.tool_calls)

        messages.append(
            {"role": "assistant", "content": content, "thinking": thinking, "tool_calls": tool_calls}
        )
        if not tool_calls:
            return

        for call in tool_calls:
            name, args = call.function.name, call.function.arguments
            yield "tool", f"Calling {name} with {args}"
            fn = TOOLS.get(name)
            try:
                result = str(fn(**args)) if fn else f"Unknown tool {name}"
            except Exception as e:
                result = f"Tool error: {e}"
            messages.append({"role": "tool", "tool_name": name, "content": result})
        # loop again so the model can present the tool result


def stream_reply_sync(messages):
    """Same as stream_reply, but usable from normal (non-async) code like Streamlit."""
    loop = asyncio.new_event_loop()
    agen = stream_reply(messages)
    try:
        while True:
            yield loop.run_until_complete(agen.__anext__())
    except StopAsyncIteration:
        pass
    finally:
        loop.close()


async def main():
    messages = new_conversation()
    print("BoilerHouse AI (type 'quit' to exit)\n")
    while True:
        user = input("You: ").strip()
        if user.lower() in ("quit", "exit"):
            break
        messages.append({"role": "user", "content": user})
        last = None
        async for kind, text in stream_reply(messages):
            if kind != last:
                print({"thinking": "\n[thinking] ", "answer": "\nAI: ", "tool": "\n[tool] "}[kind], end="")
                last = kind
            print(text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
