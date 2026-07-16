"""Polyphony and quality metrics (single-file).

Consolidates 6 single-file quality metrics from MuseGAN and MusPy.

Metrics:
    Polyphony      Average concurrent pitches (MuseGAN, AAAI 2018)
    Polyphony Rate Ratio of multi-pitch timesteps (MuseGAN, AAAI 2018)
    Pitch Entropy  128-bin Shannon entropy (MusPy, ISMIR 2020)
    Pitch Range    Highest minus lowest MIDI pitch (MusPy, ISMIR 2020)
    N_p            Unique pitches used (MusPy, ISMIR 2020)
    N_pc           Unique pitch classes used (MusPy, ISMIR 2020)

All metrics are computed via MusPy library functions. MusPy documentation
explicitly cites MuseGAN (AAAI 2018) for polyphony and polyphony_rate.

References:
    MuseGAN: https://arxiv.org/abs/1709.06298
    MusPy: https://arxiv.org/abs/2008.01951
    MusPy docs: https://salu133445.github.io/muspy/metrics.html
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Union

import muspy

__all__ = [
    "QualityResult",
    "compute_all",
    "polyphony",
    "polyphony_rate",
    "pitch_entropy",
    "pitch_range",
    "n_pitches_used",
    "n_pitch_classes_used",
]


@dataclass(frozen=True, slots=True)
class QualityResult:
    """Container for 6 single-file polyphony/quality metrics.

    Attributes:
        polyphony: Average concurrent pitches in [1, inf).
        polyphony_rate: Ratio of multi-pitch timesteps in [0, 1].
        pitch_entropy: 128-bin pitch histogram entropy in [0, 7].
        pitch_range: Highest minus lowest MIDI pitch in [0, 127].
        n_pitches_used: Unique MIDI pitches in [0, 128].
        n_pitch_classes_used: Unique pitch classes in [0, 12].
    """
    polyphony: float
    polyphony_rate: float
    pitch_entropy: float
    pitch_range: int
    n_pitches_used: int
    n_pitch_classes_used: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def _safe_float(fn, *args, **kwargs) -> float:
    try:
        val = fn(*args, **kwargs)
        return val if not math.isnan(val) else float("nan")
    except Exception:
        return float("nan")


def _safe_int(fn, *args, **kwargs) -> int:
    try:
        return fn(*args, **kwargs)
    except Exception:
        return -1


def polyphony(midi_path: Union[str, Path]) -> float:
    """Compute the average number of pitches played concurrently.

    Formula: Polyphony = sum(pitches at active timesteps) / count(active timesteps)

    Reference: Dong et al., "MuseGAN," AAAI 2018.
    URL: https://arxiv.org/abs/1709.06298
    MusPy documentation explicitly cites MuseGAN.
    Implementation: muspy.polyphony()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Polyphony >= 1, or NaN if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return _safe_float(muspy.polyphony, music)


def polyphony_rate(midi_path: Union[str, Path]) -> float:
    """Compute the ratio of timesteps where multiple pitches are on.

    Formula: PR = count(timesteps with >= 2 pitches) / count(total timesteps)

    Reference: Dong et al., "MuseGAN," AAAI 2018 (called 'polyphonicity').
    URL: https://arxiv.org/abs/1709.06298
    MusPy documentation explicitly cites MuseGAN.
    Implementation: muspy.polyphony_rate()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        PR in [0, 1], or NaN if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return _safe_float(muspy.polyphony_rate, music)


def pitch_entropy(midi_path: Union[str, Path]) -> float:
    """Compute the Shannon entropy of the 128-bin pitch histogram.

    Formula: PE = -sum(P(i) * log2(P(i))) for i in 0..127

    Reference: Dong et al., "MusPy," ISMIR 2020.
    URL: https://arxiv.org/abs/2008.01951
    Implementation: muspy.pitch_entropy()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        PE in [0, 7], or NaN if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return _safe_float(muspy.pitch_entropy, music)


def pitch_range(midi_path: Union[str, Path]) -> int:
    """Compute the pitch range (highest minus lowest MIDI pitch).

    Reference: Dong et al., "MusPy," ISMIR 2020.
    URL: https://arxiv.org/abs/2008.01951
    Implementation: muspy.pitch_range()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Pitch range in [0, 127], or 0 if no notes.
    """
    music = muspy.read_midi(str(midi_path))
    return _safe_int(muspy.pitch_range, music)


def n_pitches_used(midi_path: Union[str, Path]) -> int:
    """Compute the number of unique MIDI pitches used.

    Reference: Dong et al., "MusPy," ISMIR 2020.
    URL: https://arxiv.org/abs/2008.01951
    Implementation: muspy.n_pitches_used()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Unique pitch count in [0, 128].
    """
    music = muspy.read_midi(str(midi_path))
    return _safe_int(muspy.n_pitches_used, music)


def n_pitch_classes_used(midi_path: Union[str, Path]) -> int:
    """Compute the number of unique pitch classes used.

    Reference: Dong et al., "MusPy," ISMIR 2020.
    URL: https://arxiv.org/abs/2008.01951
    Implementation: muspy.n_pitch_classes_used()

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Unique pitch class count in [0, 12].
    """
    music = muspy.read_midi(str(midi_path))
    return _safe_int(muspy.n_pitch_classes_used, music)


def compute_all(midi_path: Union[str, Path]) -> QualityResult:
    """Compute all 6 single-file quality metrics.

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        A QualityResult dataclass.
    """
    return QualityResult(
        polyphony=polyphony(midi_path),
        polyphony_rate=polyphony_rate(midi_path),
        pitch_entropy=pitch_entropy(midi_path),
        pitch_range=pitch_range(midi_path),
        n_pitches_used=n_pitches_used(midi_path),
        n_pitch_classes_used=n_pitch_classes_used(midi_path),
    )
