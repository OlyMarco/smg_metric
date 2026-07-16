"""Distribution-level evaluation metrics for symbolic music generation.

Implements pairwise metrics that compare feature distributions between
predicted and reference MIDI files, following the evaluation methodology
from Microsoft Research (muzic) and related works.

Metrics:
    PD  Pitch Distribution similarity (overlap area)
    DD  Duration Distribution similarity (overlap area)

References:
    PD/DD: https://arxiv.org/abs/2012.05168
    Implementation: https://github.com/microsoft/muzic
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Union

import numpy as np

from smg_metrics._io import Note3, extract_notes3
from smg_metrics._stats import histogram_overlap

__all__ = ["DistributionResult", "compute_all"]

# ── Data container ────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class DistributionResult:
    """Container for distribution-level pairwise metrics.

    Attributes:
        pd: Pitch Distribution similarity in [0, 1].
        dd: Duration Distribution similarity in [0, 1].
    """
    pd: float
    dd: float

    def to_dict(self) -> dict[str, float]:
        """Return metrics as a plain dict."""
        return asdict(self)


# ── Histogram helpers ─────────────────────────────────────────────


def _pitch_distribution(notes: list[Note3]) -> np.ndarray:
    """128-bin pitch histogram from note list."""
    hist = np.zeros(128, dtype=np.float64)
    for n in notes:
        if 0 <= n.pitch < 128:
            hist[n.pitch] += 1.0
    return hist


def _duration_distribution(notes: list[Note3], n_bins: int = 64) -> np.ndarray:
    """Duration histogram (quantised to ticks, mapped to bins)."""
    if not notes:
        return np.zeros(n_bins, dtype=np.float64)
    durs = [n.dur for n in notes]
    min_dur = max(1, min(durs))
    hist = np.zeros(n_bins, dtype=np.float64)
    for n in notes:
        idx = min(int(n.dur / min_dur) - 1, n_bins - 1)
        hist[idx] += 1.0
    return hist


# ── Public API ────────────────────────────────────────────────────


def compute_all(
    pred_path: Union[str, Path],
    ref_path: Union[str, Path],
) -> DistributionResult:
    """Compute all distribution-level metrics between *pred* and *ref*.

    Metrics: PD, DD.

    Args:
        pred_path: Path to the predicted / generated MIDI file.
        ref_path:  Path to the reference / ground-truth MIDI file.

    Returns:
        A DistributionResult dataclass.

    Raises:
        FileNotFoundError: If either file does not exist.
    """
    pred_path, ref_path = Path(pred_path), Path(ref_path)
    for p in (pred_path, ref_path):
        if not p.exists():
            raise FileNotFoundError(f"MIDI file not found: {p}")

    pred_notes = extract_notes3(pred_path)
    ref_notes = extract_notes3(ref_path)

    pd_val = histogram_overlap(_pitch_distribution(ref_notes), _pitch_distribution(pred_notes))
    dd_val = histogram_overlap(_duration_distribution(ref_notes), _duration_distribution(pred_notes))

    return DistributionResult(
        pd=pd_val,
        dd=dd_val,
    )
