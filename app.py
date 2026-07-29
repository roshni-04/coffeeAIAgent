"""
Streamlit front-end for the Coffee AI Agent.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import time

import streamlit as st

from coffee_agent.agent.coffee_agent import CoffeeAgent
from coffee_agent.config import get_settings
from coffee_agent.logging_config import setup_logging
from coffee_agent.schemas import AgentResponse, Intent

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Coffee AI Agent",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="expanded",
)

_INTENT_LABELS: dict[Intent, str] = {
    Intent.EXACT_MENU: "Exact menu match",
    Intent.COMPLEX_ORDER: "Multi-item order",
    Intent.PREFERENCE: "Dietary / preference constraint",
    Intent.RECOMMENDATION: "Open-ended recommendation",
}

EXAMPLES = [
    "Latte",
    "Large Mocha with oat milk",
    "2 Large Oat Milk Lattes and a Croissant for 3 people",
    "I have a meeting in 10 minutes. Something strong but quick.",
    "Something cold and sweet",
    "Birthday coffee for my friend",
    "I am lactose intolerant",
    "I didn't sleep yesterday",
    "Surprise me",
    "Give me the healthiest option",
]

CUSTOM_CSS = """
<style>
    #MainMenu, footer, header {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", -apple-system, sans-serif;
    }

    .app-header {
        border-bottom: 1px solid #2a2a2a;
        padding-bottom: 1.1rem;
        margin-bottom: 1.6rem;
    }
    .app-header h1 {
        font-size: 1.65rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-bottom: 0.15rem;
        color: #f2ece4;
    }
    .app-header p {
        color: #9c9284;
        font-size: 0.92rem;
        margin: 0;
    }

    .result-card {
        background: #1c1a17;
        border: 1px solid #322d27;
        border-left: 3px solid #c08a4e;
        border-radius: 6px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.9rem;
    }
    .result-card .item-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f2ece4;
    }
    .result-card .item-meta {
        color: #9c9284;
        font-size: 0.85rem;
        margin-top: 0.15rem;
    }

    .intent-badge {
        display: inline-block;
        font-size: 0.72rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #c08a4e;
        border: 1px solid #4a3c28;
        border-radius: 3px;
        padding: 0.15rem 0.5rem;
        margin-bottom: 0.7rem;
    }

    .trace-row {
        border-bottom: 1px solid #2a2724;
        padding: 0.55rem 0;
        font-size: 0.85rem;
    }
    .trace-row:last-child { border-bottom: none; }
    .trace-step {
        color: #c08a4e;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .trace-tool {
        color: #6f6659;
        font-size: 0.75rem;
    }

    div[data-testid="stTextArea"] textarea {
        font-size: 0.95rem;
    }
</style>
"""


@st.cache_resource(show_spinner=False)
def load_agent() -> CoffeeAgent:
    settings = get_settings()
    setup_logging(level=settings.log_level, json_output=settings.log_json)
    return CoffeeAgent(settings=settings)


def render_result(response: AgentResponse, elapsed_s: float) -> None:
    st.markdown(f'<span class="intent-badge">{_INTENT_LABELS[response.intent]}</span>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Estimated prep time", f"{response.total_time_min:g} min")
    col2.metric("Estimated total", f"Rs {response.total_price_inr:g}")
    col3.metric("Agent confidence", f"{response.confidence * 100:.0f}%")

    st.markdown("##### Order breakdown")
    for item in response.items:
        modifiers = f" &middot; {', '.join(item.modifiers)}" if item.modifiers else ""
        st.markdown(
            f"""
            <div class="result-card">
                <div class="item-name">{item.quantity} &times; {item.name.title()}</div>
                <div class="item-meta">
                    {item.unit_time_min:g} min each{modifiers} &middot;
                    Rs {item.unit_price_inr:g} each &middot; source: {item.source.replace('_', ' ')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Agent reasoning trace"):
        for step in response.trace:
            st.markdown(
                f"""
                <div class="trace-row">
                    <span class="trace-step">{step.step.replace('_', ' ').title()}</span>
                    <span class="trace-tool">({step.tool})</span><br/>
                    {step.detail}
                    <span style="float:right; color:#6f6659;">{step.elapsed_ms:.1f} ms</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.caption(f"Total agent turnaround: {elapsed_s * 1000:.1f} ms")


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Coffee AI Agent")
        st.caption("Recommendation & prep-time estimation agent")
        st.markdown("---")
        st.markdown("**Architecture**")
        st.markdown(
            "- Rule-based intent classifier\n"
            "- Deterministic menu lookup & pricing\n"
            "- Dietary constraint filter\n"
            "- LLM fallback for open-ended asks\n"
            "- Full reasoning trace per request"
        )
        st.markdown("---")
        st.markdown("**Try an example**")
        for example in EXAMPLES:
            if st.button(example, use_container_width=True, key=f"ex_{example}"):
                st.session_state["request_text"] = example

    st.markdown(
        """
        <div class="app-header">
            <h1>Coffee AI Agent</h1>
            <p>Describe an order or a preference in plain language - the agent will resolve it against
            the menu, apply modifiers, and estimate prep time and cost.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Preparing the agent..."):
        agent = load_agent()

    request_text = st.text_area(
        "Order or request",
        key="request_text",
        value=st.session_state.get("request_text", ""),
        placeholder="e.g. '2 large oat milk lattes and a croissant for 3 people'",
        height=90,
        label_visibility="collapsed",
    )

    submitted = st.button("Ask the agent", type="primary")

    if submitted and request_text.strip():
        with st.spinner("Reasoning..."):
            t0 = time.perf_counter()
            response = agent.handle(request_text)
            elapsed = time.perf_counter() - t0
        st.markdown("---")
        render_result(response, elapsed)
    elif submitted:
        st.warning("Please enter an order or request first.")


if __name__ == "__main__":
    main()
