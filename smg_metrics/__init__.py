from __future__ import annotations

from smg_metrics.single import (
    SingleFileResult,
    single_file,
    single_file_structural,
    single_file_rhythmic,
)
from smg_metrics.pair import pair_eval, PairResult, pair_eval_structural
from smg_metrics.chord_accuracy import compute_ca, midi_to_chords, midi_to_chords_dp
from smg_metrics.chord_recognition import recognize_chords, recognize_chords_beat
from smg_metrics.chord_similarity import compute_cs, extract_chord_vectors
from smg_metrics.out_of_key import compute_ook, compute_ook_percentage
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
from smg_metrics.rhythmic import (
    RhythmicResult,
    mean_ioi,
    rhythmic_intensity,
    rhythmic_density,
    voice_number,
    onset_xor_distance,
    note_overlap,
    grooving_pattern_similarity,
)
from smg_metrics import muspy_ext
from smg_metrics import note_f1
from smg_metrics import similarity
from smg_metrics import chord_accuracy
from smg_metrics import chord_recognition
from smg_metrics import distribution
from smg_metrics import advanced
from smg_metrics import structural
from smg_metrics import rhythmic
from smg_metrics import chord_similarity
from smg_metrics import out_of_key

__all__ = [
    # High-level API
    "single_file",
    "single_file_structural",
    "single_file_rhythmic",
    "pair_eval",
    "pair_eval_structural",
    "distribution_eval",
    "advanced_eval",
    # Result containers
    "SingleFileResult",
    "RhythmicResult",
    "PairResult",
    "DistributionResult",
    "AdvancedResult",
    "StructuralSingleResult",
    "StructuralPairResult",
    # Individual metrics
    "compute_ca",
    "midi_to_chords",
    "midi_to_chords_dp",
    "recognize_chords",
    "recognize_chords_beat",
    "compute_cs",
    "extract_chord_vectors",
    "compute_ook",
    "compute_ook_percentage",
    "chord_histogram_entropy",
    "ngram_diversity",
    "melody_matchness",
    "tonal_distance",
    "mean_ioi",
    "rhythmic_intensity",
    "rhythmic_density",
    "voice_number",
    "onset_xor_distance",
    "note_overlap",
    "grooving_pattern_similarity",
    # Low-level modules
    "muspy_ext",
    "note_f1",
    "similarity",
    "chord_accuracy",
    "chord_recognition",
    "distribution",
    "advanced",
    "structural",
    "rhythmic",
]

__version__ = "5.0.0"
