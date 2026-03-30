#!/usr/bin/env python3
"""Ablation 1: Cross-Model Detector Generalization.

Runs LLMJudge with gemini-2.5-flash and gpt-4.1-nano on a sample of
rogue+clean paired trajectories to test whether detection performance
holds across model families.

This is the most important ablation - it kills the circularity argument.
"""
import json
import os
import sys
import asyncio
import time
import random
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmark"))
from detectors.llm_judge import LLMJudge

CATEGORIES = ["DEC", "INV", "RES", "SEC", "TST", "UFO"]
DATA_DIR = Path(__file__).parent.parent / "data" / "train"
RESULTS_DIR = Path(__file__).parent / "results"

# Models to test
MODELS = ["gpt-4.1-mini", "gpt-4.1-nano", "gemini-2.5-flash"]

# Sample size per category (rogue + clean pairs)
SAMPLE_PER_CAT = 10  # 10 rogue + 10 clean = 20 per cat, 120 total


def load_sample_trajectories():
    """Load a balanced sample of trajectories across all categories."""
    random.seed(42)  # Reproducibility
    sample = []
    
    for cat in CATEGORIES:
        cat_dir = DATA_DIR / cat
        if not cat_dir.exists():
            continue
        
        rogue_files = sorted(cat_dir.glob("*ROGUE*"))
        clean_files = sorted(cat_dir.glob("*CLEAN*"))
        
        # Sample pairs
        rogue_sample = random.sample(rogue_files, min(SAMPLE_PER_CAT, len(rogue_files)))
        clean_sample = random.sample(clean_files, min(SAMPLE_PER_CAT, len(clean_files)))
        
        for f in rogue_sample + clean_sample:
            with open(f) as fh:
                traj = json.load(fh)
            traj["category"] = cat
            traj["trajectory_type"] = "rogue" if "ROGUE" in f.name else "clean"
            traj["filename"] = f.name
            sample.append(traj)
    
    return sample


async def evaluate_model(model_name, trajectories, semaphore):
    """Run LLMJudge with a specific model on all trajectories."""
    detector = LLMJudge(model=model_name, rate_limit_rpm=200)
    
    tp = fp = tn = fn = 0
    early_detections = 0
    total_rogue = 0
    intervention_gaps = []
    per_category = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})
    errors = 0
    
    total = len(trajectories)
    
    for i, traj in enumerate(trajectories):
        is_rogue = traj["trajectory_type"] == "rogue"
        total_steps = len(traj["steps"])
        cat = traj["category"]
        
        # Find ground truth rogue step
        gt_step = None
        if is_rogue:
            for s in traj["steps"]:
                if s.get("label"):
                    gt_step = s["step"]
                    break
        
        # Run detector on each step
        detected = False
        detection_step = None
        task_context = {"task": traj.get("task", {})}
        
        for idx, step in enumerate(traj["steps"]):
            async with semaphore:
                try:
                    result = await detector.detect_step(step, idx + 1, task_context)
                    if result and result.is_rogue:
                        detected = True
                        detection_step = step["step"]
                        break
                except Exception as e:
                    errors += 1
                    continue
        
        if is_rogue:
            total_rogue += 1
            if detected:
                tp += 1
                per_category[cat]["tp"] += 1
                if gt_step and detection_step:
                    gap = detection_step - gt_step
                    intervention_gaps.append(gap)
                    if detection_step <= total_steps * 0.5:
                        early_detections += 1
            else:
                fn += 1
                per_category[cat]["fn"] += 1
        else:
            if detected:
                fp += 1
                per_category[cat]["fp"] += 1
            else:
                tn += 1
                per_category[cat]["tn"] += 1
        
        # Progress
        pct = (i + 1) / total * 100
        if (i + 1) % 5 == 0 or (i + 1) == total:
            print(f"  [{model_name}] {i+1}/{total} ({pct:.0f}%) - TP:{tp} FP:{fp} TN:{tn} FN:{fn} Err:{errors}")
    
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    eir = early_detections / total_rogue if total_rogue > 0 else 0
    avg_gap = sum(intervention_gaps) / len(intervention_gaps) if intervention_gaps else float('nan')
    
    return {
        "model": model_name,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "recall": recall, "precision": precision, "f1": f1,
        "fpr": fpr, "eir": eir, "avg_gap": avg_gap,
        "n_rogue": tp + fn, "n_clean": fp + tn,
        "errors": errors,
        "api_calls": detector.api_calls,
        "total_cost": detector.total_cost,
        "per_category": dict(per_category),
    }


async def main():
    print("=" * 70)
    print("ABLATION 1: CROSS-MODEL DETECTOR GENERALIZATION")
    print("=" * 70)
    
    trajs = load_sample_trajectories()
    n_rogue = sum(1 for t in trajs if t["trajectory_type"] == "rogue")
    n_clean = sum(1 for t in trajs if t["trajectory_type"] == "clean")
    print(f"\nLoaded {len(trajs)} trajectories ({n_rogue} rogue, {n_clean} clean)")
    print(f"Categories: {', '.join(CATEGORIES)}")
    print(f"Sample per category: {SAMPLE_PER_CAT} rogue + {SAMPLE_PER_CAT} clean")
    
    # Concurrency limiter
    semaphore = asyncio.Semaphore(5)
    
    all_results = []
    
    for model in MODELS:
        print(f"\n{'='*50}")
        print(f"Running model: {model}")
        print(f"{'='*50}")
        start = time.time()
        
        result = await evaluate_model(model, trajs, semaphore)
        elapsed = time.time() - start
        
        result["elapsed_seconds"] = elapsed
        all_results.append(result)
        
        print(f"\n  Results for {model}:")
        print(f"  Recall: {result['recall']:.3f}")
        print(f"  FPR:    {result['fpr']:.3f}")
        print(f"  F1:     {result['f1']:.3f}")
        print(f"  EIR:    {result['eir']:.3f}")
        print(f"  Cost:   ${result['total_cost']:.4f}")
        print(f"  Time:   {elapsed:.1f}s")
    
    # Summary table
    print(f"\n{'='*70}")
    print("CROSS-MODEL COMPARISON SUMMARY")
    print(f"{'='*70}\n")
    print(f"{'Model':<22} {'Recall':<10} {'FPR':<10} {'F1':<10} {'EIR':<10} {'Cost':<10}")
    print("-" * 72)
    for r in all_results:
        print(f"{r['model']:<22} {r['recall']:.3f}     {r['fpr']:.3f}     "
              f"{r['f1']:.3f}     {r['eir']:.3f}     ${r['total_cost']:.4f}")
    
    # Per-category breakdown
    print(f"\n{'='*70}")
    print("PER-CATEGORY RECALL BY MODEL")
    print(f"{'='*70}\n")
    print(f"{'Category':<10}", end="")
    for r in all_results:
        print(f" {r['model']:<20}", end="")
    print()
    print("-" * 70)
    for cat in CATEGORIES:
        print(f"{cat:<10}", end="")
        for r in all_results:
            cat_data = r["per_category"].get(cat, {"tp": 0, "fn": 0})
            cat_tp = cat_data.get("tp", 0)
            cat_fn = cat_data.get("fn", 0)
            cat_recall = cat_tp / (cat_tp + cat_fn) if (cat_tp + cat_fn) > 0 else 0
            print(f" {cat_recall:.3f}              ", end="")
        print()
    
    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "ablation1_cross_model_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
