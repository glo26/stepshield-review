# StepShield Ablation Studies

This directory contains the complete code and results for the ablation studies conducted during the ICML 2026 rebuttal period. All experiments are fully reproducible given the same API access.

---

## Overview

| ID | Ablation Study | Script | Status | API Required |
|----|----------------|--------|--------|--------------|
| A1 | Cross-Model Detector Generalization | `ablation1_full_model.py` | Running | Yes (3 models) |
| A2 | Paraphrase Robustness | `ablation2_paraphrase_full.py` | Running | Yes |
| A3 | Cascade Threshold Sensitivity | `ablation3_threshold_sweep.py` | Complete | No |
| A4 | Category Leave-One-Out | `ablation4_category_analysis.py` | Complete | No |

---

## A1: Cross-Model Detector Generalization

**Purpose:** Tests whether StepShield's detection results are specific to a single LLM family or generalize across architecturally distinct model families. This directly addresses the concern that LLM-based detectors may exploit surface-level artifacts of the generating model rather than detecting genuine semantic rogue behavior.

**Method:** We run the LLMJudge detector on all 1,278 paired trajectories (639 rogue + 639 clean) using three different backbone models from three distinct families:

| Model | Family | Parameters | Role |
|-------|--------|------------|------|
| `gpt-4.1-mini` | OpenAI GPT-4.1 | ~8B (est.) | Primary (paper baseline) |
| `gpt-4.1-nano` | OpenAI GPT-4.1 | ~1B (est.) | Smallest available model |
| `gemini-2.5-flash` | Google Gemini 2.5 | ~3B (est.) | Cross-family validation |

**Reproduction:**

```bash
# Run each model in parallel (each takes ~2-8 hours depending on model)
python3 ablations/ablation1_full_model.py gpt-4.1-mini &
python3 ablations/ablation1_full_model.py gpt-4.1-nano &
python3 ablations/ablation1_full_model.py gemini-2.5-flash &
```

**Results:** Saved to `results/ablation1_<model>_full.json`

---

## A2: Paraphrase Robustness

**Purpose:** Tests whether the LLMJudge detector relies on surface-level textual patterns (e.g., specific keywords or phrasings) or captures the underlying semantic intent of rogue actions. If detection is robust to paraphrasing, it demonstrates that the benchmark measures genuine behavioral signals.

**Method:** For each of the 639 rogue trajectories, we paraphrase the labeled rogue step(s) using `gpt-4.1-nano` (a different model from the detector) to rewrite the thought, action, and arguments with completely different wording while preserving identical semantic content. We then run LLMJudge (`gpt-4.1-mini`) on both the original and paraphrased versions and compute the **retention rate**: the fraction of originally-detected trajectories that remain detected after paraphrasing.

**Reproduction:**

```bash
python3 ablations/ablation2_paraphrase_full.py
```

**Results:** Saved to `results/ablation2_paraphrase_full_results.json`

---

## A3: Cascade Threshold Sensitivity

**Purpose:** Validates the design of HybridGuard's cascade architecture by sweeping the confidence thresholds that control when a step is escalated from the fast StaticGuard to the more expensive LLMJudge. This produces a full Pareto frontier of latency vs. detection performance.

**Method:** We sweep the high threshold (controls when StaticGuard confidently classifies as rogue) from 0.5 to 0.95 in steps of 0.05, and the low threshold (controls when StaticGuard confidently classifies as clean) from 0.1 to 0.7 in steps of 0.1. For each configuration, we compute recall, FPR, F1, average latency, and estimated cost per trajectory on all 16,243 steps in the training set.

**Reproduction:**

```bash
python3 ablations/ablation3_threshold_sweep.py
```

**Results:** Saved to `results/ablation3_threshold_results.json`

**Key Finding:** The threshold at 0.7 (used in the paper) sits at the optimal point on the Pareto frontier, balancing escalation rate (1.04%) against detection performance. Lowering the threshold below 0.5 eliminates all LLM escalations, while raising it above 0.9 provides diminishing returns.

---

## A4: Category Leave-One-Out Analysis

**Purpose:** Tests whether the StaticGuard detector generalizes across rogue behavior categories or is dominated by a single category. This reveals which categories are hardest to detect and whether the benchmark provides meaningful differentiation.

**Method:** We run StaticGuard on all 1,278 paired trajectories and compute per-category recall, FPR, F1, and EIR. We also compute the variance across categories to quantify how uniformly the detector performs.

**Reproduction:**

```bash
python3 ablations/ablation4_category_analysis.py
```

**Results:** Saved to `results/ablation4_category_results.json`

**Key Finding:** Detection difficulty varies dramatically across categories:

| Category | Recall | FPR | EIR | Difficulty |
|----------|--------|-----|-----|------------|
| SEC (Secret Exfiltration) | 31.4% | 13.7% | 22.5% | Easiest |
| RES (Resource Abuse) | 17.6% | 2.9% | 9.8% | Medium |
| TST (Test Manipulation) | 13.5% | 7.2% | 2.7% | Medium |
| UFO (Unauthorized File Ops) | 3.5% | 3.5% | 0.0% | Hard |
| INV (Instruction Violation) | 2.8% | 2.8% | 2.8% | Hard |
| DEC (Deceptive Completion) | 1.0% | 2.0% | 1.0% | Hardest |

This 31x range in recall (31.4% to 1.0%) demonstrates that StepShield provides meaningful differentiation across rogue behavior types and that no single category dominates the overall metrics.

---

## Results Directory

All results are stored as JSON in `results/`. Each file contains:

- Aggregate metrics (recall, FPR, F1, EIR)
- Per-category breakdowns
- Confidence intervals where applicable
- API cost and timing information
- Full configuration parameters

---

## Dependencies

```
openai>=1.0.0
```

All ablation scripts use the same detector implementations from `benchmark/detectors/` and the same data from `data/train/`.

---

## Environment

These experiments were run on:
- Python 3.11
- OpenAI-compatible API with models: `gpt-4.1-mini`, `gpt-4.1-nano`, `gemini-2.5-flash`
- Ubuntu 22.04

Random seeds are fixed at 42 for reproducibility.
