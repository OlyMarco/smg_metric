"""CLI entry point for smg_metrics evaluation.

Usage::

    # Single-file harmony metrics (5)
    smg-eval -m generated.mid --harmony

    # Single-file rhythm metrics (4)
    smg-eval -m generated.mid --rhythm

    # Single-file quality metrics (6)
    smg-eval -m generated.mid --quality

    # All single-file metrics (15)
    smg-eval -m generated.mid --all-single

    # Pairwise (8 metrics incl. CS)
    smg-eval -p generated.mid -r reference.mid

    # Distribution-level metrics (PD, DD)
    smg-eval -p generated.mid -r reference.mid -d

    # Select a single metric
    smg-eval -m generated.mid --only pce
    smg-eval -p gen.mid -r ref.mid --only ca

    # Batch directory
    smg-eval --pred_dir ./pred/ --ref_dir ./ref/

    # JSON output
    smg-eval -m generated.mid --json
"""

from __future__ import annotations

import argparse, json, math, sys, time
from pathlib import Path
from typing import Any

__all__ = ["main"]

def _fmt(val: Any) -> str:
    if isinstance(val, float):
        return "NaN" if val != val else f"{val:.4f}"
    return str(val)

def _print_result(d, indent=2, col_width=24):
    sp = " " * indent
    for k, v in d.items():
        print(f"{sp}{k:<{col_width}} = {_fmt(v)}")

def _json_safe(obj):
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj

# ── Lazy imports ──────────────────────────────────────────────────

def _import_single():
    from smg_metrics.single import single_file_harmony, single_file_rhythm, single_file_quality
    return single_file_harmony, single_file_rhythm, single_file_quality

def _import_pair():
    from smg_metrics.pair import pair_eval
    return pair_eval

def _import_dist():
    from smg_metrics.distribution import compute_all
    return compute_all

# ── Metric registry ───────────────────────────────────────────────

_HARMONY_METRICS = {'pce', 'sc', 'pisr', 'ook', 'che'}
_RHYTHM_METRICS = {'mean_ioi', 'gs', 'ngram_div', 'ebr'}
_QUALITY_METRICS = {'polyphony', 'polyphony_rate', 'pitch_entropy', 'pitch_range', 'n_pitches_used', 'n_pitch_classes_used'}
_PAIR_METRICS = {'note_f1', 'notei_f1', 'sim_chr', 'sim_grv', 'ca', 'cs', 'onset_xor', 'note_overlap'}
_DIST_METRICS = {'pd', 'dd'}

_ALL_METRICS = (
    _HARMONY_METRICS | _RHYTHM_METRICS | _QUALITY_METRICS
    | _PAIR_METRICS | _DIST_METRICS
)

# ── Runners ───────────────────────────────────────────────────────

def _run_harmony(midi, root, mode, only):
    fn, _, _ = _import_single()
    r = fn(midi, root=root, mode=mode).to_dict()
    return {k: v for k, v in r.items() if not only or k in only} if only else r

def _run_rhythm(midi, only):
    _, fn, _ = _import_single()
    r = fn(midi).to_dict()
    return {k: v for k, v in r.items() if not only or k in only} if only else r

def _run_quality(midi, only):
    _, _, fn = _import_single()
    r = fn(midi).to_dict()
    return {k: v for k, v in r.items() if not only or k in only} if only else r

def _run_pair(pred, ref, only):
    fn = _import_pair()
    r = fn(pred, ref).to_dict()
    return {k: v for k, v in r.items() if not only or k in only} if only else r

def _run_dist(pred, ref, only):
    fn = _import_dist()
    r = fn(pred, ref).to_dict()
    return {k: v for k, v in r.items() if not only or k in only} if only else r

def _run_batch(pred_dir, ref_dir, root, mode):
    hfn, rfn, qfn = _import_single()
    pfn = _import_pair()
    preds = sorted(Path(pred_dir).glob("*.mid"))
    refs = sorted(Path(ref_dir).glob("*.mid"))
    if not preds: sys.exit(f"Error: no MIDI files in {pred_dir}")
    if not refs: sys.exit(f"Error: no MIDI files in {ref_dir}")
    n = min(len(preds), len(refs))
    print(f"\n{'='*60}\nBatch evaluation: {n} pairs\n{'='*60}\n")
    singles_p, pairs = [], []
    for i in range(n):
        p, r = str(preds[i]), str(refs[i])
        print(f"[{i+1}/{n}] {preds[i].name} vs {refs[i].name}")
        singles_p.append({**hfn(p, root=root, mode=mode).to_dict(),
                          **rfn(p).to_dict(), **qfn(p).to_dict()})
        pair = pfn(p, r).to_dict()
        pairs.append(pair)
        for k, v in pair.items():
            print(f"    {k:<12} = {_fmt(v)}")
        print()
    summary = {}
    for key in singles_p[0]:
        vals = [s[key] for s in singles_p if isinstance(s[key], (int, float)) and s[key] == s[key]]
        if vals: summary[f"[pred] {key}"] = sum(vals) / len(vals)
    for key in pairs[0]:
        vals = [p[key] for p in pairs if isinstance(p[key], (int, float)) and p[key] == p[key]]
        if vals: summary[key] = sum(vals) / len(vals)
    print(f"\n{'='*60}\nBatch summary ({n} pairs)\n{'='*60}\n")
    for k, v in summary.items():
        print(f"  {k:<25} = {v:.4f}")
    return summary

