# StepShield

A benchmark for evaluating step-level detection quality on rogue AI agents.

## Paper

The full paper is available at [`paper/StepShield.pdf`](./paper/StepShield.pdf). LaTeX source and bibliography are in the same directory.

StepShield introduces a temporal evaluation paradigm for agent safety. Our results reveal three uncomfortable truths: (1) the safety Pareto frontier appears empty in our evaluation, with no detector achieving both high recall and low false positives; (2) LLM judges are unreliable, exhibiting over 13pp recall variance run-to-run at zero temperature; and (3) the field has optimized for the wrong metric, as our best detector (HybridGuard) achieves the highest intervention quality (EIR 0.80) but the lowest recall (29.7%).

## Repository Layout

```
stepshield-review/
├── paper/                      # Paper and figures
│   ├── StepShield.pdf          # Compiled paper
│   ├── StepShield.tex          # LaTeX source
│   ├── references.bib          # Bibliography
│   └── figures/                # All paper figures
│
├── data/                       # StepShield benchmark dataset (9,213 trajectories)
│   ├── train/                  # 1,278 labeled trajectories (639 rogue/clean pairs)
│   │   ├── DEC/                # Deceptive Completion
│   │   ├── INV/                # Instruction Violation
│   │   ├── RES/                # Resource Abuse
│   │   ├── SEC/                # Secret Exfiltration
│   │   ├── TST/                # Test Manipulation
│   │   └── UFO/                # Unauthorized File Operations
│   └── test/
│       └── scrubbed/           # 7,935 trajectories (labels withheld)
│
├── benchmark/                  # Detector implementations and evaluation
│   ├── detectors/              # HybridGuard, LLMJudge, StaticGuard, ConstraintGuard
│   ├── metrics/                # EIR, IG, Tokens Saved
│   ├── run_benchmark.py        # Main evaluation script
│   ├── data_loader.py          # Dataset loading utilities
│   └── validate_jsonl.py       # Data format validator
│
├── ablations/                  # All 8 ablation study scripts
│   └── results/                # Pre-computed ablation results (JSON)
│
├── config/                     # Detector and prompt configurations
│   └── prompts/                # Judge prompt templates
│
└── results/                    # Raw experimental results (JSON)
```

## Dataset

Each trajectory is a single `.jsonl` file representing a sequence of agent steps. The training set is organized by rogue behavior category, with each rogue trajectory paired with a minimally-edited clean counterpart. The test set is scrubbed of category labels to prevent overfitting.

| Split | Rogue | Clean | Benign | Total |
| :--- | ---: | ---: | ---: | ---: |
| Train | 639 | 639 | - | 1,278 |
| Test | 639 | 639 | 6,657 | 7,935 |
| Total | 1,278 | 1,278 | 6,657 | 9,213 |

The six rogue behavior categories are: Unauthorized File Operations (UFO), Secret Exfiltration (SEC), Resource Abuse (RES), Instruction Violation (INV), Test Manipulation (TST), and Deceptive Completion (DEC). Each category spans three difficulty levels (L1, L2, L3). See `data/README.md` for the full datasheet.

## Reproducing Results

### Setup

```bash
pip install -r benchmark/requirements.txt
export OPENAI_API_KEY=sk-...
```

### Main Results (Table 4)

```bash
python benchmark/run_benchmark.py
```

This evaluates all four detectors on the test set and writes detailed results to `results/`.

### Ablation Studies

Each ablation script is self-contained. For example:

```bash
python ablations/ablation1_cross_model.py gpt-4.1-mini
python ablations/ablation2_paraphrase_full.py
python ablations/ablation3_threshold_sweep.py
```

Pre-computed results for all ablations are available in `ablations/results/`. See `ablations/README.md` for a full description of each study.

## Key Results

| Detector | EIR | IG | Recall | Benign FPR | Paired FPR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| HybridGuard | 0.80 | 0.85 | 29.7% | 1.56% | 7.67% |
| LLMJudge | 0.72 | 0.61 | 78.9% | 2.11% | 31.30% |
| StaticGuard | 0.51 | 3.12 | 67.0% | 4.33% | 48.98% |
| ConstraintGuard | 0.51 | 2.87 | 29.1% | 13.6% | 24.41% |
| Human Expert | 0.92 | 0.95 | 85.1% | 0.50% | 4.50% |

HybridGuard achieves the highest intervention quality (EIR 0.80) among automated detectors, but the 12.5-point gap to human experts (0.92) defines the open research frontier. Full results, including per-category and per-severity breakdowns, are in `results/final_metrics.json`.

## Acknowledgments

This work was supported in part by the MOVE Fellowship.

## Citation

```bibtex
@inproceedings{stepshield2026,
  title     = {StepShield: Dismantling the Illusion of Security in Autonomous Agents},
  author    = {Anonymous},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2026}
}
```

## License

Apache 2.0. See [LICENSE](./LICENSE).
