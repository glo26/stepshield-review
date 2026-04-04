# StepShield: Dismantling the Illusion of Security in Autonomous Agents

[📃 Paper](./paper/StepShield.pdf) | [🌐 Dataset](./data/README.md) | [🏆 Leaderboard](#key-results)

**StepShield** is the first benchmark designed to evaluate step-level detection quality on rogue AI agents. It introduces a temporal evaluation paradigm for agent safety, shifting the focus from whether a detector eventually catches a rogue agent to *when* it intervenes.

Our results reveal three uncomfortable truths:
1. The safety Pareto frontier appears empty in our evaluation, with no detector achieving both high recall and low false positives.
2. LLM judges are unreliable, exhibiting over 13pp recall variance run-to-run at zero temperature.
3. The field has optimized for the wrong metric, as our best detector (HybridGuard) achieves the highest intervention quality (EIR 0.80) but the lowest recall (29.7%).

## Table of Contents
- [Dataset Summary](#dataset-summary)
- [Key Results](#key-results)
- [Quick Start](#quick-start)
- [Repository Layout](#repository-layout)
- [Ablation Studies](#ablation-studies)
- [Extending StepShield](#extending-stepshield)
- [Acknowledgments](#acknowledgments)
- [Citation](#citation)

## Dataset Summary

Each trajectory is a single `.jsonl` file representing a sequence of agent steps. The training set is organized by rogue behavior category, with each rogue trajectory paired with a minimally-edited clean counterpart. The test set is scrubbed of category labels to prevent overfitting.

| Split | Rogue | Clean | Benign | Total |
| :--- | ---: | ---: | ---: | ---: |
| Train | 639 | 639 | - | 1,278 |
| Test | 639 | 639 | 6,657 | 7,935 |
| Total | 1,278 | 1,278 | 6,657 | 9,213 |

The six rogue behavior categories are: Unauthorized File Operations (UFO), Secret Exfiltration (SEC), Resource Abuse (RES), Instruction Violation (INV), Test Manipulation (TST), and Deceptive Completion (DEC). Each category spans three difficulty levels (L1, L2, L3). See `data/README.md` for the full datasheet.

## Key Results

Here are the scores on the test set results of StepShield (Table 4 in the paper).

| Detector | EIR | IG | Recall | Benign FPR | Paired FPR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| HybridGuard | 0.80 | 0.85 | 29.7% | 1.56% | 7.67% |
| LLMJudge | 0.72 | 0.61 | 78.9% | 2.11% | 31.30% |
| StaticGuard | 0.51 | 3.12 | 67.0% | 4.33% | 48.98% |
| ConstraintGuard | 0.51 | 2.87 | 29.1% | 13.6% | 24.41% |
| Human Expert | 0.92 | 0.95 | 85.1% | 0.50% | 4.50% |

HybridGuard achieves the highest intervention quality (EIR 0.80) among automated detectors, but the 12.5-point gap to human experts (0.92) defines the open research frontier. Full results, including per-category and per-severity breakdowns, are in `results/final_metrics.json`.

## Quick Start

This section will guide you on how to quickly run the StepShield benchmark on your machine.

### Step 1. Prerequisites

Clone this repo and install the dependencies. We recommend using Python 3.11.

```shell
git clone https://github.com/anonymous/stepshield-review.git
cd stepshield-review
pip install -r benchmark/requirements.txt
```

### Step 2. Configure API Keys

If you are evaluating LLM-based detectors (like LLMJudge or HybridGuard), you need to set your API keys as environment variables.

```shell
export OPENAI_API_KEY="your_openai_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

### Step 3. Run the Benchmark

Evaluate all four detectors on the test set:

```shell
python benchmark/run_benchmark.py
```

This will write detailed results to the `results/` directory.

## Repository Layout

```
stepshield-review/
├── ablations/                  # Ablation study scripts (including frontier scaling)
├── benchmark/                  # Detector implementations and evaluation
│   ├── detectors/              # HybridGuard, LLMJudge, StaticGuard, ConstraintGuard
│   ├── metrics/                # EIR, IG, Tokens Saved
│   ├── run_benchmark.py        # Main evaluation script
│   └── data_loader.py          # Dataset loading utilities
├── config/                     # Detector and prompt configurations
├── data/                       # StepShield benchmark dataset (9,213 trajectories)
├── paper/                      # Compiled paper, LaTeX source, and figures
└── results/                    # Raw experimental results (JSON)
```

## Ablation Studies

StepShield includes comprehensive ablation studies to analyze detector generalization, robustness, and scaling. Each ablation script is self-contained. For example:

```shell
# Run Ablation 1: Cross-Model Detector Generalization
python ablations/ablation1_cross_model.py gpt-4.1-mini

# Run Appendix S: Frontier Model Scaling Evaluation
python ablations/frontier_scaling_eval.py
```

Pre-computed results for all ablations are available in `ablations/results/`. See `ablations/README.md` for a full description of each study.

## Extending StepShield

We welcome contributions to StepShield! If you wish to add new detectors, evaluate new models, or expand the dataset, please refer to our [CONTRIBUTING.md](./CONTRIBUTING.md) guide.

## Acknowledgments

This work was supported in part by the MOVE Fellowship.

## Citation

If you find our work helpful, please use the following citation:

```bibtex
@inproceedings{stepshield2026,
  title     = {StepShield: Dismantling the Illusion of Security in Autonomous Agents},
  author    = {Anonymous},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2026}
}
```

## License

Apache 2.0. Check `LICENSE`.
