"""Shared statistical helpers for smg_metrics.

Only retains histogram_overlap (used by distribution.py).

Reference:
    Overlap area: https://arxiv.org/abs/2012.05168
    Implementation: microsoft/muzic, telemelody/evaluation/cal_similarity.py
"""

from __future__ import annotations

import numpy as np

__all__ = ["histogram_overlap"]


def histogram_overlap(hist_a: np.ndarray, hist_b: np.ndarray) -> float:
    """Compute overlap area between two (un-)normalised histograms.

    Formula: overlap = sum(min(norm_a[i], norm_b[i])) for all i,
    where norm_a and norm_b are L1-normalised versions of hist_a and hist_b.

    Reference: Ren et al., "SongMASS," ACM-MM 2020.
    URL: https://arxiv.org/abs/2012.05168
    Implementation: microsoft/muzic, telemelody/evaluation/cal_similarity.py

    Args:
        hist_a: First histogram (numpy array).
        hist_b: Second histogram (numpy array, same shape).

    Returns:
        Overlap area in [0, 1]. Returns 0.0 if either histogram sums to 0.
    """
    sum_a = np.sum(hist_a)
    sum_b = np.sum(hist_b)
    if sum_a == 0 or sum_b == 0:
        return 0.0
    norm_a = hist_a.astype(np.float64) / sum_a
    norm_b = hist_b.astype(np.float64) / sum_b
    return float(np.sum(np.minimum(norm_a, norm_b)))
