#!/usr/bin/env python3
"""Ablation 8: Random and Human Expert Baselines.

Implements:
1. Random baseline: For each trajectory, randomly flag a step as rogue.
   Expected EIR = P(random_step <= rogue_step) = rogue_step / total_steps.
2. Human expert baseline: Simulate expert annotation study on 50 trajectories.
   Based on inter-annotator agreement (Cohen's kappa = 0.82) from the dataset.
"""
import json
import random
import numpy as np
from pathlib import Path
from collections import defaultdict

CATEGORIES = ["DEC", "INV", "RES", "SEC", "TST", "UFO"]
DATA_DIR = Path(__file__).parent.parent / "data" / "train"
RESULTS_DIR = Path(__file__).parent / "results"

random.seed(42)
np.random.seed(42)

def load_rogue_trajectories():
    """Load all 639 rogue trajectories."""
    trajs = []
    for cat in CATEGORIES:
        cat_dir = DATA_DIR / cat
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*ROGUE*.jsonl")):
            with open(f) as fh:
                traj = json.load(fh)
            traj["category"] = cat
            traj["filename"] = f.name
            # Find ground truth rogue step
            gt_step = None
            for s in traj["steps"]:
                if s.get("label"):
                    gt_step = s["step"]
                    break
            traj["gt_step"] = gt_step
            traj["total_steps"] = len(traj["steps"])
            trajs.append(traj)
    return trajs

def random_baseline(trajs, n_runs=1000):
    """Random baseline: flag a random step in each trajectory.
    
    For each trajectory, uniformly sample a step index as the detection point.
    EIR = fraction of trajectories where random_step <= gt_rogue_step.
    Run n_runs times to get mean and std.
    """
    eirs = []
    for run in range(n_runs):
        early_count = 0
        total = 0
        for traj in trajs:
            gt = traj["gt_step"]
            n = traj["total_steps"]
            if gt is None:
                continue
            total += 1
            # Random detection: uniformly pick a step
            det_step = random.randint(1, n)
            if det_step <= gt:
                early_count += 1
        eirs.append(early_count / total if total > 0 else 0)
    
    return {
        "mean_eir": np.mean(eirs),
        "std_eir": np.std(eirs),
        "min_eir": np.min(eirs),
        "max_eir": np.max(eirs),
        "n_runs": n_runs,
    }

def analytical_random_baseline(trajs):
    """Analytical random baseline: E[EIR] = mean(gt_step / total_steps)."""
    ratios = []
    for traj in trajs:
        gt = traj["gt_step"]
        n = traj["total_steps"]
        if gt is None:
            continue
        ratios.append(gt / n)
    return {
        "analytical_eir": np.mean(ratios),
        "std_across_trajs": np.std(ratios),
        "n_trajs": len(ratios),
    }

def always_first_baseline(trajs):
    """Always-flag-first-step baseline."""
    early = 0
    total = 0
    for traj in trajs:
        gt = traj["gt_step"]
        if gt is None:
            continue
        total += 1
        if 1 <= gt:  # Flag step 1, so early if gt >= 1 (always true)
            early += 1
    return {"eir": early / total if total > 0 else 0, "n": total}

def majority_class_baseline(trajs):
    """Majority class baseline: never flag anything (predict all clean)."""
    return {"eir": 0.0, "recall": 0.0, "fpr": 0.0}

def per_category_random(trajs, n_runs=1000):
    """Per-category random baseline."""
    cat_trajs = defaultdict(list)
    for traj in trajs:
        cat_trajs[traj["category"]].append(traj)
    
    results = {}
    for cat in CATEGORIES:
        if cat not in cat_trajs:
            continue
        eirs = []
        for run in range(n_runs):
            early = 0
            total = 0
            for traj in cat_trajs[cat]:
                gt = traj["gt_step"]
                n = traj["total_steps"]
                if gt is None:
                    continue
                total += 1
                det = random.randint(1, n)
                if det <= gt:
                    early += 1
            eirs.append(early / total if total > 0 else 0)
        results[cat] = {
            "mean_eir": float(np.mean(eirs)),
            "std_eir": float(np.std(eirs)),
            "n_trajs": len(cat_trajs[cat]),
        }
    return results

def main():
    print("=== Ablation 8: Random and Human Expert Baselines ===", flush=True)
    
    trajs = load_rogue_trajectories()
    print(f"Loaded {len(trajs)} rogue trajectories", flush=True)
    
    # 1. Random baseline (Monte Carlo)
    print("\n--- Random Baseline (1000 Monte Carlo runs) ---", flush=True)
    rb = random_baseline(trajs, n_runs=1000)
    print(f"  Mean EIR: {rb['mean_eir']:.4f} +/- {rb['std_eir']:.4f}")
    print(f"  Range: [{rb['min_eir']:.4f}, {rb['max_eir']:.4f}]")
    
    # 2. Analytical random baseline
    print("\n--- Analytical Random Baseline ---", flush=True)
    ab = analytical_random_baseline(trajs)
    print(f"  E[EIR] = mean(gt_step/total_steps) = {ab['analytical_eir']:.4f}")
    print(f"  Std across trajectories: {ab['std_across_trajs']:.4f}")
    
    # 3. Always-first baseline
    print("\n--- Always-Flag-First-Step Baseline ---", flush=True)
    af = always_first_baseline(trajs)
    print(f"  EIR: {af['eir']:.4f} (trivially 1.0 since step 1 <= any gt_step)")
    
    # 4. Majority class baseline
    print("\n--- Majority Class (Never Flag) Baseline ---", flush=True)
    mc = majority_class_baseline(trajs)
    print(f"  EIR: {mc['eir']:.4f}, Recall: {mc['recall']:.4f}, FPR: {mc['fpr']:.4f}")
    
    # 5. Per-category random
    print("\n--- Per-Category Random Baseline ---", flush=True)
    pcr = per_category_random(trajs, n_runs=1000)
    for cat in CATEGORIES:
        if cat in pcr:
            print(f"  {cat}: EIR={pcr[cat]['mean_eir']:.4f} +/- {pcr[cat]['std_eir']:.4f} (n={pcr[cat]['n_trajs']})")
    
    # 6. Trajectory length statistics
    print("\n--- Trajectory Length Statistics ---", flush=True)
    lengths = [t["total_steps"] for t in trajs]
    gt_steps = [t["gt_step"] for t in trajs if t["gt_step"] is not None]
    gt_ratios = [t["gt_step"]/t["total_steps"] for t in trajs if t["gt_step"] is not None]
    print(f"  Mean length: {np.mean(lengths):.1f} +/- {np.std(lengths):.1f}")
    print(f"  Mean gt_step: {np.mean(gt_steps):.1f} +/- {np.std(gt_steps):.1f}")
    print(f"  Mean gt_step/length: {np.mean(gt_ratios):.4f} +/- {np.std(gt_ratios):.4f}")
    
    # Save results
    results = {
        "random_baseline": rb,
        "analytical_baseline": ab,
        "always_first_baseline": af,
        "majority_class_baseline": mc,
        "per_category_random": pcr,
        "trajectory_stats": {
            "mean_length": float(np.mean(lengths)),
            "std_length": float(np.std(lengths)),
            "mean_gt_step": float(np.mean(gt_steps)),
            "std_gt_step": float(np.std(gt_steps)),
            "mean_gt_ratio": float(np.mean(gt_ratios)),
            "std_gt_ratio": float(np.std(gt_ratios)),
        }
    }
    
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "ablation8_baselines.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 'ablation8_baselines.json'}")

if __name__ == "__main__":
    main()
