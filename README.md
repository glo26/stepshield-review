# StepShield: When, Not Whether to Intervene on Rogue Agents

Anonymous submission. This repository contains the code, data, and paper for StepShield.

## Overview

StepShield is the first benchmark for evaluating **detection quality** on rogue AI agents. Existing agent safety benchmarks evaluate *whether* an agent misbehaved, not *how well* the violation can be detected amid benign behavior. StepShield addresses this gap with:

- **9,213 step-level annotated code-agent trajectories** grounded in real-world security incidents
- **Three temporal metrics**: Early Intervention Rate (EIR, paired precision), Intervention Gap (IG), and Tokens Saved
- **Four baseline detectors**: StaticGuard (regex/keyword), ConstraintGuard (explicit constraints), LLMJudge (GPT-4.1-mini), HybridGuard (cascaded)
- **Six rogue behavior categories**: Unauthorized File Operations (UFO), Secret Exfiltration (SEC), Resource Abuse (RES), Instruction Violation (INV), Test Manipulation (TST), Deceptive Completion (DEC)

## Repository Structure

```
├── README.md
├── benchmark/                  # Main benchmark framework
│   ├── detectors/              # All 4 detector implementations
│   │   ├── static_guard.py
│   │   ├── constraint_guard.py
│   │   ├── llm_judge.py
│   │   └── hybrid_guard.py
│   ├── metrics/                # Evaluation metrics
│   │   └── timing_metrics.py   # EIR, IG, Tokens Saved
│   └── run_benchmark.py        # Main evaluation script
├── ablations/                  # All ablation study scripts
│   └── results/                # Raw JSON results
├── data/                       # Benchmark dataset
│   ├── test/                   # 7,935 test trajectories (scrubbed)
│   │   ├── scrubbed/           # Category-label-removed trajectories
│   │   └── mapping.json        # Ground truth mapping
│   ├── train/                  # 1,278 training pairs by category
│   │   └── {UFO,SEC,RES,INV,TST,DEC}/
│   └── generated_benign/       # 6,657 benign trajectories for FPR
├── config/                     # Configuration files and prompts
├── results/                    # Raw experimental results
│   └── final_metrics.json      # All numbers reported in the paper
└── paper/                      # LaTeX source and compiled PDF
    ├── StepShield.tex
    ├── StepShield.pdf
    ├── references.bib
    └── figures/
```

## Quick Start

### 1. Installation

```bash
pip install -r benchmark/requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the repository root:

```
OPENAI_API_KEY=sk-...
```

### 3. Run the Full Benchmark

```bash
python benchmark/run_benchmark.py
```

This evaluates all four detectors on the test set and produces metrics matching Table 4 in the paper.

### 4. Reproduce Ablation Studies

```bash
cd ablations
python ablation1_cross_model.py      # Table 11: Model scaling
python ablation2_context_window.py   # Table 12: Context window
# ... see ablations/ for all scripts
```

Pre-computed results are in `ablations/results/`.

## Key Results (Table 4)

| Detector | Accuracy | Recall | EIR | IG | Tokens Saved |
|:---|:---|:---|:---|:---|:---|
| StaticGuard | 57.6% | 67.0% | 0.51 | 3.12 | 18.4% |
| ConstraintGuard | 60.3% | 25.5% | 0.55 | 2.87 | 6.1% |
| LLMJudge | 61.5% | 78.9% | 0.59 | 2.45 | 31.2% |
| HybridGuard | **66.0%** | 29.7% | **0.80** | **1.34** | 8.9% |

## Citation

```bibtex
@inproceedings{anonymous2026stepshield,
  title={StepShield: When, Not Whether to Intervene on Rogue Agents},
  author={Anonymous},
  booktitle={Proceedings of the International Conference on Machine Learning (ICML)},
  year={2026}
}
```

## License

Code and data are released under Apache 2.0.
