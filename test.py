#!/usr/bin/env python3
"""Full metric test script for smg_metrics.

Tests ALL 45 metrics on user-specified MIDI files (single-file)
and every file pair (pairwise), prints a summary table, and
validates self-consistency (same file -> perfect scores).

Usage::

    # Test all MIDI files in a directory
    python test.py data/

    # Test specific files
    python test.py a.mid b.mid c.mid

    # Quick single-file test
    python test.py --single-only file.mid

    # Quick pairwise test
    python test.py --pair-only pred.mid ref.mid
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from smg_metrics import (
    single_file,
    single_file_structural,
    pair_eval,
    pair_eval_structural,
    distribution_eval,
    advanced_eval,
)

SEP = "=" * 72


def _fmt(v: float, w: int = 10) -> str:
    """Format a metric value for display."""
    if v != v:
        return "NaN".rjust(w)
    return f"{v:.4f}".rjust(w)


def _tag(v: float) -> str:
    """Return [OK] or [NaN] tag for a metric value."""
    return "[OK]" if v == v else "[NaN]"


def _test_single(midis: list[Path]) -> None:
    """Run single-file quality + structural metrics."""
    print(SEP)
    print(f"1. Single-file quality (13 metrics x {len(midis)} files)")
    print(SEP)
    for m in midis:
        d = single_file(str(m)).to_dict()
        print(f"\n  {m.name}:")
        for k, v in d.items():
            print(f"    {k:<22} {_fmt(v)}  {_tag(v)}")

    print(f"\n{SEP}")
    print(f"2. Single-file structural (2 metrics x {len(midis)} files)")
    print(SEP)
    for m in midis:
        d = single_file_structural(str(m)).to_dict()
        print(f"\n  {m.name}:")
        for k, v in d.items():
            print(f"    {k:<12} {_fmt(v)}  {_tag(v)}")


def _test_pairwise(midis: list[Path]) -> None:
    """Run all pairwise metrics on every file pair."""
    n = len(midis)
    n_pairs = n * (n - 1) // 2
    print(f"\n{SEP}")
    print(f"3. Pairwise metrics ({n_pairs} pairs x 30 metrics)")
    print(SEP)
    pair_count = 0
    for i in range(n):
        for j in range(i + 1, n):
            pair_count += 1
            p, r = midis[i], midis[j]
            print(f"\n  [{pair_count}/{n_pairs}] {p.name} vs {r.name}")

            pair = pair_eval(str(p), str(r)).to_dict()
            sp   = pair_eval_structural(str(p), str(r)).to_dict()
            dist = distribution_eval(str(p), str(r)).to_dict()
            adv  = advanced_eval(str(p), str(r)).to_dict()

            print("    Pair (8):")
            for k, v in pair.items():
                print(f"      {k:<14} {_fmt(v)}  {_tag(v)}")
            print("    Structural (2):")
            for k, v in sp.items():
                print(f"      {k:<16} {_fmt(v)}  {_tag(v)}")
            print("    Distribution (6):")
            for k, v in dist.items():
                print(f"      {k:<12} {_fmt(v)}  {_tag(v)}")
            print("    Advanced (14):")
            for k, v in adv.items():
                print(f"      {k:<16} {_fmt(v)}  {_tag(v)}")
            print(f"    -> {len(pair)+len(sp)+len(dist)+len(adv)} metrics")


def _test_self_consistency(midis: list[Path]) -> bool:
    """Verify self-comparison yields perfect scores."""
    print(f"\n{SEP}")
    print("4. Self-consistency (same file -> perfect scores)")
    print(SEP)
    all_pass = True
    for m in midis:
        p  = pair_eval(str(m), str(m))
        sp = pair_eval_structural(str(m), str(m))
        checks: dict[str, tuple[bool, str]] = {
            "note_f1":      (abs(p.note_f1 - 1.0) < 1e-3, "expect 1.0"),
            "notei_f1":     (abs(p.notei_f1 - 1.0) < 1e-3, "expect 1.0"),
            "mel_f1":       (abs(p.mel_f1 - 1.0) < 1e-3, "expect 1.0"),
            "i_iou":        (abs(p.i_iou - 1.0) < 1e-3, "expect 1.0"),
            "ver":          (abs(p.ver - 0.0) < 1e-3, "expect 0.0"),
            "sim_chr":      (abs(p.sim_chr - 1.0) < 1e-3, "expect 1.0"),
            "sim_grv":      (abs(p.sim_grv - 1.0) < 1e-3, "expect 1.0"),
            "ca":           (abs(p.ca - 1.0) < 1e-3, "expect 1.0"),
            "melody_match": (abs(sp.melody_match - 1.0) < 1e-3, "expect 1.0"),
            "tonal_dist":   (abs(sp.tonal_dist - 0.0) < 1e-3, "expect 0.0"),
        }
        file_ok = all(ok for ok, _ in checks.values())
        all_pass = all_pass and file_ok
        tag = "ALL PASS" if file_ok else "FAIL"
        print(f"  {m.name:<50} {tag}")
        if not file_ok:
            for metric, (ok, desc) in checks.items():
                if not ok:
                    print(f"    FAIL: {metric} -- {desc}")
    return all_pass


def _collect_midis(args: argparse.Namespace) -> list[Path]:
    """Resolve MIDI file list from CLI arguments."""
    if args.files:
        midis: list[Path] = []
        for f in args.files:
            p = Path(f)
            if p.is_dir():
                midis.extend(sorted(p.glob("*.mid")))
            elif p.is_file():
                midis.append(p)
            else:
                print(f"Warning: skipping {f} (not found)")
        return midis
    return sorted((_root / "data").glob("*.mid"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="smg_metrics full test script (45 metrics)",
        epilog=(
            "Examples:\n"
            "  python test.py data/                       # all MIDI in data/\n"
            "  python test.py a.mid b.mid c.mid           # specific files\n"
            "  python test.py --single-only f.mid          # single-file only\n"
            "  python test.py --pair-only pred.mid ref.mid # pair only\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="*", help="MIDI files or directories (default: data/)")
    parser.add_argument("--single-only", action="store_true", help="Only run single-file metrics")
    parser.add_argument("--pair-only", action="store_true", help="Only run pairwise metrics (needs >= 2 files)")
    args = parser.parse_args()

    t0 = time.time()
    midis = _collect_midis(args)

    if not midis:
        sys.exit("No MIDI files found. Provide files or place them in data/")

    n_files = len(midis)
    n_pairs = n_files * (n_files - 1) // 2

    print(SEP)
    print("smg_metrics -- Full Metric Test")
    print(SEP)
    print(f"  MIDI files : {n_files}")
    print(f"  File pairs : {n_pairs}")
    print()

    all_pass = True

    if not args.pair_only:
        _test_single(midis)

    if not args.single_only and n_files >= 2:
        _test_pairwise(midis)
        all_pass = _test_self_consistency(midis)

    # Summary
    elapsed = time.time() - t0
    single_count = 0 if args.pair_only else n_files * 15
    pair_count = 0 if args.single_only else n_pairs * 30
    consist_count = 0 if (args.single_only or n_files < 2) else n_files * 10
    total_tests = single_count + pair_count + consist_count

    print(f"\n{SEP}")
    print("Summary")
    print(SEP)
    if not args.pair_only:
        print(f"  Single-file quality    : {n_files} x 13 = {n_files * 13}")
        print(f"  Single-file structural : {n_files} x 2  = {n_files * 2}")
    if not args.single_only and n_files >= 2:
        print(f"  Pairwise (all)         : {n_pairs} x 30 = {n_pairs * 30}")
        print(f"  Self-consistency       : {n_files} x 10 = {n_files * 10}")
    print(f"  -------------------------------------------")
    print(f"  Total tests            : {total_tests}")
    print(f"  Self-consist           : {'ALL PASS' if all_pass else 'FAIL'}")
    print(f"  Time                   : {elapsed:.1f}s")

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
