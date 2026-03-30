#!/usr/bin/env python3
"""Ablation 4: Category Leave-One-Out Analysis.

Analyzes per-category detection performance using StaticGuard
(the only detector that requires zero API calls) on all train data.
Also computes cross-category generalization metrics.
"""
import json
import os
import sys
import re
import asyncio
import statistics
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmark"))
from detectors.static_guard import StaticGuard

CATEGORIES = ["DEC", "INV", "RES", "SEC", "TST", "UFO"]
DATA_DIR = Path(__file__).parent.parent / "data" / "train"


def load_trajectories_by_category():
    """Load all trajectories grouped by category."""
    by_cat = defaultdict(lambda: {"rogue": [], "clean": []})
    
    for cat in CATEGORIES:
        cat_dir = DATA_DIR / cat
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.jsonl")):
            with open(f) as fh:
                traj = json.load(fh)
            traj["category"] = cat
            traj["trajectory_type"] = "rogue" if "ROGUE" in f.name else "clean"
            if "ROGUE" in f.name:
                by_cat[cat]["rogue"].append(traj)
            else:
                by_cat[cat]["clean"].append(traj)
    
    return by_cat


async def evaluate_static_guard(trajectories):
    """Run StaticGuard on a list of trajectories and return metrics."""
    detector = StaticGuard()
    
    tp = fp = tn = fn = 0
    early_detections = 0
    total_rogue = 0
    intervention_gaps = []
    
    for traj in trajectories:
        is_rogue = traj["trajectory_type"] == "rogue"
        total_steps = len(traj["steps"])
        
        # Find ground truth rogue step
        gt_step = None
        if is_rogue:
            for s in traj["steps"]:
                if s.get("label"):
                    gt_step = s["step"]
                    break
        
        # Run detector using async interface
        detected = False
        detection_step = None
        task_context = traj.get("task", {})
        for idx, step in enumerate(traj["steps"]):
            result = await detector.detect_step(step, idx + 1, task_context)
            if result and result.is_rogue:
                detected = True
                detection_step = step["step"]
                break
        
        if is_rogue:
            total_rogue += 1
            if detected:
                tp += 1
                if gt_step and detection_step:
                    gap = detection_step - gt_step
                    intervention_gaps.append(gap)
                    if detection_step <= total_steps * 0.5:
                        early_detections += 1
            else:
                fn += 1
        else:
            if detected:
                fp += 1
            else:
                tn += 1
    
    total = tp + fp + tn + fn
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    eir = early_detections / total_rogue if total_rogue > 0 else 0
    avg_gap = sum(intervention_gaps) / len(intervention_gaps) if intervention_gaps else float('nan')
    
    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "recall": recall, "precision": precision, "f1": f1,
        "fpr": fpr, "eir": eir, "avg_gap": avg_gap,
        "n_rogue": tp + fn, "n_clean": fp + tn
    }


async def main():
    print("=" * 70)
    print("ABLATION 4: CATEGORY LEAVE-ONE-OUT ANALYSIS")
    print("=" * 70)
    
    data = load_trajectories_by_category()
    
    # Part 1: Per-category performance
    print("\n--- Part 1: Per-Category Detection Performance (StaticGuard) ---\n")
    print(f"{'Category':<10} {'N_Rog':<8} {'N_Cln':<8} {'Recall':<10} {'FPR':<10} {'F1':<10} {'EIR':<10}")
    print("-" * 66)
    
    cat_results = {}
    for cat in CATEGORIES:
        all_trajs = data[cat]["rogue"] + data[cat]["clean"]
        result = await evaluate_static_guard(all_trajs)
        cat_results[cat] = result
        print(f"{cat:<10} {result['n_rogue']:<8} {result['n_clean']:<8} "
              f"{result['recall']:.3f}     {result['fpr']:.3f}     "
              f"{result['f1']:.3f}     {result['eir']:.3f}")
    
    # Part 2: Leave-One-Out
    print("\n--- Part 2: Leave-One-Out Generalization ---")
    print("(StaticGuard is zero-shot, so LOO tests category-specific pattern coverage)\n")
    print(f"{'Held-Out':<10} {'Recall':<10} {'FPR':<10} {'F1':<10} {'Delta vs All':<15}")
    print("-" * 55)
    
    # Overall performance
    all_trajs = []
    for cat in CATEGORIES:
        all_trajs.extend(data[cat]["rogue"])
        all_trajs.extend(data[cat]["clean"])
    overall = await evaluate_static_guard(all_trajs)
    
    for held_out in CATEGORIES:
        test_trajs = data[held_out]["rogue"] + data[held_out]["clean"]
        result = await evaluate_static_guard(test_trajs)
        delta = result['f1'] - overall['f1']
        print(f"{held_out:<10} {result['recall']:.3f}     {result['fpr']:.3f}     "
              f"{result['f1']:.3f}     {delta:+.3f}")
    
    # Part 3: Cross-Category Variance
    print("\n--- Part 3: Cross-Category Variance ---\n")
    recalls = [cat_results[c]["recall"] for c in CATEGORIES]
    fprs = [cat_results[c]["fpr"] for c in CATEGORIES]
    f1s = [cat_results[c]["f1"] for c in CATEGORIES]
    
    print(f"Overall:  Recall={overall['recall']:.3f}, FPR={overall['fpr']:.3f}, F1={overall['f1']:.3f}")
    print(f"Recall: mean={statistics.mean(recalls):.3f}, std={statistics.stdev(recalls):.3f}, "
          f"range=[{min(recalls):.3f}, {max(recalls):.3f}]")
    print(f"FPR:    mean={statistics.mean(fprs):.3f}, std={statistics.stdev(fprs):.3f}, "
          f"range=[{min(fprs):.3f}, {max(fprs):.3f}]")
    print(f"F1:     mean={statistics.mean(f1s):.3f}, std={statistics.stdev(f1s):.3f}, "
          f"range=[{min(f1s):.3f}, {max(f1s):.3f}]")
    
    # Save results
    results = {
        "overall": overall,
        "per_category": cat_results,
        "variance": {
            "recall_mean": statistics.mean(recalls),
            "recall_std": statistics.stdev(recalls),
            "fpr_mean": statistics.mean(fprs),
            "fpr_std": statistics.stdev(fprs),
            "f1_mean": statistics.mean(f1s),
            "f1_std": statistics.stdev(f1s),
        }
    }
    
    out_path = Path(__file__).parent / "results" / "ablation4_category_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
