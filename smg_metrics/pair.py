"""High-level pairwise evaluation entry point.

References:
    Note F1 / Notei F1: https://arxiv.org/abs/2408.15176
    simChr / simgrv: https://arxiv.org/abs/2105.04090
    CA: https://arxiv.org/abs/2410.08435
    CS: https://arxiv.org/abs/2008.07122
    OXD / NOvlp: https://github.com/jech2/D3PIA / https://github.com/mir-evaluation/mir_eval
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Union

from smg_metrics.note_f1 import NoteF1Result, compute_all as _note_all
from smg_metrics.similarity import SimilarityResult, compute_all as _sim_all
from smg_metrics.chord_accuracy import compute_ca
from smg_metrics.chord_similarity import compute_cs
from smg_metrics.rhythm import onset_xor_distance, note_overlap

__all__ = ["PairResult", "pair_eval"]


@dataclass(frozen=True, slots=True)
class PairResult:
    """Container for all 8 pairwise comparison metrics.

    Attributes:
        note_f1:      Note F1 (onset + pitch) in [0, 1].
        notei_f1:     Notei F1 (+ instrument) in [0, 1].
        sim_chr:      Chroma similarity in [0, 1].
        sim_grv:      Groove similarity in [0, 1].
        ca:           Chord Accuracy in [0, 1].
        cs:           Chord Similarity (deep embedding) in [0, 1].
        onset_xor:    Onset-pattern XOR distance in [0, 1].
        note_overlap: mir_eval transcription average overlap in [0, 1].
    """
    note_f1: float
    notei_f1: float
    sim_chr: float
    sim_grv: float
    ca: float
    cs: float
    onset_xor: float
    note_overlap: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def pair_eval(
    pred_path: Union[str, Path],
    ref_path: Union[str, Path],
    enable_cs: bool = True,
) -> PairResult:
    """Evaluate *pred* against *ref* with all 8 pairwise metrics.

    Args:
        pred_path: Path to the predicted / generated MIDI file.
        ref_path:  Path to the reference / ground-truth MIDI file.
        enable_cs: If True (default), compute CS metric. Requires model weights.

    Returns:
        A PairResult dataclass.
    """
    pred_path, ref_path = Path(pred_path), Path(ref_path)
    for p in (pred_path, ref_path):
        if not p.exists():
            raise FileNotFoundError(f"MIDI file not found: {p}")

    note_res = _note_all(pred_path, ref_path)
    sim_res = _sim_all(pred_path, ref_path)
    ca_val = compute_ca(pred_path, ref_path)

    if enable_cs:
        try:
            cs_val = compute_cs(pred_path, ref_path)
        except (ImportError, FileNotFoundError) as e:
            import warnings
            warnings.warn(f"CS metric skipped: {e}", UserWarning)
            cs_val = 0.0
    else:
        cs_val = 0.0

    return PairResult(
        note_f1=note_res.note_f1,
        notei_f1=note_res.notei_f1,
        sim_chr=sim_res.sim_chr,
        sim_grv=sim_res.sim_grv,
        ca=ca_val,
        cs=cs_val,
        onset_xor=onset_xor_distance(pred_path, ref_path),
        note_overlap=note_overlap(pred_path, ref_path),
    )
