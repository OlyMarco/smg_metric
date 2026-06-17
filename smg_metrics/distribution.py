"""Distribution-level evaluation metrics for symbolic music generation.

Implements pairwise metrics that compare feature distributions between
predicted and reference MIDI files, following the evaluation methodology
from Microsoft Research (muzic) and related works.

Metrics:
    PD  — Pitch Distribution similarity (overlap area)
    DD  — Duration Distribution similarity (overlap area)
    OOK — Out-of-Key Rate (percentage of 16th-note steps with out-of-key notes)
    SC_sim — Scale Consistency Similarity (|SC_pred - SC_ref|)
    PCE_sim — Pitch Class Entropy Similarity (|PCE_pred - PCE_ref|)
    GS_sim  — Groove Consistency Similarity (|GS_pred - GS_ref|)

References:
    - PD/DD: SongMASS (Ren et al., ACM-MM 2020) and TeleMelody
      (microsoft/muzic, telemelody/evaluation/cal_similarity.py).
    - OOK: FGG (Zhu et al., ICML 2025, arXiv:2410.08435).
    - SC/PCE/GS_sim: Variants of MusPy single-file metrics,
      converted to pairwise similarity by taking absolute difference.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Union

import numpy as np
import muspy

from smg_metrics._io import Note3, extract_notes3, load_midi, ticks_per_16th
from smg_metrics._stats import histogram_overlap

__all__ = ["DistributionResult", "compute_all"]

# ── Pitch-class set for major/minor keys (for OOK) ────────────────

_MAJOR_SCALE_PCS = {0, 2, 4, 5, 7, 9, 11}  # C major
_MINOR_SCALE_PCS = {0, 2, 3, 5, 7, 8, 10}  # A minor

# ── Data container ────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class DistributionResult:
    """Container for distribution-level pairwise metrics.

    Attributes:
        pd:     Pitch Distribution similarity — [0, 1].
                Reference: Ren et al., "SongMASS," ACM-MM 2020.
        dd:     Duration Distribution similarity — [0, 1].
                Reference: Ren et al., "SongMASS," ACM-MM 2020.
        ook:    Out-of-Key Rate — [0, 1].
                Reference: Zhu et al., "FGG," ICML 2025.
        sc_sim: Scale Consistency Similarity — [0, 1].
                Reference: MusPy, Dong et al., ISMIR 2020.
        pce_sim: Pitch Class Entropy Similarity — [0, 1].
                Reference: MusPy, Dong et al., ISMIR 2020.
        gs_sim: Groove Consistency Similarity — [0, 1].
                Reference: Wu & Yang, "Jazz Transformer," ISMIR 2020.
    """
    pd: float
    dd: float
    ook: float
    sc_sim: float
    pce_sim: float
    gs_sim: float

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


# ── OOK ───────────────────────────────────────────────────────────


def _out_of_key_rate(
    notes: list[Note3],
    midi_path: str | Path,
    key_pcs: set[int] | None = None,
) -> float:
    """Compute Out-of-Key Rate on a 16th-note grid.

    Reference:
        Zhu et al., "FGG," ICML 2025, arXiv:2410.08435.

    Args:
        notes:     Notes extracted by :func:`~smg_metrics._io.extract_notes3`.
        midi_path: Path to the MIDI file (needed for ticks_per_beat).
        key_pcs:   Pitch classes of the target key.  If ``None``, auto-detects
                   the best-fitting key across all 24 major / minor keys.

    Returns:
        Out-of-Key Rate in [0, 1].
    """
    midi = load_midi(midi_path)
    tp16 = ticks_per_16th(midi)

    if key_pcs is None:
        music = muspy.read_midi(str(midi_path))
        best_score = -1.0
        best_pcs = _MAJOR_SCALE_PCS
        for root in range(12):
            for mode, tpl in [("major", _MAJOR_SCALE_PCS), ("minor", _MINOR_SCALE_PCS)]:
                score = muspy.pitch_in_scale_rate(music, root, mode)
                if score != score:
                    continue
                if score > best_score:
                    best_score = score
                    best_pcs = {(p + root) % 12 for p in tpl}
        key_pcs = best_pcs

    if not notes:
        return 0.0

    max_tick = max(n.start + n.dur for n in notes)
    n_steps = max(1, max_tick // tp16 + 1)

    step_has_ook = np.zeros(n_steps, dtype=bool)
    step_has_note = np.zeros(n_steps, dtype=bool)
    for n in notes:
        s = n.start // tp16
        e = min((n.start + n.dur) // tp16 + 1, n_steps)
        step_has_note[s:e] = True
        if n.pitch % 12 not in key_pcs:
            step_has_ook[s:e] = True

    total_active = int(np.sum(step_has_note))
    if total_active == 0:
        return 0.0
    return float(np.sum(step_has_ook & step_has_note)) / float(total_active)


# ── Single-file similarity variants ──────────────────────────────


def _sc_sim(pred_path: str | Path, ref_path: str | Path) -> float:
    """Scale Consistency Similarity: 1 − |SC_pred − SC_ref|.

    Reference: MusPy, Dong et al., ISMIR 2020.
    """
    p = muspy.read_midi(str(pred_path))
    r = muspy.read_midi(str(ref_path))
    sc_p = muspy.scale_consistency(p)
    sc_r = muspy.scale_consistency(r)
    if sc_p != sc_p or sc_r != sc_r:
        return float("nan")
    return 1.0 - abs(sc_p - sc_r)


def _pce_sim(pred_path: str | Path, ref_path: str | Path) -> float:
    """Pitch Class Entropy Similarity: 1 − |PCE_pred − PCE_ref| / log₂(12).

    Reference: MusPy, Dong et al., ISMIR 2020.
    """
    p = muspy.read_midi(str(pred_path))
    r = muspy.read_midi(str(ref_path))
    pce_p = muspy.pitch_class_entropy(p)
    pce_r = muspy.pitch_class_entropy(r)
    if pce_p != pce_p or pce_r != pce_r:
        return float("nan")
    return 1.0 - abs(pce_p - pce_r) / np.log2(12)


def _gs_sim(pred_path: str | Path, ref_path: str | Path) -> float:
    """Groove Consistency Similarity: 1 − |GS_pred − GS_ref|.

    Reference: Wu & Yang, "The Jazz Transformer," ISMIR 2020.
    """
    p = muspy.read_midi(str(pred_path))
    r = muspy.read_midi(str(ref_path))
    gs_p = muspy.groove_consistency(p, p.resolution * 4)
    gs_r = muspy.groove_consistency(r, r.resolution * 4)
    if gs_p != gs_p or gs_r != gs_r:
        return float("nan")
    return 1.0 - abs(gs_p - gs_r)


# ── Public API ────────────────────────────────────────────────────


def compute_all(
    pred_path: Union[str, Path],
    ref_path: Union[str, Path],
    key_pcs: set[int] | None = None,
) -> DistributionResult:
    """Compute all distribution-level metrics between *pred* and *ref*.

    Args:
        pred_path: Path to the predicted / generated MIDI file.
        ref_path:  Path to the reference / ground-truth MIDI file.
        key_pcs:   Pitch classes for OOK calculation.  If ``None``,
                   auto-detects the best-fitting key across all 24
                   major / minor keys.

    Returns:
        A :class:`DistributionResult`.

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
    ook_val = _out_of_key_rate(pred_notes, pred_path, key_pcs=key_pcs)

    return DistributionResult(
        pd=pd_val,
        dd=dd_val,
        ook=ook_val,
        sc_sim=_sc_sim(pred_path, ref_path),
        pce_sim=_pce_sim(pred_path, ref_path),
        gs_sim=_gs_sim(pred_path, ref_path),
    )