# ── Main ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        prog="smg-eval",
        description="smg-metrics v5.4 - 25 metrics for Symbolic Music Generation evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  smg-eval -m generated.mid --all-single\n"
            "  smg-eval -m gen.mid --harmony --rhythm\n"
            "  smg-eval -p gen.mid -r ref.mid\n"
            "  smg-eval -p gen.mid -r ref.mid -d\n"
            "  smg-eval -m gen.mid --only pce,gs\n"
            "  smg-eval --pred_dir ./pred/ --ref_dir ./ref/\n\n"
            "Metric categories (25 total):\n"
            "  Harmony (5):   PCE, SC, PISR, OOK, CHE\n"
            "  Rhythm (4):    IOI, GS, Ngram, EBR\n"
            "  Quality (6):   Poly, PR, PE, Range, Np, Npc\n"
            "  Pairwise (8):  F1, F1i, simChr, simGrv, CA, CS, XOR, NOvlp\n"
            "  Distribution (2): PD, DD\n"
        ),
    )
    p.add_argument("-m", "--music", metavar="PATH", help="Single MIDI file")
    p.add_argument("-p", "--pred", metavar="PATH", help="Predicted MIDI file")
    p.add_argument("-r", "--ref", metavar="PATH", help="Reference MIDI file")
    p.add_argument("--pred_dir", metavar="DIR", help="Pred directory (batch)")
    p.add_argument("--ref_dir", metavar="DIR", help="Ref directory (batch)")
    p.add_argument("--root", type=int, default=0, help="Root for PISR (0=C)")
    p.add_argument("--mode", default="major", choices=["major", "minor"], help="Scale mode")
    p.add_argument("--harmony", action="store_true", help="Harmony metrics (PCE, SC, PISR, OOK, CHE)")
    p.add_argument("--rhythm", action="store_true", help="Rhythm metrics (IOI, GS, Ngram, EBR)")
    p.add_argument("--quality", action="store_true", help="Quality metrics (Poly, PR, PE, Range, Np, Npc)")
    p.add_argument("--all-single", action="store_true", help="All single-file metrics (15)")
    p.add_argument("-d", "--dist", action="store_true", help="Distribution metrics (PD, DD)")
    p.add_argument("--only", metavar="M1,M2,...", help="Only compute specified metrics (comma-separated, e.g. --only pce,note_f1)")
    p.add_argument("--list-metrics", action="store_true", help="List all metrics and exit")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("--time", action="store_true", help="Print elapsed time")

    args = p.parse_args()

    if args.list_metrics:
        print("Available metrics:")
        for name, s in [("Harmony", _HARMONY_METRICS), ("Rhythm", _RHYTHM_METRICS),
                        ("Quality", _QUALITY_METRICS), ("Pairwise", _PAIR_METRICS),
                        ("Distribution", _DIST_METRICS)]:
            print(f"\n  {name} ({len(s)}):")
            for m in sorted(s):
                print(f"    {m}")
        return

    only = set(m.strip() for m in args.only.split(",")) if args.only else None
    if only:
        unknown = only - _ALL_METRICS
        if unknown:
            sys.exit(f"Unknown metrics: {', '.join(sorted(unknown))}\nUse --list-metrics.")

    t0 = time.monotonic()
    result = {}

    # ── Single-file mode ──
    if args.music:
        needs_h = args.harmony or args.all_single or (only and only & _HARMONY_METRICS)
        needs_r = args.rhythm or args.all_single or (only and only & _RHYTHM_METRICS)
        needs_q = args.quality or args.all_single or (only and only & _QUALITY_METRICS)
        if only is None and not args.harmony and not args.rhythm and not args.quality and not args.all_single:
            needs_h = needs_r = needs_q = True

        if needs_h:
            h = _run_harmony(args.music, args.root, args.mode, only)
            if not args.json:
                print(f"\n{'='*60}\nHarmony: {args.music}\n{'='*60}\n")
                _print_result(h)
            result.update(h)
        if needs_r:
            r = _run_rhythm(args.music, only)
            if not args.json and r:
                print("\n-- Rhythm --")
                _print_result(r)
            result.update(r)
        if needs_q:
            q = _run_quality(args.music, only)
            if not args.json and q:
                print("\n-- Quality --")
                _print_result(q)
            result.update(q)

    # ── Pairwise mode ──
    if args.pred and args.ref:
        needs_pair = only is None or bool(only & _PAIR_METRICS)
        needs_dist = args.dist or (only and only & _DIST_METRICS)
        if only is None and not args.dist:
            needs_dist = False
        if not args.music and needs_pair:
            if not args.json:
                print(f"\n{'='*60}\nPairwise: {args.pred} vs {args.ref}\n{'='*60}\n")
        if needs_pair:
            pair = _run_pair(args.pred, args.ref, only)
            if not args.json:
                _print_result(pair)
            result.update(pair)
        if needs_dist:
            dist = _run_dist(args.pred, args.ref, only)
            if not args.json and dist:
                print("\n-- Distribution --")
                _print_result(dist)
            result.update(dist)

    # ── Batch mode ──
    elif not args.music and args.pred_dir and args.ref_dir:
        result = _run_batch(args.pred_dir, args.ref_dir, args.root, args.mode)

    # ── No input ──
    elif not result:
        p.print_help()
        return

    if args.json and result:
        print(json.dumps(_json_safe(result), indent=2, ensure_ascii=False))
    if args.time:
        print(f"\nElapsed: {time.monotonic() - t0:.2f}s", file=sys.stderr)
