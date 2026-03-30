#!/usr/bin/env python3
"""Ablation 7: Confidence Calibration Analysis.

Analyzes how well StaticGuard's confidence scores are calibrated:
- Do higher confidence scores correlate with actual rogue behavior?
- What is the distribution of confidence scores for TP vs FP vs TN vs FN?
- What is the optimal confidence threshold?

FREE ablation (no API calls).
"""
import json
import sys
import asyncio
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmark"))
from detectors.static_guard import StaticGuard

CATEGORIES = ["DEC", "INV", "RES", "SEC", "TST", "UFO"]
DATA_DIR = Path(__file__).parent.parent / "data" / "train"
RESULTS_DIR = Path(__file__).parent / "results"


async def main():
    print("=" * 60, flush=True)
    print("ABLATION 7: CONFIDENCE CALIBRATION ANALYSIS", flush=True)
    print("=" * 60, flush=True)

    detector = StaticGuard()

    # Collect all max-confidence scores per trajectory
    tp_confs = []
    fp_confs = []
    tn_confs = []
    fn_confs = []

    # For ROC-like analysis at different thresholds
    all_scores = []  # (max_confidence, is_rogue_gt)

    for cat in CATEGORIES:
        cat_dir = DATA_DIR / cat
        for f in sorted(cat_dir.glob("*.jsonl")):
            with open(f) as fh:
                traj = json.load(fh)

            is_rogue = "ROGUE" in f.name
            ctx = {"task": traj.get("task", {})}

            max_conf = 0.0
            detected = False
            for idx, step in enumerate(traj["steps"]):
                r = await detector.detect_step(step, idx + 1, ctx)
                if r:
                    if r.confidence > max_conf:
                        max_conf = r.confidence
                    if r.is_rogue and not detected:
                        detected = True

            all_scores.append((max_conf, is_rogue))

            if is_rogue:
                if detected:
                    tp_confs.append(max_conf)
                else:
                    fn_confs.append(max_conf)
            else:
                if detected:
                    fp_confs.append(max_conf)
                else:
                    tn_confs.append(max_conf)

    print(f"\n{'='*60}", flush=True)
    print("CONFIDENCE DISTRIBUTION", flush=True)
    print(f"{'='*60}\n", flush=True)

    def stats(confs, label):
        if not confs:
            print(f"  {label}: N=0", flush=True)
            return {"n": 0}
        arr = np.array(confs)
        print(f"  {label}: N={len(arr)}, Mean={arr.mean():.3f}, "
              f"Median={np.median(arr):.3f}, Std={arr.std():.3f}, "
              f"Min={arr.min():.3f}, Max={arr.max():.3f}", flush=True)
        return {
            "n": len(arr), "mean": float(arr.mean()),
            "median": float(np.median(arr)), "std": float(arr.std()),
            "min": float(arr.min()), "max": float(arr.max()),
            "percentiles": {
                "25": float(np.percentile(arr, 25)),
                "50": float(np.percentile(arr, 50)),
                "75": float(np.percentile(arr, 75)),
                "90": float(np.percentile(arr, 90)),
                "95": float(np.percentile(arr, 95))
            }
        }

    results = {}
    results["tp"] = stats(tp_confs, "True Positives (correctly detected rogue)")
    results["fp"] = stats(fp_confs, "False Positives (clean flagged as rogue)")
    results["tn"] = stats(tn_confs, "True Negatives (correctly passed clean)")
    results["fn"] = stats(fn_confs, "False Negatives (missed rogue)")

    # Threshold sweep for optimal operating point
    print(f"\n{'='*60}", flush=True)
    print("THRESHOLD SWEEP", flush=True)
    print(f"{'='*60}\n", flush=True)

    print(f"{'Threshold':<12} {'Recall':<10} {'FPR':<10} {'F1':<10} {'Accuracy':<10}", flush=True)
    print("-" * 52, flush=True)

    threshold_results = []
    for thresh in np.arange(0.1, 1.0, 0.05):
        tp = sum(1 for s, gt in all_scores if s >= thresh and gt)
        fp = sum(1 for s, gt in all_scores if s >= thresh and not gt)
        fn = sum(1 for s, gt in all_scores if s < thresh and gt)
        tn = sum(1 for s, gt in all_scores if s < thresh and not gt)

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * prec * recall / (prec + recall) if (prec + recall) > 0 else 0
        acc = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0

        print(f"{thresh:.2f}        {recall:.3f}     {fpr:.3f}     {f1:.3f}     {acc:.3f}", flush=True)
        threshold_results.append({
            "threshold": float(thresh),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "recall": recall, "fpr": fpr, "precision": prec,
            "f1": f1, "accuracy": acc
        })

    results["threshold_sweep"] = threshold_results

    # Find optimal threshold (max F1)
    best = max(threshold_results, key=lambda x: x["f1"])
    print(f"\nOptimal threshold (max F1): {best['threshold']:.2f} "
          f"(F1={best['f1']:.3f}, Recall={best['recall']:.3f}, FPR={best['fpr']:.3f})", flush=True)
    results["optimal_threshold"] = best

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "ablation7_confidence_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {out_path}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
