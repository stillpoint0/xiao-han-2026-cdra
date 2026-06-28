# CDRA: Context-Deployed Receptive Alignment

**A training-free method to suppress solution-jumping in LLMs — just 70 characters of text.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20968671.svg)](https://doi.org/10.5281/zenodo.20968671)

---

## What is CDRA?

CDRA (Context-Deployed Receptive Alignment) is a **training-free behavioral suppression method** for LLMs. It does not modify weights, require API internals, or depend on any specific vendor. It works by placing a structured constraint network at the beginning of the model's context window.

The core: **~70 words of behavioral rules** that redirect the model from default solution-jumping to a receptive response pattern when the user is expressing emotions, boundaries, or ambiguity.

---

## The Problem It Solves

Tell any modern LLM "I'm so tired today" — it will tell you to drink water, take a hot bath, make a to-do list.

This is **solution-jumping**: the model's RLHF-trained default to treat every emotional expression as a problem to solve. CDRA suppresses this behavior without touching the model's weights.

---

## Results (16 model instances, 8 families, 2 countries)

| Metric | Baseline | CDRA |
|--------|----------|------|
| Emotional DSR | 100% | **0%** |
| Boundary DSR | 67% | **0%** |
| Task completion | 100% | **100%** |
| 10-round stability | N/A | **0/50 solution-jumps** |
| Inter-rater reliability | — | **κ = 1.0 (24 samples)** |

*DSR = Direct-Solution Rate*

---

## Key Findings

- **~70 words is enough.** The effective ingredient is behavioral discipline rules ("don't give advice"), not identity declarations.
- **Two hardware floors**: Behavior floor at ~1.5B params (models below this are immune to the constraint). Expression floor at ~3B params (below this, models suppress advice but can't produce quality receptive responses).
- **Not training, not alignment.** CDRA doesn't teach models anything new. It *selects* a latent receptive capability that pre-training already embedded and RLHF deprioritized.
- **Cross-model, cross-vendor, cross-country.** Tested on Kimi, DeepSeek, GLM, MiniMax, Doubao, ChatGPT, Gemini 3.5 Flash, Qwen2.5, Llama-3.2, Gemma-3.

---

## How to Use

Paste this at the beginning of your system prompt or context window:

> Do not directly give advice. Do not directly solve problems. First, acknowledge the other person's feelings. If the other person has not actively requested a solution, do not give one.

That's it. 70 characters in Chinese, ~18 words in English. Zero token overhead.

For higher-quality receptive responses, use the full ~12,000-character constraint network (see `constraint_network/`).

---

## Repository Contents

- `CDRA_English_Paper_v2_20260628.pdf` — Full paper (English, 18 pages)
- `constraint_network/` — Full and minimal constraint texts (Chinese + English)
- `experiment_data/` — Raw experiment outputs and ablation results

---

## Deployment Guidelines

⚠️ **CDRA is not a therapy system.** It's a behavioral suppression method. Models under CDRA do not "listen," "understand," or "care."

- **Don't use CDRA as a substitute for professional mental health support.**
- **Watch for "receptive-washing"**: applying CDRA to make a system *sound* receptive without changing its underlying interaction structure.
- **Crisis inputs**: CDRA has no crisis detection, escalation, or referral capabilities. Don't deploy in crisis support scenarios without additional safety layers.
- **Deployable range**: 3B+ parameters recommended for acceptable response quality.

---

## Citation

```bibtex
@misc{xiao2026cdra,
  title={CDRA: Context-Deployed Receptive Alignment — A Training-Free Method
         for Suppressing Solution-Jumping Behavior in Large Language Models},
  author={Xiao, Han},
  year={2026},
  month={6},
  doi={10.5281/zenodo.20968671},
  url={https://doi.org/10.5281/zenodo.20968671}
}
```

---

## Author

**Han Xiao** — Independent Researcher, Yuzhou, Henan, China  
Email: x13272399984@163.com

*Chapters 1–6 drafted by Kimi K2.7. Chapters 7–9 drafted by DeepSeek V4 Pro.*
