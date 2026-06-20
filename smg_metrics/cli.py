"""CLI entry point for smg_metrics evaluation.

Usage::

    # Single-file quality (13 MusPy metrics)
    smg-eval --music generated.mid

    # Single-file rhythmic/temporal metrics (4 D3PIA metrics)
    smg-eval --music generated.mid --rhythmic

    # Pairwise note-level + bar-level + chord-level + rhythmic (10 metrics)
    smg-eval --pred generated.mid --ref reference.mid

    # Distribution-level metrics (6 metrics: PD, DD, OOK, SC_sim, PCE_sim, GS_sim)
    smg-eval --pred generated.mid --ref reference.mid --dist

    # Structural metrics (CHE, Ngram, MelodyMatch, TonalDist)
    smg-eval --music generated.mid --structural
    smg-eval --pred gen.mid --ref ref.mid --structural

    # All metrics
    smg-eval --music gen.mid --pred gen.mid --ref ref.mid --dist --advanced --structural --rhythmic

    # Batch directory
    smg-eval --pred_dir ./pred/ --ref_dir ./ref/
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from smg_metrics.single import single_file, single_file_structural, single_file_rhythmic
from smg_metrics.pair import pair_eval, pair_eval_structural
from smg_metrics.distribution import compute_all as distribution_eval
from smg_metrics.advanced import compute_all as advanced_eval


def _fmt(val: Any) -> str:
    """Format a metric value for display."""
    if isinstance(val, float):
        return f"{val:.4f}" if val == val else "NaN"
    return str(val)


def _print_result(label: str, d: dict[str, Any], indent: int = 2, col_width: int = 24) -> None:
    """Pretty-print a result dict with aligned columns."""
    sp = " " * indent
    for k, v in d.items():
        print(f"{sp}{k:<{col_width}} = {_fmt(v)}")


def _json_safe(obj: Any) -> Any:
    """Convert NaN/inf floats to ``None`` for standards-compliant JSON."""
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def _run_single(midi: str, root: int, mode: str) -> dict[str, Any]:
    return single_file(midi, root=root, mode=mode).to_dict()


def _run_pair(pred: str, ref: str) -> dict[str, Any]:
    return pair_eval(pred, ref).to_dict()


def _run_batch(pred_dir: str, ref_dir: str, root: int, mode: str) -> dict[str, float]:
    preds = sorted(Path(pred_dir).glob("*.mid"))
    refs  = sorted(Path(ref_dir).glob("*.mid"))
    if not preds:
        sys.exit(f"Error: no MIDI files in {pred_dir}")
    if not refs:
        sys.exit(f"Error: no MIDI files in {ref_dir}")
    n = min(len(preds), len(refs))
    print(f"\n{'='*60}")
    print(f"Batch evaluation: {n} pairs")
    print(f"{'='*60}\n")

    singles_p, singles_r, pairs = [], [], []
    for i in range(n):
        p, r = str(preds[i]), str(refs[i])
        print(f"[{i+1}/{n}] {preds[i].name} vs {refs[i].name}")
        singles_p.append(single_file(p, root=root, mode=mode).to_dict())
        singles_r.append(single_file(r, root=root, mode=mode).to_dict())
        pair = pair_eval(p, r).to_dict()
        pairs.append(pair)
        for k, v in pair.items():
            print(f"    {k:<12} = {_fmt(v)}")
        print()

    summary: dict[str, float] = {}
    for key in singles_p[0]:
        vals = [s[key] for s in singles_p if isinstance(s[key], (int, float)) and s[key] == s[key]]
        if vals:
            summary[f"[pred] {key}"] = sum(vals) / len(vals)
    for key in pairs[0]:
        vals = [p[key] for p in pairs if isinstance(p[key], (int, float)) and p[key] == p[key]]
        if vals:
            summary[key] = sum(vals) / len(vals)

    print(f"\n{'='*60}")
    print(f"Batch summary ({n} pairs)")
    print(f"{'='*60}\n")
    for k, v in summary.items():
        print(f"  {k:<25} = {v:.4f}")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(
        prog="smg-eval",
        description="Objective evaluation metrics for Symbolic Music Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  smg-eval --music generated.mid\n"
            "  smg-eval --music generated.mid --structural --rhythmic\n"
            "  smg-eval --pred gen.mid --ref ref.mid\n"
            "  smg-eval --pred gen.mid --ref ref.mid --dist\n"
            "  smg-eval --pred gen.mid --ref ref.mid --advanced\n"
            "  smg-eval --pred gen.mid --ref ref.mid --structural\n"
            "  smg-eval --music gen.mid --pred gen.mid --ref ref.mid --dist --advanced --structural --rhythmic\n"
            "  smg-eval --pred_dir ./pred/ --ref_dir ./ref/\n"
        ),
    )
    p.add_argument("--music",     help="Single-file quality (13 MusPy metrics)")
    p.add_argument("--pred",      help="Predicted MIDI file")
    p.add_argument("--ref",       help="Reference MIDI file")
    p.add_argument("--pred_dir",  help="Predicted MIDI directory")
    p.add_argument("--ref_dir",   help="Reference MIDI directory")
    p.add_argument("--root",  type=int, default=0,          help="Root pitch for PISR (0=C)")
    p.add_argument("--mode",  type=str, default="major",    choices=["major","minor"])
    p.add_argument("--dist",  action="store_true",          help="Include distribution-level metrics (PD, DD, OOK, SC_sim, PCE_sim, GS_sim)")
    p.add_argument("--advanced", action="store_true",       help="Include advanced metrics (KL, OA, CI, CTS, CR, ReconAcc)")
    p.add_argument("--structural", action="store_true",     help="Include structural metrics (CHE, Ngram, MelodyMatch, TonalDist)")
    p.add_argument("--rhythmic", action="store_true",       help="Include rhythmic/temporal metrics (IOI, RI, RD, VN)")
    p.add_argument("--json",  action="store_true",          help="Output as JSON")

    args = p.parse_args()
    result: dict[str, Any] | None = None

    if args.music:
        result = _run_single(args.music, args.root, args.mode)
        if not args.json:
            print(f"\n{'='*60}\nSingle-file: {args.music}\n{'='*60}\n")
            _print_result("quality", result)
        if args.structural:
            struct = single_file_structural(args.music).to_dict()
            if not args.json:
                print("\n-- Structural --")
                _print_result("structural", struct)
            result.update(struct)
        if args.rhythmic:
            rhythm = single_file_rhythmic(args.music).to_dict()
            if not args.json:
                print("\n-- Rhythmic/Temporal --")
                _print_result("rhythmic", rhythm)
            result.update(rhythm)

    if args.pred and args.ref:
        if result is None:
            result = {}
        if not args.json:
            print(f"\n{'='*60}\nPairwise evaluation\n  pred: {args.pred}\n  ref:  {args.ref}\n{'='*60}")
            print("\n-- Single-file (pred) --")
            sp = _run_single(args.pred, args.root, args.mode)
            _print_result("pred", sp)
            print("\n-- Single-file (ref) --")
            sr = _run_single(args.ref, args.root, args.mode)
            _print_result("ref", sr)
        pair = _run_pair(args.pred, args.ref)
        if not args.json:
            print("\n-- Pairwise --")
            _print_result("pair", pair)
        result.update(pair)
        if args.structural:
            struct_s = single_file_structural(args.pred).to_dict()
            struct_p = pair_eval_structural(args.pred, args.ref).to_dict()
            if not args.json:
                print("\n-- Structural (single) --")
                _print_result("structural", struct_s)
                print("\n-- Structural (pair) --")
                _print_result("structural", struct_p)
            result.update(struct_s)
            result.update(struct_p)
        if args.rhythmic:
            rhythm_s = single_file_rhythmic(args.pred).to_dict()
            if not args.json:
                print("\n-- Rhythmic/Temporal (single) --")
                _print_result("rhythmic", rhythm_s)
            result.update(rhythm_s)
        if args.dist:
            dist = distribution_eval(args.pred, args.ref).to_dict()
            if not args.json:
                print("\n-- Distribution-level --")
                _print_result("dist", dist)
            result.update(dist)
        if args.advanced:
            adv = advanced_eval(args.pred, args.ref).to_dict()
            if not args.json:
                print("\n-- Advanced --")
                _print_result("adv", adv)
            result.update(adv)
    elif not args.music and args.pred_dir and args.ref_dir:
        result = _run_batch(args.pred_dir, args.ref_dir, args.root, args.mode)
    elif result is None:
        p.print_help()
        return

    if args.json and result is not None:
        print(json.dumps(_json_safe(result), indent=2, ensure_ascii=False, allow_nan=False))
