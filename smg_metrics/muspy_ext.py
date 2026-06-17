"""MusPy single-file quality metrics.

Wraps 13 MusPy metrics that evaluate a MIDI file without any reference.

References:
    - PCE / GS: Wu & Yang, "The Jazz Transformer," ISMIR 2020.
    - EBR: Dong et al., "Pypianoroll," ISMIR 2018 (LBD).
    - SC: Mogren, "C-RNN-GAN," NeurIPS Workshop 2016.
    - PISR / PR / EMR / DPC: Dong et al., "MuseGAN," AAAI 2018.
    - Others: MusPy toolkit, Dong et al., ISMIR 2020.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Union

import muspy

__all__ = ["SingleFileResult", "compute_all"]


@dataclass(frozen=True, slots=True)
class SingleFileResult:
    """Container for 13 single-file quality metrics.

    Attributes:
        pce:  Pitch Class Entropy — [0, log2(12)].
              Reference: Wu & Yang, "The Jazz Transformer," ISMIR 2020.
        ebr:  Empty Beat Rate — [0, 1].
              Reference: Dong et al., "Pypianoroll," ISMIR 2018.
        gs:   Groove Consistency — [0, 1].
              Reference: Wu & Yang, "The Jazz Transformer," ISMIR 2020.
        sc:   Scale Consistency — [0, 1].
              Reference: Mogren, "C-RNN-GAN," NeurIPS Workshop 2016.
        pisr: Pitch-in-Scale Rate (major, root=C) — [0, 1].
              Reference: Dong et al., "MuseGAN," AAAI 2018.
        polyphony: Average concurrent pitches — [1, inf).
              Reference: Dong et al., "MuseGAN," AAAI 2018.
        polyphony_rate: Ratio of multi-pitch timesteps — [0, 1].
              Reference: Dong et al., "MuseGAN," AAAI 2018.
        pitch_range: Highest - lowest MIDI pitch — [0, 127].
              Reference: MusPy, Dong et al., ISMIR 2020.
        n_pitches_used: Number of unique pitches — [0, 128].
              Reference: MusPy, Dong et al., ISMIR 2020.
        n_pitch_classes_used: Number of unique pitch classes — [0, 12].
              Reference: MusPy, Dong et al., ISMIR 2020.
        emr:  Empty Measure Rate — [0, 1].
              Reference: Dong et al., "MuseGAN," AAAI 2018.
        pe:   Pitch Entropy (128-bin) — [0, 7].
              Reference: MusPy, Dong et al., ISMIR 2020.
        dpc:  Drum Pattern Consistency — [0, 1].
              Reference: Dong et al., "MuseGAN," AAAI 2018.
    """
    pce: float
    ebr: float
    gs: float
    sc: float
    pisr: float
    polyphony: float
    polyphony_rate: float
    pitch_range: int
    n_pitches_used: int
    n_pitch_classes_used: int
    emr: float
    pe: float
    dpc: float

    def to_dict(self) -> dict[str, float | int]:
        """Return metrics as a plain dict."""
        return asdict(self)


def _safe_float(fn, *args, **kwargs) -> float:
    """Call *fn*, return NaN on any failure."""
    try:
        val = fn(*args, **kwargs)
        return val if not math.isnan(val) else float("nan")
    except Exception:
        return float("nan")


def _safe_int(fn, *args, **kwargs) -> int:
    """Call *fn*, return -1 on failure."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return -1


def compute_all(
    midi_path: Union[str, Path],
    root: int = 0,
    mode: str = "major",
) -> SingleFileResult:
    """Compute all 12 single-file MusPy metrics for *midi_path*.

    Args:
        midi_path: Path to a MIDI file.
        root: Root pitch class for ``pitch_in_scale_rate`` (0=C, …, 11=B).
        mode: ``"major"`` or ``"minor"``.

    Returns:
        A :class:`SingleFileResult` with all 12 metrics.

    Raises:
        FileNotFoundError: If *midi_path* does not exist.
        ValueError: If *mode* is not ``"major"`` or ``"minor"``.
    """
    midi_path = Path(midi_path)
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    if mode not in ("major", "minor"):
        raise ValueError(f"mode must be 'major' or 'minor', got '{mode}'")

    music = muspy.read_midi(str(midi_path))
    res = music.resolution  # ticks per quarter note

    # 4/4 assumption for measure-based metrics (Groove, EMR).
    # MusPy docs: "only works for songs with a constant time signature."
    measure_res = res * 4

    return SingleFileResult(
        pce=_safe_float(muspy.pitch_class_entropy, music),
        ebr=_safe_float(muspy.empty_beat_rate, music),
        gs=_safe_float(muspy.groove_consistency, music, measure_res),
        sc=_safe_float(muspy.scale_consistency, music),
        pisr=_safe_float(muspy.pitch_in_scale_rate, music, root, mode),
        polyphony=_safe_float(muspy.polyphony, music),
        polyphony_rate=_safe_float(muspy.polyphony_rate, music),
        pitch_range=_safe_int(muspy.pitch_range, music),
        n_pitches_used=_safe_int(muspy.n_pitches_used, music),
        n_pitch_classes_used=_safe_int(muspy.n_pitch_classes_used, music),
        emr=_safe_float(muspy.empty_measure_rate, music, measure_res),
        pe=_safe_float(muspy.pitch_entropy, music),
        dpc=_safe_float(muspy.drum_pattern_consistency, music),
    )
