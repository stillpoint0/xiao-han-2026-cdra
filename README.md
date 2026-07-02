---
license: cc-by-4.0
language:
- en
- zh
---

# CDRA: Constraint-based Dynamic Receptivity Architecture

A training-free behavioral control layer for LLM dialogue systems. CDRA suppresses unsolicited advice from 100% to 0% across 16 models and 6 architectures through runtime state classification and behavioral routing — while preserving 100% task execution capability. Deployed via system prompt injection with zero weight modification.

## Quick start

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

## Files

- `CDRA_English_Paper_v2_20260628.pdf` — Formal paper
- `CDRA_Experimental_Report_EN_20260628.pdf` — Experimental report
- `CDRA_Graded_Constraints_EN_20260628.pdf` — Graded constraint library
- `CDRA_MVP_Behavior_OS_EN_20260628.pdf` — Minimum viable behavior OS
- `CDRA_vs_Prompt_Engineering_EN_20260628.pdf` — Comparison with prompt engineering
- `README_Zenodo_Package_20260628.pdf` — Package guide
- `replication/` — One-click replication kit (`run_cdra.py`)

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

## Related work

- Apert: [10.5281/zenodo.21005888](https://doi.org/10.5281/zenodo.21005888)
- Reception Science: [10.5281/zenodo.21078023](https://doi.org/10.5281/zenodo.21078023)
- Unloading Hypothesis: [10.5281/zenodo.21101755](https://doi.org/10.5281/zenodo.21101755)

**License:** CC-BY 4.0
