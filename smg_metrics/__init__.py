from __future__ import annotations

__all__ = [
    # High-level API
    "single_file_harmony",
    "single_file_rhythm",
    "single_file_quality",
    "pair_eval",
    "distribution_eval",
    # Result containers
    "HarmonySingleResult",
    "RhythmicResult",
    "QualityResult",
    "PairResult",
    "DistributionResult",
    # Individual harmony metrics
    "pitch_class_entropy",
    "scale_consistency",
    "pitch_in_scale_rate",
    "out_of_key_fraction",
    "chord_histogram_entropy",
    # Individual rhythm metrics
    "mean_ioi",
    "grooving_pattern_similarity",
    "ngram_diversity",
    "empty_beat_rate",
    "onset_xor_distance",
    "note_overlap",
    # Individual quality metrics
    "polyphony",
    "polyphony_rate",
    "pitch_entropy",
    "pitch_range",
    "n_pitches_used",
    "n_pitch_classes_used",
    # Chord metrics
    "compute_ca",
    "compute_cs",
    "midi_to_chords",
    "midi_to_chords_dp",
    "recognize_chords",
    "recognize_chords_beat",
    "extract_chord_vectors",
    "clear_cs_model_cache",
    # Low-level modules
    "harmony",
    "rhythm",
    "quality",
    "note_f1",
    "similarity",
    "chord_accuracy",
    "chord_recognition",
    "chord_similarity",
    "distribution",
]

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # High-level API
    "single_file_harmony": ("smg_metrics.single", "single_file_harmony"),
    "single_file_rhythm": ("smg_metrics.single", "single_file_rhythm"),
    "single_file_quality": ("smg_metrics.single", "single_file_quality"),
    "pair_eval": ("smg_metrics.pair", "pair_eval"),
    "distribution_eval": ("smg_metrics.distribution", "compute_all"),
    # Result containers
    "HarmonySingleResult": ("smg_metrics.harmony", "HarmonySingleResult"),
    "RhythmicResult": ("smg_metrics.rhythm", "RhythmicResult"),
    "QualityResult": ("smg_metrics.quality", "QualityResult"),
    "PairResult": ("smg_metrics.pair", "PairResult"),
    "DistributionResult": ("smg_metrics.distribution", "DistributionResult"),
    # Individual harmony metrics
    "pitch_class_entropy": ("smg_metrics.harmony", "pitch_class_entropy"),
    "scale_consistency": ("smg_metrics.harmony", "scale_consistency"),
    "pitch_in_scale_rate": ("smg_metrics.harmony", "pitch_in_scale_rate"),
    "out_of_key_fraction": ("smg_metrics.harmony", "out_of_key_fraction"),
    "chord_histogram_entropy": ("smg_metrics.harmony", "chord_histogram_entropy"),
    # Individual rhythm metrics
    "mean_ioi": ("smg_metrics.rhythm", "mean_ioi"),
    "grooving_pattern_similarity": ("smg_metrics.rhythm", "grooving_pattern_similarity"),
    "ngram_diversity": ("smg_metrics.rhythm", "ngram_diversity"),
    "empty_beat_rate": ("smg_metrics.rhythm", "empty_beat_rate"),
    "onset_xor_distance": ("smg_metrics.rhythm", "onset_xor_distance"),
    "note_overlap": ("smg_metrics.rhythm", "note_overlap"),
    # Individual quality metrics
    "polyphony": ("smg_metrics.quality", "polyphony"),
    "polyphony_rate": ("smg_metrics.quality", "polyphony_rate"),
    "pitch_entropy": ("smg_metrics.quality", "pitch_entropy"),
    "pitch_range": ("smg_metrics.quality", "pitch_range"),
    "n_pitches_used": ("smg_metrics.quality", "n_pitches_used"),
    "n_pitch_classes_used": ("smg_metrics.quality", "n_pitch_classes_used"),
    # Chord metrics
    "compute_ca": ("smg_metrics.chord_accuracy", "compute_ca"),
    "compute_cs": ("smg_metrics.chord_similarity", "compute_cs"),
    "midi_to_chords": ("smg_metrics.chord_accuracy", "midi_to_chords"),
    "midi_to_chords_dp": ("smg_metrics.chord_accuracy", "midi_to_chords_dp"),
    "recognize_chords": ("smg_metrics.chord_recognition", "recognize_chords"),
    "recognize_chords_beat": ("smg_metrics.chord_recognition", "recognize_chords_beat"),
    "extract_chord_vectors": ("smg_metrics.chord_similarity", "extract_chord_vectors"),
    "clear_cs_model_cache": ("smg_metrics.chord_similarity", "clear_cs_model_cache"),
    # Low-level modules
    "harmony": ("smg_metrics", "harmony"),
    "rhythm": ("smg_metrics", "rhythm"),
    "quality": ("smg_metrics", "quality"),
    "note_f1": ("smg_metrics", "note_f1"),
    "similarity": ("smg_metrics", "similarity"),
    "chord_accuracy": ("smg_metrics", "chord_accuracy"),
    "chord_recognition": ("smg_metrics", "chord_recognition"),
    "chord_similarity": ("smg_metrics", "chord_similarity"),
    "distribution": ("smg_metrics", "distribution"),
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_name, attr_name = _LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(module_name)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)
