from __future__ import annotations

from smg_metrics.single import single_file, SingleFileResult, single_file_structural
from smg_metrics.pair import pair_eval, PairResult, pair_eval_structural
from smg_metrics.chord_accuracy import compute_ca, midi_to_chords
from smg_metrics.distribution import DistributionResult, compute_all as distribution_eval
from smg_metrics.advanced import AdvancedResult, compute_all as advanced_eval
from smg_metrics.structural import (
    StructuralSingleResult,
    StructuralPairResult,
    chord_histogram_entropy,
    ngram_diversity,
    melody_matchness,
    tonal_distance,
)
from smg_metrics import muspy_ext
from smg_metrics import note_f1
from smg_metrics import similarity
from smg_metrics import chord_accuracy
from smg_metrics import distribution
from smg_metrics import advanced
from smg_metrics import structural

__all__ = [
    # High-level API
    "single_file",
    "single_file_structural",
    "pair_eval",
    "pair_eval_structural",
    "distribution_eval",
    "advanced_eval",
    # Result containers
    "SingleFileResult",
    "PairResult",
    "DistributionResult",
    "AdvancedResult",
    "StructuralSingleResult",
    "StructuralPairResult",
    # Individual metrics
    "compute_ca",
    "midi_to_chords",
    "chord_histogram_entropy",
    "ngram_diversity",
    "melody_matchness",
    "tonal_distance",
    # Low-level modules
    "muspy_ext",
    "note_f1",
    "similarity",
    "chord_accuracy",
    "distribution",
    "advanced",
    "structural",
]

__version__ = "0.3.0"
