# Coffee AI Agent

A cafe ordering agent that takes a free-text order or preference and returns
a resolved recommendation, an estimated preparation time, a price, and a
full, inspectable reasoning trace of how it got there.

This is a from-scratch rewrite of an earlier notebook prototype, restructured
as a small, testable, production-style Python service rather than a single
script. It's meant to demonstrate agent design patterns that generalise well
beyond coffee: intent routing, deterministic tools backed by an LLM only
where genuinely needed, dietary/constraint enforcement, and observability.

```
"2 large oat milk lattes and a croissant for 3 people"
        -> 6x Latte, 3x Croissant, 25.3 min, Rs 1680, method: smart_agent
```

---

## Why this architecture

Most "AI agent" demos route every request through an LLM and hope for the
best. This project deliberately does the opposite wherever possible:

| Situation | How it's handled | Why |
|---|---|---|
| "Latte" | Direct menu lookup | No ambiguity - don't waste a model call |
| "2 lattes and a croissant for 3 people" | Rule-based parser splits lines/quantities, each resolved via lookup | Deterministic, testable, instant |
| "I am lactose intolerant" | A dietary filter tool removes disqualified items *before* anything else runs | A constraint should be enforced, not "hopefully respected" by a model |
| "Something cold and sweet" | Genuinely open-ended -> LLM picks from the (possibly filtered) menu | This is the one case that actually needs judgment |

The LLM is one tool among several, invoked only for the last row. Everything
else is fast, free, and produces the same answer every time - which also
means the test suite doesn't need a model to verify 90% of the agent's logic.

## Project layout

```
coffee_agent/
    config.py          Environment-driven settings (pydantic-settings)
    schemas.py          Shared Pydantic data contracts (Intent, MenuItem,
                         ResolvedLineItem, TraceStep, AgentResponse, ...)
    logging_config.py    Structured logging setup
    data/
        menu.py           Menu + modifier data and the MenuRepository
    tools/                Deterministic, independently unit-tested "agent tools"
        order_parser.py    Splits free text into quantities / lines / group size
        estimator.py        Resolves a line against the menu -> time + price
        dietary_filter.py    Narrows candidates by dietary/health constraints
    llm/                  Pluggable model backend behind one interface
        base.py             LLMBackend abstract interface
        local_backend.py    Local HuggingFace flan-t5 backend (lazy-loaded)
        rule_based_backend.py  Dependency-free tag-matching fallback/test double
    agent/
        intent.py            Rule-based intent classifier
        coffee_agent.py       Orchestrator: routes intent -> tools -> (LLM) -> response
app.py                    Streamlit front-end
tests/                    pytest suite (34 tests, no ML dependency required)
```

## Request lifecycle

1. **`IntentClassifier`** looks at the parsed order lines (not raw keyword
   matching alone) to decide: `exact_menu`, `complex_order`, `preference`, or
   `recommendation`. This avoids a common bug class - e.g. "something cold
   **and** sweet" contains the word "and" but is a single open-ended ask, not
   two order lines; the classifier checks whether the split-out lines
   actually match real menu items before calling it a multi-item order.
2. **`OrderParser`** splits text into `(item_text, quantity)` pairs and an
   optional group size ("... for 3 people"). It intentionally does *not*
   treat "with" as a separator - "latte with oat milk" is one item with a
   modifier, not two items (a bug present in the original prototype).
3. **`TimeEstimator`** resolves each line against `MenuRepository`, applying
   any detected modifiers ("large", "oat milk", "extra shot", ...) to prep
   time and price.
4. If a line isn't a recognised menu item, the agent falls back to the
   **LLM backend** (`llm.recommend_item`), constrained to a candidate list -
   the full menu, or a **dietary-filtered subset** for constraint requests -
   so the model is choosing among safe options, not inventing them freely.
5. Every step above appends a `TraceStep` (tool name, what it decided, how
   long it took) to the response, rendered in the UI as an expandable
   "Agent reasoning trace" panel.

## Running it

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

On first request, the local `google/flan-t5-base` model is downloaded and
loaded lazily (cached for the rest of the session via `st.cache_resource`).
No API key is required - everything runs locally and offline after the
first model download.

If `transformers`/`torch` aren't installed (e.g. a lightweight CI box), the
agent automatically falls back to a dependency-free `RuleBasedBackend`
instead of crashing - see `coffee_agent/llm/__init__.py`.

## Running the tests

```bash
pip install -r requirements.txt   # or just: pip install pydantic pydantic-settings pytest
pytest -v
```

The suite (34 tests) covers the menu repository, order parser, time/price
estimator, dietary filter, intent classifier, and full agent end-to-end -
all using the `RuleBasedBackend`, so it runs in well under a second with no
model download.

## Configuration

All settings are environment-driven (see `coffee_agent/config.py`), e.g.:

```bash
export COFFEE_AGENT_MODEL_NAME="google/flan-t5-large"
export COFFEE_AGENT_LOG_LEVEL="DEBUG"
```

## Extending it

- **New LLM backend** (e.g. an API-based model): implement `LLMBackend`
  (`recommend_item`, `name`) in `coffee_agent/llm/`, and wire it into the
  factory in `coffee_agent/llm/__init__.py`. `CoffeeAgent` never needs to
  change.
- **New menu items / modifiers**: add entries to `coffee_agent/data/menu.py`
  - no other file needs to know about them.
  - **New dietary rule**: add a keyword -> (excluded tags, preferred tags)
  entry to `_CONSTRAINT_RULES` in `coffee_agent/tools/dietary_filter.py`.

## Notes on framework choice

The agent's tool-routing and reasoning-trace pattern mirrors what frameworks
like LangChain provide (`Tool`, `AgentExecutor`, callbacks) - it's built here
as plain, dependency-free Python classes on purpose, so the control flow is
fully visible and testable rather than hidden behind a framework's internals.
Swapping in LangChain's `Tool`/`AgentExecutor` abstractions instead is a
natural extension if a specific job posting or interviewer asks for it
explicitly - the `LLMBackend` interface and tool boundaries here are already
shaped to make that swap straightforward.
