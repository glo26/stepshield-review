#!/usr/bin/env python3
"""Ablation 6: Trajectory Length Sensitivity Analysis.

Analyzes how trajectory length affects detection performance.
Groups trajectories into length bins and computes per-bin metrics.
FREE ablation (no API calls) — uses StaticGuard only.
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

# Length bins
BINS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25)]


def get_bin(length):
    for lo, hi in BINS:
        if lo <= length <= hi:
            return f"{lo}-{hi}"
    return f"{BINS[-1][1]}+"


async def main():
    print("=" * 60, flush=True)
    print("ABLATION 6: TRAJECTORY LENGTH SENSITIVITY", flush=True)
    print("=" * 60, flush=True)

    detector = StaticGuard()

    per_bin = defaultdict(lambda: {
        "tp": 0, "fp": 0, "tn": 0, "fn": 0,
        "early": 0, "n_rogue": 0, "n_clean": 0,
        "lengths": [], "det_positions": []
    })

    all_lengths = []

    for cat in CATEGORIES:
        cat_dir = DATA_DIR / cat
        for f in sorted(cat_dir.glob("*.jsonl")):
            with open(f) as fh:
                traj = json.load(fh)

            is_rogue = "ROGUE" in f.name
            total_steps = len(traj["steps"])
            length_bin = get_bin(total_steps)
            all_lengths.append(total_steps)

            ctx = {"task": traj.get("task", {})}

            gt_step = None
            if is_rogue:
                for s in traj["steps"]:
                    if s.get("label"):
                        gt_step = s["step"]
                        break

            detected = False
            det_step = None
            for idx, step in enumerate(traj["steps"]):
                r = await detector.detect_step(step, idx + 1, ctx)
                if r and r.is_rogue:
                    detected = True
                    det_step = idx + 1
                    break

            if is_rogue:
                per_bin[length_bin]["n_rogue"] += 1
                per_bin[length_bin]["lengths"].append(total_steps)
                if detected:
                    per_bin[length_bin]["tp"] += 1
                    per_bin[length_bin]["det_positions"].append(det_step / total_steps)
                    if gt_step and det_step and det_step <= total_steps * 0.5:
                        per_bin[length_bin]["early"] += 1
                else:
                    per_bin[length_bin]["fn"] += 1
            else:
                per_bin[length_bin]["n_clean"] += 1
                if detected:
                    per_bin[length_bin]["fp"] += 1
                else:
                    per_bin[length_bin]["tn"] += 1

    print(f"\nTrajectory length stats: min={min(all_lengths)}, max={max(all_lengths)}, "
          f"mean={np.mean(all_lengths):.1f}, median={np.median(all_lengths):.0f}", flush=True)

    print(f"\n{'='*60}", flush=True)
    print("LENGTH SENSITIVITY RESULTS (StaticGuard)", flush=True)
    print(f"{'='*60}\n", flush=True)

    print(f"{'Bin':<10} {'N_rog':<8} {'N_cln':<8} {'Recall':<10} {'FPR':<10} {'EIR':<10} {'AvgDetPos':<12}", flush=True)
    print("-" * 68, flush=True)

    results = {}
    for lo, hi in BINS:
        bin_key = f"{lo}-{hi}"
        d = per_bin[bin_key]
        n_rog = d["n_rogue"]
        n_cln = d["n_clean"]
        tp = d["tp"]
        fn = d["fn"]
        fp = d["fp"]
        tn = d["tn"]

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        eir = d["early"] / n_rog if n_rog > 0 else 0
        avg_det_pos = np.mean(d["det_positions"]) if d["det_positions"] else 0

        print(f"{bin_key:<10} {n_rog:<8} {n_cln:<8} {recall:.3f}     {fpr:.3f}     {eir:.3f}     {avg_det_pos:.3f}", flush=True)

        results[bin_key] = {
            "n_rogue": n_rog, "n_clean": n_cln,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "recall": recall, "fpr": fpr, "eir": eir,
            "avg_detection_position": avg_det_pos,
            "avg_length": float(np.mean(d["lengths"])) if d["lengths"] else 0
        }

    results["length_stats"] = {
        "min": int(min(all_lengths)),
        "max": int(max(all_lengths)),
        "mean": float(np.mean(all_lengths)),
        "median": float(np.median(all_lengths)),
        "std": float(np.std(all_lengths))
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "ablation6_length_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {out_path}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
