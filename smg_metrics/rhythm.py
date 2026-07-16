"""Rhythm and temporal metrics (single-file + pairwise).

Consolidates all rhythmic metrics: IOI, GS, Ngram, EBR (single-file),
and OXD, NOvlp (pairwise).

Metrics:
    IOI   Mean Inter-Onset Interval (single-file, D3PIA convention)
    GS    Grooving Pattern Similarity (single-file, Jazz Transformer)
    Ngram N-gram Note Diversity (single-file, Yang and Lerch)
    EBR   Empty Beat Rate (single-file, MusPy/Pypianoroll)
    OXD   Onset XOR Distance (pairwise, D3PIA)
    NOvlp Note Overlap (pairwise, mir_eval)

References:
    IOI: https://github.com/jech2/D3PIA
    GS: https://archives.ismir.net/ismir2020/paper/000339.pdf
        Implemented from scratch (NOT muspy.groove_consistency which only
        compares adjacent bars; the original paper uses ALL bar pairs).
    Ngram: https://doi.org/10.1007/s00521-018-3849-7
    EBR: https://arxiv.org/abs/2008.01951
    OXD: https://github.com/jech2/D3PIA
    NOvlp: https://github.com/mir-evaluation/mir_eval
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Union

import numpy as np
import muspy

from smg_metrics._io import Note3, Note4, extract_notes3, extract_notes4, load_midi

__all__ = [
    "RhythmicResult",
    "compute_single",
    "mean_ioi",
    "grooving_pattern_similarity",
    "ngram_diversity",
    "empty_beat_rate",
    "onset_xor_distance",
    "note_overlap",
]


@dataclass(frozen=True, slots=True)
class RhythmicResult:
    """Container for single-file rhythmic metrics.

    Attributes:
        mean_ioi: Mean inter-onset interval in seconds.
        gs: Grooving Pattern Similarity in [0, 1].
        ngram_div: N-gram (4-gram) pitch-class diversity in [0, 1].
        ebr: Empty Beat Rate in [0, 1].
    """
    mean_ioi: float
    gs: float
    ngram_div: float
    ebr: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def _tick_to_second_mapper(midi) -> Callable[[int | float], float]:
    """Return a tick-to-second converter respecting tempo changes."""
    ticks_per_beat = max(1, int(midi.ticks_per_beat))
    tempo_changes = sorted(midi.tempo_changes, key=lambda t: t.time)
    if not tempo_changes or tempo_changes[0].time > 0:
        from miditoolkit.midi.containers import TempoChange
        tempo_changes.insert(0, TempoChange(tempo=120.0, time=0))

    starts, bpms, elapsed = [], [], []
    cur_sec, prev_tick, prev_bpm = 0.0, int(tempo_changes[0].time), float(tempo_changes[0].tempo) or 120.0
    starts.append(prev_tick); bpms.append(prev_bpm); elapsed.append(0.0)

    for change in tempo_changes[1:]:
        tick = int(change.time)
        if tick < prev_tick:
            continue
        cur_sec += (tick - prev_tick) * 60.0 / (ticks_per_beat * prev_bpm)
        starts.append(tick); bpms.append(float(change.tempo) or prev_bpm); elapsed.append(cur_sec)
        prev_tick, prev_bpm = tick, float(change.tempo) or prev_bpm

    starts_arr = np.asarray(starts, dtype=np.int64)
    elapsed_arr = np.asarray(elapsed, dtype=np.float64)
    bpms_arr = np.asarray(bpms, dtype=np.float64)

    def tick_to_second(tick):
        t = max(0.0, float(tick))
        idx = max(0, min(int(np.searchsorted(starts_arr, t, side="right") - 1), len(starts_arr) - 1))
        return float(elapsed_arr[idx] + (t - starts_arr[idx]) * 60.0 / (ticks_per_beat * bpms_arr[idx]))

    return tick_to_second


def _ticks_per_bar(midi) -> int:
    ts = midi.time_signature_changes[0] if midi.time_signature_changes else None
    num = int(ts.numerator) if ts else 4
    den = int(ts.denominator) if ts else 4
    return max(1, int(round(num * midi.ticks_per_beat * 4 / den)))


def _grid_ticks(midi, positions_per_bar: int) -> int:
    return max(1, int(round(_ticks_per_bar(midi) / max(1, positions_per_bar))))


def _onset_voice_vector(midi_path, positions_per_bar: int = 16) -> np.ndarray:
    midi = load_midi(midi_path)
    notes = extract_notes3(midi_path)
    if not notes:
        return np.zeros(0, dtype=np.int64)
    grid = _grid_ticks(midi, positions_per_bar)
    max_tick = max(n.start + n.dur for n in notes)
    n_steps = max(1, int(np.ceil(max_tick / grid)) + 1)
    counts = np.zeros(n_steps, dtype=np.int64)
    for note in notes:
        counts[min(n_steps - 1, int(round(note.start / grid)))] += 1
    return counts


def _binary_onset_bar_matrix(midi_path, positions_per_bar: int = 16) -> np.ndarray:
    counts = _onset_voice_vector(midi_path, positions_per_bar=positions_per_bar)
    if counts.size == 0:
        return np.zeros((1, positions_per_bar), dtype=np.int8)
    n_bars = max(1, int(np.ceil(counts.size / positions_per_bar)))
    padded = np.zeros(n_bars * positions_per_bar, dtype=np.int8)
    padded[:counts.size] = (counts > 0).astype(np.int8)
    return padded.reshape(n_bars, positions_per_bar)


def mean_ioi(midi_path: Union[str, Path]) -> float:
    """Compute mean inter-onset interval (IOI) in seconds.

    Consecutive notes with the same onset contribute zero IOI,
    matching the D3PIA implementation.

    Reference: Standard MIR rhythmic feature; D3PIA implementation.
    URL: https://github.com/jech2/D3PIA

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Mean IOI in seconds (>= 0).
    """
    midi = load_midi(midi_path)
    notes = sorted(extract_notes3(midi_path), key=lambda n: (n.start, n.pitch))
    if len(notes) < 2:
        return 0.0
    t2s = _tick_to_second_mapper(midi)
    onsets = np.asarray([t2s(n.start) for n in notes], dtype=np.float64)
    return float(np.mean(np.diff(onsets)))


def grooving_pattern_similarity(midi_path: Union[str, Path]) -> float:
    """Compute Grooving Pattern Similarity (GS) for a single MIDI file.

    GS measures rhythmic pattern consistency within a piece. Each bar is
    represented as a 64-dimensional binary onset vector (64 positions per
    bar), and GS is computed as the normalized Hamming similarity between
    ALL pairs of bars (not just adjacent bars, unlike MusPy's
    groove_consistency which only compares adjacent bars).

    Formula: GS(b_a, b_b) = 1 - (1/64) * sum(XOR(b_a[i], b_b[i])) for i in 0..63
    The function returns the average GS across all bar pairs.

    Note: MusPy's groove_consistency() only compares adjacent bars
    (groove_patterns[:-1] != groove_patterns[1:]), which differs from
    the Jazz Transformer paper that uses all bar pairs. This implementation
    follows the original paper.

    Reference: Wu and Yang, "The Jazz Transformer," ISMIR 2020.
    URL: https://archives.ismir.net/ismir2020/paper/000339.pdf

    Args:
        midi_path: Path to the MIDI file.

    Returns:
        GS in [0, 1]. Returns 0.0 if fewer than 2 bars.
    """
    bar_matrix = _binary_onset_bar_matrix(midi_path, positions_per_bar=64)
    n_bars = bar_matrix.shape[0]
    if n_bars < 2:
        return 0.0

    sims = []
    for i in range(n_bars):
        for j in range(i + 1, n_bars):
            hamming = np.mean(np.bitwise_xor(bar_matrix[i], bar_matrix[j]))
            sims.append(1.0 - hamming)
    return float(np.mean(sims))


def ngram_diversity(midi_path: Union[str, Path], n: int = 4) -> float:
    """Compute N-gram diversity of pitch-class sequences.

    Formula: Diversity = count(unique n-grams) / count(total n-grams)

    Reference: Yang and Lerch, "On the Evaluation of Generative Models in
    Music," Neural Computing and Applications, 2018.
    URL: https://doi.org/10.1007/s00521-018-3849-7

    Args:
        midi_path: Path to a MIDI file.
        n: N-gram size (default 4).

    Returns:
        Diversity in [0, 1], or NaN if too few notes.
    """
    notes = extract_notes3(midi_path)
    if len(notes) < n:
        return float("nan")
    notes_sorted = sorted(notes, key=lambda x: x.start)
    pc_seq = [n.pitch % 12 for n in notes_sorted]
    if len(pc_seq) < n:
        return float("nan")
    ngrams: set[tuple[int, ...]] = set()
    for i in range(len(pc_seq) - n + 1):
        ngrams.add(tuple(pc_seq[i:i + n]))
    total = len(pc_seq) - n + 1
    return len(ngrams) / total if total > 0 else float("nan")


def empty_beat_rate(midi_path: Union[str, Path]) -> float:
    """Compute the ratio of empty beats (no note sounding).

    Formula: EBR = count(empty beats) / count(total beats)

    Reference: Dong et al., "Pypianoroll," ISMIR 2018 (LBD).
    URL: https://arxiv.org/abs/2008.01951
    Implementation: muspy.empty_beat_rate()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        EBR in [0, 1], or NaN if song length is zero.
    """
    music = muspy.read_midi(str(midi_path))
    return float(muspy.empty_beat_rate(music))


def compute_single(midi_path: Union[str, Path]) -> RhythmicResult:
    """Compute all single-file rhythmic metrics.

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        A RhythmicResult dataclass.
    """
    return RhythmicResult(
        mean_ioi=mean_ioi(midi_path),
        gs=grooving_pattern_similarity(midi_path),
        ngram_div=ngram_diversity(midi_path),
        ebr=empty_beat_rate(midi_path),
    )


def onset_xor_distance(
    pred_path: Union[str, Path],
    ref_path: Union[str, Path],
    positions_per_bar: int = 16,
) -> float:
    """Compute mean XOR distance between aligned binary onset bar matrices.

    The two files are quantised independently to positions_per_bar grid
    positions per bar, padded to the same number of bars, then compared.
    Identical onset patterns score 0; completely opposite patterns score 1.

    Reference: Choi et al., "D3PIA," ICASSP 2026.
    URL: https://github.com/jech2/D3PIA

    Args:
        pred_path: Path to the predicted MIDI file.
        ref_path: Path to the reference MIDI file.
        positions_per_bar: Grid resolution (default 16 = 16th notes).

    Returns:
        XOR distance in [0, 1].
    """
    pred = _binary_onset_bar_matrix(pred_path, positions_per_bar=positions_per_bar)
    ref = _binary_onset_bar_matrix(ref_path, positions_per_bar=positions_per_bar)
    n_bars = max(pred.shape[0], ref.shape[0])

    def _pad(mat):
        if mat.shape[0] == n_bars:
            return mat
        out = np.zeros((n_bars, positions_per_bar), dtype=np.int8)
        out[:mat.shape[0], :] = mat
        return out

    return float(np.mean(np.abs(_pad(pred) - _pad(ref))))


def _midi_to_intervals_pitches(midi_path) -> tuple[np.ndarray, np.ndarray]:
    midi = load_midi(midi_path)
    notes = sorted(extract_notes3(midi_path), key=lambda n: (n.start, n.pitch, n.dur))
    if not notes:
        return np.empty((0, 2), dtype=np.float64), np.empty((0,), dtype=np.float64)
    t2s = _tick_to_second_mapper(midi)
    intervals = np.asarray(
        [[t2s(n.start), t2s(n.start + n.dur)] for n in notes], dtype=np.float64)
    pitches = np.asarray([n.pitch for n in notes], dtype=np.float64)
    valid = intervals[:, 1] > intervals[:, 0]
    return intervals[valid], pitches[valid]


def note_overlap(
    pred_path: Union[str, Path],
    ref_path: Union[str, Path],
    onset_tolerance: float = 0.05,
    offset_ratio: float | None = 0.2,
) -> float:
    """Compute mir_eval transcription average overlap score.

    Reference: Raffel et al., "mir_eval," ISMIR 2014.
    URL: https://github.com/mir-evaluation/mir_eval

    Args:
        pred_path: Predicted MIDI file.
        ref_path: Reference MIDI file.
        onset_tolerance: Onset matching tolerance in seconds.
        offset_ratio: Offset tolerance as note-duration ratio.

    Returns:
        Overlap score in [0, 1].
    """
    try:
        import mir_eval
    except ImportError as exc:
        raise ImportError("note_overlap requires the 'mir-eval' package") from exc

    ref_intervals, ref_pitches = _midi_to_intervals_pitches(ref_path)
    pred_intervals, pred_pitches = _midi_to_intervals_pitches(pred_path)
    if len(ref_pitches) == 0 or len(pred_pitches) == 0:
        return 0.0

    ref_hz = mir_eval.util.midi_to_hz(ref_pitches)
    pred_hz = mir_eval.util.midi_to_hz(pred_pitches)
    _, _, _, overlap = mir_eval.transcription.precision_recall_f1_overlap(
        ref_intervals, ref_hz, pred_intervals, pred_hz,
        onset_tolerance=onset_tolerance, offset_ratio=offset_ratio,
    )
    return float(overlap)
