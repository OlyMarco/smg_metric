"""Note F1 / Notei F1 metrics.

Implements two pairwise comparison metrics from:

    Ou et al., "Unifying Symbolic Music Arrangement," NeurIPS 2025.
    URL: https://arxiv.org/abs/2408.15176
    Appendix C.1.

Note events are quantised to a 16th-note grid before matching.
The matching is greedy one-to-one (provably optimal for exact-match keys).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np
import miditoolkit

__all__ = ["NoteF1Result", "compute_all"]

_TP16_DIVISOR = 4  # 16th-note = quarter / 4


# ── Data structures ────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class _Note:
    onset: int   # quantised 16th-note step
    pitch: int   # MIDI pitch


@dataclass(frozen=True, slots=True)
class _NoteI(_Note):
    instrument: int  # MIDI program (128 for drums)


@dataclass(frozen=True, slots=True)
class NoteF1Result:
    """Container for two pairwise note-level metrics.

    Attributes:
        note_f1:   Note F1 (onset + pitch) in [0, 1].
        notei_f1:  Notei F1 (onset + pitch + instrument) in [0, 1].
    """
    note_f1: float
    notei_f1: float

    def to_dict(self) -> dict[str, float]:
        """Return metrics as a plain dict."""
        from dataclasses import asdict
        return asdict(self)


# ── MIDI loading ───────────────────────────────────────────────────

def _load_notes(midi_path: str | Path) -> list[_NoteI]:
    """Extract quantised note events from *midi_path*.

    Reference: Ou et al., "Unifying Symbolic Music Arrangement," NeurIPS 2025.
    URL: https://arxiv.org/abs/2408.15176
    """
    midi = miditoolkit.MidiFile(str(midi_path))
    tp16 = max(1, midi.ticks_per_beat // _TP16_DIVISOR)
    notes: list[_NoteI] = []
    for track in midi.instruments:
        program = 128 if track.is_drum else track.program
        for n in track.notes:
            notes.append(_NoteI(
                onset=n.start // tp16,
                pitch=n.pitch,
                instrument=program,
            ))
    return notes


# ── Greedy one-to-one matching ────────────────────────────────────

def _count_matches(pred: list[_Note], ref: list[_Note]) -> int:
    """Count greedy one-to-one (onset, pitch) matches."""
    pool: dict[tuple[int, int], int] = defaultdict(int)
    for n in ref:
        pool[(n.onset, n.pitch)] += 1
    matched = 0
    for n in pred:
        key = (n.onset, n.pitch)
        if pool.get(key, 0) > 0:
            pool[key] -= 1
            matched += 1
    return matched


def _count_matches_i(pred: list[_NoteI], ref: list[_NoteI]) -> int:
    """Count greedy one-to-one (onset, pitch, instrument) matches."""
    pool: dict[tuple[int, int, int], int] = defaultdict(int)
    for n in ref:
        pool[(n.onset, n.pitch, n.instrument)] += 1
    matched = 0
    for n in pred:
        key = (n.onset, n.pitch, n.instrument)
        if pool.get(key, 0) > 0:
            pool[key] -= 1
            matched += 1
    return matched


def _f1(pred_len: int, ref_len: int, matched: int) -> float:
    """Precision / Recall / F1 from set sizes and match count."""
    if pred_len == 0 or ref_len == 0:
        return 0.0
    p = matched / pred_len
    r = matched / ref_len
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


# ── Public API ────────────────────────────────────────────────────

def compute_all(
    pred_path: Union[str, Path],
    ref_path: Union[str, Path],
) -> NoteF1Result:
    """Compute all note-level metrics between *pred* and *ref*.

    Args:
        pred_path: Path to the predicted / generated MIDI file.
        ref_path:  Path to the reference / ground-truth MIDI file.

    Returns:
        A NoteF1Result dataclass.

    Raises:
        FileNotFoundError: If either file does not exist.
    """
    pred_path, ref_path = Path(pred_path), Path(ref_path)
    for p in (pred_path, ref_path):
        if not p.exists():
            raise FileNotFoundError(f"MIDI file not found: {p}")

    pred_raw = _load_notes(pred_path)
    ref_raw  = _load_notes(ref_path)

    pred_plain = [_Note(n.onset, n.pitch) for n in pred_raw]
    ref_plain  = [_Note(n.onset, n.pitch) for n in ref_raw]

    # Note F1
    matched = _count_matches(pred_plain, ref_plain)
    nf1 = _f1(len(pred_plain), len(ref_plain), matched)

    # Notei F1
    matched_i = _count_matches_i(pred_raw, ref_raw)
    ni_f1 = _f1(len(pred_raw), len(ref_raw), matched_i)

    return NoteF1Result(
        note_f1=nf1,
        notei_f1=ni_f1,
    )
