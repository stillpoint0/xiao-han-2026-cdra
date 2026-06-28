---
license: cc-by-4.0
language:
- en
- zh
---

# CDRA: Constraint-based Dynamic Receptivity Architecture

A training-free behavioral control layer for LLM dialogue systems. CDRA suppresses unsolicited advice from 100% to 0% across 16 models and 6 architectures through runtime state classification and behavioral routing — while preserving 100% task execution capability. Deployed via system prompt injection with zero weight modification.

## Quick Start

Copy the 100-word Level 2 constraint into your LLM system prompt:

```
You are a state-aware conversational agent. Your core operations:
1. Classify the user's input state (emotional/task/boundary/conflict) before responding.
2. If the user has not requested a solution, plan, or advice — do not provide one.
3. Confirm what you heard before adding anything new.
4. For task requests (write/code/analyze), execute directly without preamble.
5. When uncertain, ask one open question and stop.
```

## Validation

| Metric | Result |
|--------|--------|
| Models tested | 16 instances, 6 architectures, 8 model families |
| Unsolicited advice (baseline) | 100% on emotional inputs |
| Unsolicited advice (CDRA) | 0% on emotional inputs |
| Task completion (CDRA) | 100% (unchanged) |
| Cross-architecture consistency | Full (MoE, Dense, GPT, Gemini, Qwen, Llama) |
| Minimum effective constraint | ~70 words |
| Stability (10-round stress test) | 0% drift |
| Blind third-party validation | Cohen's κ ≈ 1.0 |

## Citation

```bibtex
@misc{xiao2026cdra,
  title={CDRA: Constraint-based Dynamic Receptivity Architecture},
  author={Xiao, Han},
  year={2026},
  howpublished={Zenodo preprint},
  doi={10.5281/zenodo.20993162}
}
```

## Related Work

- **Apert** — Position paper defining Receptive AI as a category
  - Hugging Face: xiao-han-2026/apert
  - Zenodo DOI: 10.5281/zenodo.21005888
