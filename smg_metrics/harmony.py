"""Harmony and tonality metrics (single-file).

Consolidates all single-file harmony/tonality metrics from MusPy, FGG,
C-RNN-GAN, Jazz Transformer, and Papadopoulos and Peeters.

Metrics:
    PCE  Pitch Class Entropy (Jazz Transformer, ISMIR 2020)
    SC   Scale Consistency (C-RNN-GAN, NeurIPS-W 2016)
    PISR Pitch-in-Scale Rate (MuseGAN, AAAI 2018)
    OOK  Out-of-Key Fraction (FGG, ICML 2025)
    CHE  Chord Histogram Entropy (Papadopoulos and Peeters, ISMIR 2012)

All single-file metrics take a single MIDI path and return a float.
No reference file is needed.

References:
    PCE: https://archives.ismir.net/ismir2020/paper/000339.pdf
    SC:  https://arxiv.org/abs/1611.09904
    PISR: https://arxiv.org/abs/1709.06298
    OOK: https://arxiv.org/abs/2410.08435
    CHE: https://hal.science/hal-00726774
    MusPy: https://arxiv.org/abs/2008.01951
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Union

import numpy as np
import muspy
import miditoolkit

from smg_metrics._io import Note3, extract_notes3, load_midi

__all__ = [
    "HarmonySingleResult",
    "compute_all",
    "pitch_class_entropy",
    "scale_consistency",
    "pitch_in_scale_rate",
    "out_of_key_fraction",
    "chord_histogram_entropy",
]


@dataclass(frozen=True, slots=True)
class HarmonySingleResult:
    """Container for 5 single-file harmony metrics.

    Attributes:
        pce: Pitch Class Entropy in [0, 3.585]. Lower means more tonal focus.
        sc: Scale Consistency in [0, 1]. Higher means better key adherence.
        pisr: Pitch-in-Scale Rate in [0, 1]. Higher means more in-scale notes.
        ook: Out-of-Key Fraction in [0, 1]. Lower means fewer out-of-key notes.
        che: Chord Histogram Entropy in [0, log2(C)]. Higher means more chord diversity.
    """
    pce: float
    sc: float
    pisr: float
    ook: float
    che: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def pitch_class_entropy(midi_path: Union[str, Path]) -> float:
    """Compute the Shannon entropy of the 12-bin pitch-class histogram.

    Formula: PCE = -sum(P(i) * log2(P(i))) for i in 0..11,
    where P(i) is the proportion of notes in pitch class i.

    Reference: Wu and Yang, "The Jazz Transformer," ISMIR 2020.
    URL: https://archives.ismir.net/ismir2020/paper/000339.pdf
    Implementation: muspy.pitch_class_entropy()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        PCE in [0, 3.585], or NaN if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return float(muspy.pitch_class_entropy(music))


def scale_consistency(midi_path: Union[str, Path]) -> float:
    """Compute the largest pitch-in-scale rate over all 24 major/minor scales.

    Formula: SC = max over (root, mode) of PISR(root, mode).

    Reference: Mogren, "C-RNN-GAN," NeurIPS Workshop 2016.
    URL: https://arxiv.org/abs/1611.09904
    Implementation: muspy.scale_consistency()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        SC in [0, 1], or NaN if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return float(muspy.scale_consistency(music))


def pitch_in_scale_rate(
    midi_path: Union[str, Path],
    root: int = 0,
    mode: str = "major",
) -> float:
    """Compute the ratio of notes that belong to a given musical scale.

    Formula: PISR = count(notes in scale) / count(total notes).

    Reference: Dong et al., "MuseGAN," AAAI 2018.
    URL: https://arxiv.org/abs/1709.06298
    MusPy documentation explicitly cites MuseGAN.
    Implementation: muspy.pitch_in_scale_rate()

    Args:
        midi_path: Path to a MIDI file.
        root: Root pitch class (0=C, ..., 11=B).
        mode: "major" or "minor".

    Returns:
        PISR in [0, 1], or NaN if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return float(muspy.pitch_in_scale_rate(music, root, mode))


_MAJOR_SCALE = np.array([0, 2, 4, 5, 7, 9, 11])
_MINOR_SCALE = np.array([0, 2, 3, 5, 7, 8, 10])
_PITCH_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
_KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def _detect_key(notes: list) -> tuple[int, str]:
    """Detect key using Krumhansl-Schmuckler algorithm."""
    if not notes:
        return (0, 'major')
    pc_hist = np.zeros(12)
    for note in notes:
        pc_hist[note.pitch % 12] += (note.end - note.start)
    total = pc_hist.sum()
    if total > 0:
        pc_hist /= total
    best_corr, best_tonic, best_mode = -1.0, 0, 'major'
    for tonic in range(12):
        rotated = np.roll(pc_hist, -tonic)
        for profile, mode in [(_KK_MAJOR, 'major'), (_KK_MINOR, 'minor')]:
            corr = float(np.corrcoef(rotated, profile)[0, 1])
            if corr > best_corr:
                best_corr, best_tonic, best_mode = corr, tonic, mode
    return (best_tonic, best_mode)


