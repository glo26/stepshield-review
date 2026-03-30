# StepShield: A Comprehensive Benchmark for Step-Level Agent Intervention

This repository contains the official code and data for the ICML 2026 submission, "StepShield: A Comprehensive Benchmark for Step-Level Agent Intervention."

## Overview

StepShield is a benchmark designed to evaluate the effectiveness of intervention mechanisms in language agent systems. It provides a comprehensive framework for assessing the ability of detectors to identify and mitigate harmful or undesirable agent behaviors at the step level.

This repository includes:

*   The full benchmark framework, including all detectors and evaluation scripts.
*   The complete dataset, comprising 9,213 trajectories (7,935 test, 1,278 train) across 6 categories of agent failure.
*   All ablation study scripts and their corresponding results.
*   The full LaTeX source and compiled PDF of the paper.

## Repository Structure

```
├── README.md
├── benchmark/      # Main benchmark framework
│   ├── detectors/  # Detector implementations (LLMJudge, HybridGuard, etc.)
│   ├── metrics/    # Evaluation metrics
│   └── run_benchmark.py # Main script to run the benchmark
├── ablations/      # All 10 ablation study scripts and results
│   └── results/    # Raw JSON results from each ablation
├── data/           # Benchmark dataset
│   ├── test/       # Test set trajectories (scrubbed and mapping)
│   ├── train/      # Train set trajectories by category
│   └── generated_benign/ # Benign trajectories for FPR analysis
├── config/         # Configuration files and prompts
└── paper/          # LaTeX source and compiled PDF
```

## Reproduction Instructions

To reproduce the main results from the paper (Table 4), follow these steps:

**1. Installation**

```bash
# Navigate to the benchmark directory
cd benchmark

# Install dependencies
pip install -r requirements.txt
```

**2. Set up API Keys**

Create a `.env` file in the root directory of this repository and add your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

**3. Run the Benchmark**

From the `benchmark` directory, run the main evaluation script:

```bash
python run_benchmark.py
```

This will evaluate all detectors on the full test set and generate a `results.json` file with the metrics reported in Table 4.

**4. Reproduce Ablation Studies**

To reproduce any of the 10 ablation studies, navigate to the `ablations` directory and run the corresponding Python script (e.g., `python ablation1_cross_model.py`). The raw results are also available in the `ablations/results` directory.

## Paper

The full paper can be found in the `paper` directory as `StepShield.pdf`. The LaTeX source is also provided for review.
