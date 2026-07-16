"""High-level single-file evaluation entry point.

References:
    - Harmony: PCE/SC/PISR (Jazz Transformer, C-RNN-GAN, MuseGAN) +
                OOK (FGG) + CHE (Yeh et al.)
    - Rhythm: IOI/GS/Ngram/EBR (D3PIA, Jazz Transformer, Yang & Lerch, MusPy)
    - Quality: Poly/PR/PE/Range/Np/Npc (MuseGAN, MusPy)
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from smg_metrics.harmony import HarmonySingleResult, compute_all as _harmony_all
from smg_metrics.rhythm import RhythmicResult, compute_single as _rhythm_single
from smg_metrics.quality import QualityResult, compute_all as _quality_all

__all__ = [
    "single_file_harmony",
    "single_file_rhythm",
    "single_file_quality",
    "HarmonySingleResult",
    "RhythmicResult",
    "QualityResult",
]


def single_file_harmony(
    midi_path: Union[str, Path],
    root: int = 0,
    mode: str = "major",
) -> HarmonySingleResult:
    """Evaluate a single MIDI file with 5 harmony metrics (PCE, SC, PISR, OOK, CHE).

    Args:
        midi_path: Path to a MIDI file.
        root: Root pitch class for PISR (0=C).
        mode: ``"major"`` or ``"minor"``.

    Returns:
        A HarmonySingleResult dataclass.
    """
    return _harmony_all(midi_path, root=root, mode=mode)


def single_file_rhythm(
    midi_path: Union[str, Path],
) -> RhythmicResult:
    """Evaluate a single MIDI file with 4 rhythm metrics (IOI, GS, Ngram, EBR).

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        A RhythmicResult dataclass.
    """
    return _rhythm_single(midi_path)


def single_file_quality(
    midi_path: Union[str, Path],
) -> QualityResult:
    """Evaluate a single MIDI file with 6 quality metrics (Poly, PR, PE, Range, Np, Npc).

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        A QualityResult dataclass.
    """
    return _quality_all(midi_path)
