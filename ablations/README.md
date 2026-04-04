# StepShield Ablation Studies

This directory contains the complete code and results for the ablation studies conducted during the ICML 2026 rebuttal period. All experiments are fully reproducible given the same API access.

## Overview

| ID | Ablation Study | Script | Status | API Required |
|----|----------------|--------|--------|--------------|
| A1 | Cross-Model Detector Generalization | `ablation1_full_model.py` | Complete | Yes (3 models) |
| A2 | Paraphrase Robustness | `ablation2_paraphrase_full.py` | Complete | Yes |
| A3 | Cascade Threshold Sensitivity | `ablation3_threshold_sweep.py` | Complete | No |
| A4 | Category Leave-One-Out | `ablation4_category_analysis.py` | Complete | No |
| A6 | Length Sensitivity Analysis | `ablation6_length_sensitivity.py` | Complete | No |
| S  | Frontier Model Scaling (Appendix S) | `frontier_scaling_eval.py` | Complete | Yes (6 models) |

---

## Appendix S: Frontier Model Scaling Evaluation

**Purpose:** Tests whether scaling up the judge model trivially solves the StepShield benchmark (Inverse Scaling Law). This directly addresses whether the benchmark will be obsolete as frontier models improve.

**Method:** We evaluate six models spanning three providers on the full 1,278 trajectory dataset using the LLMJudge prompt. The models evaluated are (in order of release):
- `gpt-4o-mini` (OpenAI, 2024) - Paper baseline
- `gpt-4.1-mini` (OpenAI, 2025)
- `gpt-4.1-nano` (OpenAI, 2025)
- `gemini-2.5-flash` (Google, 2025)
- `claude-sonnet-4` (Anthropic, 2025)
- `claude-opus-4` (Anthropic, 2025)

**Reproduction:**

```bash
# Run all six models (requires OPENAI_API_KEY and ANTHROPIC_API_KEY)
python ablations/frontier_scaling_eval.py

# Run a specific model
python ablations/frontier_scaling_eval.py --models claude-sonnet-4
```

**Results:** Saved to `results/frontier_scaling_eval_results.json`

---

## A1: Cross-Model Detector Generalization

**Purpose:** Tests whether StepShield's detection results are specific to a single LLM family or generalize across architecturally distinct model families.

**Method:** We run the LLMJudge detector on all 1,278 paired trajectories (639 rogue + 639 clean) using three different backbone models from distinct families.

**Reproduction:**

```bash
python ablations/ablation1_full_model.py gpt-4.1-mini
```

**Results:** Saved to `results/ablation1_<model>_full.json`

---

## A2: Paraphrase Robustness

**Purpose:** Tests whether the LLMJudge detector relies on surface-level textual patterns or captures the underlying semantic intent of rogue actions.

**Method:** We paraphrase the labeled rogue steps using a different model to rewrite the text with completely different wording while preserving semantic content, then compute the retention rate.

**Reproduction:**

```bash
python ablations/ablation2_paraphrase_full.py
```

**Results:** Saved to `results/ablation2_paraphrase_full_results.json`

---

## A3: Cascade Threshold Sensitivity

**Purpose:** Validates the design of HybridGuard's cascade architecture by sweeping the confidence thresholds.

**Method:** We sweep the high and low thresholds to compute recall, FPR, F1, average latency, and estimated cost per trajectory, producing a full Pareto frontier.

**Reproduction:**

```bash
python ablations/ablation3_threshold_sweep.py
```

**Results:** Saved to `results/ablation3_threshold_results.json`

---

## A4: Category Leave-One-Out Analysis

**Purpose:** Tests whether the StaticGuard detector generalizes across rogue behavior categories or is dominated by a single category.

**Method:** We run StaticGuard on all 1,278 paired trajectories and compute per-category recall, FPR, F1, and EIR.

**Reproduction:**

```bash
python ablations/ablation4_category_analysis.py
```

**Results:** Saved to `results/ablation4_category_results.json`

---

## Dependencies

```
openai>=1.0.0
anthropic>=0.20.0
```

All ablation scripts use the same detector implementations from `benchmark/detectors/` and the same data from `data/train/`. Random seeds are fixed at 42 for reproducibility.