def out_of_key_fraction(
    midi_path: Union[str, Path],
    step_resolution: int = 4,
) -> float:
    """Compute the fraction of 16th-note steps containing out-of-key notes.

    Reference: Zhu et al., "FGG," ICML 2025.
    URL: https://arxiv.org/abs/2410.08435
    Original quote: "the percentage of steps in the generated sequences
    containing at least one out-of-key note, where each step corresponds
    to a 16th note."

    Uses Krumhansl-Schmuckler key detection to determine the key, then
    checks each 16th-note step for any note outside the detected scale.

    Args:
        midi_path: Path to a MIDI file.
        step_resolution: Steps per quarter note (4 = 16th notes).

    Returns:
        OOK fraction in [0, 1].
    """
    midi = miditoolkit.MidiFile(str(midi_path))
    notes = [n for inst in midi.instruments if not inst.is_drum for n in inst.notes]
    if not notes:
        return 0.0
    tonic, mode = _detect_key(notes)
    scale = _MINOR_SCALE if mode == 'minor' else _MAJOR_SCALE
    in_key = set((tonic + d) % 12 for d in scale)
    tpq = midi.ticks_per_beat
    tp_step = max(1, tpq // step_resolution)
    start_tick = min(n.start for n in notes)
    end_tick = max(n.end for n in notes)
    n_steps = max(1, (end_tick - start_tick + tp_step - 1) // tp_step)
    has_ook = np.zeros(n_steps, dtype=bool)
    for note in notes:
        if note.pitch % 12 not in in_key:
            s = max(0, (note.start - start_tick) // tp_step)
            e = min(n_steps - 1, (note.end - start_tick) // tp_step)
            has_ook[s:e + 1] = True
    return float(has_ook.mean())


_CHORD_TEMPLATES: dict[str, list[int]] = {
    "maj": [0, 4, 7], "min": [0, 3, 7], "dim": [0, 3, 6],
    "aug": [0, 4, 8], "7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10], "dim7": [0, 3, 6, 9],
    "sus4": [0, 5, 7], "sus2": [0, 2, 7],
}


def _classify_chord(chroma: np.ndarray) -> str:
    """Classify a 12-dim chroma vector via template matching."""
    if chroma.sum() < 1:
        return "N"
    normed = chroma / (np.linalg.norm(chroma) + 1e-12)
    best_score, best_label = 0.0, "N"
    for root in range(12):
        for kind, intervals in _CHORD_TEMPLATES.items():
            tmpl = np.zeros(12)
            for iv in intervals:
                tmpl[(root + iv) % 12] = 1.0
            tmpl /= np.linalg.norm(tmpl) + 1e-12
            score = float(np.dot(normed, tmpl))
            if score > best_score:
                best_score, best_label = score, f"{root}:{kind}"
    return best_label if best_score >= 0.5 else "N"


def chord_histogram_entropy(midi_path: Union[str, Path]) -> float:
    """Compute the Shannon entropy of the chord-type histogram.

    Extracts chords per bar using chroma template matching, builds a
    histogram of chord types, and computes its Shannon entropy.

    Formula: CHE = -sum(p(c) * log2(p(c))) over all chord types c,
    where p(c) is the proportion of bars with chord type c.

    Reference: Papadopoulos and Peeters, "Large-scale Study of Chord
    Estimation Algorithms Based on Chroma," ISMIR 2012.
    URL: https://hal.science/hal-00726774

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        CHE in bits, or NaN if no chords found.
    """
    notes = extract_notes3(midi_path)
    if not notes:
        return float("nan")
    midi = load_midi(midi_path)
    tp_bar = max(1, midi.ticks_per_beat * 4)
    max_tick = max(n.start + n.dur for n in notes)
    n_bars = max(1, max_tick // tp_bar + 1)
    bar_chroma = np.zeros((n_bars, 12), dtype=np.float64)
    for n in notes:
        bar = n.start // tp_bar
        if 0 <= bar < n_bars:
            bar_chroma[bar, n.pitch % 12] += 1.0
    counts: dict[str, int] = {}
    for b in range(n_bars):
        label = _classify_chord(bar_chroma[b])
        counts[label] = counts.get(label, 0) + 1
    counts.pop("N", None)
    total = sum(counts.values())
    if total == 0:
        return float("nan")
    return float(-sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0))


def compute_all(
    midi_path: Union[str, Path],
    root: int = 0,
    mode: str = "major",
) -> HarmonySingleResult:
    """Compute all 5 single-file harmony metrics.

    Args:
        midi_path: Path to a MIDI file.
        root: Root pitch class for PISR (0=C).
        mode: Scale mode for PISR ("major" or "minor").

    Returns:
        A HarmonySingleResult dataclass.
    """
    return HarmonySingleResult(
        pce=pitch_class_entropy(midi_path),
        sc=scale_consistency(midi_path),
        pisr=pitch_in_scale_rate(midi_path, root, mode),
        ook=out_of_key_fraction(midi_path),
        che=chord_histogram_entropy(midi_path),
    )
