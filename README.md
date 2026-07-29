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
