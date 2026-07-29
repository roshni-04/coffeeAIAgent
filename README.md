# Coffee AI Agent — LLM-Driven Queue and Recommendation System

> **Live interactive demo:** run the fully functional Colab notebook prototype below.

An intelligent, hybrid AI agent built with PyTorch and Hugging Face (`google/flan-t5-base`) that processes unstructured natural language coffee orders, handles dietary preferences, and calculates preparation time and pricing through deterministic tool execution.

---

## Project overview

Most AI demos route every request through an LLM and hope for accurate results. This project uses a hybrid tool-calling architecture instead:

- **The LLM (`flan-t5-base`)** acts as the decision-maker, handling intent classification, entity extraction, dietary filtering, and open-ended recommendations from unstructured text.
- **Deterministic Python tools** handle time and price calculations, avoiding the arithmetic errors that small language models are prone to.

The model decides *what* the customer wants; the code computes the numbers.

---

## Key features

- **Natural language order parsing** — extracts item names, quantities, modifiers (e.g. "extra hot", "oat milk"), and group sizes from conversational input.
- **Intent-based routing** — classifies each request into `exact_menu`, `complex_order`, `preference`, or `recommendation`, and executes the corresponding pipeline.
- **Local inference, no API cost** — runs entirely offline using open-source models via Hugging Face `transformers` and PyTorch.
- **Interactive UI with full observability** — an `ipywidgets` dashboard with example prompts, confidence scoring, and a step-by-step reasoning trace for every response.

---

## How it works

User input
-> Intent classification (LLM)
-> exact_menu / complex_order -> entity extraction (LLM) -> price and time calculation (Python)
-> preference / recommendation -> constraint filtering (LLM) -> recommendation engine (LLM)
-> Agent response + step-by-step reasoning trace


---

## Quickstart: Google Colab demo

The interactive prototype runs in Google Colab with no paid API keys required.

1. Click the **Open in Colab** badge above.
2. Select **Runtime > Run all**.
3. The notebook downloads `google/flan-t5-base`, loads the PyTorch backend, and launches the interactive `ipywidgets` interface in the final cell.

---

## Project status and roadmap

- [x] **Phase 1 — Colab interactive prototype** (complete)
  - End-to-end LLM intent classification and entity extraction pipeline
  - Interactive UI with live reasoning traces and example prompts
- [ ] **Phase 2 — Modular service architecture** (in progress)
  - Refactoring single-script logic into separate modules (`schemas.py`, `tools/`, `llm/`, `agent/`)
  - Unit test suite using `pytest` with mock backends for fast CI
- [ ] **Phase 3 — Web deployment** (planned)
  - Containerized FastAPI backend with a Streamlit front end

---

## Tech stack

- **Language:** Python 3.10+
- **Deep learning framework:** PyTorch (`torch`)
- **Model inference:** Hugging Face `transformers` (`google/flan-t5-base`)
- **Interface:** `ipywidgets`, `IPython.display`

---

## 📚 Acknowledgments & References

This project leverages open-source models, frameworks, and tools:

* **Language Model:** Powered by Google's [`google/flan-t5-base`](https://huggingface.co/google/flan-t5-base) hosted on Hugging Face.
* **Deep Learning Framework:** Built using [PyTorch](https://pytorch.org/) and Hugging Face [Transformers](https://huggingface.co/docs/transformers/index).
* **UI & Interactivity:** Interface built with [IPyWidgets](https://ipywidgets.readthedocs.io/) inside Google Colab.
* **Design Pattern:** Architecture inspired by deterministic tool-calling and hybrid LLM agent design patterns.
