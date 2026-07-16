#!/usr/bin/env python3
"""Full metric test script for smg_metrics v5.4.

Tests ALL 25 metrics on user-specified MIDI files (single-file)
and every file pair (pairwise), prints a summary table, and
validates self-consistency (same file -> perfect scores).

Usage::

    # Test all MIDI files in a directory
    python test.py data/gen/ data/gt/

    # Test specific files
    python test.py a.mid b.mid c.mid

    # Quick single-file test
    python test.py --single-only file.mid

    # Quick pairwise test
    python test.py --pair-only pred.mid ref.mid

    # Quick metric subset
    python test.py --only pce ebr note_f1 ca sim_chr pred.mid ref.mid
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from smg_metrics import (
    single_file_harmony,
    single_file_rhythm,
    single_file_quality,
    pair_eval,
    distribution_eval,
    clear_cs_model_cache,
)

SEP = "=" * 72

# Metric counts (v5.4)
N_HARMONY = 5
N_RHYTHM = 4
N_QUALITY = 6
N_SINGLE = N_HARMONY + N_RHYTHM + N_QUALITY  # 15

N_PAIR = 8
N_DIST = 2
N_PAIR_TOTAL = N_PAIR + N_DIST  # 10

N_TOTAL = N_SINGLE + N_PAIR_TOTAL  # 25
N_SELF_CHECKS = 8


def _fmt(v: float, w: int = 10) -> str:
    if v != v:
        return "NaN".rjust(w)
    return f"{v:.4f}".rjust(w)


def _tag(v: float) -> str:
    return "[OK]" if v == v else "[NaN]"


def _test_single(midis: list[Path], only: set[str] | None = None) -> dict:
    """Run single-file harmony + rhythm + quality metrics."""
    results = {}

    # Harmony (5)
    print(SEP)
    print(f"1. Single-file harmony ({N_HARMONY} metrics x {len(midis)} files)")
    print(SEP)
    for m in midis:
        d = single_file_harmony(str(m)).to_dict()
        if only:
            d = {k: v for k, v in d.items() if k in only}
        if not d:
            continue
        results[m.name] = {"harmony": d}
        print(f"\n  {m.name}:")
        for k, v in d.items():
            print(f"    {k:<22} {_fmt(v)}  {_tag(v)}")

    # Rhythm (4)
    print(f"\n{SEP}")
    print(f"2. Single-file rhythm ({N_RHYTHM} metrics x {len(midis)} files)")
    print(SEP)
    for m in midis:
        d = single_file_rhythm(str(m)).to_dict()
        if only:
            d = {k: v for k, v in d.items() if k in only}
        if not d:
            continue
        if m.name not in results:
            results[m.name] = {}
        results[m.name]["rhythm"] = d
        print(f"\n  {m.name}:")
        for k, v in d.items():
            print(f"    {k:<22} {_fmt(float(v))}  {_tag(float(v))}")

    # Quality (6)
    print(f"\n{SEP}")
    print(f"3. Single-file quality ({N_QUALITY} metrics x {len(midis)} files)")
    print(SEP)
    for m in midis:
        d = single_file_quality(str(m)).to_dict()
        if only:
            d = {k: v for k, v in d.items() if k in only}
        if not d:
            continue
        if m.name not in results:
            results[m.name] = {}
        results[m.name]["quality"] = d
        print(f"\n  {m.name}:")
        for k, v in d.items():
            print(f"    {k:<22} {_fmt(float(v))}  {_tag(float(v))}")
    return results


def _eval_pair_worker(pred_path: str, ref_path: str, only: set[str] | None = None) -> dict:
    """Worker function for parallel pairwise evaluation."""
    pair = pair_eval(pred_path, ref_path).to_dict()
    dist = distribution_eval(pred_path, ref_path).to_dict()
    if only:
        pair = {k: v for k, v in pair.items() if k in only}
        dist = {k: v for k, v in dist.items() if k in only}
    return {"pair": pair, "dist": dist}


def _test_pairwise(midis: list[Path], only: set[str] | None = None) -> dict:
    """Run all pairwise metrics on every file pair."""
    n = len(midis)
    n_pairs = n * (n - 1) // 2
    print(f"\n{SEP}")
    print(f"4. Pairwise metrics ({n_pairs} pairs x {N_PAIR_TOTAL} metrics)")
    print(SEP)

    results = {}
    pairs = [(midis[i], midis[j]) for i in range(n) for j in range(i + 1, n)]

    if n >= 2:
        max_workers = min(os.cpu_count() or 1, 4)
        pred_paths = [str(p) for p, _ in pairs]
        ref_paths = [str(r) for _, r in pairs]
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            eval_results = list(
                tqdm(
                    executor.map(_eval_pair_worker, pred_paths, ref_paths, [only] * n_pairs),
                    total=n_pairs,
                    desc="Evaluating pairs",
                    unit="pair",
                )
            )

        for pair_count, (result, (p, r)) in enumerate(zip(eval_results, pairs), 1):
            pair = result["pair"]
            dist = result["dist"]
            key = f"{p.name} vs {r.name}"
            results[key] = {"pair": pair, "distribution": dist}
            print(f"\n  [{pair_count}/{n_pairs}] {p.name} vs {r.name}")

            if pair:
                print(f"    Pair ({len(pair)}):")
                for k, v in pair.items():
                    print(f"      {k:<14} {_fmt(v)}  {_tag(v)}")

            if dist:
                print(f"    Distribution ({len(dist)}):")
                for k, v in dist.items():
                    print(f"      {k:<12} {_fmt(v)}  {_tag(v)}")

            total_shown = len(pair) + len(dist)
            print(f"    -> {total_shown} metrics shown")
    return results


def _test_self_consistency(midis: list[Path]) -> tuple[bool, dict]:
    """Verify self-comparison yields perfect scores."""
    print(f"\n{SEP}")
    print(f"5. Self-consistency ({N_SELF_CHECKS} checks per file)")
    print(SEP)
    all_pass = True
    results = {}
    for m in midis:
        p = pair_eval(str(m), str(m))
        checks: dict[str, tuple[bool, str]] = {
            "note_f1":      (abs(p.note_f1 - 1.0) < 1e-3, "expect 1.0"),
            "notei_f1":     (abs(p.notei_f1 - 1.0) < 1e-3, "expect 1.0"),
            "sim_chr":      (p.sim_chr > 0.95, "expect ~1.0"),
            "sim_grv":      (p.sim_grv > 0.95, "expect ~1.0"),
            "ca":           (abs(p.ca - 1.0) < 1e-3, "expect 1.0"),
            "onset_xor":    (abs(p.onset_xor - 0.0) < 1e-3, "expect 0.0"),
            "note_overlap": (abs(p.note_overlap - 1.0) < 1e-3, "expect 1.0"),
            "cs":           (p.cs > 0.95, "expect ~1.0 (deep embedding)"),
        }
        file_ok = all(ok for ok, _ in checks.values())
        all_pass = all_pass and file_ok
        tag = "ALL PASS" if file_ok else "FAIL"
        results[m.name] = {"pass": file_ok, "checks": {k: {"pass": ok, "expect": desc} for k, (ok, desc) in checks.items()}}
        print(f"  {m.name:<50} {tag}")
        if not file_ok:
            for metric, (ok, desc) in checks.items():
                if not ok:
                    print(f"    FAIL: {metric} -- {desc}")
    return all_pass, results


def _collect_midis(args: argparse.Namespace) -> list[Path]:
    if args.files:
        midis: list[Path] = []
        for f in args.files:
            p = Path(f)
            if p.is_dir():
                midis.extend(sorted(p.rglob("*.mid")))
            elif p.is_file():
                midis.append(p)
            else:
                print(f"Warning: skipping {f} (not found)")
        return midis
    gen_dir = _root / "data" / "pred"
    gt_dir = _root / "data" / "ref"
    midis = []
    if gen_dir.is_dir():
        midis.extend(sorted(gen_dir.rglob("*.mid")))
    if gt_dir.is_dir():
        midis.extend(sorted(gt_dir.rglob("*.mid")))
    if not midis:
        midis = sorted((_root / "data").glob("*.mid"))
    return midis


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"smg_metrics v5.4 - Full Metric Test ({N_TOTAL} metrics)",
        epilog=(
            "Examples:\n"
            "  python test.py data/gen/ data/gt/            # all MIDI in dirs\n"
            "  python test.py a.mid b.mid c.mid             # specific files\n"
            "  python test.py --single-only f.mid            # single-file only\n"
            "  python test.py --pair-only pred.mid ref.mid   # pair only\n"
            "  python test.py --only pce ebr note_f1 a.mid b.mid  # subset\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="*", help="MIDI files or directories (default: data/gen/ + data/gt/)")
    parser.add_argument("--single-only", action="store_true", help="Only run single-file metrics (15)")
    parser.add_argument("--pair-only", action="store_true", help="Only run pairwise metrics (10, needs >= 2 files)")
    parser.add_argument("--only", metavar="M1,M2,...", help="Only test specified metrics (comma-separated, e.g. --only pce,note_f1)")
    parser.add_argument("--json", action="store_true", help="Save results to JSON file")
    args = parser.parse_args()

    t0 = time.time()
    midis = _collect_midis(args)

    if not midis:
        sys.exit("No MIDI files found. Provide files or place them in data/pred/ and data/ref/")

    n_files = len(midis)
    n_pairs = n_files * (n_files - 1) // 2

    print(SEP)
    print(f"smg_metrics v5.4 - Full Metric Test ({N_TOTAL} metrics)")
    print(SEP)
    print(f"  MIDI files : {n_files}")
    print(f"  File pairs : {n_pairs}")
    if args.only:
        print(f"  --only     : {args.only}")
    print()

    only = set(m.strip() for m in args.only.split(",")) if args.only else None
    all_pass = True
    single_results = {}
    pairwise_results = {}
    self_consistency_results = {}

    if not args.pair_only:
        single_results = _test_single(midis, only=only)

    if not args.single_only and n_files >= 2:
        pairwise_results = _test_pairwise(midis, only=only)
        if only is None:
            all_pass, self_consistency_results = _test_self_consistency(midis)

    elapsed = time.time() - t0
    single_count = 0 if args.pair_only else n_files * N_SINGLE
    pair_count = 0 if args.single_only else n_pairs * N_PAIR_TOTAL
    consist_count = 0 if (args.single_only or n_files < 2 or only) else n_files * N_SELF_CHECKS
    total_tests = single_count + pair_count + consist_count

    print(f"\n{SEP}")
    print("Summary")
    print(SEP)
    if not args.pair_only:
        print(f"  Single-file harmony  : {n_files} x {N_HARMONY} = {n_files * N_HARMONY}")
        print(f"  Single-file rhythm  : {n_files} x {N_RHYTHM}  = {n_files * N_RHYTHM}")
        print(f"  Single-file quality : {n_files} x {N_QUALITY} = {n_files * N_QUALITY}")
    if not args.single_only and n_files >= 2:
        print(f"  Pairwise (all)      : {n_pairs} x {N_PAIR_TOTAL} = {n_pairs * N_PAIR_TOTAL}")
        if not only:
            print(f"  Self-consistency    : {n_files} x {N_SELF_CHECKS} = {n_files * N_SELF_CHECKS}")
    print(f"  {'-' * 43}")
    print(f"  Total tests         : {total_tests}")
    print(f"  Self-consist        : {'ALL PASS' if all_pass else 'SKIP' if only else 'FAIL'}")
    print(f"  Time                : {elapsed:.1f}s")

    if not args.single_only:
        cleared = clear_cs_model_cache()
        if cleared > 0:
            print(f"  CS model cache cleared : {cleared} model(s)")

    if args.json:
        output = {
            "version": "5.4.0",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": [str(m) for m in midis],
            "n_files": n_files,
            "n_pairs": n_pairs,
            "single_file": single_results,
            "pairwise": pairwise_results,
            "self_consistency": self_consistency_results,
            "summary": {
                "total_tests": total_tests,
                "all_pass": all_pass,
                "elapsed_seconds": round(elapsed, 2),
            },
        }
        json_path = _root / "test_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n  JSON saved: {json_path}")

    if not all_pass and not only:
        sys.exit(1)


if __name__ == "__main__":
    main()
